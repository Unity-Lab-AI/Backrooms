"""Read-only monitor for the A2 background voice preparation (launched by ChatGPT 2026-10-12, PID 12020).

    python .local/voice-lab/monitor.py            # one report
    python .local/voice-lab/monitor.py --json     # same, machine-readable

Opens nothing for writing, sends no signal, imports nothing from training/voice/ (its 89 frozen inputs
must not change while the job runs). Reads: launcher.json, pipeline/status.json, the seed/expansion
metadata.jsonl and screening.jsonl, WAV file times (for pace), stderr sizes and the process table.
"""
import glob, json, os, subprocess, sys, time
from datetime import datetime, timezone

LAB = os.path.dirname(os.path.abspath(__file__))
JOB = os.path.join(LAB, "background", "A2-expanded-2026-10-12-v2")
PIPE = os.path.join(JOB, "pipeline")
SEED = os.path.join(LAB, "dataset", "A2-full-1378-draft-v3")
SEED_QA = os.path.join(LAB, "dataset", "A2-full-1378-screen-v2")
SEED_TOTAL, EXP_TOTAL = 1378, 3622


def jl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:          # a line still being written
                    pass
    return out


def jload(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def procs(pids):
    cmd = ("Get-CimInstance Win32_Process | ? { $_.ProcessId -in %s } | "
           "ForEach-Object { $_.ProcessId.ToString() + '|' + $_.CommandLine }" % ",".join(str(p) for p in pids))
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=30)
    alive = {}
    for line in r.stdout.splitlines():
        pid, _, cl = line.partition("|")
        if pid.strip().isdigit():
            alive[int(pid)] = cl
    return alive


def pace(wavdir, window_s=1800):
    """Clips per minute over the last window, from finished WAV modification times."""
    now = time.time()
    times = sorted(os.path.getmtime(p) for p in glob.glob(os.path.join(wavdir, "*.wav")))
    recent = [t for t in times if now - t <= window_s]
    if len(recent) < 2:
        return None, times
    return (len(recent) - 1) / ((recent[-1] - recent[0]) / 60), times


def main():
    rep = {}
    st = jload(os.path.join(PIPE, "status.json")) or {}
    rec = st.get("recorded_at")
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(rec)).total_seconds() if rec else None
    rep["supervisor"] = dict(stage=st.get("stage"), status_age_s=round(age) if age is not None else None,
                             elapsed_h=round(st.get("elapsed_seconds", 0) / 3600, 2),
                             training_started=st.get("training_started"), pod_rented=st.get("pod_rented"),
                             owned_children=st.get("owned_children"))
    seed_rows = jl(os.path.join(SEED, "metadata.jsonl"))
    qa = jl(os.path.join(SEED_QA, "screening.jsonl"))
    flags = {}
    for r in qa:
        for fl in r.get("flags") or ["clean"]:
            flags[fl] = flags.get(fl, 0) + 1
    secs = sum(r.get("seconds", 0) for r in qa)
    rate, _ = pace(os.path.join(SEED, "wavs"))
    by_emo = {}
    for r in seed_rows:
        by_emo[r.get("emotion")] = by_emo.get(r.get("emotion"), 0) + 1
    rep["seed"] = dict(recorded=len(seed_rows), of=SEED_TOTAL, screened=len(qa), flags=flags,
                       screened_audio_h=round(secs / 3600, 3), clips_per_min_30m=round(rate, 2) if rate else None,
                       eta_min=round((SEED_TOTAL - len(seed_rows)) / rate) if rate else None,
                       done_receipt=os.path.exists(os.path.join(SEED, "source-build.json")),
                       screen_summary=os.path.exists(os.path.join(SEED_QA, "summary.json")), by_emotion=by_emo)
    exp_meta = glob.glob(os.path.join(PIPE, "expansion-source", "**", "metadata.jsonl"), recursive=True)
    exp_rows = sum(len(jl(p)) for p in exp_meta)
    rep["expansion"] = dict(recorded=exp_rows, of=EXP_TOTAL, started=bool(exp_meta))
    rep["outputs_present"] = sorted(os.path.basename(p) for p in glob.glob(os.path.join(PIPE, "*")))
    rep["failure"] = jload(os.path.join(PIPE, "failure.json"))
    rep["result"] = (jload(os.path.join(PIPE, "result.json")) or {}).get("status") if os.path.exists(os.path.join(PIPE, "result.json")) else None
    rep["stderr_bytes"] = {os.path.relpath(p, JOB): os.path.getsize(p) for p in
                           [os.path.join(JOB, "run.stderr.log")] + glob.glob(os.path.join(PIPE, "logs", "**", "*stderr*"), recursive=True)
                           if os.path.exists(p)}
    launch = jload(os.path.join(JOB, "launcher.json")) or {}
    want = [launch.get("pid", 12020), launch.get("existing_seed_pid_at_launch", 31052),
            launch.get("existing_seed_screen_pid_at_launch", 3800)] + [int(p) for p in (st.get("owned_children") or {}).values() if str(p).isdigit()]
    alive = procs(want)
    rep["processes"] = {str(p): ("alive " + alive[p][:90]) if p in alive else "GONE" for p in want}
    if "--json" in sys.argv:
        print(json.dumps(rep, indent=1)); return
    s, e = rep["seed"], rep["expansion"]
    print("supervisor : %s  (status %ss old, %s h elapsed, training %s, pod %s)" % (
        rep["supervisor"]["stage"], rep["supervisor"]["status_age_s"], rep["supervisor"]["elapsed_h"],
        rep["supervisor"]["training_started"], rep["supervisor"]["pod_rented"]))
    print("seed       : %d / %d recorded, %d screened, %.2f h audio screened, %s clips/min, ETA %s min, done-receipt %s, screen-summary %s" % (
        s["recorded"], s["of"], s["screened"], s["screened_audio_h"], s["clips_per_min_30m"], s["eta_min"], s["done_receipt"], s["screen_summary"]))
    print("seed flags : %s" % s["flags"])
    print("expansion  : %d / %d recorded (started: %s)" % (e["recorded"], e["of"], e["started"]))
    print("total      : %d / 5000 clips" % (s["recorded"] + e["recorded"]))
    print("outputs    : %s" % rep["outputs_present"])
    print("failure    : %s   result: %s" % (rep["failure"] and rep["failure"].get("stage"), rep["result"]))
    print("stderr     : %s" % {k: v for k, v in rep["stderr_bytes"].items()})
    for p, v in rep["processes"].items():
        print("pid %-6s : %s" % (p, v))


if __name__ == "__main__":
    main()
