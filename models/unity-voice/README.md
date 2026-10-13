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

## The designators: how a line says how to say it

Every line is text plus up to three labels. These are exactly what she was trained on, read from
`voice-meta.json` (`delivery_support`, `event_support`). Anything else is refused with the reason, never faked.

**Emotion** (`emotion`, default `neutral`): one of nine.

| Emotion | Trained intensity | Laughter allowed |
|---|---|---|
| `neutral` | 0 only | no |
| `warm` | 0.35 | yes |
| `happy` | 0.35 | yes |
| `amused` | 0.35 | yes |
| `excited` | 0.35 | yes |
| `surprised` | 0.35 | yes |
| `frustrated` | 0.35 | yes |
| `sad` | 0.35 | no |
| `concerned` | 0.35 | no |

**Intensity** (`intensity`): leave it out. She was recorded at one strength per emotion (0.35, or 0 for
neutral); any other number is refused.

**Speech act** (`speech_act` on the server / `--speech-act`): how the sentence is delivered. Every emotion has all
seven. Leave it out and it is guessed from the punctuation (`?` -> a question, `!` -> exclamation, else statement).

| Speech act | Use it for |
|---|---|
| `statement` | a plain sentence |
| `yes_no_question` | "Did the raid start?" |
| `wh_question` | "Where did Scar go?" (who/what/where/when/why/how) |
| `exclamation` | "That actually worked!" |
| `instruction` | telling someone to do something |
| `reassurance` | "It's fine, we've got this." |
| `aside` | a quieter side comment |

**Events in the text:** `[laughter]` anywhere in the line is a real recorded laugh (394 training clips), allowed
with the six emotions marked above. `[breath]` is understood but had no training clips, so it is refused.
Stage directions like `(laughs)` or `(sighs)`, and the characters `[ ] < > { } ` * ` outside those two markers,
are refused: take them out of the text before sending it.

**Pace:** she speaks at her natural pace. `UNITY_VOICE_LENGTH_SCALE` (environment) stretches every sound: 1.0 is
natural, 1.1 a little slower, 0.9 a little faster.

**Long lines:** split at sentence ends automatically; one request can be up to 120 seconds of speech.

### Examples

```
python unity_voice.py "Did you see that?" a.wav --emotion surprised --speech-act yes_no_question
python unity_voice.py "[laughter] okay that was actually great." b.wav --emotion amused
curl -X POST localhost:5123/say -d "{\"text\": \"Stay inside, it is raining fire.\", \"emotion\": \"concerned\", \"speech_act\": \"instruction\"}" -o c.wav
```

A refused request on the server is HTTP 422 with `{"error": "..."}` saying exactly what was not trained.
