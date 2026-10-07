# PLAYBOOK — every order the owner has given for playing the colony

**Why this file exists, owner's words, 2026-10-07:** *"u need to make meals sooner than later and get your shellves organized so like i already told you. so wtf are you not making a guide of everything ive told you becasue im not fucking around you are gonna die if u dont take care of them"*

**Read this before every play session and walk it top to bottom every in-game day.** Every order is quoted verbatim. Colony evidence and the full test rows live in [`TEST.md`](TEST.md); this is the checklist that is worked, not the record.

---

## 1. Keep the colonists alive — FIRST, every check

- *"u need to make meals sooner than later"* — a cook bill is running **and somebody is actually cooking it**. A bill nobody prioritizes is not food.
- *"cook bill maintained at 50 rather than 10"* — the stove's simple meal bill is **Do until you have X = 50**.
- *"maintain ur colonists' needs"* — food, rest, mood, health checked every in-game day.
- *"maintain and watch your resources"*
- *"meds in hospital"*
- *"get your freezer storages set up so that noraml non needing frozen goods arent in the freezer and things like ambrosia, wort, food, healroot are in the freezer"*

## 2. Defence — the drill when something comes

- *"set everyone to attack not flee and group up when something attacks and draft and flee attack never letting someone melle person or animal get close to your pawns kill them with range at all costs"*
- *"defend your base"*
- *"embracures near boarders as rooms to shoot frioom to where u head to the closest defences bewteen ur base and the enmies do ranged first and retrating/firing so mele guys cant get to close"*
- *"and u have to pause at the right times as not to wit to long to give commands in combat situations"* — **play in short bursts and read alerts between every burst.**

## 3. Storage

- *"get your shellves organized so like i already told you"*
- *"oraganize ur shelfs"*
- *"build a vault ... cash silver gold high valuable gemms irvory in vaults"*

## 4. Work and pawns

- *"set theri scheldule to anything at all times for all pawns"*
- *"research and manage your pawns"*
- *"research what u need to unlock better things u can produce"*
- *"accept neew employees hire them"*

## 5. Food and money

- *"collecting resources planting crops and setting bills for food"*
- *"grow resources"*
- *"start growing cash cropsa"*
- *"start buisnesss"*
- *"make company money from quests"*
- *"do quests and missions increase ur cash"*

## 6. Building

- *"expand the base build prisons and more facilities"*
- *"build prison build guest questers"*
- *"upgrade build shit you need"*
- *"lab upgrade"*
- *"get prisoners working keep then contained use locks to allow them to enter work areas with exterial walls and defences containing them , layers of security"*

## 7. The gate

- *"get the gate connected"*
- *"work towrds starting up the gate and get in to the back rooms"*
- *"start seting up the gate"*

## 8. How to play without wrecking things

- *"you still have t explored your facility to find the bed rooms and other unexplored rooms"* — the facility is fogged and only walking reveals it.
- *"saw an error, u tried mining an area that was unexplored yet ... half a fucking mountain was set to mine out"* — **only designate cells that have been read; a mine order is a seam or a room, never a block.**
- *"there is no wood no trees on this map, thats why in advanced setting on world gen setup you set 300x300 mapo and spring, and then when choosing a map tile u pic on that has mountains(the rock areas on map) in forest area and jungle areas"* — new colonies are rolled that way.
- *"use ask me question where u need my eyes"*
- Drive the UI with semantic clicks (`.local/qa/click-label.py`); pixels last. Clear any live designator before a pixel click.
- **A survey or contract is an EXPEDITION, and the expedition opens the gate itself.** Do not open a session by hand first: the expedition dispatch refuses on a gate that is already open, and the survey only pays when its route recording comes home as an expedition's cargo -- a hand-ordered crossing creates no expedition and its payment never settles. *Order a crossing* on an open session is for moving people, not for contract work. On the refusal, the owner: *"this isnt a issue for me u just dont know what ur doing i think"*.
- **Never click an unlabelled icon on a bill row without proving what it is** — on a bill row the order is plus, minus, delete. One unproven click deleted the cook bill on 2026-10-07.

## 9. A survey, start to payout — learned by playing AI-01, 2026-10-07

1. **Debrief** anyone back from a trip (Operations → Facilities → *Debrief*), or they cannot go out again.
2. **Kit:** tick the crew on Expedition, *Order physical shared-kit pickup*, and give each a meal and two glow pods. **Never keep them drafted for long — drafted pawns do not eat.**
3. **Operator on the console** before dispatch, then *Approach gate and dispatch*. Do not open a session by hand first.
4. **On site, pick up the bound record** in the office copy room — a textbook already lying there, which the menu offers as *"Order … to collect the record book"*. The blank company books do not count.
5. **Witness the first room of each family** with the bound record carried by anyone on the map: threshold room, survey lobby, office copy, service passage, borrowed corridor, return gallery. The Atlas lists surveyed rooms; the Investigation pane says which ones count.
6. **Route mismatch:** drop a glow pod, install it in a proper room, *Mark this pod* → Route home, then walk into a borrowed corridor.
7. **Come home** with *Recall crew along the return route*.
8. **File the record** on a shelf linked to the gate as *Records archive* (gate → *Linked equipment*), with that shelf allowing **Books** at **Critical** priority.
9. **Analyse** at the company laboratory bench (Investigation → designate one). The survey pays when analysis reaches 100 %.
