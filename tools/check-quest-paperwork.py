# -*- coding: utf-8 -*-
"""Checker 28 -- the company's paperwork has one writer, a reachable job, and no dead kinds.

WHY THIS INSTRUMENT EXISTS

The owner chose *"Both, and they must agree"* for what the green light reads from, and the risk was
stated when the option was offered: two things holding one truth is *"two derivations of one rule"*,
the defect this project keeps meeting. The design spends that risk down to **one writer and two
readers** -- and nothing except this checker can tell whether it stayed spent. A second caller of
`FileWriteUp`, or a second place that stamps a book, would reintroduce the whole problem silently
and every other instrument would stay green.

It also guards the two ways this feature can be *built and unreachable*, which is the failure mode
this repository has met most often: a write-up kind no request ever asks for, and a records desk no
work giver ever looks at.

THE RULES

 1. `RequestRecord.FileWriteUp` is the only thing that appends to the tally, and
    `FileWriteUpAndStamp` is its only caller.
 2. `CompRouteEvidence.StampForQuest` is only reachable from the operation that advances the record
    and the one that binds a new book -- and **every** call must pass the record's own
    `WriteUpsFiled.Count`, never a literal. That is what keeps the record authoritative.
 3. The record is written **before** the book in that method. The reverse order would stamp a book
    for work the record never recorded.
 4. Every `RimroomsWriteUpDef` is asked for by at least one request. A kind nobody wants is dead
    content that reads as a feature.
 5. Every `writeUps` entry on every request resolves to a real kind.
 6. Every `WriteUpPrecondition` member is handled in `WriteUpPreconditionMet`, and the default case
    **refuses** rather than returning true.
 7. The job driver asks `GateWatch.MustLeave` in both places -- the `FailOn` and the tick -- exactly
    as the gate console job does.
 8. The work giver asks the floor too, so a starving pawn is never offered the post.
 9. The desk def exists, carries a **Core** texture path, and is named by the work giver.
10. There is exactly one `HasArchivedCustody` derivation taking a `Thing`.
"""
import io
import os
import re
import sys

NL = chr(10)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join("Mod", "Rimrooms - Async Industries", "1.6")

PAPERWORK = os.path.join("src", "RimroomsAsyncIndustries", "Company", "QuestPaperwork.cs")
REQUEST_LINE = os.path.join("src", "RimroomsAsyncIndustries", "Company", "RequestLine.cs")
COMP = os.path.join("src", "RimroomsAsyncIndustries", "Investigation", "CompRouteEvidence.cs")
DRIVER = os.path.join("src", "RimroomsAsyncIndustries", "Company", "JobDriver_WriteUp.cs")
GIVER = os.path.join("src", "RimroomsAsyncIndustries", "Company", "WorkGiver_WriteUp.cs")
SETTLEMENT = os.path.join("src", "RimroomsAsyncIndustries", "Company", "EvidenceSettlement.cs")
WRITEUP_DEFS = os.path.join(MOD, "Defs", "RimroomsWriteUpDefs", "RR_WriteUps.xml")
REQUEST_DEFS = os.path.join(MOD, "Defs", "RimroomsRequestDefs", "RR_Requests.xml")
DESK_DEF = os.path.join(MOD, "Defs", "ThingDefs_Buildings", "RR_RecordsDesk.xml")
SOURCE_ROOT = os.path.join("src", "RimroomsAsyncIndustries")


def read(relative):
    path = os.path.join(ROOT, relative)
    return io.open(path, encoding="utf-8-sig").read() if os.path.isfile(path) else None


def body_of(text, signature):
    """One method's body, by signature, to the first dedented close brace.

    Used so a rule about `Resolve()` reads `Resolve()` rather than the whole file. Returns None when
    the signature is absent, and **the caller must treat that as a failure rather than as a pass** --
    an absent body contains nothing, so every `in` test against it is trivially false.
    """
    at = text.find(signature)
    if at < 0:
        return None
    end = text.find(NL + "        }", at)
    return text[at:end] if end > at else text[at:]


def strip_comments(source):
    """Drop comments so a rule cannot pass on prose describing itself.

    These files quote their own rules at length -- *"one writer, two readers"*, the owner's words,
    Core's own method bodies -- and every containment rule below would pass on the quotation alone.
    That is the single most repeated false green in this battery.
    """
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    return NL.join(line for line in source.split(NL) if not line.lstrip().startswith("//"))


def every_source_file():
    for folder, _, names in os.walk(os.path.join(ROOT, SOURCE_ROOT)):
        if os.sep + "bin" + os.sep in folder or os.sep + "obj" + os.sep in folder:
            continue
        for name in names:
            if name.endswith(".cs"):
                path = os.path.join(folder, name)
                yield os.path.relpath(path, ROOT), strip_comments(
                    io.open(path, encoding="utf-8-sig").read())


def main():
    problems = []

    paperwork = read(PAPERWORK)
    body = strip_comments(paperwork) if paperwork else ""
    if paperwork is None:
        problems.append("%s is missing; there is no green light and no paperwork service" % PAPERWORK)

    # ---------------------------------------------------- rules 1 and 2, exactly one writer each
    writers = []
    stampers = []
    for relative, source in every_source_file():
        for match in re.finditer(r"\.FileWriteUp\(", source):
            writers.append(relative)
        for match in re.finditer(r"\.StampForQuest\(", source):
            stampers.append(relative)
    # The definitions themselves are not calls; `FileWriteUp(` without a dot is the declaration.
    if len(writers) != 1 or writers[0] != PAPERWORK:
        problems.append("FileWriteUp is called from %d place(s) (%s); exactly one caller, "
                        "FileWriteUpAndStamp, may advance the tally or the record and the book can "
                        "drift apart" % (len(writers), ", ".join(sorted(set(writers))) or "none"))
    # **TWO LEGITIMATE STAMPERS, NAMED, AND A STRONGER RULE THAN "ONLY ONE".** The first draft
    # allowed one and the batch that added quest-book delivery tripped it -- correctly, because a
    # second call site had appeared. Reading it showed the call was legitimate: binding a BRAND NEW
    # book to a quest at the record's existing tally advances nothing.
    #
    # So the rule became the thing that actually matters: a stamp may only ever be handed
    # `request.WriteUpsFiled.Count`. Not a literal, not a computed number, not a cached one. That is
    # what keeps the record authoritative no matter how many places bind a book, and it is a tighter
    # rule than a caller count ever was.
    allowed_stampers = {PAPERWORK, os.path.join("src", "RimroomsAsyncIndustries", "Company",
                                                "QuestBookDelivery.cs")}
    unexpected = sorted(set(stampers) - allowed_stampers)
    if unexpected:
        problems.append("StampForQuest is called from %s, which is neither the one operation that "
                        "advances the record nor the one that binds a new book"
                        % ", ".join(unexpected))
    for relative, source in every_source_file():
        # Anchored on the dot: the first draft matched the DECLARATION, whose parameter list is
        # obviously not a call argument. `.StampForQuest(` is a call and nothing else is.
        for match in re.finditer(r"\.StampForQuest\(([^)]*)\)", source):
            arguments = match.group(1)
            if "WriteUpsFiled.Count" not in arguments:
                problems.append("%s stamps a book with %r instead of the record's own "
                                "WriteUpsFiled.Count. The record is the authority, so a stamp carrying "
                                "any other number is a receipt for something nobody recorded"
                                % (relative, arguments.strip()[:60]))

    # ---------------------------------------------------- rule 3, the record goes first
    if body:
        method = body.split("FileWriteUpAndStamp", 1)[-1]
        file_at = method.find("FileWriteUp(")
        stamp_at = method.find("StampForQuest(")
        if file_at < 0 or stamp_at < 0:
            problems.append("FileWriteUpAndStamp does not both file and stamp; it is the one place "
                            "that must do both")
        elif stamp_at < file_at:
            problems.append("FileWriteUpAndStamp stamps the book before writing the record. The "
                            "record is the authority, so the reverse order can stamp a book for "
                            "work the record never recorded")

    # ---------------------------------------------------- rules 4 and 5, nothing dead, nothing unresolved
    kinds = read(WRITEUP_DEFS)
    requests = read(REQUEST_DEFS)
    declared = set(re.findall(r"<defName>(RR_WriteUp_[A-Za-z0-9_]+)</defName>", kinds or ""))
    if not declared:
        problems.append("%s declares no write-up kinds" % WRITEUP_DEFS)
    wanted = set()
    for block in re.findall(r"<writeUps>([\s\S]*?)</writeUps>", requests or ""):
        wanted.update(re.findall(r"<li>([^<]+)</li>", block))
    for name in sorted(declared - wanted):
        problems.append("write-up kind %s is declared and no request asks for it. A kind nobody "
                        "wants is dead content that reads as a feature" % name)
    for name in sorted(wanted - declared):
        problems.append("a request asks for write-up %s, which is not declared. Outstanding "
                        "paperwork nobody can file is a green light that never comes on" % name)

    # ---------------------------------------------------- rule 6, every precondition handled
    defs_source = read(os.path.join("src", "RimroomsAsyncIndustries", "Company", "WriteUpDefs.cs"))
    members = re.findall(r"^\s{8}([A-Z][A-Za-z]*) = \d+,", strip_comments(defs_source or ""), re.M)
    if not members:
        problems.append("no WriteUpPrecondition members were found to check")
    for member in members:
        if body and ("WriteUpPrecondition." + member) not in body:
            problems.append("WriteUpPrecondition.%s is never handled in WriteUpPreconditionMet; an "
                            "unhandled precondition is paperwork that can never be written" % member)
    # **The FIRST statement after `default:`, not merely a `return false;` somewhere nearby.** The
    # first draft allowed 400 characters of slack and a plant walked straight through it: changing
    # `default:` to `default: return true;` left the original refusal further down, still inside the
    # window, and the rule passed on it. A guard that accepts any matching text in the vicinity is
    # not reading the guard.
    if body and not re.search(r"default:\s*return false;", body):
        problems.append("WriteUpPreconditionMet's default case does not refuse IMMEDIATELY. A new "
                        "precondition that silently returned true would hand a branch free "
                        "paperwork, and the failure would look like the feature working")

    # ---------------------------------------------------- rules 7 and 8, the need floor
    driver = read(DRIVER)
    driver_body = strip_comments(driver) if driver else ""
    if driver is None:
        problems.append("%s is missing; nothing writes the paperwork" % DRIVER)
    else:
        floors = driver_body.count("GateWatch.MustLeave(pawn)")
        if floors < 2:
            problems.append("the write-up job asks GateWatch.MustLeave %d time(s); it must be in the "
                            "FailOn AND in the tick, because a FailOn alone is only consulted when "
                            "the job is re-checked and a pawn starves between checks" % floors)
    giver = read(GIVER)
    giver_body = strip_comments(giver) if giver else ""
    if giver is None:
        problems.append("%s is missing; the desk is built and nothing offers work at it" % GIVER)
    elif "GateWatch.MustLeave(pawn)" not in giver_body:
        problems.append("the write-up work giver does not ask the need floor, so a starving pawn is "
                        "offered the job, fails out on the first tick and is offered it again")

    # ---------------------------------------------------- rule 9, the desk
    desk = read(DESK_DEF)
    if desk is None:
        problems.append("%s is missing; the approved buildable does not exist" % DESK_DEF)
    else:
        if "<defName>RR_RecordsDesk</defName>" not in desk:
            problems.append("the desk def does not declare RR_RecordsDesk")
        texture = re.search(r"<texPath>([^<]+)</texPath>", desk)
        if texture is None:
            problems.append("the desk def names no texture")
        elif texture.group(1).startswith("RR_") or texture.group(1).startswith("UI/"):
            problems.append("the desk's texture is %r, which is not a Core path. The records desk is "
                            "an approved exception to the content rule and NOT to the art rule: "
                            "\"The breach was the ART, not the defs\"" % texture.group(1))
    # **The GUARD, not merely a mention.** The giver names the desk twice -- once to resolve the def
    # and once to refuse anything else -- so a containment test passed while the refusal had been
    # pointed at a different def entirely. A plant proved it.
    if giver_body:
        if "GetNamedSilentFail(\"RR_RecordsDesk\")" not in giver_body:
            problems.append("the work giver does not resolve RR_RecordsDesk, so it never enumerates "
                            "any desk and the buildable is inert")
        if not re.search(r'defName\s*!=\s*"RR_RecordsDesk"', giver_body):
            problems.append("the work giver does not refuse things that are not RR_RecordsDesk, so "
                            "it would offer paperwork at any building it was handed")

    # ---------------------------------------------------- rule 10, one custody derivation
    settlement = read(SETTLEMENT)
    thing_forms = len(re.findall(r"bool HasArchivedCustody\(Thing ",
                                 strip_comments(settlement or "")))
    if thing_forms != 1:
        problems.append("%d Thing-form HasArchivedCustody derivation(s) exist; exactly one must, or "
                        "the quest book and the evidence record can disagree about what an archive "
                        "is" % thing_forms)

    # ------------------------------------- rules 11 to 13, two desks are not two people on one page
    #
    # **THE OWNER ASKED FOR PARALLEL AND PARALLEL IS WHERE THE BUG WAS.** *"u can have more than one
    # to have more than one pawn doing it as u can have multiple quests going"*. The desk was
    # uncapped and the giver scanned every desk, so two pawns could sit down at once -- and both
    # wrote the same report, because the scan returned the first outstanding one and knew nothing
    # about who was already writing it.
    #
    # Worse than a wasted session: the job re-derived its target every tick and carried its progress
    # across, so the moment the first writer filed, the second's progress was tested against the NEXT
    # report's requirement. A pawn 900 ticks into a 1000-tick report instantly completed a 600-tick
    # one. **One session of work, two reports filed.**
    #
    # Three rules, because the repair has three parts and any one of them alone is undone by the
    # other two being absent.
    paperwork_body = strip_comments(paperwork or "")
    if paperwork_body:
        if "private static bool ClaimedByAnother(" not in paperwork_body:
            problems.append("nothing excludes a report another pawn is already writing, so two desks "
                            "put two people on the same page")
        if re.search(r"bool TryFindWriteUpWork\(out ", paperwork_body):
            problems.append("a pawn-less TryFindWriteUpWork overload exists. Everything that asks "
                            "this is a pawn about to sit down, and an overload passing no pawn is a "
                            "quiet way back to the behaviour that let two people write one page")
    if driver_body:
        # **WORD-BOUNDED, BECAUSE A SUBSTRING TEST PASSES ON A RENAME.** A plant renamed the field
        # to `unclaimedRequestId` and this rule did not notice: the new name CONTAINS the old one.
        # And declaring a field is not claiming anything, so the assignment is asserted too -- a
        # claim that is never taken is two writers on one page with extra steps.
        if (not re.search(r"\bclaimedRequestId\b", driver_body)
                or not re.search(r"\bclaimedKindName\b", driver_body)):
            problems.append("the write-up job does not claim the report it sat down to write, so its "
                            "progress can land on a different one")
        if (not re.search(r"claimedRequestId\s*=\s*chosen\.Request\.Id", driver_body)
                or not re.search(r"claimedKindName\s*=\s*chosen\.Kind\.defName", driver_body)):
            problems.append("the claim is declared and never taken, which is the same as having no "
                            "claim at all -- the session would answer with whatever is outstanding")
        # **ABSENCE IS A FAILURE HERE, NOT A PASS.** `body_of` returns None when the signature is
        # gone, and an `in` test against `or ""` would then be false and the rule would report
        # nothing -- which is how a rule gets satisfied by its subject not existing. This repository
        # has shipped that mistake four times, once in a proof written in this same batch.
        resolve_body = body_of(driver_body, "private WriteUpTarget Resolve()")
        if resolve_body is None:
            problems.append("the write-up job has no Resolve() to read, so nothing here can tell "
                            "whether the session answers with its claim or goes looking for work")
        elif "TryFindWriteUpWork" in resolve_body:
            problems.append("Resolve() still searches for work instead of answering with the claim. "
                            "That is the defect itself: a session's progress migrates to whatever "
                            "report is outstanding next")
        if not re.search(r"Scribe_Values\.Look\(ref claimedRequestId", driver_body):
            problems.append("the claim is not scribed, so a save mid-session resumes writing a "
                            "different report than the one the pawn sat down to")
    # **EVERY call site, not merely one, and a plant proved the difference.** The giver asks twice --
    # once to enumerate desks and once to make the job -- and a rule satisfied by either one passing
    # a pawn let the other go stale. One stale call site IS the bug: that is the path that offers a
    # second writer the page the first is already on.
    if giver_body:
        asked = len(re.findall(r"TryFindWriteUpWork\(", giver_body))
        per_pawn = len(re.findall(r"TryFindWriteUpWork\(pawn,", giver_body))
        if asked == 0 or asked != per_pawn:
            problems.append("the work giver asks for work %d time(s) and only %d pass a pawn. Every "
                            "call must, or a second writer is offered the page the first is already "
                            "on" % (asked, per_pawn))

    print("check-quest-paperwork")
    print("  write-up kinds declared : %d" % len(declared))
    print("  kinds requested         : %d" % len(wanted))
    print("  preconditions checked   : %d" % len(members))
    print("  FileWriteUp callers     : %d" % len(writers))
    print("  StampForQuest callers   : %d" % len(stampers))
    print("  claim on the session    : %s"
          % ("yes" if driver_body and "claimedRequestId" in driver_body else "NO"))
    print("")
    if problems:
        for problem in problems:
            print("  FAIL   : %s" % problem)
        print("")
        print("  %d problem(s)" % len(problems))
        return 1
    print("  PASS   : one writer, two readers, and nothing built that cannot be reached")
    return 0


if __name__ == "__main__":
    sys.exit(main())
