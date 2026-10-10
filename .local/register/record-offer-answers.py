# -*- coding: utf-8 -*-
import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = u"""

**Verbatim owner direction (2026-09-29), to ask then build:** *"use ask me question then get to the work of getting this mod done as ouutlined and as described in totality and what/how it needs implimentation useing the prep docs and mod chart's information to properlly build everything as detailed and layed out and as the lkayout needs currects or has conflicts use ask me question soon than later"*

- [x] **HELD as the standing method from here.** Four blocking questions were asked before building, and a conflict is raised **at the point it is found**, not after.

**Four answers at the fork, recorded because each one decides an architecture:**

- [x] **Quest surface: our Operations tab records.** The existing `ContractRecord` system is extended rather than native `QuestScriptDef` adopted. Core's quest system is built around time-limited offers with single objectives, which is precisely the two things the absolutes forbid; fighting it would be work spent to arrive back where we started.
- [x] **Route model: *"1 and 3"*** - fixed set per request family **and** an authored floor plus derived extras. These are the same answer at two strengths: **every family declares at least two routes of different kinds in XML, and branch capability may add more on top.** The authored floor is what makes the absolute unbreakable; the derived extras are what make a developed branch feel developed.
- [x] **Research: our project defs**, as the gate branch already is. Insight plus completed logs, worked at the laboratory. Native research points cannot express *"you need a distortion log"*, which is the whole mechanic.
- [x] **Contact is a state, not a scenario.** Owner, verbatim: *"clena up tema is only once u are in communication and working with the corporation Async industries starts with this tech research and other basic gate techs it needs to operate and begin researching and gate operations at basic levels but the other two scenerios need special treatment in theri layout and starts as its all going off whats the game play will be like as you can imagine the differernt points of view of starts build out as each one does into the samw universial rimworld tech tree of all our mods in the collection on top of our mod"*
  - [ ] **Async Industries starts in contact**, with basic gate tech already researched, and can operate and research at basic levels from the first minute.
  - [ ] **The Store and Solo/Group starts need their own layout and treatment**, each a different point of view on the same world, and **neither begins in contact**. Reaching contact is what turns the clean-up team on for them.
  - [ ] **All three feed the same universal RimWorld tech tree** shared by every mod in the collection - **our research layers on top of it and never forks it.** That is a compatibility constraint on every branch still to be built.

"""

anchor = u'\n## Owner directions recorded late, second pass'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('direction and four answers recorded verbatim in TODO.md')
