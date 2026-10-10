# -*- coding: utf-8 -*-
import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = u"""

**Verbatim owner direction (2026-09-29), on facility equipment links:** *"get to it and remmebr these facilities when built will be big so some shelves and multiples need to be like connect via a option like beds connect to other furnature in making the gate work properly with everything needed and like things needed to be on shelves/records that computers and workbenches need to connect to ie we can use things like the research computer multianalysers and other such things and tool cabnets for enginners research benches and the like and these facilitys can be massive so thes connections need to be like on the same power systems and connected to gether via connections like furnature to beds and reach fare and through walls and manually connected for use of multi gate facilities"*

Nine items, one task each.

- [ ] **"these facilities when built will be big so some shelves and multiples need to be like connect via a option like beds connect to other furnature"** - the link affordance is RimWorld's own facility linkage: a thing you select shows lines to what it is connected to, and **multiples** of a role are allowed rather than exactly one.
- [ ] **"in making the gate work properly with everything needed"** - the link set is what a gate needs to work. Today a gate binds exactly one console, one battery and one assembly bench, and that is the whole shape being generalised.
- [ ] **"like things needed to be on shelves/records that computers and workbenches need to connect to"** - a **shelf is a record store a gate links to**, not scenery. This subsumes the queued *evidence case -> designated HQ shelf archive* replacement: the archive becomes one link role among several.
- [ ] **"ie we can use things like the research computer multianalysers and other such things and tool cabnets for enginners research benches and the like"** - the fillable equipment is **existing Core content**: `Multianalyzer`, `ToolCabinet`, `SimpleResearchBench`, `HiTechResearchBench`, `Shelf`, `CommsConsole`, `TableMachining`. Named by capability, per the standing content rule.
- [ ] **"these facilitys can be massive so thes connections need to be like on the same power systems"** - a link is only valid when both ends sit on the **same power network**. That is the constraint that makes a big facility a facility rather than a scatter of unrelated rooms.
- [ ] **"and connected to gether via connections like furnature to beds"** - the *feel* of Core's facility links, including the drawn lines, so nobody has to learn a new idea.
- [ ] **"and reach fare and through walls"** - **this is why Core's facility comps cannot simply be reused.** All the geometry lives on the facility side in `CompProperties_Facility`: `maxDistance = 8f` and `requiresLOS = true` by default, read from decompiled Core. Patching those on Core's `Multianalyzer` would change vanilla research-bench linking for every player and every other mod - and the register has three wall-mounted facility mods in the profile (rows 254, 256, 257) plus room-size changes (row 184). So the reach and the wall-transparency are **ours**, on our own link record, and Core's facility comps are left exactly as they are.
- [ ] **"and manually connected"** - never automatic. The same explicit designation the gate already uses for its providers; proximity never binds anything by itself.
- [ ] **"for use of multi gate facilities"** - **more than one gate in one facility**, each with its own link set, and a piece of equipment bound to one gate is not silently shared with another. The existing `ProviderAlreadyBound` refusal is the seed of this rule and already covers one case of it.

**Register checked before designing** (LAW). Families read: `facilities` (23), `furniture` (12), `storage` (15), `power` (13). Nothing to integrate with, and one thing to avoid: rows **254 Wall Heater**, **256 Wall Televisions** and **257 Wall Vitals Monitor** are wall-mounted **facility-linking** furniture, and row **184 Realistic Rooms Rewritten** changes room sizing. Row 257's review records a publisher comment about monitors stacking. None of them needs integration, and all of them are a reason **not** to alter Core's shared facility geometry.

"""

anchor = u'\n## Owner directions recorded late, second pass'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('links direction recorded verbatim in TODO.md, nine tasks')
