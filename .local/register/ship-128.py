# -*- coding: utf-8 -*-
"""Ledger for 0.12.8-dev: site staffing and the stranded-crew guarantee."""
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


insert_before('CHANGELOG.md', u'## 0.12.7-dev', u"""## 0.12.8-dev - 2026-09-29 - remote sites need people

- **A shipment to a site with nobody at it waits.** The supplier will not unload with no one to receive it. Nothing is lost - the cargo is held and the payment stands - and it lands as soon as somebody is there.
- **You can still order ahead.** Staffing is checked when the shipment arrives, not when you place it, so you can send supplies while the crew is still walking there.
- **The Sites pane tells you which sites are empty**, because that is the state quietly holding your deliveries.
- **Somebody unconscious on the floor does not count as staffing a site.** Neither do prisoners.
- **Closing a gate on your people does not take them away from you.** They stay yours, on a map that is never unloaded, and they have to survive until you reopen a connection. There is no time limit on getting them back, and an alert tells you they are waiting. This was already how the mod worked; it is now guaranteed against a future change breaking it.

Full record: [remote sites need people](docs/implementation/SITE_STAFFING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - site staffing, and the stranded-crew guarantee (0.12.8-dev)

**Verbatim user quote:** *"get to it"*

**Verbatim owner direction, arriving mid-checkpoint:** *"and remmebr turning off a company gate with pawns inside doesnt lose control of those pawns they have to survive till a reconnection is made so they can escape"*

### What shipped

Staffing: a shipment to an unstaffed site **waits** rather than landing in an empty field. And the stranded-crew guarantee, which was **already true in every part** and is now enforced by an eleventh proof rather than rebuilt.

### Files touched

`src/RimroomsAsyncIndustries/Company/RemoteSites.cs`, `Procurement/RimroomsProcurementComponent.cs`, `UI/OperationsRemoteSites.cs`, keyed strings in `RR_Procurement.xml` and `RR_Operations.xml`, `docs/implementation/SITE_STAFFING_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and two proofs.

### Closure notes

- **Staffing gates ARRIVAL, not ordering**, and both alternatives were wrong: gating the order punishes planning, and gating nothing makes *"remote sites need people"* a sentence in a document. Two predicates - `CanReceiveDeliveryAt` for the address, `CanUnloadAt` for the arrival - and the split is the whole piece.
- **Staffed means employed, alive, present on that map and not downed.** Somebody unconscious cannot take delivery of anything. Checked live, so there is no assignment to maintain and no record to go stale.
- **The stranded-crew direction was already satisfied in every part, and verified rather than assumed:** `ShouldRemoveMapNow` returns false **unconditionally**; the expiry path touches no pawn; no gate source calls `PassToWorld`; `RecoverPortalOpening` exists and costs energy; the recovery path has no countdown; and `Alert_RimroomsRecoveryOverdue` tells the player.
- **So nothing was built for it and a proof was written instead.** The way it would break is an obvious-looking optimisation - *"a coordinate with nobody on it does not need to stay loaded"* - which would delete a map with a crew on it, **take colonists away permanently**, and produce no compiler error, no checker failure and no symptom until somebody lost five people. The proof fails the instant `ShouldRemoveMapNow` grows **any** condition.
- **A THIRD proof claim of mine could not fail**, found by fault-planting. It had a conditional fallback keyed off a method name that does not exist in the file, so it collapsed to a trivially-true expression. **A claim with a conditional fallback is a claim that can be trivially true.** Replaced with exact call-site counts. The replacement's first version was also wrong (`== 2` where the answer is three) - and it **failed immediately**, which is the difference between a wrong claim and one that cannot fail: the wrong one tells you.
- Build 0.12.8-dev, 172 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, eleven proofs hold, fault-planted seven ways across two of them. Assembly reproduced by two clean recompiles. **No game was launched, and nothing here has been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.7-dev**.', u'| Published | **0.12.8-dev**.'),
    (u'| Proofs | **ten** in `.local/register/proof-*.py`, all holding.',
     u'| Proofs | **eleven** in `.local/register/proof-*.py`, all holding.'),
    (u'## What shipped this session, 0.7.1 → 0.12.7',
     u'## What shipped this session, 0.7.1 → 0.12.8'),
    (u'| 0.12.7 | **Company-to-site logistics** — shipments reach a registered site; a latent cross-map reroute bug fixed before it could bite |',
     u'| 0.12.7 | **Company-to-site logistics** — shipments reach a registered site; a latent cross-map reroute bug fixed before it could bite |\n'
     u'| 0.12.8 | **Remote sites need people** — a shipment to an empty site waits; the stranded-crew guarantee proved rather than rebuilt |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

old_still = u"""     - **Still owed:** **staffing** a site — a site with nobody at it is a line on a ledger — and
       **the exit plan**, which the arc names and which a gate anchored at a site now makes
       possible rather than theoretical."""
new_still = u"""     - **Staffing it: DONE, 0.12.8-dev.** A shipment to an unstaffed site waits rather than
       landing in an empty field, checked at arrival so ordering ahead stays possible.
     - **Still owed: the exit plan.** A gate anchored at a registered site — which the ownership
       predicate now permits and nothing yet does. **This is where a second gate stops being
       theoretical.**"""
assert old_still in s, 'still-owed block not found'
s = s.replace(old_still, new_still, 1)

marker = u'168. **Permitted is not reachable.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'169. **A crew left on the far side is stranded, never taken.** Owner, verbatim: *"turning '
     u'off a company gate with pawns inside doesnt lose control of those pawns they have to '
     u'survive till a reconnection is made so they can escape"*. `ShouldRemoveMapNow` returns '
     u'false **unconditionally** — any condition there is a condition under which somebody’s '
     u'colonists vanish. No gate source may ever call `PassToWorld`. Asserted by '
     u'`proof-stranded-crew.py`.\n'
     u'170. **A claim with a conditional fallback is a claim that can be trivially true.** The '
     u'ordering claim keyed off a method name absent from the file and collapsed to a tautology. '
     u'**Third fail-open in one day, all three found by fault-planting and none by reading** — '
     u'which is what fault-planting is for (109, 152, 167).\n'
     u'171. **Gate a requirement where it bites, not where it is convenient.** Staffing is checked '
     u'at a shipment’s **arrival**, never at its ordering: gating the order punishes planning, and '
     u'gating nothing makes the rule a sentence in a document.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

insert_before('docs/TODO.md', u'\n## Owner directions recorded late, second pass', u"""
**Arc 5 continued (2026-09-29, 0.12.8-dev): staffing, and a guarantee verified.**

- [x] **A shipment to an unstaffed site waits.** Checked at **arrival**, not at ordering, so a player may order ahead while the crew walks there. Nothing is lost: the cargo is held and the payment stands.
- [x] **Staffed means employed, alive, present on that map and not downed.** Prisoners and slaves are never staff.
- [x] **"turning off a company gate with pawns inside doesnt lose control of those pawns"** - **ALREADY TRUE, verified rather than assumed, and now proved.** `ShouldRemoveMapNow` returns false unconditionally, the expiry path touches no pawn, no gate source calls `PassToWorld`, `RecoverPortalOpening` is the reconnection, it has no countdown, and `Alert_RimroomsRecoveryOverdue` tells the player.
- [x] **"they have to survive till a reconnection is made so they can escape"** - exactly what happens. Nothing was built; `proof-stranded-crew.py` was written instead, because the way this breaks is an innocuous-looking optimisation that would delete a map with a crew standing on it.
""")
