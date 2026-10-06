"""Author original gate/event PCM assets; no playback, game launch or SoundDef edits.

Requires Python 3.10+ and NumPy. Run with --group oneshots, --group loops, or
--group all (default). Existing four shipping cues are hash-checked and untouched.
All sources are mathematical oscillators, filtered seeded noise, and envelopes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RATE = 48_000
MASTER = ROOT / "assets/source/audio"
PACKAGE = ROOT / "Mod/Rimrooms - Async Industries/1.6/Sounds/Rimrooms"
DELIVERY = ROOT / "outputs/gate-cycle-assets-2026-10-06/audio"
TAU = 2.0 * math.pi
EXISTING = ("RR_GatePowerRise", "RR_GateWarning", "RR_FieldRadio", "RR_SpatialTell")


def axis(seconds: float) -> np.ndarray:
    return np.arange(round(seconds * RATE), dtype=np.float64) / RATE


def smooth_noise(rng, count, low, high):
    """A seeded smooth noise band, normalized to unit RMS before mixing."""
    frequencies = np.fft.rfftfreq(count, 1 / RATE)
    spectrum = np.fft.rfft(rng.normal(0, 1, count))
    high_pass = 1 - np.exp(-np.power(frequencies / max(low, 1), 4))
    low_pass = np.exp(-np.power(frequencies / high, 4))
    noise = np.fft.irfft(spectrum * high_pass * low_pass, n=count)
    return noise / max(float(np.sqrt(np.mean(noise * noise))), 1e-12)


def interval(t, start, length, attack=0.006, release=0.018):
    u = t - start
    result = np.zeros_like(t)
    active = (u >= 0) & (u < length)
    v = u[active]
    rise = np.minimum(v / attack, 1)
    fall = np.minimum((length - v) / release, 1)
    result[active] = np.sin(np.minimum(rise, fall) * math.pi / 2) ** 2
    return result


def strike(t, start, modes, decay=0.1, level=1.0):
    """Inharmonic, damped resonances: a mechanism, not a musical note."""
    u = np.maximum(t - start, 0)
    active = t >= start
    attack = 1 - np.exp(-u / 0.0016)
    out = np.zeros_like(t)
    for index, frequency in enumerate(modes):
        modal_decay = decay / (1 + 0.31 * index)
        out += (np.sin(TAU * frequency * u) * np.exp(-u / modal_decay)
                / (1 + 0.55 * index))
    return level * out * attack * active


def motor(t, phase, gain=1.0):
    return gain * (np.sin(phase) + 0.24 * np.sin(2.03 * phase)
                   + 0.08 * np.sin(4.11 * phase))


def ramp_up(t, rng):
    length = len(t) / RATE
    progress = t / length
    # Integral of f(t)=42+93*(t/L)^1.45. Rev rises to 135 Hz and
    # deliberately remains at speed until the short anti-click tail.
    phase = TAU * (42 * t + 93 * length * progress ** 2.45 / 2.45)
    pressure = smooth_noise(rng, len(t), 150, 1700)
    pulse = 0.84 + 0.16 * np.sin(TAU * (0.6 * t + 0.47 * t * t))
    return ((0.34 + 0.66 * progress ** 0.7) * motor(t, phase) * pulse
            + pressure * (0.025 + 0.038 * progress))


def calibrate(t, rng):
    # A subdued detent and relay click, little ringing: repeated four times.
    noise = smooth_noise(rng, len(t), 480, 5200)
    return (strike(t, 0.002, (247, 671, 1523), 0.10, 0.75)
            + strike(t, 0.082, (391, 1327), 0.065, 0.22)
            + 0.16 * noise * np.exp(-t / 0.045)
            + 0.025 * noise * np.exp(-t / 0.18))


def activate(t, rng):
    # A pressure release and deep settling motor, not an explosion.
    u = np.maximum(t - 0.055, 0)
    phase = TAU * (49 * u + 45 * 0.26 * (1 - np.exp(-u / 0.26)))
    pressure = smooth_noise(rng, len(t), 110, 2300)
    swell = (1 - np.exp(-t / 0.030)) * np.exp(-t / 0.55)
    return (0.92 * motor(t, phase) * swell
            + 0.20 * pressure * swell
            + strike(t, 0.007, (151, 383, 991), 0.23, 0.35)
            + strike(t, 0.34, (201, 827), 0.14, 0.18)
            + 0.075 * np.sin(TAU * 49 * t) * np.exp(-t / 0.92))


def ramp_down(t, rng):
    # Rev decelerates to a resting mechanism; final latch decays to silence.
    phase = TAU * (38 * t + 107 * 0.62 * (1 - np.exp(-t / 0.62)))
    noise = smooth_noise(rng, len(t), 130, 1800)
    rev = motor(t, phase) * np.exp(-t / 0.72)
    latch = strike(t, 1.85, (103, 319, 787), 0.145, 0.35)
    settled = 0.06 * np.sin(TAU * 38 * t) * np.exp(-t / 0.63)
    return rev + 0.05 * noise * np.exp(-t / 0.7) + latch + settled


def emergency(t, rng):
    noise = smooth_noise(rng, len(t), 240, 3400)
    phase = TAU * (81 * t + 6 * np.sin(TAU * 2.4 * t) / (TAU * 2.4))
    # Irregular gaps and three uneven mechanical impacts, no warning siren.
    failure = (0.25 + 0.75 * np.maximum(0, np.sin(TAU * (3.3 * t + 0.71 * t * t))))
    failing_motor = 0.5 * motor(t, phase) * failure * np.exp(-t / 0.8)
    out = failing_motor
    for start, level in ((0.013, 1.0), (0.39, 0.68), (0.87, 0.44)):
        out += strike(t, start, (117, 293, 733, 1741), 0.18, level)
        out += 0.08 * noise * np.exp(-np.maximum(t - start, 0) / 0.08) * (t >= start)
    return out + 0.015 * noise * np.exp(-t / 0.37)


def cutoff(t, rng):
    noise = smooth_noise(rng, len(t), 600, 5400)
    return (strike(t, 0.003, (132, 347, 1091), 0.09, 1.0)
            + strike(t, 0.053, (287, 947), 0.07, 0.3)
            + noise * 0.22 * np.exp(-t / 0.027)
            + noise * 0.025 * np.exp(-t / 0.16))


def section(t, rng):
    noise = smooth_noise(rng, len(t), 350, 4100)
    return (strike(t, 0.004, (171, 529, 1381), 0.12, 0.62)
            + strike(t, 0.19, (184, 547, 1433), 0.12, 0.75)
            + strike(t, 0.37, (126, 317, 877), 0.15, 0.98)
            + noise * 0.08 * interval(t, 0.006, 0.38) * np.exp(-t / 0.32)
            + noise * 0.012 * np.exp(-t / 0.22))


def journal(t, rng):
    paper = smooth_noise(rng, len(t), 1100, 6800)
    page = interval(t, 0.003, 0.29, 0.006, 0.027)
    page *= 0.65 + 0.35 * np.sin(TAU * 23.0 * t) ** 2
    return (paper * 0.28 * page
            + strike(t, 0.31, (209, 743, 1531), 0.10, 0.46)
            + strike(t, 0.48, (121, 387), 0.08, 0.13)
            + 0.012 * paper * np.exp(-t / 0.21))


def analysis(t, rng):
    noise = smooth_noise(rng, len(t), 800, 4500)
    phase = TAU * (680 * t - 57 * t * t)
    verification = 0.18 * np.sin(phase) * interval(t, 0.08, 0.19) * np.exp(-t / 0.2)
    return (strike(t, 0.004, (261, 947, 1913), 0.10, 0.58)
            + verification + strike(t, 0.36, (347, 1187), 0.14, 0.33)
            + noise * 0.024 * np.exp(-t / 0.25))


def marker(t, rng):
    noise = smooth_noise(rng, len(t), 900, 5700)
    return (strike(t, 0.002, (341, 1297), 0.06, 0.60)
            + strike(t, 0.089, (791, 2111), 0.065, 0.12)
            + noise * 0.09 * np.exp(-t / 0.034)
            + noise * 0.01 * np.exp(-t / 0.12))


def contract(t, rng):
    # Thermal receipt feed, paper pull, and a restrained approval stamp.
    paper = smooth_noise(rng, len(t), 900, 6200)
    motor_phase = TAU * (137 * t + 0.4 * np.sin(TAU * 9 * t))
    feed = interval(t, 0.004, 0.49)
    feed_sound = (0.21 * np.sin(motor_phase) + 0.10 * paper) * feed
    tear = paper * 0.19 * interval(t, 0.55, 0.14, 0.004, 0.033)
    return (feed_sound + tear + strike(t, 0.72, (167, 491, 1259), 0.095, 0.61)
            + paper * 0.01 * np.exp(-t / 0.22))


def spin_loop(t, rng):
    # Every frequency and modulation is an integer number of periods in 3 s.
    length = len(t) / RATE
    pulse = 0.77 + 0.13 * np.cos(TAU * 2 * t / length) + 0.10 * np.cos(TAU * 4 * t / length)
    motor_bed = (np.sin(TAU * 61 * t) + 0.22 * np.sin(TAU * 122 * t)
                 + 0.085 * np.sin(TAU * 183 * t) + 0.07 * np.sin(TAU * 287 * t))
    # DFT-filtered noise is periodic too, including its boundary derivative.
    body = smooth_noise(rng, len(t), 85, 1250)
    return motor_bed * pulse + 0.055 * body * (0.82 + 0.18 * np.cos(TAU * t / length))


def open_loop(t, rng):
    # A quieter, stable electrical mechanism with a slow periodic pulse.
    length = len(t) / RATE
    pulse = 0.91 + 0.065 * np.cos(TAU * t / length) + 0.025 * np.cos(TAU * 3 * t / length)
    body = smooth_noise(rng, len(t), 110, 1000)
    motor_bed = (np.sin(TAU * 48 * t) + 0.19 * np.sin(TAU * 96 * t)
                 + 0.07 * np.sin(TAU * 167 * t) + 0.035 * np.sin(TAU * 333 * t))
    return motor_bed * pulse + 0.035 * body


# name, duration, renderer, seed, peak linear full scale, loop, brief
SPECS = (
    ("RR_GateRampUp", 2.5, ramp_up, 80601, 0.18, False, "Ascending industrial rev; holds its upper speed and ends unresolved."),
    ("RR_GateCalibrate", 0.6, calibrate, 80602, 0.115, False, "Quiet dry detent and relay; suited to four repeated calibration beats."),
    ("RR_GateActivate", 2.0, activate, 80603, 0.21, False, "Pressure release and low settling motor; the gate-cycle payoff."),
    ("RR_GateRampDown", 2.5, ramp_down, 80604, 0.18, False, "Descending motor, final latch and damped settling; resolves to rest."),
    ("RR_GateEmergency", 2.0, emergency, 80605, 0.205, False, "Uneven stressed impacts and a sputtering mechanism; distinct from the existing warning cue."),
    ("RR_CutoffThrown", 0.45, cutoff, 80606, 0.16, False, "Heavy switch throw, contact clack and brief spring rattle."),
    ("RR_SectionAssembled", 0.8, section, 80607, 0.16, False, "Two restrained assembly strikes and a locking detent."),
    ("RR_JournalFiled", 0.7, journal, 80608, 0.12, False, "Paper friction, archive latch and a muted settling tap."),
    ("RR_AnalysisComplete", 1.0, analysis, 80609, 0.12, False, "Instrument click, short verification signal and relay release."),
    ("RR_MarkerSet", 0.4, marker, 80610, 0.105, False, "Small plastic click and a restrained lamp/relay acknowledgement."),
    ("RR_ContractPaid", 1.0, contract, 80611, 0.12, False, "Receipt feed, paper pull and approval stamp; no jackpot jingle."),
    ("RR_GateSpinLoop", 3.0, spin_loop, 80612, 0.10, True, "Periodic low motor, faint cycling pulse and mechanical texture."),
    ("RR_GateOpenLoop", 4.0, open_loop, 80613, 0.065, True, "Quieter stable motor presence; a restrained slow pulse."),
)


def dbfs(value):
    return round(20 * math.log10(max(float(value), 1e-12)), 4)


def preserved_hashes():
    paths = [PACKAGE / f"{name}.wav" for name in EXISTING]
    paths += [ROOT / "assets/source/phase2/audio" / f"{name}.wav" for name in EXISTING]
    return {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def render(spec):
    name, seconds, synth, seed, target_peak, loop, _brief = spec
    t = axis(seconds)
    values = synth(t, np.random.default_rng(seed))
    if not loop:
        # No lead/tail padding: only 3 ms onset and 12 ms release de-clicks.
        onset = np.sin(np.minimum(t / 0.003, 1) * math.pi / 2) ** 2
        tail = np.sin(np.minimum((seconds - t - 1 / RATE) / 0.012, 1) * math.pi / 2) ** 2
        values *= onset * np.maximum(tail, 0)
    values -= np.mean(values)
    if not loop:
        # The tiny DC correction must not introduce an edge step.
        values *= onset * np.maximum(tail, 0)
    values *= target_peak / max(float(np.max(np.abs(values))), 1e-12)
    if not np.isfinite(values).all() or np.max(np.abs(values)) >= 1:
        raise ValueError(f"{name}: invalid/clipping samples")
    pcm = np.rint(values * 32767).astype("<i2")
    for folder in (MASTER, PACKAGE):
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{name}.wav"
        with wave.open(str(path), "wb") as writer:
            writer.setnchannels(1)
            writer.setsampwidth(2)
            writer.setframerate(RATE)
            writer.writeframes(pcm.tobytes())


def inspect(spec):
    name, seconds, _synth, seed, target_peak, loop, brief = spec
    path = MASTER / f"{name}.wav"
    with wave.open(str(path), "rb") as reader:
        assert (reader.getframerate(), reader.getnchannels(), reader.getsampwidth(), reader.getcomptype()) == (RATE, 1, 2, "NONE"), name
        count = reader.getnframes()
        pcm = np.frombuffer(reader.readframes(count), dtype="<i2").astype(np.int64)
    assert count == round(seconds * RATE), name
    assert np.max(np.abs(pcm)) < 32767, name
    package_path = PACKAGE / path.name
    assert path.read_bytes() == package_path.read_bytes(), name
    nonzero = np.flatnonzero(pcm)
    assert len(nonzero), name
    leading = int(nonzero[0])
    trailing = int(count - nonzero[-1] - 1)
    assert leading <= 0.003 * RATE and trailing <= 0.012 * RATE, name
    values = pcm / 32768.0
    metrics = dict(
        name=name, durationSeconds=count / RATE, sampleRate=RATE, channels=1,
        bitsPerSample=16, encoding="signed 16-bit little-endian PCM", frames=count,
        loop=loop, seed=seed, brief=brief, targetSamplePeakDbfs=dbfs(target_peak),
        samplePeakDbfs=dbfs(np.max(np.abs(values))),
        rmsDbfs=dbfs(np.sqrt(np.mean(values * values))),
        dcMean=float(np.mean(values)), clippedSamples=int(np.sum(np.abs(pcm) >= 32767)),
        leadingZeroFrames=leading, trailingZeroFrames=trailing,
        firstSample=int(pcm[0]), lastSample=int(pcm[-1]),
        onset20msRmsDbfs=dbfs(np.sqrt(np.mean(values[:960] ** 2))),
        final20msRmsDbfs=dbfs(np.sqrt(np.mean(values[-960:] ** 2))),
        masterPath=path.relative_to(ROOT).as_posix(),
        packagePath=package_path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    if loop:
        delta = np.diff(pcm)
        wrap_delta = int(pcm[0] - pcm[-1])
        previous_delta = int(delta[-1])
        next_delta = int(delta[0])
        second_differences = np.diff(delta)
        boundary_curvature = max(abs(wrap_delta - previous_delta), abs(next_delta - wrap_delta))
        max_delta = int(np.max(np.abs(delta)))
        max_curvature = int(np.max(np.abs(second_differences)))
        # Wrap is the ordinary next sample of an exactly periodic construction.
        # Duplicating the last sample or fading the loop would itself stutter.
        assert abs(wrap_delta) <= max_delta + 2, name
        assert boundary_curvature <= max_curvature + 3, name
        metrics["periodicConstruction"] = "Integer-cycle oscillators/modulators and inverse DFT periodic noise; no fade, duplicated endpoint or silence seam."
        metrics["wrapStepPcm"] = wrap_delta
        metrics["stepImmediatelyBeforeWrapPcm"] = previous_delta
        metrics["stepImmediatelyAfterWrapPcm"] = next_delta
        metrics["local64SamplesMaxStepPcm"] = int(max(np.max(np.abs(delta[:32])), np.max(np.abs(delta[-32:]))))
        metrics["maxInteriorStepPcm"] = max_delta
        metrics["wrapCurvaturePcm"] = boundary_curvature
        metrics["local64SamplesMaxCurvaturePcm"] = int(max(np.max(np.abs(second_differences[:32])), np.max(np.abs(second_differences[-32:]))))
        metrics["maxInteriorCurvaturePcm"] = max_curvature
        metrics["wrapStepDbfs"] = dbfs(abs(wrap_delta) / 32768)
        metrics["seamNumericalCheck"] = "pass: boundary slope/curvature within ordinary interior range, allowing PCM quantization"
    return metrics


def write_records(before):
    available = [spec for spec in SPECS if (MASTER / f"{spec[0]}.wav").is_file()]
    rows = [inspect(spec) for spec in available]
    record = dict(
        schemaVersion=1, authoredDate="2026-10-06", creator="Operator (original procedural DSP audio)",
        license="MIT - original project assets", source="tools/assets/render-gate-cycle-audio.py",
        dependencies={"Python": "3.10+", "NumPyAuthoringVersion": np.__version__},
        authoring="Seeded noise filtered in the Fourier domain, mathematical motor oscillators, inharmonic damped mechanical modes and paper-friction envelopes. No third-party recordings, music, speech or provider assets.",
        review="PCM format, duration, finite values, sample peak/RMS, zero padding, loop wrap slope/curvature and source/package byte identity inspected. No auditory playback, in-game mix, true-peak, LUFS or sustainer lifecycle acceptance performed.",
        integrationBoundary="Assets only. Claude owns SoundDefs, one-shot call sites, animation timing and sustainer start/stop across closure, destruction, map unload and reload. Existing Usable rejects sustain; loops are delivered, not claimed playable.",
        existingCueSha256=before, assets=rows,
    )
    MASTER.mkdir(parents=True, exist_ok=True)
    DELIVERY.mkdir(parents=True, exist_ok=True)
    (MASTER / "gate-cycle-provenance-2026-10-06.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    (DELIVERY / "audio-metrics.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    lines = ["# Gate-cycle and event audio delivery", "", "Original assets-only delivery, 2026-10-06. All WAVs are 48 kHz, mono, signed 16-bit PCM.", "", "| Cue | Seconds | Sample peak dBFS | RMS dBFS | Loop |", "| --- | ---: | ---: | ---: | --- |"]
    for row in rows:
        lines.append(f"| {row['name']} | {row['durationSeconds']:.2f} | {row['samplePeakDbfs']:.2f} | {row['rmsDbfs']:.2f} | {'yes' if row['loop'] else 'no'} |")
    lines += ["", "## Loop boundary measurements", "", "The wrap is an ordinary sample transition of a periodic waveform, not a required zero-crossing. Values below are signed PCM16 sample differences.", "", "| Loop | Step before wrap | Wrap step | Step after wrap | Nearby max absolute step | Wrap curvature | Nearby max curvature |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows:
        if row["loop"]:
            lines.append(f"| {row['name']} | {row['stepImmediatelyBeforeWrapPcm']} | {row['wrapStepPcm']} | {row['stepImmediatelyAfterWrapPcm']} | {row['local64SamplesMaxStepPcm']} | {row['wrapCurvaturePcm']} | {row['local64SamplesMaxCurvaturePcm']} |")
    lines += ["", "## Authoring and delivery", "", "- Masters: `assets/source/audio/`. Package copies: `Mod/Rimrooms - Async Industries/1.6/Sounds/Rimrooms/`.", "- Reproduce with `python tools/assets/render-gate-cycle-audio.py --group all` (Python 3.10+, NumPy). `--group oneshots` and `--group loops` allow separate deliveries.", "- The ramp-up accelerates and holds its final speed until a short anti-click release; it deliberately leaves tension unresolved. Ramp-down decelerates, then seats a final latch and decays to rest.", "- Calibration is dry and quieter than activation. Filing uses synthetic paper friction and a latch; payment uses a receipt feed, paper pull and muted stamp, without a money jingle.", "- One-shots have 3 ms onset/12 ms tail anti-click envelopes, not silence padding. WAV quantization can leave a few zero-valued endpoint samples; their counts are recorded.", "- Both loops use exact integer-cycle oscillators and modulators plus Fourier-periodic filtered noise. The boundary step and curvature are checked against interior steps, not forced to zero or made by duplicating an endpoint.", "- `audio-metrics.json` records complete PCM metrics, hashes, loop seam measurements and the preserved original four cue/master hashes.", "", "## Integration handoff and limits", "", "This delivery contains no SoundDefs, C# call sites or sustainer implementation. Claude owns those changes. In particular, loops are not playable through the current one-shot-only `RimroomsAudio.Usable` route; they need explicit start/stop handling for normal closure, emergency, destruction, map unload and reload mid-cycle.", "", "No audio was played or evaluated in-game. Numerical sample-peak/RMS and loop continuity checks do not establish perceptual quality, game loudness, true peak, LUFS or release acceptance. Preserve existing text/pane signals; audio must not become the only way to understand a gate state.", "", "No existing cue was re-rendered or modified. No music, room ambience, stereo sound or Quiet Pursuer audio was authored.", ""]
    (DELIVERY / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("oneshots", "loops", "all"), default="all")
    args = parser.parse_args()
    before = preserved_hashes()
    chosen = [spec for spec in SPECS if args.group == "all" or spec[5] == (args.group == "loops")]
    for spec in chosen:
        render(spec)
        print(f"Authored {spec[0]}: {spec[1]:.2f} s {'periodic loop' if spec[5] else 'one-shot'}")
    after = preserved_hashes()
    if before != after:
        raise RuntimeError("An existing cue changed; do not accept delivery")
    rows = write_records(before)
    print(f"Recorded {len(rows)}/13 original assets; existing four package cues and their masters unchanged. No audio was played.")


if __name__ == "__main__":
    main()
