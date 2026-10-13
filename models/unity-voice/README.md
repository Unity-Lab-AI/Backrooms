# unity-voice

Unity's speaking voice. Text in, speech out (24 kHz wav), with emotion and recorded laughter/breath.
Everything needed to run it is in this folder.

## What's here

| File | What it is |
|---|---|
| `acoustic.pt` | Turns phonemes into sound features (109 MB) |
| `vocoder.pt` | Turns those features into audio (56 MB) |
| `voice-meta.json` | Her phoneme list, normalisation and the deliveries she was trained on |
| `unity_voice.py` | The loader: `Voice().say(...)` and a command line |
| `serve.py` | Optional local HTTP server, so a program can get a line with one request |
| `model.py`, `vocoder.py`, `infer.py`, `dataset_contract.py`, `speech_text.py`, `speech_turns.py`, `feature_arrays.py`, `student_state.py` | The model code the loader needs |
| `requirements.txt` | Python packages |

## Setup

Python 3.10+. A CUDA GPU is used when present (~0.5 GB); it also runs on CPU, slower.

```
pip install -r requirements.txt
```

`misaki` must be exactly 0.9.4 (it turns text into the phonemes she learned). It uses espeak-ng for words it
doesn't know; on Windows install espeak-ng, on Linux `apt install espeak-ng`.

## Use it

Command line:

```
python unity_voice.py "Hey chat, what are we doing today?" out.wav --emotion amused --intensity 0.35
```

From Python:

```python
from unity_voice import Voice
import soundfile as sf
voice = Voice()                                   # loads once
wav = voice.say("That raid went badly.", "concerned", 0.4)
sf.write("line.wav", wav, 24000)
```

As a server (127.0.0.1 only):

```
python serve.py --port 5123
curl -X POST localhost:5123/say -d "{\"text\": \"Hello chat.\", \"emotion\": \"happy\"}" -o line.wav
curl localhost:5123/health
```

## Options

- **emotion:** `neutral`, `warm`, `happy`, `amused`, `excited`, `sad`, `concerned`, `frustrated`, `surprised`
- **intensity:** 0 to 1 (default 0.35; 0 for neutral)
- **speech act** (optional, guessed from punctuation otherwise): `statement`, `yes_no_question`, `wh_question`,
  `exclamation`, `instruction`, `reassurance`, `aside`
- **laughter / breath:** put `[laughter]` or `[breath]` in the text
- **pace:** `UNITY_VOICE_LENGTH_SCALE` environment variable; 1.0 is her natural pace, higher is slower

A delivery she was never trained on (an unknown emotion, or an intensity outside what she recorded for that
emotion) is refused with the reason instead of being faked.
