# -*- coding: utf-8 -*-
"""Ledger for 0.12.11-dev: the mission line reaches a player."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def insert_before(rel, anchor, block):
    s = read(rel)
    assert anchor in s, '%s: anchor not found' % rel
    write(rel, s.replace(anchor, block + anchor, 1))


insert_before('CHANGELOG.md', u'## 0.12.10-dev', u"""## 0.12.11-dev - 2026-09-29 - the corporation starts asking

- **The company now actually asks you for things.** Six requests in order, each teaching one part of the job, and then a seventh where it stops naming things and asks where you intend to take this.
- **Every request offers more than one way through**, and the card shows all of them - including the ones you cannot do yet, so you can see what to work toward. A tick appears beside the ones you have already done.
- **Nothing ever expires.** There is no date on any of it. The company waits as long as it takes, and you can turn any request down without penalty.
- **Two ways through that used to mean the same thing now mean different things.** Filing the analysed paperwork and having a crew member who was there and can speak to it are separate routes: one survives the witness dying, the other survives the book burning.
- **"Two crew accounts" now really means two people.** It was accepting one.
- **The bonus on bringing back your first record is paid when everybody you had on the books comes back.** It previously had no condition at all.

Honest note: all of this was authored two versions ago and **no part of the game ever showed it to you**. This is the version where it reaches the screen.

Full record: [the mission line reaches a player](docs/implementation/REQUEST_LINE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the mission line reaches a player (0.12.11-dev)

**Verbatim user quote:** *"read Now.md to resume the work and okay shoot ask me all you want on those question u had that were blocking and lets get to finishing all this work so we have a finished mod with nothing to do but test and bug hunt"*

**Verbatim owner correction:** *"wtf are you talking about core only we have 294 recommend mods you fuck!!!!"*

**Verbatim owner decision on the route conflict:** *"Both - filter picks the family, card never shrinks"*

### What shipped

The surface that presents a corporation request to a player. **The request shape and all seven authored requests shipped in 0.11.1-dev and 0.11.2-dev and were read by nothing** - the whole tutorial line and the hinge, validated at def load, checked by two tools, proved by a proof, and invisible.

### Files touched

`src/RimroomsAsyncIndustries/Company/RequestLine.cs` (new), `UI/OperationsRequests.cs` (new), `Company/RimroomsCampaignComponent.cs`, `Company/CampaignServices.cs`, `UI/MainTabWindow_Operations.cs`, `1.6/Defs/RimroomsRequestDefs/RR_Requests.xml`, `1.6/Languages/English/Keyed/RR_Requests.xml`, `docs/implementation/REQUEST_LINE_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, and `proof-request-line.py` (new, the sixteenth).

### Closure notes

- **THE CAMPAIGN DID NOT EXIST IN THE GAME.** `grep` for `RequestDef|RequestRoutes|SuccessRoute|TutorialLine` across every `.cs` outside the two files defining them returned **nothing**. `ConfigErrors` validated the defs at load, `check-campaign-absolutes.py` checked them and `proof-offer-routes.py` proved their shape - **none of which is a player seeing a request.** Same defect as the five `PawnKindDef`s found authored and read by nothing, at feature scale. The proof's first claim is now exactly that: the request def is read by source outside its own definition, and commenting out the pane call makes it fail.
- **This reordered the queue for a real reason.** The chart authorises arcs 5-8 next, but **arcs 6, 7 and 8 are request content**, and writing them first would have authored more defs nothing reads.
- **TWO of the three "open owner questions" in my own handoff had already been answered.** The route model was answered *"1 and 3"* on 2026-09-29, recorded in three places and **shipped** - and I re-asked it one turn after publishing a checkpoint whose whole purpose was fixing that exact defect. The adjacent-door-run fallback was likewise already answered *"BOTH paths"*. The rule that comes out of it: **grep the ledger before asking; it costs one command.**
- **Zero hard dependencies and Core-only are not the same claim**, and the owner's correction named it. The package must *load and run* against Core alone - a **build** property, and it holds. The install this mod is *designed for* is **the 294**. No option, doc line or design argument may treat a vanilla install as the audience.
- **Document and Testify would have been one check wearing two hats**, and request 5's only two routes are those two - so the def rule forbidding it would have kept passing on text alone. Split on what actually differs: **Document is the paperwork and survives the witness dying; Testify is the person and survives the book burning.** `Research` and `Redirect` had the same collision at the hinge and are split the same way: arriving versus saying where you are going.
- **Two labels were lying and the checks caught both.** Request 5's *"two crew accounts"* accepted one account; it now asks for two distinct living witnesses. `bonusUsd` was a number that would always have paid; it now requires everybody on the books at acceptance to still be there, measured against a **snapshot** so firing the casualty cannot earn it.
- **A runtime-built keyed string, for the third time in this project.** `"RR_Requests_Status_" + status`, caught by `check-keyed-strings.py`, which sees a prefix and nothing else. Replaced with literal keys.
- **A proof rule banned its own negation, then matched its own comment.** `RR_Requests_NoDeadline` said *"There is no time limit"* and tripped a rule against the word. **The key was renamed rather than the rule softened.** It then matched an XML comment of mine stating no string mentions a deadline - invariant 130 again - so comments are now stripped, which is **narrowing the population rather than softening the rule**, and a planted fault proves the narrowing did not blind it.
- **The C# file count had been wrong for five checkpoints**, claimed 172 against a real 170. Exactly the stale assembly hash, found the same way: by measuring instead of copying. It is genuinely 172 now because this checkpoint adds two files, **which is how a wrong number outlives its correction**.
- **Five planted faults, five catches, clean on restore** - including the original defect restaged by commenting out the pane call. Every plant asserted its anchor before writing.
- Build 0.12.11-dev, **172 C# files (measured)**, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, **sixteen** proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, and nothing in this mod has ever been played.**

---

""")

# ---------------------------------------------------------------- NOW.md
s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.10-dev**.', u'| Published | **0.12.11-dev**.'),
    (u'| Build | **172 C# files, 86 package files**, zero warnings, zero errors |',
     u'| Build | **172 C# files, 86 package files**, zero warnings, zero errors. '
     u'**Measure this, never carry it** — it said 172 against a real 170 for five checkpoints and '
     u'only came true by accident: `git ls-tree -r HEAD --name-only | grep -c \'^src/.*\\.cs$\'` |'),
    (u'## What shipped this session, 0.7.1 → 0.12.10',
     u'## What shipped this session, 0.7.1 → 0.12.11'),
    (u'| 0.12.10 | **The handoff** — four live proofs found unrun, five patch scripts un-named as proofs, a stale hash corrected |',
     u'| 0.12.10 | **The handoff** — four live proofs found unrun, five patch scripts un-named as proofs, a stale hash corrected |\n'
     u'| 0.12.11 | **The corporation starts asking** — the mission line reaches a player. **The whole campaign had been authored and read by nothing** |'),
]
for old, new in pairs:
    assert old in s, 'NOW anchor missing: %r' % old[:70]
    s = s.replace(old, new, 1)

old_proofs = u'| Proofs | **FIFTEEN** in `.local/register/proof-*.py`.'
new_proofs = u'| Proofs | **SIXTEEN** in `.local/register/proof-*.py`.'
assert old_proofs in s
s = s.replace(old_proofs, new_proofs, 1)

old_set = u"""   The set: `displacement`, `facilities`, `facility-relief`, `fit`, `gate-links`, `incidents`,
   `live-effects`, `offer-routes`, `portal-footprint`, `remote-sites`, `research-branches`,
   `spinup`, `starts`, `stranded-crew`, `tier-ladder`."""
new_set = u"""   The set: `displacement`, `facilities`, `facility-relief`, `fit`, `gate-links`, `incidents`,
   `live-effects`, `offer-routes`, `portal-footprint`, `remote-sites`, `request-line`,
   `research-branches`, `spinup`, `starts`, `stranded-crew`, `tier-ladder`."""
assert old_set in s, 'proof set list not found'
s = s.replace(old_set, new_set, 1)

old_ritual = u'7b. **Every proof (FIFTEEN), by exit status:**'
assert old_ritual in s
s = s.replace(old_ritual, u'7b. **Every proof (SIXTEEN), by exit status:**', 1)

# Queue item 3 is now half done.
old_item3 = u"""3. **Generated requests after the hinge**, from branch state, coordinate history and capability.
   Route selection for a generated request is an **open owner question** (chart §6)."""
new_item3 = u"""3. **Generated requests after the hinge.** **The surface shipped 0.12.11-dev** — requests now
   reach a player, are accepted, complete on any one route coming true, and pay. What is left is
   **generation**: the arc 4–8 request families, and the eligibility filter the owner decided on.
   - **Route selection is ANSWERED** (chart §6 item 3 closed): *"Both — filter picks the family,
     card never shrinks."* A family is offered only if the branch can take **two routes of two
     different kinds** from its pool; the card it then shows is the **full authored floor,
     unfiltered**. `RequestRoutes.Available` is not to be modified.
   - **The filter must have teeth.** Invariant 136: every clause has to be able to refuse. A
     `Deliver` route that is "always takeable" makes the whole filter hollow. Refusable readings
     exist for all seven kinds — catalogue carriage, completed logs, living witnesses, project
     availability, redirect target existence."""
assert old_item3 in s, 'queue item 3 not found'
s = s.replace(old_item3, new_item3, 1)

# Invariants.
marker = u'174. **Two questions may share a place-set and must not share a name.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'175. **A def shape with content and no reader is not a feature.** `ConfigErrors`, a checker '
     u'and a proof can all validate a def while nothing in the game consumes it — which is how the '
     u'entire campaign shipped twice as content nobody could see. **Assert that a content surface '
     u'is read from outside its own definition**, and restage the defect as a planted fault.\n'
     u'176. **Where two route kinds could resolve to the same expression, split them on what '
     u'actually differs.** A def rule demanding two different kinds is satisfied by text alone if '
     u'the runtime asks one question twice. Document is the paperwork and survives the witness '
     u'dying; Testify is the person and survives the book burning.\n'
     u'177. **Re-measure every count in the handoff; never carry one forward.** The C# file count '
     u'was wrong by two for five checkpoints, exactly as the assembly hash was. A plausible number '
     u'is never checked by reading.\n'
     u'178. **Narrowing what a rule measures is legitimate; softening the rule is not.** A word '
     u'search matching a comment is the wrong population (invariant 130). Strip the comments — '
     u'then **plant a fault to prove the narrowing did not blind it.**\n'
     u'179. **Grep the ledger before asking the owner anything.** Two of the three questions in the '
     u'0.12.10 handoff had already been answered and recorded, and one of them was re-asked the '
     u'turn after that handoff shipped. One `grep` across `.local/register/` and `docs/` is cheaper '
     u'than the owner’s patience.\n'
     u'180. **Zero hard dependencies and Core-only are different claims.** The package must load '
     u'and run against Core alone — a build property. The install it is *designed for* is the 294. '
     u'Never write an option, doc line or design argument treating a vanilla install as the '
     u'audience. *"wtf are you talking about core only we have 294 recommend mods you fuck!!!!"*\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# ---------------------------------------------------------------- TODO
insert_before('docs/TODO.md', u'\n## Owner decisions, 2026-09-29', u"""
**Built 2026-09-29, 0.12.11-dev: the mission line reaches a player.**

- [x] **The corporation request surface exists in the game.** `RimroomsRequestDef`, `RequestRoutes` and seven authored requests shipped in 0.11.1-dev and 0.11.2-dev and **were read by nothing** - the whole tutorial line and the hinge, invisible to every player. Records, offering, acceptance, cancellation, completion, payment and a pane.
- [x] **Offering refuses three ways:** no line before corporation contact, one request open at a time, and prerequisites satisfied by Completed **or Cancelled** so a refusal never strands the line.
- [x] **The tutorial line is deliberately NOT capability-filtered.** The owner's eligibility answer is about generated requests; applied here it would offer a fresh branch nothing, for ever.
- [x] **All seven route kinds have distinct checks.** Document reads an analysed record; Testify reads distinct living employees on a matching observation. Research is finishing a project; Redirect is starting one.
- [x] **Request 5's "two crew accounts" now asks for two people.** It accepted one.
- [x] **`bonusUsd` has a real condition** - everybody on the books at acceptance still employed and alive, from a snapshot.
- [x] **The C# file count had been wrong for five checkpoints**, 172 claimed against 170 real. Now measured, with the command recorded.
- [ ] **Next: generation after the hinge.** The arc 4-8 request families plus the eligibility filter, which **must have teeth** - every clause able to refuse, per invariant 136.
""")
