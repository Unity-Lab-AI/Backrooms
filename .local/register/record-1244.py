# -*- coding: utf-8 -*-
"""Record the three first-launch fixes and the owner's decisions. Status changes only."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

# --------------------------------------------------------------------------------- the queue
todo = io.open(TODO, encoding="utf-8").read()

EDITS = [
    (u"- [ ] **F12 collides with HugsLib's \"Publish log file\", and every function key F1–F12 "
     u"is bound across Core plus the 288 installed mods.**",
     u"- [x] **FIXED 0.12.44-dev: the default is `Backslash`, owner's choice, and it is bound by "
     u"nothing in Core and nothing in the 288-mod profile.** The proof now refuses **any** "
     u"function key rather than only the ones Core takes — that is the rule which would have "
     u"stopped 0.12.40-dev shipping the collision, and it is portable in a way \"free in this "
     u"profile\" is not. A plant puts F12 back and is caught. It remains only a **default**: "
     u"Core's generator still emits a rebindable `MainTab_RR_Operations`, and the help pane reads "
     u"the player's live binding rather than the shipped one. Was: **F12 collides with HugsLib's "
     u"\"Publish log file\", and every function key F1–F12 is bound across Core plus the 288 "
     u"installed mods.**"),

    (u"- [ ] **EdB Prepare Carefully cannot classify our GlowPod scenario grant**",
     u"- [x] **FIXED 0.12.44-dev: the glow pods are pre-placed in each start's fixed facility, "
     u"owner's choice.** EdB never sees them now, so the warning is gone — and a placed glow pod "
     u"can still be uninstalled, minified and carried, so the only thing given up is editing them "
     u"in Prepare Carefully. **Eight cells for Async, three for the Store, every one computed "
     u"free against the occupied set rather than eyeballed**, because `GenStep_Headquarters` "
     u"**throws** on an occupied or out-of-bounds cell: a wrong coordinate is a hard crash at map "
     u"generation, not a cosmetic slip. The Async eight sit on the store-room floor beside the "
     u"stock cell rather than in a bedroom. Was: **EdB Prepare Carefully cannot classify our "
     u"GlowPod scenario grant**"),

    (u"- [ ] **The Furniture Store start places no machining table, so it cannot run the gate "
     u"assembly bill from what it arrives with.**",
     u"- [x] **NOT A DEFECT — owner's answer, verbatim: *\"the store start has a natural portal "
     u"and to build a machanical one they need to contact the company and resaerch whats "
     u"needed\"*.** The defs already said exactly that and I had not read them together: "
     u"`beginsInCorporationContact` is **false** and `completedProjects` is **empty** for both "
     u"the Store and the solo start, against Async's **eight** including `RR_GateTelemetry`. So "
     u"the bench is not the gate to building a gate — **contact and research are** — and the "
     u"Store is simply earlier in its own progression. **What needed fixing was the readout**, "
     u"which called it *\"does not arrive able to raise a gate\"* and described a designed step "
     u"as a deficiency. It now has three conclusions for the three real situations: everything "
     u"standing; missing hardware **while in contact and holding the research**, which really is "
     u"something to build or buy; and **out of contact with no research**, where a built gate is "
     u"later work and there is already a way through that nobody built. No change to the Store's "
     u"facility. Was: **The Furniture Store start places no machining table, so it cannot run the "
     u"gate assembly bill from what it arrives with.**"),
]

problems = []
for old, _ in EDITS:
    if todo.count(old) != 1:
        problems.append("%d of %r" % (todo.count(old), old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    todo = todo.replace(old, new, 1)
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("three first-launch rows closed")

# ----------------------------------------------------------------------------------- NOW.md
now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"SHA-256 `4A2986BEA5B4A315FFF93773F58340C01750BC317040B79EC463E40BBD33EB7B`",
     u"SHA-256 `D0EF34D3358A9390E74D5DEA7BB066AB3F8FC27A343AECD35A02009112378F63`"),
    (u"| Published | **0.12.43-dev**.", u"| Published | **0.12.44-dev**."),
    (u"**OPEN — F12 collides with HugsLib.**",
     u"**FIXED — the hotkey is `Backslash`.** Bound by nothing in Core and nothing in the "
     u"profile, and **the proof now refuses any function key at all** rather than only the ones "
     u"Core takes, which is the portable form of the rule that would have caught this.\n\n"
     u"**FIXED — the glow pods are pre-placed** in each start's fixed facility, so EdB never "
     u"parses them and the warning is gone. Eleven cells, **every one computed free**, because "
     u"`GenStep_Headquarters` throws on a clash rather than skipping it.\n\n"
     u"**NOT A DEFECT — the Store's missing bench.** Owner: *\"the store start has a natural "
     u"portal and to build a machanical one they need to contact the company and resaerch whats "
     u"needed\"*. `beginsInCorporationContact` false and `completedProjects` empty for the Store "
     u"and solo, against Async's eight. **The readout was the defect**, calling a designed "
     u"progression step a deficiency; it has three conclusions now for the three real situations.\n\n"
     u"**The original, for the record — F12 collided with HugsLib.**"),
]
problems = []
for old, _ in NOW_EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:60]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in NOW_EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.44-dev")
