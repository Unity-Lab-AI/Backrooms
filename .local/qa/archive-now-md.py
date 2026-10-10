"""Archive the accumulated docs/NOW.md into FINALIZED.md, then truncate it.

Owner direction, 2026-10-02, verbatim:
  "and the now.md needs to be completedy deleted, then written current. The NOW
   .md is a temp read file not a history of all work ever done.. its a one time
   record only ever holding one record"

`docs/NOW.md` had become a history: 3,053 lines, 238 KB, 37 `##` sections, NINE
separate `STATE AT THIS HANDOFF` records stacked on top of each other. It is the
handoff -- one record, replaced each time, never appended to.

"Completely deleted" means deleted from `NOW.md`. It does not mean destroyed:
`§FINALIZED BEFORE DELETE` applies to any verbatim record, so the whole file goes
to the archive first and is confirmed present there before `NOW.md` is touched.
The replacement handoff is written separately, by hand, because what the next
session needs to know is a judgement and not a transform of what this one did.
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
NOW = os.path.join(REPO, "docs", "NOW.md")
FINALIZED = os.path.join(REPO, "docs", "FINALIZED.md")

BEGIN = "<!-- archived-queue:begin -->"
END = "<!-- archived-queue:end -->"


def main():
    apply_it = "--apply" in sys.argv
    original = io.open(NOW, encoding="utf-8").read()
    lines = original.split("\n")
    heads = [line for line in lines if line.startswith("## ")]
    handoffs = [line for line in heads if "STATE AT THIS HANDOFF" in line]

    print("archive-now-md")
    print("  docs/NOW.md              : %d lines, %.1f KB"
          % (len(lines), len(original.encode("utf-8")) / 1024.0))
    print("  '## ' sections           : %d" % len(heads))
    print("  stacked handoff records  : %d" % len(handoffs))
    for line in handoffs:
        print("      %s" % line[:88])

    if not apply_it:
        print()
        print("  PLAN ONLY. Nothing written. Re-run with --apply.")
        return 0

    archive = []
    archive.append("")
    archive.append("---")
    archive.append("")
    archive.append("## Archived from the queue - the whole of docs/NOW.md before it was reset (2026-10-02)")
    archive.append("")
    archive.append(BEGIN)
    archive.append("")
    archive.append("**Verbatim owner direction (2026-10-02):** *\"and the now.md needs to be completedy "
                   "deleted, then written current. The NOW .md is a temp read file not a history of all "
                   "work ever done.. its a one time record only ever holding one record\"*")
    archive.append("")
    archive.append("`docs/NOW.md` is the **handoff**: one record, read at the start of a session and "
                   "replaced at the end of one. It had become a history instead - **%d lines, %.1f KB, "
                   "%d `##` sections, and NINE separate `STATE AT THIS HANDOFF` records stacked on top of "
                   "each other**, each one a checkpoint's worth of narrative that nobody was ever going "
                   "to delete. A file that only grows is not a handoff; it is an archive with a "
                   "misleading name, and `FINALIZED.md` is the archive."
                   % (len(lines), len(original.encode("utf-8")) / 1024.0, len(heads)))
    archive.append("")
    archive.append("**\"Completely deleted\" means deleted from `NOW.md`, not destroyed.** The entire file "
                   "as it stood is reproduced below, unaltered, and was confirmed present here before "
                   "`NOW.md` was touched - `§FINALIZED BEFORE DELETE` applies to any verbatim record, not "
                   "only to a task row. The replacement handoff was then written by hand, because what "
                   "the next session needs to know is a judgement rather than a transform of this one.")
    archive.append("")
    archive.append("> the whole of `docs/NOW.md`, as it stood on 2026-10-02 before the reset")
    archive.append("")
    archive.extend(lines)
    archive.append("")
    archive.append(END)
    archive.append("")

    existing = io.open(FINALIZED, encoding="utf-8").read()
    io.open(FINALIZED, "w", encoding="utf-8", newline="").write(
        existing.rstrip("\n") + "\n" + "\n".join(archive)
    )

    written = io.open(FINALIZED, encoding="utf-8").read()
    missing = [line for line in lines if line.strip() and line not in written]
    if missing:
        io.open(FINALIZED, "w", encoding="utf-8", newline="").write(existing)
        raise SystemExit("ABORT: %d lines of NOW.md are not present in the archive; "
                         "FINALIZED.md restored, NOW.md untouched. First: %r"
                         % (len(missing), missing[0][:110]))

    io.open(NOW, "w", encoding="utf-8", newline="").write(
        "# NOW\n\n_(reset 2026-10-02; the handoff is being written)_\n"
    )

    print()
    print("  docs/FINALIZED.md        : archive appended, %d lines" % len(archive))
    print("  verbatim confirmation    : all %d non-blank lines present" % len([l for l in lines if l.strip()]))
    print("  docs/NOW.md              : TRUNCATED, awaiting the single current record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
