# -*- coding: utf-8 -*-
import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = u"""

**Verbatim owner direction (2026-09-29), on logs gating tech and the corporation's rescue:** *"ie u need certain logs complete to operate the higher teri techs and shit and gate features and upgrades all story line in quests layed out and coporation requasts and missions.. and remember the mega mother corp is greedy and will basic do anything and put up with anything to make sure you succssed to the point of sending clean up teams to your base with all access passses to wipe the facitly of all hostals and requisition a new basic team supplies drops like a fresh start of sorts so that facilities never die, this is liken the store and solo/group scenerios once they reach contact with the corporation"*

Five items, one task each.

- [ ] **"u need certain logs complete to operate the higher teri techs and shit and gate features and upgrades"** - a company project requires **named completed logs**, not only spendable insight. The log kinds already exist on every evidence record (`routeRecorded`, `distortionRecorded`, `entityRecorded`) and nothing reads them as a prerequisite yet.
  - **This direction landed on a real defect.** `GateProps.portalWindowTierProjects` holds **one** project, `RR_GateTelemetry`, so `PortalWindowTier` can never exceed **1** - while `portalIndefiniteTier` is **4**. An indefinite connection is **permanently unreachable**, and incursion at tier 1 sits at the very top of what exists. A ladder with four rungs declared and one built, and no checker can see it. Same class as the retired-beacon condition found in 0.10.7-dev.
- [ ] **"all story line in quests layed out and coporation requasts and missions"** - the storyline as quests plus corporation requests and missions. **Nothing exists yet**: there is no `QuestScriptDef` in the package and the contract system holds exactly one template, `rr.survey.onboarding.v1`. Depends on the ladder above existing, because a quest that unlocks a tier needs tiers to unlock.
- [ ] **"the mega mother corp is greedy and will basic do anything and put up with anything to make sure you succssed"** - the parent corporation's character, and the reason the rescue below is not charity. It protects an investment.
- [ ] **"to the point of sending clean up teams to your base with all access passses to wipe the facitly of all hostals and requisition a new basic team supplies drops like a fresh start of sorts so that facilities never die"** - **a facility never dies.** On collapse the corporation sends a clean-up team with all-access passes, clears every hostile from the facility, requisitions a fresh basic team, and drops supplies - a restart rather than a loss. This is a **no-fail floor**, which is a deliberate, owner-chosen departure from RimWorld's ordinary willingness to end a colony.
- [ ] **"this is liken the store and solo/group scenerios once they reach contact with the corporation"** - scoped to the **Store** and **Solo/Group** starts, and **only after contact with the corporation**. Before contact there is no rescue, which is what makes those openings frightening and the rescue meaningful.

**Register checked before designing** (LAW). Families read: `contracts` (12), `faction standing` (11), `subject casework` (19), `evidence` (7). Nothing to integrate with. Two rows are adjacent and neither needs anything: **148 No Quests Without Comms** gates quest arrival on a comms console, which our own gate already requires a `CommsConsole` for, and **132 More Faction Interaction** adds its own faction quests without touching a mod's own quest defs. Row **100 Go Explore!** adds exploration quests, likewise independent.

"""

anchor = u'\n## Owner directions recorded late, second pass'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('corporation direction recorded verbatim in TODO.md, five tasks')
