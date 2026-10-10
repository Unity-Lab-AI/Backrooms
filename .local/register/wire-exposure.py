# -*- coding: utf-8 -*-
"""Wire staff prior exposure: recorded where the fact is known, consumed where it matters.

**Recorded** inside `NoteReturnedFromField`, which is the one place in the mod where *this person
came back from there* is already established. A second caller would be a second definition of
"came back".

**Consumed** in `SpinUpWorkRequiredFor`, which is the single place that decides what bringing a
gate up costs. The operator who has personally walked an address dials it faster. That is *"staff
prior exposure affecting how an expedition goes"* landing on existing, proven machinery rather
than inventing a parallel one.

**Applied once, and never compounding.** The branch factor multiplies once per previous
connection because a branch keeps records; a person has either walked it or not. And it sits
**after the floor is computed and inside the same `Mathf.Max`**, so a well-worn route stays quick
and still never free -- the property the familiarity discount already guarantees.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
DEBRIEF = os.path.join(SRC, "Company", "StaffDebrief.cs")
COMPONENT = os.path.join(SRC, "Company", "RimroomsCampaignComponent.cs")
SPINUP = os.path.join(SRC, "Gate", "GateSpinUp.cs")

EDITS = []

# ---------------------------------------------------------------- 1. record it
EDITS.append((DEBRIEF, u"""                if (pawn == null || pawn.Dead || pawn.Destroyed) { continue; }
                if (HoldFor(pawn) != null) { continue; }""",
              u"""                if (pawn == null || pawn.Dead || pawn.Destroyed) { continue; }
                // **Staff prior exposure, recorded here because this is where the fact is
                // known.** Above the idempotence guard on purpose: the hold is a transient
                // debrief obligation and the exposure is a permanent field history, so a
                // second completion must not be able to skip the history along with the hold.
                NoteFieldExposure(pawn, coordinateId);
                if (HoldFor(pawn) != null) { continue; }"""))

# ---------------------------------------------------------------- 2. save it
EDITS.append((COMPONENT, u"            ExposeClearSquad();",
              u"            ExposeClearSquad();\n            ExposeFieldExposure();"))

# ---------------------------------------------------------------- 3. consume it
EDITS.append((SPINUP, u"""            float floor = required * GateProps.dialSpinUpFloorFraction;
            int prior = PriorConnectionsTo(coordinateId);
            float familiarity = SpinUpFamiliarityFactor;
            for (int step = 0; step < prior; step++)
            {
                required *= familiarity;
                if (required <= floor) { return floor; }
            }
            return Mathf.Max(floor, required);""",
              u"""            float floor = required * GateProps.dialSpinUpFloorFraction;
            int prior = PriorConnectionsTo(coordinateId);
            float familiarity = SpinUpFamiliarityFactor;
            for (int step = 0; step < prior; step++)
            {
                required *= familiarity;
                if (required <= floor) { return floor; }
            }
            // **Staff prior exposure.** The loop above is the BRANCH's history -- one discount
            // per previous connection, because a branch keeps records. This is the PERSON's,
            // and it applies **once**: the operator has either walked this address or they have
            // not, and the tenth walk does not teach them the way a tenth filed report teaches
            // the branch. Owner's prep item: *"field history, trust/stress/exposure"*.
            if (dialCampaign != null)
            { required *= dialCampaign.ExposureDialFactor(assignedOperator, coordinateId); }
            return Mathf.Max(floor, required);"""))

problems = []
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    if text.count(old) != 1:
        problems.append("%d of %r in %s" % (text.count(old), old[:52], os.path.basename(path)))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    io.open(path, "w", encoding="utf-8-sig", newline="").write(text.replace(old, new, 1))

debrief = io.open(DEBRIEF, encoding="utf-8-sig").read()
component = io.open(COMPONENT, encoding="utf-8-sig").read()
spinup = io.open(SPINUP, encoding="utf-8-sig").read()

failures = []
if u"NoteFieldExposure(pawn, coordinateId);" not in debrief:
    failures.append("exposure is never recorded")
if debrief.index(u"NoteFieldExposure(pawn, coordinateId);") > debrief.index(
        u"if (HoldFor(pawn) != null) { continue; }"):
    failures.append("exposure is recorded after the idempotence guard, so a repeat skips it")
if u"ExposeFieldExposure();" not in component:
    failures.append("exposure is never saved")
if u"dialCampaign.ExposureDialFactor(assignedOperator, coordinateId)" not in spinup:
    failures.append("exposure is never consumed -- built and unreachable")
if u"return Mathf.Max(floor, required);" not in spinup:
    failures.append("the floor is no longer applied, so a route could become free")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("exposure wired: recorded at the one place it is known, saved, and spent on the dial")
