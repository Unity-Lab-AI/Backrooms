"""Train one of Unity's shells (a LoRA) on the pod, merge it into the base, and write a 16-bit HF folder.

    python train.py voice   -> /workspace/out/voice-merged   (Qwen3-8B, lines she says on stream)
    python train.py player  -> /workspace/out/player-merged  (Qwen3.6-35B-A3B, tool calls that play RimWorld)

Data comes from /workspace/data/{voice,player}.jsonl (+ tools.json for the player), built and checked locally by
training/check_voice.py and training/check_player.py. Loss is on her (assistant) turns only.
"""
import json, os, sys, time

KIND = sys.argv[1]
W = "/workspace"
CFG = {
    "voice": dict(base="unsloth/Qwen3-8B", data=["voice.jsonl", "voice_stream.jsonl"], seq=3072, r=32, epochs=3, lr=1.5e-4, bs=8, ga=2,
                  targets=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]),
    # attention (full + linear) and the shared expert: every layer learns, the 256 routed experts stay as they are
    "player": dict(base="Qwen/Qwen3.6-35B-A3B", data=["player.jsonl", "knowledge_game.jsonl", "knowledge_mods.jsonl", "knowledge_code.jsonl", "knowledge_walkthrough.jsonl"], seq=20480, r=32, epochs=1, lr=1e-4, bs=1, ga=8,
                   targets=["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "out_proj",
                            "gate_proj", "up_proj", "down_proj"]),
}[KIND]

t0 = time.time()
from unsloth import FastLanguageModel                      # noqa: E402  (unsloth must import first)
import torch                                                # noqa: E402
from datasets import Dataset                                # noqa: E402
import re                                                   # noqa: E402
from transformers import Trainer, TrainingArguments, DataCollatorForSeq2Seq  # noqa: E402

model, tok = FastLanguageModel.from_pretrained(CFG["base"], max_seq_length=CFG["seq"], load_in_4bit=False,
                                               dtype=torch.bfloat16)
model = FastLanguageModel.get_peft_model(
    model, r=CFG["r"], lora_alpha=CFG["r"] * 2, lora_dropout=0.0, bias="none",
    # the 35B's routed experts are fused 3D tensors; only these 2D projections get adapters
    target_modules=CFG["targets"], use_gradient_checkpointing="unsloth", random_state=7)
tok = getattr(tok, "tokenizer", tok)                        # a multimodal processor wraps the text tokenizer

tools = json.load(open(os.path.join(W, "data", "tools.json"))) if KIND == "player" else None

SPAN = re.compile(r"<\|im_start\|>assistant\n(.*?<\|im_end\|>)", re.S)
rows, skipped = [], 0
def _lines():
    for name in CFG["data"]:
        f = os.path.join(W, "data", name)
        if os.path.exists(f):
            yield from open(f, encoding="utf-8")
        else:
            print("missing data file (skipped):", name, flush=True)


for line in _lines():
    ex = json.loads(line)
    t = ex.get("tools")
    t = tools if (t is None or t == "TOOLS") else t
    kw = {"tools": t} if t else {}
    msgs = [{k: v for k, v in m.items() if k != "weight"} for m in ex["messages"]]
    text = tok.apply_chat_template(msgs, tokenize=False, enable_thinking=False, **kw)
    # loss only on her turns; a turn marked weight 0 (a mistake the game refuses) is context, not a lesson
    keep = [m.get("weight", 1) != 0 for m in ex["messages"] if m["role"] == "assistant"]
    spans = [(m.start(1), m.end(1)) for m in SPAN.finditer(text)]
    if len(spans) != len(keep):
        keep = [True] * len(spans)
    spans = [s for s, k in zip(spans, keep) if k]
    enc = tok(text, return_offsets_mapping=True, truncation=True, max_length=CFG["seq"], add_special_tokens=False)
    labels = [tid if any(a <= o[0] < b for a, b in spans) else -100
              for tid, o in zip(enc["input_ids"], enc["offset_mapping"])]
    if all(l == -100 for l in labels):
        skipped += 1
        continue
    rows.append({"input_ids": enc["input_ids"], "attention_mask": enc["attention_mask"], "labels": labels})
ds = Dataset.from_list(rows).shuffle(seed=7)
print("examples", len(ds), "skipped", skipped, "longest tokens", max(len(r["input_ids"]) for r in rows), flush=True)

trainer = Trainer(
    model=model, train_dataset=ds,
    data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100),
    args=TrainingArguments(per_device_train_batch_size=CFG["bs"], gradient_accumulation_steps=CFG["ga"],
                           num_train_epochs=CFG["epochs"], learning_rate=CFG["lr"], lr_scheduler_type="cosine",
                           warmup_ratio=0.03, logging_steps=5, save_strategy="no", bf16=True, optim="adamw_8bit",
                           weight_decay=0.0, seed=7, output_dir=os.path.join(W, "ckpt", KIND), report_to="none",
                           group_by_length=True, remove_unused_columns=False))
trainer.train()
print("trained in %.1f min" % ((time.time() - t0) / 60), flush=True)

out = os.path.join(W, "out", KIND + "-merged")
model.save_pretrained(os.path.join(W, "out", KIND + "-lora"))   # the small adapter too, for re-merging later
model.save_pretrained_merged(out, tok, save_method="merged_16bit")
print("merged ->", out, "total %.1f min" % ((time.time() - t0) / 60), flush=True)
