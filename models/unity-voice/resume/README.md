# Resume training (not needed to use the voice)

For continuing the vocoder's training, not for speaking. The voice itself is `../acoustic.pt` + `../vocoder.pt`.

| File | What it is |
|---|---|
| `vocoder-full-step25000.pt` | The full working vocoder from the 2026-10-12 pod run: generator (13.9M), discriminators (70.7M), both optimizers, schedulers and random state. **Step 25,000**, saved on the pod as a progress snapshot. ~1 GB. |
| `vocoder.log.txt` | The run's log: the held-out mel score every 5,000 steps, to the end (step 120,000). |

**This is not where the run ended.** The run finished at step 120,000 (100,000 on real audio, then 20,000 polishing on
the acoustic model's own output). The full checkpoint at the end was never pulled before the pods were deleted, so it
is gone. Step 25,000 is the latest full checkpoint that exists (copied from
`D:\voice-lab\pod-results\voice-2026-10-12\out\progress\...\20261012T184525Z-898\loaded-checkpoint\`; a later
snapshot there is a truncated partial download). The shipped `../vocoder.pt` is the step-120,000 generator only.

Held-out score from the log: 0.221 at 25k, best 0.189 at 100k. From 105k on the vocoder trains on the acoustic model's
own output and the number jumps to ~0.50: a different input, not a regression.
