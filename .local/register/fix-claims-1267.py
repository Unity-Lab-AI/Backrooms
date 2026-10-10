# -*- coding: utf-8 -*-
"""The two plants that got through, and both were my claims' fault.

* **`RR_GateTelemetry` appears in a COMMENT in the same file** -- the def's own note explains that
  it *"puts PortalWindowTier at 1, which is the floor at which something may follow a crew out"*.
  So a plant deleting it from `<completedProjects>` left the comment standing and the whole-file
  claim was satisfied by it. Fortieth instance of the scoping trap; the claim reads the
  `completedProjects` element now.

* **The toggle claim asserted the machinery and not the refusal.** It pinned the three
  `SoleCandidate` calls, the headquarters check and the bind call -- all of which a plant that
  replaced `if (console == null || battery == null || bench == null)` with `if (false)` leaves
  untouched. The branch is the behaviour: without it the toggle binds whatever the scan happened
  to hand back, including null. Seventh instance this run.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-starts.py")

EDITS = [
    (u'''check("and the corporate start is the only one that begins with research finished",
      starts_xml.count("<completedProjects>") == 1
      and "RR_GateTelemetry" in starts_xml and "RR_Commerce_NegotiatedTerms" in starts_xml,''',
     u'''# **SCOPED TO THE ELEMENT.** `RR_GateTelemetry` also appears in this file's own COMMENT, which
# explains that it puts PortalWindowTier at 1 -- so a plant deleting it from the list left the
# comment standing and a whole-file claim was satisfied by it. Fortieth instance.
_cp = starts_xml.find("<completedProjects>")
completed_block = None if _cp < 0 else starts_xml[_cp:starts_xml.find("</completedProjects>", _cp)]
check("and the corporate start is the only one that begins with research finished",
      starts_xml.count("<completedProjects>") == 1
      and completed_block is not None
      and completed_block.count("<li>") == 8
      and "RR_GateTelemetry" in completed_block
      and "RR_Commerce_NegotiatedTerms" in completed_block,'''),

    (u'''      and "campaign.Headquarters != parent.Map" in gatecomp
      and "ShowOrderResult(BindNativeInfrastructure(console, battery, bench));" in gatecomp,''',
     u'''      and "campaign.Headquarters != parent.Map" in gatecomp
      and "ShowOrderResult(BindNativeInfrastructure(console, battery, bench));" in gatecomp
      # **THE REFUSAL BRANCH, not just the calls that feed it.** A plant replacing this test with
      # `if (false)` left every asserted line standing while the toggle bound whatever the scan
      # handed back, including null. Seventh instance this run of the same gap.
      and "if (console == null || battery == null || bench == null)" in gatecomp,'''),
]

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:62]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("both claims now read what the plants change")
