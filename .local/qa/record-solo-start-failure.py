# -*- coding: utf-8 -*-
"""Record and close the solo/group start failure the owner's fourteenth launch found."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "### Owner direction — anything standing on your map may cross a gate, and zoning is the control (2026-10-06)"

S = NL.join([
"### Owner report — the solo/group start left everybody on the surface with no gate (2026-10-06)",
"",
"**Verbatim owner report (2026-10-06):** *" + Q + "major problem!!! i tried the solo/group start and "
"the people and everything spawned in the world tile map incorrectly... i didnt even see a natrual "
"gate in the world of the starting map chossed, and they were to spawn in the backrooms and didnt to "
"find the gate that leads to that world tile map thewy started in so there seemsed to be multiple "
"problems and u need to thouroughly understand the issues and make the fixed and ducment "
"them" + Q + "*",
"",
"**Recorded after the diagnosis rather than before it, because this was a live failure report and the "
"evidence was a log that is overwritten by the next launch.** Everything below was read out of "
"`Player.log` and the source, not reasoned from the symptoms.",
"",
"**ONE THROW PRODUCED ALL THREE SYMPTOMS, AND THE LOG NAMES IT.** "
"`[Rimrooms][Generation] Site layout stopped; existing coordinate/map are retained: "
"System.InvalidOperationException: RR_Generation_UnreachableRoom`, thrown from "
"`GenStep_BackroomsDestination.ValidatePlacedLayoutCore`. The chain, each link verified in source:",
"",
"| Step | What happened |",
"|---|---|",
"| 1 | `ValidatePlacedLayoutCore` threw, so **`MarkLayoutReady` on line 334 never ran** |",
"| 2 | `ValidateExistingMap` saw `!parent.LayoutReady` and returned a failure |",
"| 3 | `DestinationService.EnsureSite` returned `Fail(...)` |",
"| 4 | `SoloGroupOpening.Open` returned at **step 2 of 5** |",
"| 5 | Step 3 marks the surface door as the way out -- **never reached**, so no natural gate |",
"| 6 | Step 5 moves the party inside -- **never reached**, so everybody stayed on the surface |",
"",
"**So *" + Q + "multiple problems" + Q + "* was one fault wearing three faces**, which is why it "
"could not be found by looking at any of them.",
"",
"**AND THE BUILD THE OWNER RAN WAS NOT THE BUILD ON DISK.** Measured: the staged assembly is dated "
"**02:51** and the built one **23:00** the same day, both declaring `0.12.99-dev`. So the launch "
"contained none of that day's work. **The fault is genuinely pre-existing and not a regression from "
"it** -- established by timestamp rather than assumed -- but the staging gap is its own row below.",
"",
"- [x] **The fatal reachability check contradicted a deliberate feature, and that is the root cause.**"
" `ValidatePlacedLayoutCore` walked **every** room in `coordinate.Rooms` and demanded each be "
"`Reachable` from the entry. **`RoomLayoutPlanner.SealedFamily` rooms are authored with zero links on "
"purpose** -- `CandidateIsSafe` asserts exactly that -- because a sealed vault is meant to be found by "
"mining, which is the owner's own *" + Q + "veins leading to other rooms so insentive to mine things "
"out to find isolated undiscorvered rooms" + Q + "*. "
"**THE PLANNER HAD ALREADY SETTLED THE RULE AND THE VALIDATOR WAS ASKING A DIFFERENT QUESTION**, which "
"is *two derivations of one rule*, the defect this project keeps meeting. The planner's own words: "
"*" + Q + "the reachability proof now asks its question of rooms that **claim** a route. A room with "
"links must be walkable to; a room with none is a vault, and the rock around it is `Mineable` like all "
"the fill, so it is reachable in the only sense this room wants to be." + Q + "* **So the planner "
"approved a layout and the validator then destroyed the coordinate for containing the feature the "
"planner had deliberately put in it** -- which is why it was intermittent: it only fires when the "
"rolled candidate includes a vault. "
"**FIXED 0.12.99-dev** by asking the planner's question: a room with no links is skipped. "
"**Tested on `Links` rather than on the family name**, so a future sealed family inherits the rule "
"instead of needing to be remembered in a second place. "
"**And the sibling check two lines down was audited rather than assumed safe:** "
"`content.Clues.Count != coordinate.Rooms.Count` would have been the same bug one rung lower if "
"vaults got no clue -- they do, because `AddClue` runs for every room in the loop including the "
"vault's own `Gold`/`Plasteel` case. One pattern, all the references it guards.",
"- [x] **The failure named nothing, which is why it cost a log dive to attribute.** "
"`RR_Generation_UnreachableRoom` is a keyed string a player reads and `FailedSiteRecovery` matches on "
"it, so the thrown message **stays the bare key**; the detail now goes beside it in a `Log.Error` "
"naming the coordinate, the room index, its family, its bounds, how many links it claims, and "
"**which of the two failures it was** -- no standable interior cell at all, versus a standable cell "
"with no route from the entry. **A fatal error that does not say which room means the next launch "
"reproduces the same uninformative log.**",
"- [x] **A wall lamp could never be wired, so a coordinate ships dark.** The same log: "
"*" + Q + "WallLamp is not on the generator's power net" + Q + "*. Measured cause: `voidFloor` is "
"`WaterDeep`, and `BuildShell` sets it on **every cell of the map** before the rooms are carved -- so "
"only a room's *interior* ever gets a floor and **a room's own wall cells keep void terrain.** Both "
"`FindConduitRoute` and `TrySpawnNativeConduit` refuse a void cell, and a `WallLamp` is mounted *in* "
"a wall, so its only cell is a void cell: the route could never arrive and the lamp was never wired. "
"**Wall lamps are the Backrooms look**, so this is the fixture most likely to be left dark, and on a "
"solo start it means waking up in the dark. "
"**FIXED 0.12.99-dev by exempting the consumer's own footprint from the void rule, in both places.** "
"Both, because exempting only the search would end a route one cell short -- a change that passes a "
"reading and fixes nothing, which is worse than the defect for looking solved. **The void rule still "
"keeps conduits out of solid rock everywhere else**, which is the whole reason it exists, and a "
"conduit under a wall is ordinary vanilla construction. "
"**Stated plainly: this half is unverified until a launch.** The arithmetic and the terrain are "
"measured; whether Core then joins that lamp to the net is a thing only the game answers.",
"- [ ] **The owner launched a build 21 hours older than the one on disk, and the instrument already "
"said so.** `check-package-integrity` rule 10 reported *" + Q + "THE STAGED COPY IS NOT THIS "
"BUILD" + Q + "* with nine differing files before the launch, and it was read as an expected "
"environmental note because RimWorld was open at the time. **It was the warning working.** The rule "
"to draw is not a new instrument but an ordering one: **staging belongs immediately before the owner "
"launches, not at publication**, because a launch loads the staged copy and nothing else. Until that "
"is settled in `PUBLISHING.md` and `NOW.md`, every launch report risks describing code that is not "
"the code on disk -- which is the most expensive kind of wasted session there is.",
"- [ ] **Core's mineable scatter step was not found, so coordinate ore density is a guess.** Same "
"log: *" + Q + "Core's mineable scatter step was not found; coordinate ore density falls back to 10 "
"lumps per 10k cells before the owner's x3" + Q + "*. `OreVeinBuilder.CoreLumpsPer10kCells` scans for "
"a `GenStep_ScatterLumpsMineable` and did not find one on the owner's 294-mod profile. **It is a "
"stated fallback rather than a fault**, and ore still spawns -- but the number is this mod's guess "
"instead of Core's own, which is exactly the shape of claim this repository measures rather than "
"assumes. Worth finding out why the scan missed it.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "the solo/group start left everybody on the surface" in text:
        print("already recorded")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("solo start failure recorded: 3 closed, 2 open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
