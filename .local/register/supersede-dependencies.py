# -*- coding: utf-8 -*-
"""Record the dependency decision where decisions live, and mark every document it overturns.

Owner direction, 2026-10-01: *"see thats WRONG the mod DOES HAVE HARD DEPENDANCIES SO GET IT RIGHT
AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*, and *"there are alot more
depeandacies than just the DLC we have alkinds of mods in the 274 mod list WE ARE USING ALL OF
THEM!!!!"*.

That overturns **D3** and **D4**, recorded 2026-09-27. `docs/GATE_0_DECISIONS.md` already has the
house pattern for this: D1 carries its own change inline, with the owner's words and what it
supersedes. D3 and D4 get the same treatment.

## Why a banner and not 43 inline parentheticals

Forty-three lines across twenty documents say the package needs Core only. Every one was true when
written. Rewriting each sentence in place would mean editing design contracts that record what was
decided at a date -- and **this project's standing practice is to scope superseded reasoning, not
delete it**: the clean-up team's trigger comment was scoped rather than removed today, and the DLC
checker kept its rule while losing its stale reason.

So each affected document gets **one banner, at the top, where a reader sees it before the prose**.
The near-public documents are additionally corrected inline, because somebody reads those for
current truth rather than for history.

## The verbatim ledger is untouchable

`TODO.md`, `NOW.md`, `ROADMAP.md` and `PREPRODUCTION_AND_IMPLEMENTATION_TODO.md` carry twenty-nine
of the seventy-two matches, and **LAW #0 forbids altering the owner's recorded words**. They are
records of what was said, not claims about what is true. The rule exempts them by name, with that
reason written down.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-doc-conformance.py")

BANNER = u"""> **Superseded 2026-10-01 — dependencies.** This document predates the owner's decision that the
> package has hard dependencies. `About.xml` now declares all five expansions and the whole
> collection as requirements, so anything here describing a Core-only route is history rather than
> a current claim. Recorded as a change to D3 and D4 in
> [Gate 0 decisions](GATE_0_DECISIONS.md#decision-log).

"""

# Relative to the repository root. `AGENTS.md` sits at the root, so its link needs a prefix.
MARKED = [
    os.path.join("docs", "ARCHITECTURE.md"),
    os.path.join("docs", "CAMPAIGN_CONTENT_CATALOG.md"),
    os.path.join("docs", "CAMPAIGN_ECONOMY_MODEL.md"),
    os.path.join("docs", "CAMPAIGN_ECONOMY_PROGRESSION.md"),
    os.path.join("docs", "CAMPAIGN_ROSTER_FREEZE.md"),
    os.path.join("docs", "COMPATIBILITY.md"),
    os.path.join("docs", "CONTENT_REUSE_POLICY.md"),
    os.path.join("docs", "FEATURE_TRACEABILITY.md"),
    os.path.join("docs", "FIRST_PLAYABLE_CONTRACT.md"),
    os.path.join("docs", "FIRST_SLICE_CONTENT_INVENTORY.md"),
    os.path.join("docs", "MOD_INTEGRATION_PLAN.md"),
    os.path.join("docs", "MULTIPLAYER.md"),
    os.path.join("docs", "OPERATIONS_ACTION_CONTRACTS.md"),
    os.path.join("docs", "PLAYING.md"),
    os.path.join("docs", "PUBLIC_RELEASE_PLAN.md"),
    os.path.join("docs", "SCENARIOS.md"),
    os.path.join("docs", "SKILL_TREE.md"),
    os.path.join("docs", "SYSTEMS_CATALOG.md"),
    os.path.join("docs", "TECHNICAL_ARCHITECTURE.md"),
    os.path.join("docs", "GATE_0_DECISIONS.md"),
    "AGENTS.md",
]

written = 0
for rel in MARKED:
    path = os.path.join(REPO, rel)
    if not os.path.isfile(path):
        print("MISSING %s" % rel)
        raise SystemExit(1)
    text = io.open(path, encoding="utf-8-sig").read()
    if u"Superseded 2026-10-01 — dependencies" in text:
        continue
    banner = BANNER
    if rel == "AGENTS.md":
        banner = banner.replace(u"[Gate 0 decisions](GATE_0_DECISIONS.md",
                                u"[Gate 0 decisions](docs/GATE_0_DECISIONS.md")
    # After the H1 so the title still reads first.
    lines = text.split(u"\n")
    insert = 0
    for index, line in enumerate(lines):
        if line.startswith(u"# "):
            insert = index + 1
            break
    while insert < len(lines) and lines[insert].strip() == u"":
        insert += 1
    lines.insert(insert, banner.rstrip(u"\n") + u"\n")
    io.open(path, "w", encoding="utf-8-sig", newline="").write(u"\n".join(lines))
    written += 1
print("banner written into %d document(s)" % written)

# ---------------------------------------------------------------- the decision log
DECISIONS = os.path.join(REPO, "docs", "GATE_0_DECISIONS.md")
text = io.open(DECISIONS, encoding="utf-8-sig").read()

EDITS = [
    (u"| D3 | B — all 294 are the research/test target; only Core + Harmony/RWT required; other profile mods optional. Owner says test rows 182 and 274 in the co-op candidate despite publisher warnings; no support claim before results. | 2026-09-27 | TODO, compatibility, mod plan, technical architecture, interaction map |",
     u"| D3 | **CHANGED by the owner 2026-10-01: every mod in the collection is a hard dependency.** *\"there are alot more depeandacies than just the DLC we have alkinds of mods in the 274 mod list WE ARE USING ALL OF THEM!!!!\"*. `About.xml` declares 289 mods plus the five expansions, each with a display name and a link, and every one also as a load-order constraint. Supersedes B (all 294 are the research/test target; only Core + Harmony/RWT required; other profile mods optional), recorded 2026-09-27. | 2026-09-27, **changed 2026-10-01** | About.xml, compatibility, mod plan, technical architecture, the wiki |"),
    (u"| D4 | A — all five DLC optional; Core-only campaign; validate all-five profile | 2026-09-27 | TODO, compatibility, scenario, mod plan, systems catalog |",
     u"| D4 | **CHANGED by the owner 2026-10-01: all five expansions are hard dependencies.** *\"the mod DOES HAVE HARD DEPENDANCIES SO GET IT RIGHT AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE\"*. Supersedes A (all five DLC optional; a Core-only campaign), recorded 2026-09-27. **The graceful guards stay** — the owner chose to declare the requirement and still look content up by name, so a player who ignores the warning degrades rather than crashes. | 2026-09-27, **changed 2026-10-01** | About.xml, compatibility, scenario, mod plan, systems catalog, the wiki |"),
]
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:44]))
if problems:
    for problem in problems:
        print("DECISION ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(DECISIONS, "w", encoding="utf-8-sig", newline="").write(text)
print("D3 and D4 recorded as changed, following D1's own pattern")

# ---------------------------------------------------------------- the rule learns both
OLD_RULE = u'''def check_dependency_claims(rel, raw, declared, problems):'''
NEW_RULE = u'''# **The verbatim ledger is exempt, and the reason is a LAW.** These four carry the owner's own
# recorded words, and LAW #0 forbids altering them. They are records of what was said, not claims
# about what is true, and twenty-nine of the seventy-two matches live in them.
DEPENDENCY_LEDGER = {
    os.path.join("docs", "TODO.md"),
    os.path.join("docs", "NOW.md"),
    os.path.join("docs", "ROADMAP.md"),
    os.path.join("docs", "PREPRODUCTION_AND_IMPLEMENTATION_TODO.md"),
}

# A document may carry one supersession banner instead of rewriting forty-three sentences that
# were each true when written. It has to be near the top, because a supersession a reader meets
# after the prose it supersedes has not superseded anything.
DEPENDENCY_SUPERSEDED = re.compile(r"Superseded 2026-10-01 .{0,4} dependencies", re.I)


def check_dependency_claims(rel, raw, declared, problems):'''

text = io.open(CHECKER, encoding="utf-8").read()
if text.count(OLD_RULE) != 1:
    print("RULE ANCHOR PROBLEM: %d" % text.count(OLD_RULE))
    raise SystemExit(1)
text = text.replace(OLD_RULE, NEW_RULE, 1)

OLD_BODY = u'''    if declared <= 0:
        return
    fenced = False'''
NEW_BODY = u'''    if declared <= 0:
        return
    if rel in DEPENDENCY_LEDGER:
        return
    head = u"\\n".join(raw.split(u"\\n")[:18])
    if DEPENDENCY_SUPERSEDED.search(head):
        return
    fenced = False'''
if text.count(OLD_BODY) != 1:
    print("BODY ANCHOR PROBLEM: %d" % text.count(OLD_BODY))
    raise SystemExit(1)
text = text.replace(OLD_BODY, NEW_BODY, 1)
io.open(CHECKER, "w", encoding="utf-8", newline="").write(text)

after = io.open(CHECKER, encoding="utf-8").read()
failures = []
if u"if rel in DEPENDENCY_LEDGER:" not in after:
    failures.append("the ledger exemption was not applied")
if u"if DEPENDENCY_SUPERSEDED.search(head):" not in after:
    failures.append("the banner exemption was not applied")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("rule learns the ledger exemption and the top-of-document banner")
