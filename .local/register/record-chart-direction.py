# -*- coding: utf-8 -*-
import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = u"""

**Verbatim owner direction (2026-09-29), on designing the whole chart before building any of it:** *"make sure the whole mission line and tech linkange and research tree line chart is full complete before you start building out all the corporation requests tech research lines and all of that and any and all things i didnt mention that apply before you randomly and will nilly build out the scenerio quests that all should play out like a tutoriasl of sorts that turn open ended to campaine and nothing ever ever have time restripctions but the gate(ie power tech and maintanance and workflorce and other factors all determine the time a gate can be open) but missions and quests and offeres and trades are never time senstive the company will wait as long as possible for you to complete their task offers and never offer only one path but multiple success routes"*

Seven items, one task each. **This is a stop-building instruction and it is being obeyed: the chart is designed first, and no quest, contract or research content is written until it is complete.**

- [ ] **"make sure the whole mission line and tech linkange and research tree line chart is full complete before you start building out all the corporation requests tech research lines and all of that"** - the complete chart, as a document, before any content. The four-rung window ladder built in 0.10.9-dev is **one branch of it**, not the chart.
- [ ] **"and any and all things i didnt mention that apply"** - the chart must cover what the owner did not enumerate, drawn from the prep material and the register rather than invented. Explicitly a licence to include, not a licence to guess: anything added has to trace to a prep document or an existing system.
- [ ] **"before you randomly and will nilly build out the scenerio quests"** - no ad-hoc content. A quest is written only once the chart says where it sits and what it unlocks.
- [ ] **"that all should play out like a tutoriasl of sorts that turn open ended to campaine"** - the scenario quests are a **tutorial that becomes a campaign**. The early line teaches by being played, and the transition to open-ended is a designed point on the chart, not a fade-out.
- [ ] **"nothing ever ever have time restripctions but the gate(ie power tech and maintanance and workflorce and other factors all determine the time a gate can be open)"** - **AN ABSOLUTE.** The only clock in the mod is how long a gate holds a connection, and that clock is the *consequence* of power, tech, maintenance, workforce and the other physical factors rather than a timer set against the player. **This needs to be enforced, not just written down**, because a deadline is the easiest thing in the world to add by accident.
- [ ] **"but missions and quests and offeres and trades are never time senstive the company will wait as long as possible for you to complete their task offers"** - no expiry on a mission, quest, offer or trade. The corporation waits. This is consistent with the corporation's greed already recorded: an investment it is protecting is not an investment it withdraws for being slow.
- [ ] **"and never offer only one path but multiple success routes"** - **AN ABSOLUTE.** Every offer carries **at least two** ways to succeed. Also to be enforced rather than trusted, because one route is what an offer naturally has unless somebody insists otherwise.

"""

anchor = u'\n## Owner directions recorded late, second pass'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('chart direction recorded verbatim in TODO.md, seven tasks')
