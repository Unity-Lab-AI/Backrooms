# Writing the handoff found four unrun proofs — 0.12.10-dev, 2026-09-29

**Dated record.** A handoff checkpoint. No gameplay changed; what changed is what the next session
can trust. Never rewritten.

---

## What this is

The owner asked for the `NOW.md` handoff procedure before compaction. Doing it properly — reading
every claim in the file against the thing it describes rather than tidying prose — turned up four
defects **in the handoff and in the ritual itself.**

That is the argument for the procedure. A handoff written from memory would have carried all four
across the compaction boundary.

---

## Four defects, in order of how bad they were

### 1. Four live proofs had gone unrun for most of the session

The ritual said *"every proof (four)"* and named four. The directory held **fifteen**.

Worse than the stale count: my per-checkpoint runner was

```sh
python "$p" | grep -q "^PROOF HELD"
```

**Eleven proofs end `PROOF HELD`. Four end `PASS:`.** So `proof-displacement`,
`proof-facilities`, `proof-fit` and `proof-spinup` were skipped every single checkpoint — and a
skipped proof reports nothing, which is indistinguishable from a passing one.

All four pass, and passing is luck rather than evidence: **they were not being consulted while
the code they guard was edited.** They cover revisit displacement, facility formation, the
body-size fit ladder and the spin-up decay curve — all of which this session touched.

**The ritual now runs them by exit status**, which is phrasing-independent:

```sh
for p in .local/register/proof-*.py; do python "$p" >/dev/null || echo "FAILED: $p"; done
```

This is the same failure as the three claims that could not fail, one level up: **a runner that
matches a phrasing is a check keyed off a token.** It was found only by writing the handoff, which
is why the handoff is worth writing.

### 2. Five patch scripts were named `proof-*`

`proof-gate-at-site.py`, `proof-site-deliveries.py`, `proof-site-staffing.py`,
`proof-solo-rework.py`, `proof-starts-inside.py` are **one-shot edit scripts that patch proofs** —
mine, from this session, and badly named.

So `proof-*.py` had stopped meaning *"a proof"*. A future session globbing that directory would
run a landed patch, watch its `assert` fail, and have to work out whether a proof had broken.
Renamed to `patch-*`, and the distinction is now stated in the ritual.

### 3. The assembly hash had been stale for five checkpoints

The State table still held **0.12.4's** hash while the file said 0.12.9. Nobody would have caught
it by reading, because a SHA-256 looks equally plausible wrong.

Corrected — and then **immediately stale again**, because bumping to 0.12.10 rebuilds the assembly
and changes it. It is now read from the live build after the determinism run, which is the only
order that can be right. The line says so, so the next person does not copy the old value forward.

### 4. Two "open owner questions" had been answered hours earlier

`reserveChargePowerWatts` and the 250 W idle draw were both settled in 0.12.4-dev and were still
sitting in the open list. A handoff that asks a closed question wastes the owner's time and
suggests nothing was written down.

Both moved to a **Closed this session** block with their answers, alongside the three other
decisions the owner made today, so nobody re-asks any of them.

---

## What else the rewrite corrected

- **The gotcha counts were wrong and flattering.** The heredoc trap says *"hit six times"*; the
  real count is **eight**, and three of those were **after** the line already warned about it. It
  now says so, and says what to do instead.
- **The `--` in XML comments** was *four*; it is **five**.
- **A new gotcha worth its place:** a patch script asserts before it writes, so a fault-plant with
  a mistyped anchor plants *nothing* — and the proof passing afterwards proves nothing. That
  happened once this session and was caught only because the assert printed.
- **The top warning was two sessions out of date.** It was about checkers; the live lesson is
  sharper and evidenced: **four things that could not fail, all mine, three found by
  fault-planting and the fourth only by writing this file.**
- **The queue and "done since" block** now say what shipped — all three starts, arc 5's complete
  named list, research through tier 2 with 3–4 deliberately deferred — so the next session does
  not rebuild any of it.

---

## Why no gameplay changed, and why that is right

Nothing in this checkpoint touches the mod. It changes **what the next session is told**, and
every one of the four defects would have survived compaction silently:

- four proofs would have stayed unrun,
- a patch script would eventually have been run as a proof,
- a wrong hash would have been copied forward as evidence of a reproducible build,
- and the owner would have been asked two questions they had already answered.

**A handoff is a claim about the state of the work, and a claim nobody checks is the thing this
project keeps learning not to trust.**

---

## Receipts

| | |
|---|---|
| Version | 0.12.10-dev |
| Build | 172 C# files, 86 package files, **0 warnings, 0 errors** |
| Gameplay changed | **none, deliberately** |
| Live proofs found unrun | **4** |
| Patch scripts misnamed as proofs | **5**, renamed |
| Stale facts corrected in the handoff | **3** — the hash, two closed questions, the proof count |
| Checkers | **eight**, all passing |
| Proofs | **fifteen**, all exiting zero |
| Game launched | **no**, and nothing in this mod has ever been played |
