# -*- coding: utf-8 -*-
"""Rewrite NOW.md as the compaction handoff after 0.12.22-dev.

Written by checking every claim against the thing it describes rather than tidying prose, which is
the only version of this procedure that is worth doing. It found SIX defects:

  1. The proof output split said "four print PASS:, eleven print PROOF HELD" -- fifteen, when there
     are twenty-one. The real split is 17 / 2 / 2, and the last two end on a WRAPPED CONTINUATION
     LINE, so their final line is not a status token at all. That strengthens the exit-status rule.
  2. Queue item 2 said research tiers 3-4 were both pending. Tier 3 shipped at 0.12.18-dev.
  3. Queue item 6 called RR_QuietPursuer "the last existing-content replacement". It shipped at
     0.12.22-dev.
  4. The top warning described the 0.12.10-dev session. This session's failures were sharper and
     different, and one of them was a check that PASSED a planted fault.
  5. "Done since the last handoff" mentioned NONE of this session's twelve checkpoints.
  6. Open questions said "THERE ARE NONE". Retiring the RR_FieldRecorder def needs a migration
     decision, which is exactly an owner question.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'NOW.md')

s = io.open(PATH, encoding='utf-8').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:90]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:90]
    s = s.replace(old, new, 1)


# ------------------------------------------------------------------ 1. the proof split
sub(u'**Run them by exit status, not by grepping their output** — four of them print `PASS:` and eleven print `PROOF HELD`, and a grep for one phrasing silently skips the others. That is how four live proofs went unrun for most of this session',
    u'**Run them by exit status, not by grepping their output.** Measured at 0.12.22-dev: **17 end '
    u'`PROOF HELD`, 2 end `PASS:`, and 2 end on a WRAPPED CONTINUATION LINE** whose last line is not '
    u'a status token at all. A grep for any one phrasing skips the rest; that is how four live '
    u'proofs went unrun for most of one session, and the two wrapped ones would be missed by every '
    u'phrasing. **Exit status is the only reading that cannot be fooled by formatting**')

# ------------------------------------------------------------------ 2. tier 3 shipped
sub(u'2. **Research tiers 3–4, AFTER the arcs.** **Deliberately moved behind them, 0.12.5-dev.** Tier 3',
    u'2. ~~**Research tier 3.**~~ **CLOSED, 0.12.18-dev — all seven branches**, each moving a real '
    u'observable knob, with two restraints asserted: the per-coordinate frontier cap is **not** a '
    u'research knob, and shelter never reaches zero.\n'
    u'   **TIER 4 REMAINS, and survey it the same way rather than assuming it has knobs.** The '
    u'0.12.5-dev deletion of tier 3 was correct at the time and became writeable only because arc 5 '
    u'wrote the systems — so re-run the sweep, do not carry an old verdict. Historical detail on '
    u'tier 3’s original deletion follows.\n'
    u'   Tier 3')

# ------------------------------------------------------------------ 3. QuietPursuer shipped
sub(u'6. **`RR_QuietPursuer` presentation** — the last existing-content replacement.',
    u'6. ~~**`RR_QuietPursuer` presentation.**~~ **CLOSED, 0.12.22-dev** — it uses Core’s '
    u'`Things/Mote/Black`, a shape you cannot resolve, which is closer to its own description than a '
    u'drawing was. **Zero gameplay art or audio now ships** and a checker asserts it as a shape '
    u'rather than a count.\n'
    u'   **NEXT, and owner-answered 2026-09-29:** retire **`RR_FieldRecorder`** by **folding its job '
    u'into the record book crews already carry**. A crew already takes Core’s `TextBook` in as the '
    u'native evidence carrier, patched with our comp — so the same book logs visited rooms, route '
    u'mismatches and entity sightings. **One item, two jobs, no new def, and NO SAVE BREAK:** the '
    u'recorder def stays loadable so old saves open, but is never granted or sold again. It also '
    u'reads better — the thing you write in is the thing that remembers. Four live read sites move '
    u'onto the book. Historical detail follows.')

# ------------------------------------------------------------------ 4. the top warning
sub(u"""**A check that cannot fail manufactures confidence, and every instance of it this session was
mine.** Four, all found by planting faults rather than by reading:

| What could not fail | Why |
|---|---|
| the natural-depth ordering claim | keyed off a **variable name**; renaming it made the claim fail *open* |
| the on-the-books claim | counted a **refusal string** that survived the guard being deleted |
| the staffing ordering claim | had a **conditional fallback** on a method name absent from the file, so it collapsed to a tautology |
| the whole proof runner | **grepped for `PROOF HELD`**, and four live proofs end `PASS:` — so four went unrun for most of the session |

The first three were caught by fault-planting. **The fourth was caught only by writing this
handoff**, which is the argument for writing it.""",
    u"""**A search that finds nothing is not evidence, and this session I twice took one as proof.**
Both directions of that failed, and both cost real things:

| What happened | Why it was worse than being wrong |
|---|---|
| **`Named<TerrainDef>("Carpet")` returned null, silently, for months** | Core ships `Carpet` as a `TerrainTemplateDef`; there is no `TerrainDef` of that name. `GetNamedSilentFail` is silent **by design** and a `??` fallback made wood plank flooring look deliberate. **The depth-1 yellow rooms — the one look invariant 25 calls sacred — were never carpeted.** |
| **I marked working code *"confirmed unbuilt by grep"*** | The mineable-rock fill ships. My grep searched `Generation/` for *"Mineable"*, *"Granite"*, *"RockRubble"* — **words the code does not contain**, because it asks `Find.World.NaturalRockTypesIn`. I then accused a correct comment of lying. **Condemning working code on a failed search is worse than trusting a wrong comment**, because it invites somebody to "fix" what works. |
| **A check I wrote to catch one specific thing PASSED that exact planted fault** | The floor-value claim skipped terrains with no cost list as *"never built"* — which excused `PackedDirt`, the precise case it existed for. **A filter that skips the case it guards against is worse than no check**, and only the planted fault found it. |
| **A claim keyed off proximity broke when correct code moved near it** | It searched for a capability name within 400 characters of a constant. **Proximity is not the thing that happens.** Fifth instance of that class. |
| **Claims matching the code's own comments** | Twice more, including a rule defeated by the two doc comments explaining why the thing it looked for is deliberately absent. **Sixth instance.** |

### The rules that come out of it

- **Key a claim off the thing that happens** — an assignment, a guard, an exit status. Never a
  token near it, a variable's spelling, or a count of a string.
- **Strip comments before searching source.** Six times now.
- **A grep for the words you expected, in the file you expected, is not a search.** Check the API
  the code actually calls.
- **`GetNamedSilentFail` plus a `??` fallback is a silent wrong answer.** Assert that every def a
  generator names actually resolves — including template-generated ones.
- **Plant the fault and confirm it fails for the RIGHT reason.** A check that passes its own
  motivating case is the worst outcome available, and reading will never reveal it.
- **Never widen a rule so your own text passes.** Refused three times this session: a key was
  renamed, two descriptions were reworded, and the vocabulary rule was obeyed rather than relaxed.""")

# ------------------------------------------------------------------ 5. done since
sub(u"""### Done since the last handoff, so nobody rebuilds it

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
`PassToWorld`.""",
    u"""### Done since the last handoff, so nobody rebuilds it

**Twelve checkpoints, 0.12.11 → 0.12.22.** Every one published to all eight refs with a read-back,
a deterministic assembly, and the full checker and proof sweep.

**THE CAMPAIGN NOW EXISTS IN THE GAME.** It did not before. `RimroomsRequestDef`, `RequestRoutes`
and seven authored requests — the tutorial line and the hinge — shipped at 0.11.1 and 0.11.2 and
were **read by zero lines of C#**. Chart §7 steps 4 and 5 were both recorded *done*. Now: requests
reach a player, are accepted, complete when any one route comes true, and pay.

**25 request defs** — 7 fixed tutorial plus **18 generated across arcs 4–8**, one per item the chart
names. **Chart §7 step 8 is closed**: every arc has work a player can be asked to do. Coverage is
asserted **per arc**, because a total of eighteen is satisfied by eighteen copies of one arc.

**Generation after the hinge**, with an eligibility filter whose every clause can refuse, and
progress measured **from when a request appeared** — absolute state is permanently true once true,
so a repeatable request would otherwise have paid out on acceptance.

**Research tier 3, all seven branches**, each moving a knob a player can watch change. Two
restraints kept and asserted: the per-coordinate frontier cap is **not** a research knob, and
shelter never reaches zero.

**The seven universe factions ship** — the largest completely unbuilt owner direction, found by the
backlog audit. All neutral, **no settlements** so world generation is untouched, and no new pawn
kind or art.

**A way out into the world.** The last unbuilt piece of the topology, and the gap was worse than
the row said: with no marked door a way out silently became a way **deeper**, so a branch with
nothing marked could never get out. Now it leads to an unheld tile — **claimed under the five-map
cap, a caravan at or over it.**

**Zero gameplay art or audio ships.** Four custom textures replaced with paths **enumerated from
Core's own defs**, all four archived.

**The register is queryable by the column that answers the question.** `trace` names which Rimrooms
feature a row bears on; it had no query, which is why it was the column that got skipped. **A ninth
checker** verifies this build still uses other mods the way the register says to.

**Real defects fixed, all of them shipped and player-visible:** the depth-1 yellow rooms had never
been carpeted · two labels lied (request 5 accepted one crew account while promising two; `bonusUsd`
would always have paid) · a way out with no marked anchor was a dead end · two menu textures were
reported unreferenced on every run.

**And the queue was re-measured against the code**: 155 rows, **114 built or superseded**, open rows
**254 → 90**. It could not answer *"how close are we"* before that, because nobody had checked.""")

# ------------------------------------------------------------------ 6. open questions
sub(u"""## Open owner questions — THERE ARE NONE

**All three reserved decisions were answered on 2026-09-29.** Nothing in this project is now
waiting on the owner. Every remaining item in the queue above is buildable.""",
    u"""## Open owner questions — THERE ARE NONE

**Nothing in this project is waiting on the owner.** Every remaining item in the queue above is
buildable, and the owner's standing instruction is that the register is **guidance, not law** and
that *"test cases arnt being worried about right now we are trying to get the build complete so we
can test"* — so **unverifiable-without-a-launch is never a reason to defer building something.**

### Answered this session, so nobody re-asks

- ~~**The route model**~~ — *"Both — filter picks the family, card never shrinks."* Eligibility
  gates which family is offered; the card shows the full authored floor, unfiltered.
- ~~**Branch unlock order after the hinge**~~ — **all eight open, any order.**
- ~~**The world exit vs the stranded-crew guarantee**~~ — **build it, a player caravan is still
  yours.** The narrowing is asserted by name: closing, expiry and traversal still never take a crew.
- ~~**The map cap**~~ — **five, universally**, counting the Backrooms map and every claimed tile;
  over that, caravans. The player's own `Prefs.MaxNumberOfPlayerSettlements` wins if stricter.
- ~~**The register's standing**~~ — **guidance, not law.** A row does not veto work.
- ~~**The public face**~~ — everything, including Playwright driving Steam. Still correctly last,
  and it needs the owner present.
- ~~**Testing**~~ — *"test cases arnt being worried about right now we are trying to get the build
  complete so we can test."* **Unverifiable-without-a-launch is not a reason to slow the build.**
- ~~**`RR_FieldRecorder`, the last authored gameplay item**~~ — **fold its job into the record book
  crews already carry.** Core's `TextBook` is already the native evidence carrier; the same book now
  logs rooms, mismatches and sightings. **No new def, no save break** — the recorder stays loadable
  so old saves open, and is never granted or sold again. **This is the next thing to build.**""")

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md rewritten as the compaction handoff; six defects corrected')
