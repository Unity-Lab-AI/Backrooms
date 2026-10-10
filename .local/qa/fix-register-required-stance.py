# -*- coding: utf-8 -*-
"""Two register rows claimed this package requires a mod. It requires none.

**Owner, 2026-10-05, asked the question that found this:** *"we dont need to do this do we? ... as
the Rimrooms Mod is stand alond only adding to it when mopds are added? right?"*

Counting the register to answer it turned up three rows whose `stance` column reads **Required**,
while `About.xml` has declared **zero** `modDependencies` since 0.12.86-dev.

**Both cards were already precise and neither is edited:** Harmony is *"required only for the
selected RWT co-op path, not solo Core play"*, and Vanilla Expanded Framework is *"required by the
selected Gravship Expanded chain; optional to the Core-only Rimrooms campaign"*. A one-word column
cannot carry *required by something else*, so it said the opposite of its own card -- and a reader
who filters the register by `stance=Required` and finds three rows concludes this mod needs three.

**Core stays Required.** It is the game, not a mod, and nobody reading *"Core: Required"* is misled.

Only the pill text, the pill class and the summary count change. No card, no disposition, no
`Backrooms Dependency` field and no evidence is touched.
"""
import glob
import io
import os
import sys

NL = chr(10)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def register_path():
    found = glob.glob(os.path.join(REPO, "outputs", "**", "*Register.html"), recursive=True)
    if not found:
        raise SystemExit("register HTML not found under outputs/")
    return sorted(found)[-1]


# (row number, mod name) -> the exact cell to retune. Addressed by the row's own number AND name so
# a renumbered register cannot be edited in the wrong place.
TARGETS = [
    ("1", "Harmony"),
    ("14", "Vanilla Expanded Framework"),
]

PILL_OLD = '<span class="pill s-Required">Required</span>'
PILL_NEW = '<span class="pill s-Optional">Optional</span>'


def main():
    path = register_path()
    raw = io.open(path, "rb").read()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    before = text

    for number, name in TARGETS:
        anchor = "<td>%s</td><td><strong>%s</strong></td>" % (number, name)
        if text.count(anchor) != 1:
            print("ROW NOT FOUND EXACTLY ONCE (%d): row %s %r"
                  % (text.count(anchor), number, name))
            return 1
        start = text.index(anchor)
        end = text.index("</tr>", start)
        row = text[start:end]
        if row.count(PILL_OLD) != 1:
            print("row %s %r does not carry exactly one Required pill (%d)"
                  % (number, name, row.count(PILL_OLD)))
            return 1
        text = text[:start] + row.replace(PILL_OLD, PILL_NEW, 1) + text[end:]

    # The summary table counts stances. Three became one, and a count that disagrees with the rows
    # it summarises is the same defect one level up.
    summary_old = '<tr><td><span class="pill s-Required">Required</span></td><td>3</td></tr>'
    summary_new = '<tr><td><span class="pill s-Required">Required</span></td><td>1</td></tr>'
    if text.count(summary_old) != 1:
        print("summary count row not found exactly once (%d)" % text.count(summary_old))
        return 1
    text = text.replace(summary_old, summary_new, 1)

    # Optional's count rises by the same two, so the summary still totals the rows.
    import re
    match = re.search(r'<tr><td><span class="pill s-Optional">Optional</span></td><td>(\d+)</td></tr>',
                      text)
    if match is None:
        print("Optional summary count row not found")
        return 1
    bumped = '<tr><td><span class="pill s-Optional">Optional</span></td><td>%d</td></tr>' \
             % (int(match.group(1)) + 2)
    text = text[:match.start()] + bumped + text[match.end():]

    if text == before:
        print("nothing changed; refusing to write")
        return 1
    out = text.encode("utf-8")
    if had_bom:
        out = b"\xef\xbb\xbf" + out
    io.open(path, "wb").write(out)
    print("register updated: %s" % os.path.relpath(path, REPO).replace(os.sep, "/"))
    print("  rows retuned      : %s" % ", ".join("%s %s" % t for t in TARGETS))
    print("  Required summary  : 3 -> 1 (Core only, which is the game)")
    print("  Optional summary  : %s -> %d" % (match.group(1), int(match.group(1)) + 2))
    print("  cards, dispositions and evidence: untouched")
    print("  BOM %s" % ("kept" if had_bom else "absent"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
