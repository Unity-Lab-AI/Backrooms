# -*- coding: utf-8 -*-
"""Transfer the Forgejo outage diagnosis into the permanent archive before the
NOW.md section that holds it is deleted. Narrative goes to FINALIZED.md -- the
owner's own rule for what NOW.md is."""
import io

NL = chr(10)
PATH = "docs/FINALIZED.md"

ENTRY = NL.join([
"",
"---",
"",
"## The Forgejo outage, and the cascade back to ten refs (2026-10-05, 0.12.92-dev)",
"",
"**Recorded here because `docs/NOW.md` is a one-record handoff and this is finished narrative.**",
"The section this replaces told the next reader to treat a Forgejo refusal as known rather than",
"as a defect to investigate. The host is back, so the instruction is spent -- but **the diagnosis",
"is not**, and it is kept here so nobody spends that time a second time if it ever recurs.",
"",
"### The arc, in the owner's own words",
"",
"**Owner, 2026-10-04, verbatim:** *\"hold up you should not have any problems making the cascade on",
"forgejo you are probably doing it wrong\"* -- **and on the procedure they were right.** I had",
"improvised the cascade instead of reading `docs/PUBLISHING.md`, and the specific thing I did",
"wrong -- creating local `Prep`/`Develop`/`Main` tracking branches -- is named in that file as a",
"way previous agents have already got this wrong. It was **not** the cause of the failure, and it",
"was still the wrong way to do it. The rule that came out of it stands regardless: **push by",
"refspec from the feature branch.**",
"",
"**Owner, 2026-10-05, verbatim:** *\"okay apparently forgejo is down, so until we get it back up we",
"are stuck cascading to github only\"* -- so 0.12.91-dev and 0.12.92-dev published to **five** refs,",
"and that was correct rather than a shortfall. Forgejo sat at `2d0b677` (0.12.90-dev) for four",
"commits.",
"",
"**Owner, 2026-10-05, verbatim:** *\"okay read now.md to continue then first we need to make the",
"forgejo pushes, its back up and last cascade to forgejo was a while ago\"* -- and it was back. The",
"first push I attempted, the same one that had failed ten times, was accepted.",
"",
"### The root cause, so it is never re-derived",
"",
"```",
"error: remote unpack failed: unable to create temporary object directory",
"```",
"",
"That is **`tmp_objdir_create()`** in Git: the push *quarantine* directory,",
"`objects/incoming-XXXXXX` inside the repository **on the server**. `receive-pack` creates it on",
"**every** push, before reading a single object -- so pack size, object count, refspec form and ref",
"count are **irrelevant by construction**, which is why no amount of reshaping the push helped.",
"",
"Ruled out from this end, each with evidence rather than assumption: the SSH key (`ssh -T`",
"authenticated by name), read versus write (`ls-remote` listed every ref), the procedure",
"(`PUBLISHING.md` §4 followed literally), pack shape (`--no-thin`, single-threaded, one ref",
"alone), our own repository (`gc` and `fsck` clean), the namespace (`GFourteen/Backrooms` is the",
"only target that exists; `UnityAILab/Backrooms` does not), and transience (ten attempts).",
"**Everything left was server-side disk or permissions on the Forgejo host, and the recovery",
"confirms it: nothing changed on this machine between the last failure and the first success.**",
"",
"### The recovery, which needed no rebuilding",
"",
"`2d0b677` was an ancestor of `0c2712d`, so this was `PUBLISHING.md` §4 **Case A** exactly -- five",
"fast-forwards by refspec, no merge, no force, no local integration branches:",
"",
"```",
"2d0b677..0c2712d  feature/bug-testing -> feature/bug-testing",
"2d0b677..0c2712d  feature/bug-testing -> Prep",
"2d0b677..0c2712d  feature/bug-testing -> Develop",
"2d0b677..0c2712d  feature/bug-testing -> Main",
"2d0b677..0c2712d  feature/bug-testing -> feature/connected-colony-portals",
"```",
"",
"Four commits delivered in one pack: `6145f4a`, `6953169`, `96092db`, `0c2712d`. Read back per §5",
"at **ten** refs, not five -- `forgejo refs at 0c2712d: 5 of 5`,",
"`github refs at 0c2712d: 5 of 5`.",
"",
"### What is kept as a standing rule",
"",
"- **The cascade is ten refs.** Both remotes, five branches each. A publish that reads back fewer",
"  has silently left something unpublished, and the count is the trap `PUBLISHING.md` §5 warns",
"  about in its own words.",
"- **An outage is recorded, not re-investigated.** The cost of this one was not the push; it was",
"  the hour spent proving the failure was not ours. A written diagnosis is the only thing that",
"  makes that hour a one-time cost.",
"- **A doc that claims a dead host while the host is alive is a lie in the handoff**, which is why",
"  the deletion of that section is part of the same commit as the push that made it false.",
"",
])

text = io.open(PATH, encoding="utf-8").read()
if "The Forgejo outage, and the cascade back to ten refs" in text:
    print("already recorded; nothing written")
    raise SystemExit(1)
before = len(text)
io.open(PATH, "a", encoding="utf-8", newline=NL).write(ENTRY)
after = len(io.open(PATH, encoding="utf-8").read())
print("FINALIZED.md: %d -> %d chars (+%d), appended %d lines"
      % (before, after, after - before, ENTRY.count(NL)))
