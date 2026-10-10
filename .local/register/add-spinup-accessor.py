# -*- coding: utf-8 -*-
"""Expose the address a gate is ramping toward.

The crew panel has to ask *has this person walked the address we are dialling* and the field
`spinUpCoordinateId` was private with no accessor. Added as a read-only property rather than
widening the field, so nothing outside the gate can change what it is ramping toward -- the gate
stays the only thing that decides that.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPINUP = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Gate", "GateSpinUp.cs")

ANCHOR = u"""        public bool IsSpinningUp"""

ADDITION = u'''        /// <summary>
        /// The address this gate is ramping toward, or null when it is not ramping.
        ///
        /// Read-only on purpose. The crew panel needs it to say whether a candidate has walked
        /// this route before -- staff prior exposure -- and nothing outside the gate may change
        /// what it is dialling.
        /// </summary>
        public string SpinUpCoordinateId { get { return spinUpCoordinateId; } }

'''

text = io.open(SPINUP, encoding="utf-8-sig").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(SPINUP, "w", encoding="utf-8-sig", newline="").write(
    text.replace(ANCHOR, ADDITION + ANCHOR, 1))

after = io.open(SPINUP, encoding="utf-8-sig").read()
failures = []
if u"public string SpinUpCoordinateId { get { return spinUpCoordinateId; } }" not in after:
    failures.append("the accessor was not added")
if u"set { spinUpCoordinateId" in after:
    failures.append("the accessor is writable; the gate must stay the only thing that sets it")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("SpinUpCoordinateId exposed read-only")
