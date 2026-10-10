# -*- coding: utf-8 -*-
"""Ledger and queue for 0.12.35-dev: containment you can see from the other side of a gate."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


sub("CHANGELOG.md", u"## 0.12.34-dev", u"""## 0.12.35-dev - 2026-09-29 - containment you can see from the other side of a gate

- **You are now told when containment fails somewhere you are not looking.** The base game warns you about the map you have open; this warns you about every other place the company holds something, which is the warning that actually matters when you are standing in a coordinate watching a crew work.
- **A holding platform that has lost power with something on it now says so.** The base game has no warning for that at all.
- **The branch has a standing order for a containment failure: cut every open connection and bring the crews home.** It is on by default, the facilities pane says which way it is set, and you can turn it off if you would rather decide each time.
- **You can sound the alarm yourself** from the comms console, which does the same thing on demand.
- **The facilities report has a containment section** listing what the company is holding across every site, and a containment category that finds any holding platform or prisoner bed without naming a single one.

Full record: [containment you can see from the other side of a gate](docs/implementation/CONTAINMENT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.34-dev""")

sub("docs/FINALIZED.md", u"## Completed sessions", u"""## Session 2026-09-29 - containment you can see from the other side of a gate (0.12.35-dev)

**Verbatim user quote:** *"keep up the work left completeing them asll we are trying to complete this mother"*

### What shipped

Three of row 761's five remaining halves: containment rooms, security procedures, and alarm/escape response. Staff debrief and quarantine remain and the row stays open for them.

### Files touched

`src/.../Threats/ContainmentWatch.cs` **new**, `src/.../Presentation/RimroomsContainmentAlerts.cs` **new**, `src/.../Company/ContainmentProtocol.cs` **new**, `src/.../Company/ContainmentAlarmGizmo.cs` **new**, `src/.../Company/RimroomsCampaignComponent.cs`, `src/.../Company/CampaignServices.cs`, `src/.../Facilities/FacilityReport.cs`, `src/.../UI/OperationsFacilities.cs`, `src/.../Gate/CompRimroomsGateConsole.cs`, `1.6/Defs/RimroomsFacilityDefs/RR_FacilityCategories.xml`, `1.6/Languages/English/Keyed/RR_Company.xml`, `1.6/Languages/English/Keyed/RR_Portals.xml`, `.local/register/proof-containment.py` **new**, `docs/implementation/CONTAINMENT_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **THE FIRST DESIGN WAS WRONG AND CORE SAID SO.** The obvious build was alerts for low containment strength, high activity and an untended subject. Enumerating Core's own alert classes first found **four already exist** - `Alert_InsufficientContainmentStrength`, `Alert_DangerousActivity`, `Alert_EntityNeedsTend`, `Alert_NeedHoldingPlatform`. Shipping ours would have been **a second opinion beside a rule the player is already shown**, which is the exact defect a fault plant caught at 0.12.33-dev.
- **READING THEM FOUND THE REAL GAP.** Every one of the four opens with `if (Find.CurrentMap == null) { return false; }` and then reads `Find.CurrentMap.listerThings`. **Core's containment warnings are about the map on screen.** That is correct for RimWorld, where a colony is one map, and wrong for a mod whose premise is several live maps at once. A player standing in a coordinate watching a crew work **gets no warning at all** that something is coming off a platform back home. Same gap the gate alerts closed at 0.10.5-dev, same fix: walk `Find.Maps`.
- **AND THE TWO SETS NEVER OVERLAP, BY CONSTRUCTION.** Both new alerts skip `Find.CurrentMap` entirely. On the map in view Core's four are the only voice; ours speak only about the maps you are not looking at. Making the sets disjoint is cheaper and safer than matching Core's conditions exactly and hoping they stay matched across a game update. The unpowered alert also stands down for a platform already being escaped from, so one platform never produces both.
- **The unpowered-holder condition is genuinely unclaimed.** Core has no alert for a holding platform that has lost power, on any map. That is the one condition worth stating that is not a restatement.
- **CONTAINMENT ROOMS ARE A CAPABILITY MATCH, AND THE NAMED VERSION WAS WRONG TWICE.** The first attempt listed `HoldingPlatform` in `buildingDefNames`. `HoldingPlatform` is an **Anomaly** defName, so a `<li>` naming it is read by `check-dlc-gating.py` as an ungated expansion reference in a Core-only mod; and a named list covers **no modded holder**. The def now carries no names at all: `includeContainment` matches any building with `CompEntityHolder` plus any bed Core calls a prisoner bed. **Prisoner beds are in deliberately** - containment is not an Anomaly-only idea here, and on a Core-only install it is the only kind there is.
- **"SECURITY PROCEDURES" WAS SETTLED FROM EXISTING MACHINERY, NOT INVENTED.** Two things already existed: `PersonnelRoles` has carried a **`security`** role since the hiring layer shipped, and `CompRimroomsGate.TriggerEmergencyCutoff()` is a public entry point that closes a live connection **and starts the return window**, so one call shuts the door and brings the crew home. So the procedure is a **standing order the player sets once and the branch executes without being asked** - which is what a procedure is, as against an order. It calls that same method the player's own cutoff button calls, so the two can never disagree about what closing a connection means.
- **It defaults to ARMED, and that was the save-compatibility decision.** `Scribe_Values` hands back the default for a missing field, so an older save loads with the procedure armed rather than silently disarmed. Defaulting to `false` is one of the seventeen planted faults and it is caught.
- **The procedure never re-decides what a breach is.** `ContainmentWatch` reports that Core's own `isEscaping` is set; the proof asserts `isEscaping` appears **nowhere** in the protocol. It opens nothing, moves nobody and touches no subject - one call on gates that are already open.
- **The manual alarm runs the same body as the automatic one**, because two code paths for slam-the-doors are two chances to disagree, and it **refuses with a reason** when nothing is open rather than reporting a success that closed nothing.
- **A CHECKER CAUGHT A REAL MISS BEFORE IT SHIPPED.** `RR_Company_Unavailable` was referenced in the protocol's refusals and did not exist. `check-keyed-strings` found it.
- **MY OWN CHECK WAS THE DEFECT ONCE, AGAIN.** The proof asserted no expansion defName appears in `ContainmentWatch.cs` by matching the substring `HoldingPlatform`, and flagged `CompHoldingPlatformTarget` - a comp **type** in the base assembly, which is exactly the right thing to use. Tightened to `ThingDefOf.HoldingPlatform` and the quoted literal. **That is the third time this session the measurement was wrong and the code was fine.**
- Build 0.12.35-dev, **186 C# files, 87 package files**, **0 warnings, 0 errors**, assembly identical across two clean rebuilds. Eleven checkers pass, **thirty-two** proofs exit zero, **17 of 17** planted faults caught. **No game was launched.**

---

## Completed sessions""")

sub("README.md", u"**Current development version: 0.12.34-dev.**",
    u"**Current development version: 0.12.35-dev.**")

# ------------------------------------------------------------------ the queue row
sub("docs/TODO.md",
    u"**Containment rooms, security procedures, staff debrief, quarantine and alarm/escape "
    u"response remain**, and evidence custody and case records already shipped.",
    u"**CONTAINMENT ROOMS, SECURITY PROCEDURES AND ALARM/ESCAPE RESPONSE BUILT 0.12.35-dev.** "
    u"Core already ships four containment alerts and **every one reads `Find.CurrentMap`**, so "
    u"the real gap was never *\"containment has no warning\"* but *\"containment has no warning "
    u"about the maps you are not looking at\"* - which is this mod's whole premise. Two alerts "
    u"cover exactly that and skip the current map entirely so they can never duplicate Core's. "
    u"Containment rooms are a tenth facility category matched by **capability** "
    u"(`CompEntityHolder` plus Core's own prisoner-bed test), naming no expansion def. The "
    u"security procedure is a standing order - on a breach, cut every open connection through "
    u"the gate's own existing `TriggerEmergencyCutoff`, which also starts the return window - "
    u"armed by default, readable in both directions, with a manual alarm on the console running "
    u"the same body. Record `implementation/CONTAINMENT_IMPLEMENTATION.md`, proof "
    u"`proof-containment.py`. **Staff debrief and quarantine remain**, and evidence custody and "
    u"case records already shipped.")

print("ledger and queue written for 0.12.35-dev")
