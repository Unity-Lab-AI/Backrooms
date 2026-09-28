"""Render original deterministic short cues; never plays audio or starts RimWorld."""
from pathlib import Path
import hashlib
import json
import math
import random
import struct
import wave

ROOT = Path(__file__).resolve().parents[2]
RATE = 48000
MASTER = ROOT / 'assets/source/phase2/audio'
PACKAGE = ROOT / 'Mod/Rimrooms - Async Industries/1.6/Sounds/Rimrooms'


def render(name, duration, synth, seed):
    rng = random.Random(seed)
    count = round(RATE * duration)
    values = []
    for index in range(count):
        t = index / RATE
        # Smooth both edges; no abrupt step or loud transient.
        edge = min(1.0, t / 0.07, (duration - t) / 0.16)
        envelope = math.sin(max(0.0, edge) * math.pi / 2) ** 2
        values.append(synth(t, rng) * envelope)
    peak = max(abs(v) for v in values)
    gain = 0.18 / max(peak, 1e-9)
    pcm = [round(max(-1, min(1, value * gain)) * 32767) for value in values]
    data = struct.pack('<' + 'h' * len(pcm), *pcm)
    for folder in (MASTER, PACKAGE):
        folder.mkdir(parents=True, exist_ok=True)
        with wave.open(str(folder / (name + '.wav')), 'wb') as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(RATE)
            output.writeframes(data)
    rms = math.sqrt(sum((sample / 32768) ** 2 for sample in pcm) / len(pcm))
    path = PACKAGE / (name + '.wav')
    return dict(name=name, durationSeconds=duration, sampleRate=RATE, channels=1,
                bitsPerSample=16, samplePeakDbfs=20 * math.log10(max(abs(v) for v in pcm) / 32768),
                rmsDbfs=20 * math.log10(rms), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                masterPath=(MASTER / (name + '.wav')).relative_to(ROOT).as_posix(),
                packagePath=path.relative_to(ROOT).as_posix())


def gate_rise(t, rng):
    phase = 2 * math.pi * (62 * t + 4 * t * t)
    return (math.sin(phase) + 0.26 * math.sin(phase * 2) + 0.10 * math.sin(phase * 3)) * (0.35 + 0.65 * min(t, 1))


def warning(t, rng):
    pulse = max(0.0, math.sin(math.pi * 3 * t)) ** 2
    return pulse * (math.sin(2 * math.pi * 440 * t) + 0.18 * math.sin(2 * math.pi * 660 * t))


def radio(t, rng):
    bed = rng.uniform(-1, 1) * 0.16
    tone = math.sin(2 * math.pi * 780 * t) * math.exp(-7 * t)
    return bed + tone


def spatial(t, rng):
    return math.sin(2 * math.pi * 113 * t) * math.sin(math.pi * t / 1.4) ** 2 + 0.08 * rng.uniform(-1, 1)


if __name__ == '__main__':
    rows = [render('RR_GatePowerRise', 2.0, gate_rise, 7101),
            render('RR_GateWarning', 1.1, warning, 7102),
            render('RR_FieldRadio', 0.6, radio, 7103),
            render('RR_SpatialTell', 1.4, spatial, 7104)]
    record = dict(schemaVersion=1, creator='Operator (original procedural audio)',
                  license='MIT - original project assets', source='tools/assets/render-phase2-audio.py',
                  review='Deterministically rendered original PCM; sample peak and RMS calculated. No playback or in-game mix review performed. RMS is not LUFS or true peak.',
                  assets=rows)
    destination = ROOT / 'docs/implementation/assets/phase2-original-audio.json'
    destination.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'Rendered {len(rows)} original cues. No audio was played.')
