"""Train Unity's single brain (a LoRA on Qwen3.5-9B), merge it into the base, and write a 16-bit HF folder.

    python train.py              -> /workspace/out/brain-merged (+ brain-lora, + calib.txt for the imatrix)
    python train.py --preflight  -> builds the whole dataset and runs 2 steps on the longest rows, then exits
                                    (a cheap proof the run fits in memory before the paid hours start)

Data: /workspace/data/brain/train.jsonl (+ tools.json, screens/), built and checked locally by
training/build_brain.py and training/check_brain.py. eval_voice.jsonl / eval_tools.jsonl are never read here.
Loss is on her (assistant) turns only; a turn marked weight 0 (a mistake the game refused) is context, not a lesson.
The vision tower is not trained: screen rows teach the language side to answer about what the projector sees.
"""
import json, os, random, re, sys, time

W = "/workspace"
D = os.path.join(W, "data", "brain")
PREFLIGHT = "--preflight" in sys.argv
CFG = dict(base=os.environ.get("BRAIN_BASE", "Qwen/Qwen3.5-9B"), seq=24576, r=32, epochs=2, lr=1e-4, bs=2, ga=8,
           # full attention, the linear-attention (gated delta) projections and the MLP: every text layer learns
           targets=["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "out_proj",
                    "gate_proj", "up_proj", "down_proj"])
# Owner: "make sure we are peggin these GPUS pod when we do it". The effective batch stays 16 sequences per optimizer
# step (what is learned does not change); BRAIN_BS sets how many go through the GPU at once, and run.sh picks the
# largest of 8/4/2 that survives the preflight on the longest rows, so the H100 is filled instead of half idle.
CFG["bs"] = int(os.environ.get("BRAIN_BS", CFG["bs"]))
if CFG["bs"] < 1 or 16 % CFG["bs"]:
    raise SystemExit("BRAIN_BS must divide 16")
CFG["ga"] = 16 // CFG["bs"]

t0 = time.time()
from unsloth import FastLanguageModel                      # noqa: E402  (unsloth must import first)
import torch                                                # noqa: E402
from datasets import Dataset                                # noqa: E402
from transformers import Trainer, TrainingArguments        # noqa: E402

model, proc = FastLanguageModel.from_pretrained(CFG["base"], max_seq_length=CFG["seq"], load_in_4bit=False,
                                                dtype=torch.bfloat16)
model = FastLanguageModel.get_peft_model(
    model, r=CFG["r"], lora_alpha=CFG["r"] * 2, lora_dropout=0.0, bias="none",
    target_modules=CFG["targets"], use_gradient_checkpointing="unsloth", random_state=7)
tok = getattr(proc, "tokenizer", proc)                      # the multimodal processor wraps the text tokenizer
tools = json.load(open(os.path.join(D, "tools.json"), encoding="utf-8"))

SPAN = re.compile(r"<\|im_start\|>assistant\n(.*?<\|im_end\|>)", re.S)
rows, skipped, cut = [], 0, 0
for line in open(os.path.join(D, "train.jsonl"), encoding="utf-8"):
    ex = json.loads(line)
    kw = {"tools": tools} if ex.get("tools") == "TOOLS" else {}
    msgs = [{k: v for k, v in m.items() if k != "weight"} for m in ex["messages"]]
    text = tok.apply_chat_template(msgs, tokenize=False, enable_thinking=False, **kw)
    keep = [m.get("weight", 1) != 0 for m in ex["messages"] if m["role"] == "assistant"]
    spans = [(m.start(1), m.end(1)) for m in SPAN.finditer(text)]
    if len(spans) != len(keep):
        keep = [True] * len(spans)
    spans = [s for s, k in zip(spans, keep) if k]
    images = ex.get("images") or []
    if images:
        from PIL import Image
        pics = [Image.open(os.path.join(D, p)).convert("RGB") for p in images]
        enc = proc(text=[text], images=pics, return_offsets_mapping=True, add_special_tokens=False)
        enc = {k: (v[0] if k in ("input_ids", "attention_mask", "offset_mapping") else v) for k, v in enc.items()}
    else:
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
    if len(enc["input_ids"]) > CFG["seq"]:
        if images:                                          # an image row is never cut through its image tokens
            skipped += 1
            continue
        cut += 1
        enc = {k: v[:CFG["seq"]] for k, v in enc.items()}
    labels = [tid if any(a <= o[0] < b for a, b in spans) else -100
              for tid, o in zip(enc["input_ids"], enc["offset_mapping"])]
    if all(l == -100 for l in labels):
        skipped += 1
        continue
    row = {"input_ids": list(enc["input_ids"]), "attention_mask": list(enc["attention_mask"]), "labels": labels}
    # only the paths are kept; the pixels are made again per batch in collate(). Holding every 4K screenshot's
    # pixel_values as Python lists took ~1.5 GB each and the pod was OOM-killed at step 8 (2026-10-12). Every row
    # carries the key (empty for text rows) because Dataset.from_list takes its columns from the first row.
    row["image_paths"] = list(images)
    rows.append(row)
print("examples", len(rows), "skipped", skipped, "cut to seq", cut, "longest tokens",
      max(len(r["input_ids"]) for r in rows), flush=True)


def collate(batch):
    """Pad text; images (if any) are concatenated the way Qwen's vision forward expects."""
    n = max(len(b["input_ids"]) for b in batch)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    out = {"input_ids": torch.tensor([b["input_ids"] + [pad] * (n - len(b["input_ids"])) for b in batch]),
           "attention_mask": torch.tensor([b["attention_mask"] + [0] * (n - len(b["attention_mask"])) for b in batch]),
           "labels": torch.tensor([b["labels"] + [-100] * (n - len(b["labels"])) for b in batch])}
    paths = [p for b in batch for p in (b.get("image_paths") or [])]
    if paths:
        from PIL import Image
        pics = [Image.open(os.path.join(D, p)).convert("RGB") for p in paths]
        img = proc.image_processor(images=pics, return_tensors="pt")   # same processor and settings as tokenizing
        out["pixel_values"] = img["pixel_values"].to(torch.bfloat16)
        out["image_grid_thw"] = img["image_grid_thw"]
    return out


if PREFLIGHT:                                               # the longest rows, plus any image row, 2 steps
    rows.sort(key=lambda r: -len(r["input_ids"]))
    rows = rows[:CFG["bs"] * CFG["ga"] * 2] + [r for r in rows if r.get("image_paths")][:2]
ds = Dataset.from_list(rows).shuffle(seed=7)


def _args(**kw):
    """TrainingArguments with only the settings this transformers version accepts; settings that change what is
    learned or whether progress survives are never dropped silently -- the run stops instead."""
    import inspect
    ok = set(inspect.signature(TrainingArguments.__init__).parameters)
    dropped = sorted(k for k in kw if k not in ok)
    if dropped:
        print("TrainingArguments: not supported here, skipped:", dropped, flush=True)
    with open(os.path.join(W, "gguf", "dropped-options.txt"), "w") as f:
        f.write("".join(k + "\n" for k in dropped))
    must = {"per_device_train_batch_size", "gradient_accumulation_steps", "num_train_epochs", "learning_rate",
            "bf16", "save_strategy", "save_steps", "save_total_limit", "output_dir", "seed", "max_steps"}
    if must & set(dropped):
        raise SystemExit("required TrainingArguments unsupported: %s" % sorted(must & set(dropped)))
    return TrainingArguments(**{k: v for k, v in kw.items() if k in ok})


ckdir = os.path.join(W, "ckpt", "preflight" if PREFLIGHT else "brain")
trainer = Trainer(
    model=model, train_dataset=ds, data_collator=collate,
    args=_args(per_device_train_batch_size=CFG["bs"], gradient_accumulation_steps=CFG["ga"],
               num_train_epochs=CFG["epochs"], max_steps=2 if PREFLIGHT else -1, learning_rate=CFG["lr"],
               lr_scheduler_type="cosine", warmup_steps=15, logging_steps=5, save_strategy="steps", save_steps=40,
               save_total_limit=2, bf16=True, optim="adamw_8bit", weight_decay=0.0, seed=7, output_dir=ckdir,
               report_to="none", group_by_length=not PREFLIGHT, remove_unused_columns=False, dataloader_num_workers=0))
# an interrupted run resumes from its newest checkpoint (run.sh clears them whenever the inputs change)
resume = not PREFLIGHT and os.path.isdir(ckdir) and any(d.startswith("checkpoint-") for d in os.listdir(ckdir))
if resume:
    print("resuming from the newest checkpoint in", ckdir, flush=True)
trainer.train(resume_from_checkpoint=True if resume else None)
print("peak GPU memory %.1f GB" % (torch.cuda.max_memory_allocated() / 2 ** 30), flush=True)
if PREFLIGHT:
    print("preflight ok in %.1f min" % ((time.time() - t0) / 60), flush=True)
    sys.exit(0)
print("trained in %.1f min" % ((time.time() - t0) / 60), flush=True)

out = os.path.join(W, "out", "brain-merged")
model.save_pretrained(os.path.join(W, "out", "brain-lora"))   # the small adapter too, for re-merging later
model.save_pretrained_merged(out, proc, save_method="merged_16bit")
# calibration text for the imatrix quant: her own rendered conversations, so the quant keeps what she uses
random.seed(7)
sample = random.sample(open(os.path.join(D, "train.jsonl"), encoding="utf-8").readlines(), 600)
with open(os.path.join(W, "out", "calib.txt"), "w", encoding="utf-8") as f:
    for line in sample:
        ex = json.loads(line)
        if ex.get("images"):
            continue
        kw = {"tools": tools} if ex.get("tools") == "TOOLS" else {}
        f.write(tok.apply_chat_template(ex["messages"], tokenize=False, enable_thinking=False, **kw)[-12000:] + "\n")
print("merged ->", out, "total %.1f min" % ((time.time() - t0) / 60), flush=True)
