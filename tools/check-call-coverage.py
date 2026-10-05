# -*- coding: utf-8 -*-
"""Refuse a feature that is wired to SOME of its call sites and not the rest.

Why this exists
---------------
**Owner, 2026-10-05, verbatim:** *"u have a habit of half completing and half wiring up and half
connecting things"*. The criticism is accurate and the same checkpoint produced four examples of
it:

  * the generation notice was wired to **three of six** paths that can generate a map;
  * the solo/group two-map start was fully built and guarded by **nothing**;
  * grand rooms could be *anywhere* but there was still only **one**;
  * the viewing-wall direction was answered in code and its queue row was **lost**.

`check-wiring.py` refuses a def nothing reads and an action nothing calls. **Neither of those is
this defect.** A feature called from one site out of seven passes both, because every individual
file is correct and the thing that is missing is a call nobody wrote. Nothing looked at whether a
guard reaches *everywhere it has to*.

The shape of the rule
---------------------
A chokepoint is a function everything funnels through. For each one, `tools/call-coverage.json`
holds a **census**: every file that reaches it, each marked

  * `covered` -- and by a **named** wrapper, whose presence in that same file is then asserted, so
    deleting the wrapper and leaving the call behind fails; or
  * `exempt` -- with a **stated reason**, because some call sites genuinely cannot be covered. A
    tick cannot queue a long event and read its result.

Then three rules, and the third is the one that earns the file:

  1. every declared site must still be a real caller, so the census cannot rot;
  2. every `covered` site must still contain its wrapper;
  3. **every real caller must be declared.** A new path appearing undeclared fails the build --
     which is the one moment anybody is in a position to notice they are wiring up half of
     something.

What it deliberately does not do
--------------------------------
It does not try to prove coverage by following control flow. A wrapper reached through a lambda,
a delegate and a registrar is not something text can trace, and a rule that guessed would either
cry wolf or quietly accept anything. **The judgement is declared and the census is enforced**,
which is the same division `tools/retired-vocabulary.json` uses for the same reason.

Exit status is the result. Run from the repository root.
"""
import io
import json
import os
import sys

NL = chr(10)
SEP = chr(92)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
DECLARATION = os.path.join(REPO, "tools", "call-coverage.json")


def say(line):
    """Print without dying on a console that cannot encode a character in a reason."""
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def sources():
    found = {}
    for root, _, names in os.walk(SRC):
        parts = root.split(os.sep)
        if "obj" in parts or "bin" in parts:
            continue
        for name in sorted(names):
            if not name.endswith(".cs"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, SRC).replace(SEP, "/").replace(os.sep, "/")
            found[rel] = io.open(path, encoding="utf-8-sig").read()
    return found


def callers(files, callees, declaring):
    """Files that name any callee, excluding the files that declare the chokepoint itself."""
    hits = set()
    for rel, text in files.items():
        if rel in declaring:
            continue
        for callee in callees:
            if callee in text:
                hits.add(rel)
                break
    return hits


def main():
    if not os.path.isfile(DECLARATION):
        say("FAILED: the coverage declaration is missing: tools/call-coverage.json")
        return 1
    declaration = json.load(io.open(DECLARATION, encoding="utf-8-sig"))
    files = sources()
    problems = []
    say("call-coverage")
    say("  source files scanned      : %d" % len(files))

    for chokepoint in declaration.get("chokepoints", []):
        name = chokepoint.get("name", "<unnamed>")
        declared = chokepoint.get("sites", {})
        actual = callers(files, chokepoint.get("callees", []),
                         set(chokepoint.get("declaring_files", [])))
        covered = [rel for rel, entry in declared.items() if entry.get("status") == "covered"]
        exempt = [rel for rel, entry in declared.items() if entry.get("status") == "exempt"]
        # **COVERAGE IS SOMETIMES ONE FILE AWAY, and pretending otherwise would have forced a
        # false exemption.** `GateSpinUp.DialRememberedAddress` reaches the chokepoint, and the
        # wrapper that guards it sits in `GateConnectionHistory.cs`, the float menu that calls it.
        # The honest declaration names the other file and the rule checks it there -- which is
        # strictly stronger than marking the site exempt and writing a reason nobody can verify.
        elsewhere = [rel for rel, entry in declared.items()
                     if entry.get("status") == "covered_by_caller"]

        say("")
        say("  %s" % name)
        say("    call sites declared     : %d (%d covered, %d covered by caller, %d exempt)"
            % (len(declared), len(covered), len(elsewhere), len(exempt)))
        say("    call sites found        : %d" % len(actual))

        # 1. The census cannot rot: a declared site that no longer calls anything is a decision
        #    about code that is gone, and the next reader would trust it.
        for rel in sorted(declared):
            if rel not in actual:
                problems.append("%s: %r is declared but no longer reaches the chokepoint. Remove "
                                "the entry rather than leaving a decision about code that is gone."
                                % (name, rel))

        # 2. A covered site must still contain the thing that covers it. Deleting the wrapper and
        #    leaving the call is precisely "half wired", and it would otherwise read as covered.
        for rel in sorted(covered):
            wrapper = declared[rel].get("by")
            if not wrapper:
                problems.append("%s: %r is marked covered with no wrapper named. 'Covered' with "
                                "nothing to check is a comment, not a guard." % (name, rel))
                continue
            if rel in files and wrapper not in files[rel]:
                problems.append("%s: %r is declared covered by %r and does not contain it. The "
                                "guard was removed and the call left behind."
                                % (name, rel, wrapper))

        # 2b. A site covered from elsewhere must name BOTH the wrapper and the file holding it,
        #     and that file must really contain it. Without the file the claim is unverifiable,
        #     which is the same as an exemption with a nicer label.
        for rel in sorted(elsewhere):
            wrapper = declared[rel].get("by")
            holder = declared[rel].get("in")
            if not wrapper or not holder:
                problems.append("%s: %r is marked covered_by_caller without naming both the "
                                "wrapper and the file that holds it. An unverifiable claim is an "
                                "exemption wearing a better label." % (name, rel))
                continue
            if holder not in files:
                problems.append("%s: %r is declared covered from %r, which is not a source file "
                                "any more." % (name, rel, holder))
                continue
            if wrapper not in files[holder]:
                problems.append("%s: %r is declared covered from %r by %r, and that file does not "
                                "contain it. The guard moved or went."
                                % (name, rel, holder, wrapper))

        # 3. An exemption has to say why, or it is just a list of things somebody waved through.
        for rel in sorted(exempt):
            if not (declared[rel].get("reason") or "").strip():
                problems.append("%s: %r is exempt with no reason. An exemption without a reason "
                                "is the half-wiring this file exists to refuse, written down."
                                % (name, rel))

        # 4. **THE RULE THAT EARNS THE FILE.** A new path that reaches the chokepoint and says
        #    nothing about whether it is guarded is exactly how a feature ends up wired to some of
        #    its call sites.
        for rel in sorted(actual):
            if rel not in declared:
                problems.append("%s: %r REACHES THE CHOKEPOINT AND IS NOT DECLARED. Mark it "
                                "covered by a named wrapper, or exempt with a reason. This is the "
                                "moment to decide, not later." % (name, rel))

    say("")
    if problems:
        say("FAIL: %d coverage problem(s)" % len(problems))
        for problem in problems:
            say("  - %s" % problem)
        return 1
    say("PASS: every call site of every declared chokepoint is covered or exempt with a reason")
    return 0


if __name__ == "__main__":
    sys.exit(main())
