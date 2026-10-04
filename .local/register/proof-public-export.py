# -*- coding: utf-8 -*-
"""Claims about the public export: the mod as staged, the public face, and nothing else.

**Owner direction, 2026-10-05, verbatim:** *"the repo for the mod only is
:https://git.unityailab.com/GFourteen/Rimrooms-AsyncIndustries.git which should include only public
facing documents and wiki htmls for deploying the github.io static page but for forgejo, and the
same thing for a github repo of the same name that you will make and set up to have only the mod
and only the public facing docs and wiki htmls for deployment to pages"*.

And on what *the mod* means, three times: *"make sure as far as what goes in it is only what the
game need to run the mod"*, *"ie what we stage"*, *"what goes into the game as the mod"*.

THE TWO PROPERTIES THESE CLAIMS EXIST FOR
-----------------------------------------
**One definition of "the mod."** The payload comes from `artifacts/build/package-manifest.json` --
the same file `tools/stage-mod.ps1` copies from -- with every SHA256 verified on the way out. So
*what we stage* and *what we publish* cannot drift, and an export cannot ship a file edited after
the build.

**An allowlist decides, and a denylist refuses the result.** Both run. 0.12.93-dev learned why the
hard way: `docs/_config.yml` described an exclusion policy it did not implement, and enabling Pages
would have put the entire work ledger on the internet. The second pass is the one that catches a
mistake in the first, and it earned that on its first run by refusing `CHANGELOG.md`.

Absence claims go through `code_only`. Every file here names the hazards in order to explain the
guards -- `DropAllNearPawn`, `subtree split`, the ledger filenames -- so a claim reading comments
would fail on the documentation that justifies them.
"""
import io
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EXPORTER = os.path.join(REPO, "tools", "export-public-repo.py")
RENDERER = os.path.join(REPO, "tools", "render-wiki-html.py")
CHECKER = os.path.join(REPO, "tools", "check-public-export.py")
CONFORM = os.path.join(REPO, "tools", "check-doc-conformance.py")
ABOUT = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "About", "About.xml")


def read(path):
    return io.open(path, encoding="utf-8-sig").read()


def code_only(text):
    """Python with docstrings and `#` comments removed."""
    text = re.sub(r'""".*?"""', " ", text, flags=re.S)
    text = re.sub(r"'''.*?'''", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*#.*$", " ", text)


def flat(text):
    return " ".join(text.split())


def slice_function(text, name):
    match = re.search(r"(?m)^(\s*)def\s+" + re.escape(name) + r"\s*\(", text)
    if not match:
        return ""
    indent = len(match.group(1))
    rest = text[match.end():]
    following = re.search(r"(?m)^\s{0,%d}(def|class)\s" % indent, rest)
    return text[match.start():match.end() + (following.start() if following else len(rest))]


exporter = read(EXPORTER)
exporter_code = code_only(exporter)
renderer = read(RENDERER)
renderer_code = code_only(renderer)
checker_code = code_only(read(CHECKER))
conform_code = code_only(read(CONFORM))

CLAIMS = []


def claim(label, ok, detail=""):
    CLAIMS.append((label, bool(ok), detail))


# ---------------------------------------------- one definition of "the mod", and it is the manifest
copy_mod = slice_function(exporter_code, "copy_mod")
claim("the mod payload comes from the build manifest",
      "package-manifest.json" in exporter_code and 'data["Files"]' in copy_mod)
claim("the exporter never globs the package directory for the payload",
      "glob" not in exporter_code and "os.walk(PACKAGE" not in exporter_code,
      "a second way of deciding what the mod is would be a second definition of it")
claim("every payload file's SHA256 is verified against the manifest",
      "sha256(source)" in copy_mod and 'entry["SHA256"]' in copy_mod)
claim("a hash mismatch refuses the export instead of warning",
      "edited after the build" in flat(copy_mod) and "problems.append" in copy_mod)
claim("the copy is read back and verified, not trusted",
      "sha256(target)" in copy_mod)
claim("a manifest naming a file the package lacks is a refusal",
      "the manifest names a file the package does not have" in flat(copy_mod))

# ------------------------------------------------------- only public-facing material goes in
claim("only the licence is copied verbatim",
      re.search(r"PUBLIC_FILES\s*=\s*\[\s*\(\"LICENSE\", \"LICENSE\"\),\s*\]",
                flat(exporter_code).replace("[ (", "[\n    (")) is not None
      or flat(exporter_code).count('("LICENSE", "LICENSE")') == 1,
      "the working readme's links all point at files the export does not have")
claim("the readme is GENERATED rather than copied",
      "def write_readme" in exporter_code and '"README.md"' not in
      flat(exporter_code).split("PUBLIC_FILES")[1].split("]")[0])
claim("the development changelog is not copied",
      '"CHANGELOG.md", "CHANGELOG.md"' not in flat(exporter_code),
      "it is a development log; the owner's rule is no actual work information in public docs")
claim("the readme is built from About.xml, the text a player already reads",
      "ET.parse(ABOUT)" in slice_function(exporter_code, "write_readme"))
claim("the readme refuses to link to a page the export does not have",
      "the readme would link to a page the export does not have"
      in flat(slice_function(exporter_code, "write_readme")))
claim("the readme does not hard-code the published site's own address",
      "github.io" not in slice_function(exporter_code, "write_readme"))

# ----------------------------------------------------------------- the denylist refuses
audit = slice_function(exporter_code, "audit")
claim("the audit walks what is on disk, not what the allowlist intended",
      "os.walk(EXPORT)" in audit,
      "the whole value of the pass is catching the difference between those two")
claim("the ledger filenames are refused by name",
      all(name in exporter_code for name in
          ('"TODO.md"', '"NOW.md"', '"FINALIZED.md"', '"DECOMPOSED.md"', '"ROADMAP.md"')))
claim("the generated ledger HTML names are refused too",
      '"TODO.html"' in exporter_code and '"NOW.html"' in exporter_code,
      "which is what the row asked for in its own words")
claim("working directories are refused as path components",
      all(part in exporter_code for part in
          ('".claude"', '".local"', '"implementation"', '"research"', '"src"', '"tools"')))
claim("ledger TEXT is refused even under an innocent filename",
      "VERBATIM TRANSFER CONFIRMED" in exporter_code
      and "archived-queue:begin" in exporter_code)
claim("a queue row's own shape is refused anywhere in the tree",
      r"^\s*- \[[ x~T]\] " in exporter_code)
claim("the .git directory is not audited as content",
      'd != ".git"' in audit)
claim("the tree is rebuilt from scratch every run, except .git",
      "shutil.rmtree" in exporter_code and 'name == ".git"' in exporter_code,
      "an incremental copy keeps a page alive the day its source is deleted")

# ----------------------------------------------------- fresh history, never a subtree split
# **NO WORD BOUNDARIES, AND A PLANT PROVED WHY.** `\bsubtree\b` does not match inside
# `git_subtree_split`, because an underscore is a word character so the boundary never occurs. A
# history rewrite could arrive under any identifier, so the substring is the property.
claim("no subtree split and no history rewrite anywhere in the exporter",
      not re.search(r"subtree|filter.branch|filter.repo", exporter_code, re.I),
      "Backrooms' history carries the ledger in essentially every commit")
claim("the export repository is its own, under .local",
      "os.path.join(REPO, \".local\", \"export\"" in exporter_code)
# **THE WHOLE STATEMENT, ANCHORED.** `"--push" in sys.argv` appears twice -- the other is on the
# commit-or-push line -- so containment was satisfied by that occurrence while a plant replaced the
# push guard itself with `if True:`. The property is that the guard is the condition of its own
# block, which is the same defect as asserting a signature while the guard inside it is gone.
claim("a push happens only when asked for",
      re.search(r'(?m)^\s{4}if "--push" in sys\.argv:\s*$', exporter_code) is not None
      and exporter_code.count('git("push"') == 1)
claim("a commit happens only when asked for",
      '"--commit" in sys.argv' in exporter_code)
claim("the two remote URLs are exactly the ones the owner named",
      "git.unityailab.com/GFourteen/Rimrooms-AsyncIndustries.git" in exporter_code
      and "github.com/G-Fourteen/Rimrooms-AsyncIndustries.git" in exporter_code)
claim("the export's branch is main",
      '"refs/heads/main"' in exporter_code)

# ----------------------------------------------------------------------- the renderer
claim("the reading order is IMPORTED from build-site.py, never copied",
      "build-site.py" in renderer_code and "SECTIONS = _bs.SECTIONS" in renderer_code,
      "two indexes that disagree is the problem the generated nav exists to prevent")
claim("the title and summary rules are imported too",
      "page_title = _bs.page_title" in renderer_code
      and "page_summary = _bs.page_summary" in renderer_code)
claim("no local SECTIONS literal shadows the imported one",
      not re.search(r"(?m)^SECTIONS\s*=\s*\[", renderer_code))
rewrite = slice_function(renderer_code, "rewrite_target")
claim("markdown links are rewritten to the rendered filenames",
      '".html"' in rewrite and '".md"' in rewrite)
claim("an absolute URL, an anchor and a mail link are left alone",
      all(part in rewrite for part in ('"http://"', '"https://"', '"#"', '"mailto:"')))
claim("an anchor is preserved through the rewrite",
      '"#" in target' in rewrite)
blocks = slice_function(renderer_code, "render_blocks")
claim("paragraphs join wrapped lines rather than one per source line",
      'out.append("<p>%s</p>" % inline(" ".join(block)))' in blocks,
      "every wiki page is hard-wrapped, so per-line paragraphs was the internal reader's bug")
claim("blockquote is rendered, which is the wiki's callout",
      "<blockquote>" in blocks)
claim("an all-empty table header row is dropped rather than demoted",
      "not any(c.strip() for c in cells(rows[0]))" in blocks and "rows = rows[2:]" in blocks,
      "an empty <th> announces nothing to a screen reader; a demoted row shows as a blank row")
# **THE CALL, NOT THE NAME.** `stash` is the nested function's own name, so it stays in the slice
# when the `re.sub` that uses it is deleted. A plant removed the call and this claim passed.
claim("code spans are stashed before emphasis is applied",
      "stash, out)" in flat(slice_function(renderer_code, "inline")),
      "or a star inside a code span becomes italics")
claim("the output is escaped before any markup is inserted",
      "esc(text)" in slice_function(renderer_code, "inline"))
# **ASSERTED ON THE TEMPLATE, NOT ON THE SOURCE FILE.** The first version looked for `http://`
# anywhere in the renderer and failed on `rewrite_target`, which *names* both schemes in order to
# leave absolute links alone. That is the rule working, not a violation. The property is that the
# page the renderer emits fetches nothing, and the page comes from `shell`.
_shell = slice_function(renderer_code, "shell")
claim("the rendered page makes no external request and carries no script",
      _shell and "http://" not in _shell and "https://" not in _shell
      and "<script" not in _shell.lower(),
      "no webfont, no CDN, no analytics -- the same instinct as the package depending on "
      "nothing but Core")
claim("the current page is marked with aria-current, as the Jekyll layout does",
      'aria-current="page"' in renderer_code)
claim("the stylesheet is copied from the one the Jekyll site uses",
      "docs\", \"assets\", \"css\", \"rimrooms.css\"" in renderer_code.replace("'", '"'))
claim("output is flat, so every link is a sibling",
      '"%s.html" % slug' in renderer_code and '"wiki/%s' not in renderer_code)
claim(".nojekyll is written, or Pages builds the static site anyway",
      ".nojekyll" in exporter_code)
claim("the renderer has a --check mode for the battery",
      '"--check" in sys.argv' in renderer_code)

# -------------------------------------------- the battery runs the audit, not just the exporter
claim("a checker fronts the export audit so the battery runs it",
      "export-public-repo.py" in checker_code)
claim("the checker never commits and never pushes",
      "--commit" not in checker_code and "--push" not in checker_code)
claim("the checker SKIPS rather than fails when there is no build to export",
      "SKIPPED" in read(CHECKER) and "return 0" in slice_function(checker_code, "main"))
claim("the checker does not reimplement the denylist",
      "FORBIDDEN" not in checker_code,
      "a second copy of the denylist is a second place the truth lives")

# ------------------------------------- About.xml's description, the document nothing checked
claim("About.xml's description is held to the claims rules",
      "def check_about_description" in conform_code)
claim("it is wired into the entry point",
      "check_about_description(" in slice_function(conform_code, "main"))
claim("with nothing declared, a dependency ASSERTION is refused",
      "DEPENDENCY_ASSERTION_CLAIMS" in conform_code
      and "declares every member" in conform_code)
claim("which rule applies is read off About.xml, never typed",
      "if declared <= 0:" in slice_function(conform_code, "check_about_description"))
claim("the description is held to the banned vocabulary a player must not read",
      "DOC_BANNED" in slice_function(conform_code, "check_about_description"))
claim("the description is held to the expansion-optional rule",
      "check_expansion_claims(" in slice_function(conform_code, "check_about_description"))
claim("XML entities are resolved before the description is read as prose",
      "&amp;" in slice_function(conform_code, "about_description"))

# ------------------------------------------- and the two defects that found, now actually fixed
about = read(ABOUT)
claim("About.xml no longer tells a player the mod declares dependencies",
      "declares every member of it as a dependency" not in about,
      "it said so while declaring zero, in the most-read document the mod has")
claim("About.xml now states the truth: it needs nothing",
      "needs nothing but RimWorld itself" in about)
claim("About.xml no longer says the banned word to a player",
      "doorway" not in about.lower())
claim("About.xml points at the public repository, which exists",
      "github.com/G-Fourteen/Rimrooms-AsyncIndustries" in about)
claim("About.xml still declares no dependencies at all",
      "<modDependencies>" not in about,
      "the fix was to the description; the decision itself is unchanged")

# ------------------------------------- ONE Pages deploy, and nothing references the build repos
claim("a document telling a reader to deploy Pages from this repository is refused",
      "def check_only_one_pages_deploy" in conform_code
      and "check_only_one_pages_deploy(" in slice_function(conform_code, "check_reader_facing"))
claim("the rule also runs over every living document, not only reader-facing ones",
      conform_code.count("check_only_one_pages_deploy(") >= 3,
      "definition plus the living-document walk plus the reader-facing walk")
claim("a sentence naming the public repository is allowed, so recording the rule passes",
      "if PAGES_ALLOWED.search(sentence):" in conform_code,
      "the CALL, not the constant: a plant replaced the test with `if False:` and the "
      "definition alone satisfied the first version")
claim("the rule is negation-aware in ALL THREE of its passes",
      conform_code.count("for negator in PAGES_NEGATORS)") == 3,
      "the USE SITE: a plant renamed the constant to PAGES_NEGATORS_UNUSED, which still "
      "contains PAGES_NEGATORS as a substring, so the first version passed")
claim("a foreign Pages address is scanned on RAW LINES, not on stripped prose",
      "FOREIGN_PAGES_ADDRESS.search(line)" in conform_code,
      "the address was hiding inside a code span, which readable_prose removes")
claim("the export refuses any file referencing a build repository",
      "for marker in FORBIDDEN_REFERENCES:" in exporter_code
      and "A BUILD REPOSITORY IS REFERENCED IN THE EXPORT" in exporter,
      "the LOOP, not the constant: a plant iterated an empty tuple instead")
claim("the build-repo rule matches repository forms, never the bare word",
      '"Unity-Lab-AI/Backrooms"' in exporter_code
      and '"git.unityailab.com"' in exporter_code
      and '"Backrooms",' not in exporter_code,
      "Backrooms is the name of the setting and appears all over the wiki as prose")
claim("the published wiki no longer points a reader at a build repository",
      "Unity-Lab-AI" not in read(os.path.join(REPO, "docs", "wiki", "links.md")))

# ------------------------------------------ the dependency rectification, enforced in three places
claim("a reader document asserting this mod needs something is refused",
      "def check_reader_dependency_assertions" in conform_code
      and len(re.findall(r"(?<!def )check_reader_dependency_assertions\(rel, prose, problems\)",
                         conform_code)) == 1,
      "COUNTED WITH A LOOKBEHIND: the definition line contains the call text, so a plant that "
      "replaced the call with `pass` left the claim satisfied by the signature")
claim("the negator must sit in the SAME CLAUSE as the claim",
      "def negated_in_clause" in conform_code
      and "clause = lowered[left:right]" in conform_code,
      "an incidental 'rather than' about failing later excused a false claim on the install page")
claim("a comma ends a clause for that test",
      '"[.;,]"' in conform_code.replace("r\"[.;,]\"", '"[.;,]"'),
      "which is exactly where the excuse was hiding")
claim("the rule runs on paragraphs, so a table cell is not read as an assertion",
      "for paragraph in paragraphs(prose):"
      in slice_function(conform_code, "check_reader_dependency_assertions"))
claim("a finding needs a dependency SUBJECT, not just an assertion phrase",
      # **THE NEEDLE IS BUILT FROM chr(92), NOT WRITTEN AS AN ESCAPE.** Written as a normal
      # string, r"\b" inside it is the BACKSPACE escape, so the needle became a control
      # character and could never match. One backslash has now broken this single line three
      # times: doubled in the checker (making the rule a no-op), a real backspace in the
      # repair, and an escape in the claim written to guard it.
      ('if not any(re.search(r"%sb" + subject + r"%sb", lowered)'
       % (chr(92), chr(92))) in conform_code
      and "for subject in DEPENDENCY_SUBJECTS)" in conform_code,
      "or 'Nothing special is required' and a heading both become findings")
# **MARKUP STRIPPED BEFORE THE PHRASE IS LOOKED FOR.** `install.md` writes
# `**This build declares no dependencies at all.**` and `mods.md` writes
# `declares **no dependencies at all**` -- the same sentence with the emphasis in a different place,
# so a literal needle matched one and missed the other. The claim is about what the page says, and
# where the asterisks fall is not part of that.
def plain(text):
    return " ".join(text.replace("*", "").replace("`", "").split())


for page, label in (("install.md", "the install page"), ("mods.md", "the mods page")):
    text = plain(read(os.path.join(REPO, "docs", "wiki", page)))
    claim("%s no longer tells a player an expansion is required" % label,
          "declares no dependencies" in text and "declares every" not in text)
claim("the install page no longer lists Harmony as required",
      "Not used and not needed" in read(os.path.join(REPO, "docs", "wiki", "install.md")))
claim("PLAYING.md no longer claims hard dependencies",
      "declares hard dependencies" not in read(os.path.join(REPO, "docs", "PLAYING.md")))
claim("README.md no longer claims every requirement is declared",
      "requirement is **declared**" not in read(os.path.join(REPO, "README.md")))

# ------------------------------------------------- a checker must be able to report what it finds
claim("the report survives a character the console cannot encode",
      "def say(" in conform_code and "UnicodeEncodeError" in conform_code,
      "the Pages rule quotes the offending sentence, one contained an arrow, and the run died "
      "after finding six real problems and before naming five of them")
claim("the findings are printed through it",
      'say("  - %s" % problem)' in conform_code)

# ---------------------------------------------------------------------------------- report
bad = [(label, detail) for label, ok, detail in CLAIMS if not ok]
for label, ok, detail in CLAIMS:
    print("%s  %s" % ("ok   " if ok else "FAIL!", label))
    if detail and not ok:
        print("       %s" % detail)
print("")
print("%d of %d claims hold" % (len(CLAIMS) - len(bad), len(CLAIMS)))
sys.exit(1 if bad else 0)
