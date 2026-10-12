# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — buildable work only |
| `docs/DECOMPOSED.md` | smallest execution units |
| `docs/TEST.md` | the test phase, `[T]` rows; a build closes none of them |
| `docs/PLAYBOOK.md` / `docs/PLAYSCRIPT.md` | every play order the owner has given, verbatim |
| `docs/playbook.gates.json` / `docs/playbook.rules.json` | the ladder and the owner orders the local model plays by |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## The record, 2026-10-11: Unity's own text-to-speech voice. **It does not sound human. Another AI is to review it.**

Owner, verbatim, at the end of the session: *"okay this does not sound human, im going to have another ai check it out write a now.md of the audio shit and issue u have of it not sounding human for next ai"* and *"u r done just write the now.md for the other ai to look at"*.

**Nothing has been trained and nothing is running on RunPod.** The owner's standing order: *"let me know before u start a training"*. Do not launch without it. Owner leans H100 (*"it would be better to use the H100 yeah?"*).

### What the owner wants

In their words, in order:
- *"i thhink we need to make our own text to speech model"*
- *"we make it from ground up with sampling and what we want"*
- Spec: *"Soft, warm underneath"* + *"Bright and lively"*, *"American, mid-20s"*, *"GPU, expressive"*
- *"#5 withpropr human expression for acutal getting emotional"*
- *"we wont need kokoror right? once we have our own voice with no other peoples shit"*
- *"no we dont need 3 things when we can do one our selves"* (Chatterbox was dropped and uninstalled)
- Emotion source chosen: *"Build emotion into our model"*

The goal: **one voice model that is ours**, sounds like a real young woman on stream, and can actually emote (choked up, laughing, panic, warm). It must run on the rig's 16 GB card beside RimWorld + OBS + the brain, and every spoken line obeys the clean-stream LAW.

### What exists

| Piece | Where | State |
|---|---|---|
| Today's voice | `.claude/tools/unity-speak.py`: stock Piper `en_US-hfc_female-medium` reads every line | live |
| Voice design | `.local/voice-lab/sample.py`, `breed.py`, `round1/`, `round2/`. Kokoro-82M style vectors blended and exaggerated from the mean voice | done |
| The locked voice | `training/voice/unity-voice.pt` = round2 #5 (round1 #4 + #6 at 50/50, exaggerated 1.7x from the mean of 11 Kokoro American-female vectors) | locked by owner |
| Dataset | `training/voice/make_dataset.py`: Kokoro renders #5 reading the text. Local copy `.local/voice-lab/dataset/` (gitignored): 7.63 h, 5,206 clips, 24 kHz | built |
| Our model | `training/voice/`: `prep.py`, `model.py` (FastSpeech2-style, 24.8 M params, own aligner, pitch/energy/duration predictors), `vocoder.py` (HiFi-GAN V1, 13.9 M), `train_acoustic.py`, `train_vocoder.py`, `infer.py` (emotion presets) | written, smoke- and speed-tested, **never trained to completion** |
| Pod pipeline | `training/voice/pod/bootstrap_voice.sh` + `run_voice.sh`, hash-locked by `VOICE_MANIFEST.json` (digest `582b1815a20f1aedd8bb788f8bd43a933432cdf61fcc38a49a63563ae2aedd7c`), cost cap, stops itself, network volume, resumable | ready, not launched |
| Full plan | `training/voice/VOICE_PLAN.md` | current |

### THE ISSUE: why it does not sound human

The owner heard 10 random clips **from the training dataset itself** and said it does not sound human. That is the important point: the dataset *is* the ceiling. A model trained on it can at best reproduce it, so training as things stand would spend ~$38 learning a voice the owner already rejected.

My diagnosis, most likely first:

1. **The source audio is Kokoro, and a blended, exaggerated Kokoro vector is further from human than any stock voice.** Kokoro is an 82M StyleTTS2-style model. Its stock voices are decent, but #5 is a 50/50 blend of two blends, then pushed 1.7x *away from the average voice*. That exaggeration was meant to kill the monotone, and it also pushes the style vector out of the region the model was trained on. Out there you get warbly vowels, odd formants and an uncanny "synthetic" timbre. Round 2 had less-exaggerated siblings: #2-#4 at 1.35x and #1 at 1.0x. **The cheapest test: render the same lines with round2 #1 (1.0x) and #2 (1.35x) and A/B them against #5.**
2. **No human prosody anywhere in the pipeline.** Every clip is a TTS model reading text flat. There is no breath, hesitation, vocal fry, laughter, pitch drop at phrase ends, or uneven timing. The only variation I added was a global speed per clip (0.9-1.12). Kokoro cannot act, which the owner noticed in round 2.
3. **Half the text is unspeakable.** About 45% of clips are "knowledge" sentences scraped from the brain's training data: mod-register boilerplate repeated hundreds of times (*"So I play X for what it does on its own, and I don't build the company plan around it."*), jargon (*"Provisional: optional injury-history UI; no Rimrooms dependency."*), licence text. No human says these lines, so they are read like a manual, and the model would learn manual-reading delivery.
4. **The design itself caps quality.** Even a perfectly trained FastSpeech2 + HiFi-GAN on 7.6 h of synthetic speech sounds like a slightly worse copy of its source: the source's artefacts plus its own. The emotion presets in `infer.py` only shift pitch, energy and pace. That gives exaggerated robot, not emotion. Real emotion needs real emotional examples in the data.
5. **Piper in the A/B was a confound.** In the sampling rounds I spoke the numbers with the old Piper voice before each candidate, so the owner compared candidates to Piper. Fine for picking, but nobody compared anything to a *human* recording.

### What the next AI should check / decide

- **Listen first.** `.local/voice-lab/dataset/wavs/` (any clip; `metadata.csv` has key|text|pace|seconds), `.local/voice-lab/round1/*.wav`, `round2/*.wav`, `unity-ref.wav`. Owner's picks: round1 #4 and #6, round2 #5.
- **Is the timbre the problem or the delivery?** Render one natural line with round2 #1 / #2 / #5 and with the unblended parents (af_bella, af_heart, af_aoede, af_river at 1.0). If a plain stock vector already sounds human enough, the exaggeration broke it.
- **The source-of-truth question is the owner's to decide** (ask with options). A from-scratch model cannot be more human than its training audio, and nothing that runs locally today produces human emotional speech. Realistic paths:
  - (a) **A real person records a script** (1-2 h for a fine-tune, more from scratch), with consent. This is the only clean route to genuinely human and emotional, and it keeps "no other people's voices" literally true only if that person agrees to *be* Unity's voice.
  - (b) **Make the source audio expressive first**, using a modern expressive TTS as the *data generator only*, then train ours on that. The owner rejected Chatterbox as a third thing (*"no we dont need 3 things"*), so present this honestly as a build-time tool, not a runtime piece.
  - (c) **Skip from-scratch** and fine-tune a strong open expressive base on a small set of her lines. Best quality per dollar, but it is "other people's" weights, which the owner did not want.
- **If training goes ahead on synthetic data anyway:** rebuild the dataset with talky lines only (drop the knowledge text), use a less-exaggerated voice, and add more pace and emphasis variety per line. The pipeline handles that without code changes: `make_dataset.py` takes the text, then re-run `manifest.py`.

### Verified engineering (so the next AI does not redo it)

- **Alignment search:** compiled with numba and parallel across the batch; **0 mismatches** against a reference in 180 random cases; 48 ms vs 516 ms on GPU for 96 clips. Batched CTC equals the per-clip loss (11.80138 = 11.80138). Test: `.local/scratch/mas-check.py`.
- **4070 speeds:** acoustic 85k frames/s; vocoder 3.41 steps/s at 93-98% GPU; both together 100% GPU.
- **Held-out:** 2% by name hash. After a few hundred steps held-out tracks train, so it learns rather than memorizes; it does **not** mean it sounds good.
- **Pod digest:** a fresh GitHub clone checks clean against `582b1815…`.
- **Gotchas hit and fixed:**
  - Git Bash rewrites `/paths` in sparse-checkout, so use `MSYS_NO_PATHCONV=1` locally; the Linux pod is unaffected.
  - Python `open(..., "w")` on Windows writes CRLF and breaks the pod's hash check, so write with `newline="\n"`.
  - `grep $'\r'` does not detect CR on this machine, so check bytes in Python.
  - Never `git add` `.local/voice-lab` checkpoints: GitHub rejects files over 100 MB. They are gitignored now.

### Other current state (same session, 2026-10-10/11)

- **Brain:** `unity-brain` (Qwen3.5-9B + LoRA, IQ4_XS) is applied in Ollama. It plays, chats and reads screens. **Its voice did not replace today's voice in the pod eval** (pass 0.944 vs 0.984), but a local 10-line A/B went brain 10 / old 6, so the owner may flip it (`training/models/brain-voice.ok`). The pods were deleted by RunPod; the gguf was downloaded first. Next training must use a network volume.
- **Before streaming:** RimBridgeServer must be re-enabled in RimSort (the owner disabled it), or she cannot see or act.
- **Mod:** the working copy is the game's `Mods/Rimrooms - Async Industries` (0.13.0-dev, works in multiplayer). It equals `Mod/` and the build manifest; the GitHub mod repo was re-exported to match (`51540ff`); the friends zip on the Desktop matches. **A game is open using the mod. Do NOT stage or change the game's Mods folder unless the owner says so.**
- **Forgejo:** pushes are held, and its SSH host key changed. Unverified; ask Sponge before clearing it.
- **Branches:** `feature/bug-testing`, `develop` and `main` are all pushed to `Unity-Lab-AI/Backrooms`; last cascade PRs #25/#26.
