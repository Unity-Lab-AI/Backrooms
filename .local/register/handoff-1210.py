# -*- coding: utf-8 -*-
"""Rewrite NOW.md as the compaction handoff for 0.12.10-dev."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'docs', 'NOW.md')
s = io.open(p, encoding='utf-8').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:80]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:80]
    s = s.replace(old, new, 1)


# ------------------------------------------------------------------ state: the stale hash
sub(u'| Published | **0.12.9-dev**.', u'| Published | **0.12.10-dev**.')
sub(u'| Assembly | SHA-256 `E62DF5326AC89E59E744E4AD10F054CA6674439AA7F73C34075DF1CF14AD2BE3`, reproduced by two clean recompiles |',
    u'| Assembly | SHA-256 `CE41BB0D133F0FAA745196B3EF4C76D33823D92C3518E4836FEBEF827BEE2CCB`, reproduced by two clean recompiles. '
    u'**This line was stale for five checkpoints** — it still held 0.12.4’s hash. Re-read it from the build, never from memory |')
sub(u'| Proofs | **eleven** in `.local/register/proof-*.py`, all holding. They assert; they do not print. |',
    u'| Proofs | **FIFTEEN** in `.local/register/proof-*.py`. **Run them by exit status, not by grepping their output** — four of them print `PASS:` and eleven print `PROOF HELD`, and a grep for one phrasing silently skips the others. That is how four live proofs went unrun for most of this session |')

# ------------------------------------------------------------------ the session table
sub(u'## What shipped this session, 0.7.1 → 0.12.9',
    u'## What shipped this session, 0.7.1 → 0.12.10')
sub(u'| 0.12.9 | **The exit plan** — a gate may stand at a registered site, with its own facility. Arc 5’s named list complete |',
    u'| 0.12.9 | **The exit plan** — a gate may stand at a registered site, with its own facility. Arc 5’s named list complete |\n'
    u'| 0.12.10 | **The handoff** — four live proofs found unrun, five patch scripts un-named as proofs, a stale hash corrected |')

# ------------------------------------------------------------------ done-since
sub(u"""### Done since the last handoff, so nobody rebuilds it

Glow-pod markers with colour-as-meaning · evidence custody on a linked archive shelf · the survey
tag, evidence case and their recipes retired · gate equipment links · the log-gated window ladder
with four rungs · the campaign chart · the request shape with success routes · the full tutorial
line and the hinge · research tiers 0 and 1 across seven branches · the alerts readout.""",
u"""### Done since the last handoff, so nobody rebuilds it

**Research:** tiers 0, 1 and 2 across seven branches — **tier 2 complete, and tiers 3–4 deliberately
deferred behind the arcs** (see the queue).

**The corporation:** the clean-up team that means a facility never dies, deterministic and
uncapped · the first two `IncidentDef`s so the player's own storyteller paces the lighter events ·
**no `StorytellerDef`, ever, and it is asserted.**

**All three starts ship.** Async Industries (now opening with eight completed projects) · the
Furniture & Knickknack Store · solo/group, whose map is a real Backrooms coordinate with a
**guaranteed** registered way out and a natural chain that stops at depth 3.

**Arc 5's named list is complete:** sites on the books and billed daily · company-to-site
logistics · staffing, so a shipment to an empty site waits · and the exit plan, a gate at a
registered site with its own console, battery and bench.

**Real defects fixed:** a wall beside a gate no longer bricks it for the life of the save · a
cross-map reroute no longer strands a paid shipment for ever · a tier-0 research card that
promised an unlock and moved nothing now moves something · three dead gate accessors wired ·
five `PawnKindDef`s found authored and read by nothing.

**Guarantees proved rather than rebuilt:** a gate closing on a crew strands them and never takes
them — `ShouldRemoveMapNow` returns false **unconditionally** and no gate source may call
`PassToWorld`.""")

# ------------------------------------------------------------------ the ritual
sub(u"""7. **Every checker** (eight): `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, `check-campaign-absolutes.py`, `check-doc-conformance.py`, `research/audit-gate0.py`.
7b. **Every proof** (four): `.local/register/proof-{research-branches,offer-routes,tier-ladder,gate-links}.py`. **Sanity-test any new rule by planting a fault in both directions** before believing it.""",
u"""7. **Every checker** (eight): `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, `check-campaign-absolutes.py`, `check-doc-conformance.py`, `research/audit-gate0.py`.
7b. **Every proof (FIFTEEN), by exit status:**

```sh
for p in .local/register/proof-*.py; do python "$p" >/dev/null || echo "FAILED: $p"; done
```

   **Do not grep their output.** Eleven end `PROOF HELD` and four end `PASS:`; grepping one
   phrasing skipped four live proofs for most of one session. Exit status is phrasing-independent.

   The set: `displacement`, `facilities`, `facility-relief`, `fit`, `gate-links`, `incidents`,
   `live-effects`, `offer-routes`, `portal-footprint`, `remote-sites`, `research-branches`,
   `spinup`, `starts`, `stranded-crew`, `tier-ladder`.

   **`patch-*.py` in that directory are one-shot edit scripts, not proofs.** They were once named
   `proof-*` and re-running one would try to re-apply a landed patch and fail confusingly.

   **Sanity-test any new claim by planting a fault** and confirming it fails **for the right
   reason**. Three claims this session passed a planted fault; all three were mine.""")

# ------------------------------------------------------------------ gotchas
sub(u'- **XML comments cannot contain `--`.** Hit **four times**. The checker names the rule and the line.',
    u'- **XML comments cannot contain `--`.** Hit **five times**. The checker names the rule and the line.')
sub(u'- **Bash heredocs mangle `\\n` and break on apostrophes.** Hit **six times**. Use Write, and a message file for commits.',
    u'- **Bash heredocs mangle `\\n` and break on apostrophes.** Hit **EIGHT times**, the last three after '
    u'this line already said so. **Stop reaching for a heredoc when the payload contains a backslash '
    u'escape or an apostrophe** — use the Write tool, and a message file for commits.')
sub(u'- **A failed `assert` in a patch script means nothing was written** — the write comes last.',
    u'- **A failed `assert` in a patch script means nothing was written** — the write comes last. So a '
    u'fault-plant whose anchor was wrong plants nothing, and the proof passing afterwards proves '
    u'nothing. Check the plant landed.')

# ------------------------------------------------------------------ open questions: two are closed
sub(u"""1. **`reserveChargePowerWatts`** — restored, deliberately not wired. The reserve is a Core battery
   RimWorld already charges, so three readings are all defensible: a supply requirement (duplicates
   `minimumPowerHeadroomWatts`), a display estimate (honest but only a readout), or a second charge
   path (double-charges unless it replaces Core's). **Details in `TODO.md`.**
2. **A designated gate now costs 250 W while idle**, scaled by footprint, on every existing save.
   Made because an unused value is an unfinished job. **If zero idle cost was the intent, this is
   the one to reverse.**
3. **How a generated request picks its routes** — a fixed set per family, or derived from what the
   branch has. Chart §6.
4. **Whether the eight branches unlock in any order after the hinge.** Chart §6.""",
u"""1. **How a generated request picks its routes** — a fixed set per family, or derived from what the
   branch has. Chart §6. **Blocks queue item 3.**
2. **Whether the eight branches unlock in any order after the hinge.** Chart §6.
3. **The public face** — site domain, Pages branch, and whether Playwright may drive a Steam page.
   `PUBLIC_RELEASE_PLAN.md`. Correctly last.

### Closed this session, so nobody re-asks

- ~~**`reserveChargePowerWatts`**~~ — **a supply requirement before opening.** Wired 0.12.4-dev,
  and wiring it revived `RR_Cap_ReserveDiscipline`, a tier-0 card that had promised an unlock and
  moved nothing.
- ~~**The 250 W idle draw**~~ — **kept.** Confirmed as the intended behaviour; no change needed.
- ~~**Natural gates indestructible**~~ — **relaxed by the owner** to a confirmation warning.
  *"dont worry about it, can we at least do a rim style pop up warning"*.
- ~~**The solo/group tutorial line**~~ — **option three:** no request line until contact, plus four
  hints in the survivors' own voice. None is an objective.
- ~~**The solo/group exit**~~ — **two maps, coordinate is real.** Superseded the earlier
  seed-tile answer once `RimroomsPortalNetwork.Register` was read.""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md rewritten as the compaction handoff')
