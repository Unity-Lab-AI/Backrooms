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
    "voice": dict(base="unsloth/Qwen3-8B", data="voice.jsonl", seq=2048, r=32, epochs=3, lr=1.5e-4, bs=8, ga=2,
                  targets=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]),
    # attention (full + linear) and the shared expert: every layer learns, the 256 routed experts stay as they are
    "player": dict(base="Qwen/Qwen3.6-35B-A3B", data="player.jsonl", seq=12288, r=32, epochs=2, lr=1e-4, bs=1, ga=8,
                   targets=["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "out_proj",
                            "gate_proj", "up_proj", "down_proj"]),
}[KIND]

t0 = time.time()
from unsloth import FastLanguageModel                      # noqa: E402  (unsloth must import first)
import torch                                                # noqa: E402
from datasets import Dataset                                # noqa: E402
from trl import SFTTrainer, SFTConfig                       # noqa: E402
from unsloth.chat_templates import train_on_responses_only  # noqa: E402

model, tok = FastLanguageModel.from_pretrained(CFG["base"], max_seq_length=CFG["seq"], load_in_4bit=False,
                                               dtype=torch.bfloat16)
model = FastLanguageModel.get_peft_model(
    model, r=CFG["r"], lora_alpha=CFG["r"] * 2, lora_dropout=0.0, bias="none",
    # the 35B's routed experts are fused 3D tensors; only these 2D projections get adapters
    target_modules=CFG["targets"], use_gradient_checkpointing="unsloth", random_state=7)
tok = getattr(tok, "tokenizer", tok)                        # a multimodal processor wraps the text tokenizer

tools = json.load(open(os.path.join(W, "data", "tools.json"))) if KIND == "player" else None
rows = []
for line in open(os.path.join(W, "data", CFG["data"]), encoding="utf-8"):
    ex = json.loads(line)
    t = ex.get("tools")
    t = tools if (t is None or t == "TOOLS") else t
    kw = {"tools": t} if t else {}
    text = tok.apply_chat_template(ex["messages"], tokenize=False, enable_thinking=False, **kw)
    rows.append({"text": text})
ds = Dataset.from_list(rows).shuffle(seed=7)
print("examples", len(ds), "longest chars", max(len(r["text"]) for r in rows), flush=True)

trainer = SFTTrainer(
    model=model, tokenizer=tok, train_dataset=ds,
    args=SFTConfig(dataset_text_field="text", max_seq_length=CFG["seq"], per_device_train_batch_size=CFG["bs"],
                   gradient_accumulation_steps=CFG["ga"], num_train_epochs=CFG["epochs"], learning_rate=CFG["lr"],
                   lr_scheduler_type="cosine", warmup_ratio=0.03, logging_steps=5, save_strategy="no",
                   bf16=True, optim="adamw_8bit", weight_decay=0.0, seed=7, output_dir=os.path.join(W, "ckpt", KIND),
                   report_to="none", packing=False))
# loss on her turns only (Qwen chat markers)
trainer = train_on_responses_only(trainer, instruction_part="<|im_start|>user\n",
                                  response_part="<|im_start|>assistant\n")
trainer.train()
print("trained in %.1f min" % ((time.time() - t0) / 60), flush=True)

out = os.path.join(W, "out", KIND + "-merged")
model.save_pretrained(os.path.join(W, "out", KIND + "-lora"))   # the small adapter too, for re-merging later
model.save_pretrained_merged(out, tok, save_method="merged_16bit")
print("merged ->", out, "total %.1f min" % ((time.time() - t0) / 60), flush=True)
