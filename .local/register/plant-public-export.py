# -*- coding: utf-8 -*-
"""Prove every claim about the public export can fail.

The export puts files on the public internet. A guard here that has never been watched refusing is
worse than one on an internal tool, because the failure is not a broken build -- it is a ledger
somebody can read.

**BYTE-LEVEL IO, DELIBERATELY.** Every other suite reads and writes text, which is fine for files
that have no byte-order mark. This one plants into `About.xml`, which **has** one, and
`io.open(..., "w", encoding="utf-8")` would silently strip it -- the exact defect recorded two
batches ago when a version bump stripped three BOMs. Bytes in, bytes out, nothing assumed.

Four plants are the ones that matter:

* `CHANGELOG.md` restored to the copy list. It is the plant that mirrors the real refusal: the
  audit caught the development changelog on its first ever run.
* The payload globbed from the package instead of read from the manifest -- *"ie what we stage"*
  stops being true and nothing visibly breaks.
* `subtree split` appearing. The owner was warned about it and agreed to avoid it; the claim is
  what stops it coming back by accident.
* An external request added to the rendered page. It serves fine, looks fine, and quietly phones
  somewhere on every page view.
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)

PROOF = [".local/register/proof-public-export.py"]

EXPORTER = "tools/export-public-repo.py"
RENDERER = "tools/render-wiki-html.py"
CHECKER = "tools/check-public-export.py"
CONFORM = "tools/check-doc-conformance.py"
ABOUT = "Mod/Rimrooms - Async Industries/About/About.xml"

_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def read_bytes(path):
    return io.open(path, "rb").read()


def write_verified(path, data):
    """Bytes, verified. A BOM is part of the file and must come back exactly as it went."""
    for _ in range(6):
        try:
            io.open(path, "wb").write(data)
            if read_bytes(path) == data:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND%s" % (path, chr(10)))
    sys.exit(3)


def b(text):
    return text.encode("utf-8")


PLANTS = [
    # ---- the mod stops being "what we stage" --------------------------------------------
    ("the payload is globbed from the package instead of read from the manifest", EXPORTER,
     'for entry in data["Files"]:', 'import glob\n    for entry in data["Files"]:', 1),

    ("the SHA256 verification is removed", EXPORTER,
     "        actual = sha256(source)", "        actual = entry[\"SHA256\"].upper()", 1),

    ("a hash mismatch stops being a refusal", EXPORTER,
     '            problems.append("%s does not match the build manifest (edited after the build?); "\n'
     '                            "rebuild, then export" % rel)',
     '            pass', 1),

    ("the copy is trusted instead of read back", EXPORTER,
     "        if sha256(target) != entry[\"SHA256\"].upper():",
     "        if False:", 1),

    # ---- the denylist stops refusing ----------------------------------------------------
    ("THE DEVELOPMENT CHANGELOG IS RESTORED to the copy list", EXPORTER,
     '    ("LICENSE", "LICENSE"),',
     '    ("LICENSE", "LICENSE"),\n    ("CHANGELOG.md", "CHANGELOG.md"),', 1),

    ("the readme is copied instead of generated", EXPORTER,
     '    ("LICENSE", "LICENSE"),',
     '    ("LICENSE", "LICENSE"),\n    ("README.md", "README.md"),', 1),

    ("the queue file is dropped from the refused names", EXPORTER,
     '"TODO.md", "TODO.html",', '"TODO.html",', 1),

    ("the handoff is dropped from the refused names", EXPORTER,
     '"NOW.md", "NOW.html",', '"NOW.html",', 1),

    ("the archive banner stops being refused as text", EXPORTER,
     '    "VERBATIM TRANSFER CONFIRMED",', "", 1),

    ("a queue row's own shape stops being refused", EXPORTER,
     r'            if re.search(r"(?m)^\s*- \[[ x~T]\] ", text):',
     "            if False:", 1),

    ("the audit reads the allowlist instead of the disk", EXPORTER,
     "    for base, dirs, names in os.walk(EXPORT):",
     "    for base, dirs, names in []:", 1),

    ("working directories stop being refused as path components", EXPORTER,
     'FORBIDDEN_PARTS = (".claude", ".local", "implementation"',
     'FORBIDDEN_PARTS = ("nothing_at_all", ".local", "implementation"', 1),

    ("the tree is no longer rebuilt from scratch", EXPORTER,
     "            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)",
     "            pass", 1),

    # ---- the history and the remotes ----------------------------------------------------
    # Planted the way it would really arrive -- as git arguments -- because the first version used
    # an identifier name, which is not how anybody writes a subtree split, and `\bsubtree\b` could
    # not see it. The plant was unrealistic AND the claim was too narrow; both were fixed.
    ("a subtree split creeps in, carrying the ledger's history", EXPORTER,
     '        git("add", "-A")',
     '        git("subtree", "split", "--prefix=Mod")\n        git("add", "-A")', 1),

    ("a push happens whether it was asked for or not", EXPORTER,
     '    if "--push" in sys.argv:', "    if True:", 1),

    ("a remote is pointed somewhere else", EXPORTER,
     "github.com/G-Fourteen/Rimrooms-AsyncIndustries.git",
     "github.com/G-Fourteen/Somewhere-Else.git", 1),

    # ---- the renderer -------------------------------------------------------------------
    ("the reading order is copied into the renderer instead of imported", RENDERER,
     "SECTIONS = _bs.SECTIONS",
     'SECTIONS = [("Start", ["index"])]\nSECTIONS_UNUSED = _bs.SECTIONS', 1),

    ("paragraphs go back to one per source line", RENDERER,
     '            out.append("<p>%s</p>" % inline(" ".join(block)))',
     '            out.append("<p>%s</p>" % inline(block[0]))', 1),

    ("blockquote stops being rendered, so every callout vanishes", RENDERER,
     '            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(block).strip()))',
     "            pass", 1),

    ("an all-empty header row is demoted instead of dropped", RENDERER,
     "                rows = rows[2:]", "                rows = rows[:1] + rows[2:]", 1),

    ("code spans stop being protected from emphasis", RENDERER,
     '    out = re.sub(r"`([^`]+)`", stash, out)', "", 1),

    ("the rendered page starts fetching a webfont", RENDERER,
     '\'<link rel="stylesheet" href="assets/css/rimrooms.css">\',',
     '\'<link rel="stylesheet" href="https://fonts.example/x.css">\',', 1),

    ("markdown links stop being rewritten to the rendered filenames", RENDERER,
     '        target = target[:-3] + ".html"', "        pass", 1),

    (".nojekyll is no longer written, so Pages builds the static site", EXPORTER,
     '    io.open(os.path.join(target, ".nojekyll"), "w", encoding="utf-8", newline=NL).write("")',
     "    pass", 1),

    # ---- the battery's entry point ------------------------------------------------------
    ("the checker reimplements the denylist instead of running the exporter", CHECKER,
     "    if not os.path.isfile(EXPORTER):",
     '    FORBIDDEN_NAMES = set()\n    if not os.path.isfile(EXPORTER):', 1),

    ("the checker starts pushing", CHECKER,
     "    code = subprocess.call([sys.executable, EXPORTER], cwd=REPO)",
     '    code = subprocess.call([sys.executable, EXPORTER, "--push"], cwd=REPO)', 1),

    # ---- About.xml, the document nothing used to check ----------------------------------
    ("About.xml tells a player it declares dependencies again", ABOUT,
     "This mod needs nothing but RimWorld itself.",
     "This build declares every member of it as a dependency.", 1),

    ("About.xml says the banned word to a player again", ABOUT,
     "follows your crew to the threshold", "follows your crew to the doorway", 1),

    ("the About description check is unwired from the entry point", CONFORM,
     "    about_checked = check_about_description(version, branch, checkers,",
     "    about_checked = True and (lambda *a: True)(version, branch, checkers,", 1),
]

caught = 0
attempted = 0
for label, path, old, new, want in PLANTS:
    attempted += 1
    original = read_bytes(path)
    needle = b(old)
    if original.count(needle) < 1:
        print("PLANT SETUP BROKEN (0 matches for %r): %s" % (old[:55], label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(needle, b(new), 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable] + PROOF,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code == want
    caught += 1 if ok else 0
    print("%s  %s (exit %d, wanted %d)"
          % ("CAUGHT " if ok else "MISSED!", label, code, want))

print("")
print("%d of %d planted faults caught" % (caught, attempted))
sys.exit(0 if caught == attempted else 1)
