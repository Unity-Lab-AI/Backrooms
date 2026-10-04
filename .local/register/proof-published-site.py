# -*- coding: utf-8 -*-
"""Claims about the published-site guard, the generated exclude list and the front door.

Two queue rows, one piece of work:

* *"`check-doc-conformance.py` must cover the published site"* -- the site's **non-markdown**
  published files were uncovered. `living_docs()` already globs every `.md`, so the wiki prose
  never was; a version in a layout or a branch in a stylesheet comment would have shipped
  unexamined.
* *"The generator stays internal, by the finding that opened this"*, noted as **stated in the
  config, not yet enforced**, because *"a comment is not a guard"*.

**AND THE COMMENT WAS WRONG AS WELL AS UNENFORCED.** `docs/_config.yml` claimed everything but the
wiki was *"deliberately excluded"* while naming four directories, two of which do not exist, with
fifty-four documents sitting at `docs/` root. Jekyll publishes what it is not told to exclude, so
enabling Pages would have published `TODO.md`, `NOW.md`, `FINALIZED.md` and `DECOMPOSED.md` as raw
downloads.

EVERY ABSENCE CLAIM GOES THROUGH A COMMENT-STRIPPED VIEW
--------------------------------------------------------
Good documentation explains the thing it avoids **by naming it**, so an absence claim that reads
comments fails on the comment that justifies it. This has now bitten three times in three batches,
and it bit once more while this file was being written: the rule that refuses a wrong checker count
flagged the very sentence written to correct one, because that sentence has to quote the wrong
phrase in order to explain it. `code_only`, `yaml_only` and `html_only` exist for exactly this.
"""
import io
import os
import re
import sys

NL = chr(10)
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

CHECK = os.path.join(REPO, "tools", "check-doc-conformance.py")
BUILD = os.path.join(REPO, "tools", "build-site.py")
CONFIG = os.path.join(REPO, "docs", "_config.yml")
FRONT = os.path.join(REPO, "docs", "index.html")
LAYOUT = os.path.join(REPO, "docs", "_layouts", "default.html")


def read(path):
    return io.open(path, encoding="utf-8-sig").read()


def code_only(text):
    """Python source with docstrings and `#` comments removed.

    Narrow on purpose: a `#` inside a string literal would be cut too. Every claim below asserts
    the presence or absence of an identifier or a call, none of which live inside string literals
    containing hashes, and a narrow cut that is wrong in the safe direction beats a parser.
    """
    text = re.sub(r'"""' + r".*?" + r'"""', " ", text, flags=re.S)
    text = re.sub(r"'''.*?'''", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*#.*$", " ", text)


def yaml_only(text):
    """YAML with `#` comments removed, so the block's own explanation is not read as data."""
    return re.sub(r"(?m)^\s*#.*$", " ", text)


def html_only(text):
    """A template's markup with every kind of comment removed.

    **BOTH SYNTAXES, BECAUSE ONE WAS NOT ENOUGH.** `_layouts/default.html` carries its rationale in
    an HTML comment *and* in a Liquid `{%- comment -%}` block, and the Liquid one is where it
    explains that `page.url contains` is deliberately not used. A claim that stripped only HTML
    comments failed on that explanation -- the same read-its-own-documentation defect, caught a
    second time in this file by a different comment syntax.
    """
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    return re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", " ", text, flags=re.S)


def flat(text):
    """Whitespace-normalised, because a positional or layout-shaped claim encodes layout.

    This battery has been caught twice asserting a property that a reformat satisfied. Containment
    on normalised source is the property; the line it sits on is not.
    """
    return " ".join(text.split())


def slice_function(text, name):
    """A function's body, cut to the NEXT top-level definition rather than the next brace.

    A previous claim cut a method at its first closing brace -- an inline guard -- and examined
    four lines while a planted fault sat safely below it. The equivalent error in Python is cutting
    at the first blank line, so this cuts at the next `def ` or `class ` in column zero or at
    four-space indentation, which is where the next sibling starts.
    """
    match = re.search(r"(?m)^(\s*)def\s+" + re.escape(name) + r"\s*\(", text)
    if not match:
        return ""
    start = match.start()
    indent = len(match.group(1))
    rest = text[match.end():]
    following = re.search(r"(?m)^\s{0,%d}(def|class)\s" % indent, rest)
    return text[start:match.end() + (following.start() if following else len(rest))]


check = read(CHECK)
check_code = code_only(check)
build = read(BUILD)
build_code = code_only(build)
config = read(CONFIG)
config_data = yaml_only(config)
front = read(FRONT)
front_markup = html_only(front)

CLAIMS = []


def claim(label, ok, detail=""):
    CLAIMS.append((label, bool(ok), detail))


# ------------------------------------------------------------------ the checker count, derived
claim("the checker count is read off tools/ and not typed",
      "glob.glob(os.path.join(REPO, \"tools\", \"check-*.py\")" in flat(check_code))
claim("no hard-coded CHECKER_COUNT literal survives",
      not re.search(r"(?m)^CHECKER_COUNT\s*=\s*\d+", check_code))
claim("the old fixed phrase list is gone, not merely extended",
      check_code.count("CHECKER_PHRASES") == 0)
claim("the count rule reads a number of any size, spelled or in digits",
      "WORD_NUMBERS" in check_code and r"\d{1,3}" in check_code)
claim("'other N checkers' is counted as N+1, so correct prose is not punished",
      "claimed + 1 if match.group(1) else claimed" in flat(check_code))
count_body = slice_function(check_code, "check_checker_count")
claim("the count rule strips owner-quoted spans before scanning",
      "OWNER_INLINE_QUOTE.sub" in count_body)
claim("the count rule strips any quoted span before scanning",
      "QUOTED_SPAN.sub" in count_body)
claim("the count rule is called for living documents",
      check_code.count("check_checker_count(") >= 3,
      "definition plus the markdown path plus the non-markdown path")

# ------------------------------------------------------- what the site publishes, modelled
publishes = slice_function(check_code, "jekyll_publishes")
claim("publishability is modelled rather than read out of the exclude list",
      "def jekyll_publishes" in check_code)
claim("an include match short-circuits, which is Jekyll's own precedence",
      publishes.index("for pattern in includes") < publishes.index("startswith(\"_\")"))
claim("a leading underscore or dot is treated as never published",
      "startswith(\"_\")" in publishes and "startswith(\".\")" in publishes)
claim("anything not provably excluded is treated as PUBLISHED",
      flat(publishes).rstrip().endswith("return True"),
      "the one failure a ledger guard must not have is calling a published file safe")
claim("the walk prunes directories it would not descend into",
      "dirs[:] = [d for d in dirs" in build_code or "dirs[:] = [d for d in dirs" in check_code)
# **ASSERT THE CONDITION, NOT THE MESSAGE.** The first version of this claim looked for the
# refusal's wording and failed on its own string-concatenation boundary -- `"cannot be " "determined"`
# flattens with a quote pair in the middle. A message is not a rule: rewording the sentence must
# not break the claim, and changing the behaviour must.
site_body = slice_function(check_code, "check_published_site")
claim("a missing config is a problem, never a silent pass",
      "if includes is None and excludes is None:" in site_body
      and site_body.index("includes is None and excludes is None") <
          site_body.index("problems.append"))
claim("no third-party YAML library is imported",
      "import yaml" not in check_code and "from yaml" not in check_code)

# ---------------------------------------------------------------------- the ledger guard
claim("the row's own two filenames are refused",
      '"TODO.html"' in check_code and '"NOW.html"' in check_code)
claim("the markdown sources are refused too, which is what actually sits in docs/",
      '"TODO.md"' in check_code and '"NOW.md"' in check_code)
claim("the rest of the ledger is refused, not only the two named",
      all(name in check_code for name in ('"FINALIZED.md"', '"DECOMPOSED.md"', '"ROADMAP.md"')))
claim("a published file outside the declared site surface is a finding on its own",
      "is not part of the declared site " in flat(check_code))
claim("the site surface is declared rather than inferred",
      "SITE_SURFACE = " in check_code)
claim("the ledger guard is reached from the entry point",
      "check_published_site(" in slice_function(check_code, "main"))
claim("the ledger guard is reached from check_published_site",
      "check_ledger_never_published(" in slice_function(check_code, "check_published_site"))

# ------------------------------------------------- the non-markdown coverage the row asked for
non_md = slice_function(check_code, "check_published_non_markdown")
claim("published non-markdown files are checked for a version claim",
      "VERSION_CLAIM.finditer" in non_md)
claim("published non-markdown files are checked for a stale branch name",
      "STALE_BRANCHES" in non_md)
claim("published non-markdown files are checked for a retired def",
      "RETIRED_DEFS" in non_md)
claim("markdown is skipped here because living_docs already holds it",
      'rel.endswith(".md")' in slice_function(check_code, "site_text_files"))
claim("the templates whose text rides inside every page are included",
      all(part in check_code for part in ("_layouts", "_includes", "SITE_TEMPLATES")))
claim("the config itself is one of those templates",
      flat(check_code).count('"_config.yml"') >= 1)
claim("vocabulary and the wall rule apply only to files a reader meets as words",
      'if not rel.endswith((".html", ".htm")):' in non_md)
claim("the wall rule measures <p> elements, not blank-line blocks",
      "HTML_PARAGRAPH.findall" in non_md,
      "an HTML file has no blank line between paragraphs, so the markdown splitter "
      "would read a whole page as one wall")
claim("a template's own comments are cut before its prose is read",
      "HTML_COMMENT.sub" in slice_function(check_code, "template_prose"))
claim("liquid tags are cut as instructions rather than read as words",
      "LIQUID_TAG.sub" in slice_function(check_code, "template_prose"))

# ------------------------------------------------- the expansions are optional, and docs must say so
expansion = slice_function(check_code, "check_expansion_claims")
claim("a reader document claiming an expansion is required is refused",
      "def check_expansion_claims" in check_code and "EXPANSION_CLAIM.search" in expansion)
claim("all five expansions are covered, not just the ones with content",
      all(name in check_code for name in
          ('"royalty"', '"ideology"', '"biotech"', '"anomaly"', '"odyssey"')))
claim("the rule pairs a name with a requirement word rather than matching the name alone",
      "REQUIREMENT_WORDS" in check_code,
      "mods.md exists to say the expansions are optional, so it must be able to name them")
claim("the rule is negation-aware, like the multiplayer rule it sits beside",
      "CLAIM_NEGATORS" in expansion,
      "a document written to obey the rule must not fail it")
claim("the rule reaches reader-facing documents",
      "check_expansion_claims(rel, prose, problems)" in slice_function(check_code,
                                                                      "check_reader_facing"))

# ---------------------------------------------------------------------------- the CNAME rule
cname = slice_function(check_code, "check_cname")
claim("a CNAME is only checked when one exists",
      "if not os.path.isfile(path):" in cname)
claim("a CNAME holding more than one line is refused",
      "must hold exactly one" in flat(cname))
claim("a CNAME holding a comment is refused",
      "contains a comment" in flat(cname))
claim("the placeholder from CNAME.example is refused by name",
      "PUT-YOUR-HOSTNAME-HERE" in cname)

# ------------------------------------------------------- the generated exclude list
claim("what the published site consists of is declared in one place",
      "PUBLISHED_ENTRIES = " in build_code)
claim("the stylesheet is published, or the layout is a text wall again",
      '"assets"' in build_code)
claim("CNAME is published, because Pages reads it out of the published root",
      '"CNAME"' in build_code)
claim("the front door is published",
      '"index.html"' in build_code)
material = slice_function(build_code, "working_material")
claim("the exclude list is read off the directory, not listed by hand",
      "os.listdir(DOCS)" in material)
claim("underscore and dot entries are never listed, because Jekyll already skips them",
      'startswith("_")' in material and 'startswith(".")' in material)
claim("the list is written as explicit names and never as a glob",
      '"  - %s"' in build_code and "fnmatch" not in build_code)
up_to_date = slice_function(build_code, "excludes_up_to_date")
claim("--check fails on a working-material entry that is not excluded",
      "missing" in up_to_date and "does not exclude" in flat(up_to_date))
claim("--check also fails on an exclude naming something that is gone",
      "extra" in up_to_date and "not at docs/ root" in flat(up_to_date),
      "a dead exclude reads as protection and gives none -- two of the four it replaced "
      "named directories that do not exist")
claim("the splice refuses rather than guessing where the block belongs",
      "return None" in slice_function(build_code, "splice_excludes"))
claim("--check covers both artefacts in one run",
      "failures.append" in slice_function(build_code, "main"))

# --------------------------------------------------------------------- the config as it stands
claim("the generated block exists in the config",
      "BEGIN GENERATED EXCLUDE LIST" in config and "END GENERATED EXCLUDE LIST" in config)
claim("TODO.md is excluded as data, not merely discussed in a comment",
      re.search(r"(?m)^\s*-\s*TODO\.md\s*$", config_data) is not None)
claim("NOW.md is excluded as data",
      re.search(r"(?m)^\s*-\s*NOW\.md\s*$", config_data) is not None)
claim("FINALIZED.md and DECOMPOSED.md are excluded as data",
      re.search(r"(?m)^\s*-\s*FINALIZED\.md\s*$", config_data) is not None
      and re.search(r"(?m)^\s*-\s*DECOMPOSED\.md\s*$", config_data) is not None)
claim("the two dead excludes are gone from the data",
      re.search(r"(?m)^\s*-\s*evidence\s*$", config_data) is None
      and re.search(r"(?m)^\s*-\s*reviews\s*$", config_data) is None,
      "they named directories that do not exist, which is protection a reader believes in")
claim("the wiki is still explicitly included",
      re.search(r"(?m)^\s*-\s*wiki\s*$", config_data) is not None)
claim("no remote theme returned with the rewrite",
      "remote_theme" not in config_data)

# ------------------------------------------------------------------------------ the front door
claim("the published site has a root document at all",
      os.path.isfile(FRONT), "without one the site's own address answers 404")
claim("the front door carries no front matter, so Jekyll copies it verbatim",
      not front.lstrip().startswith("---"))
claim("the front door links relatively, because a project site is served from a subpath",
      'href="wiki/"' in front_markup and 'href="/wiki/"' not in front_markup)
claim("the front door has a real link and not only a meta refresh",
      front_markup.count('href="wiki/"') >= 2,
      "a reader whose browser ignores a refresh still needs a way in")
claim("the front door makes no external request",
      "http://" not in front_markup and "https://" not in front_markup)
claim("the front door carries no script",
      "<script" not in front.lower())
# **THROUGH `html_only`, AND THE FIRST VERSION WAS NOT.** The layout's comment names
# `page.url contains` in order to explain why it is not used, so a claim reading the raw file fails
# on the documentation that justifies it. Fourth instance of this exact defect, and the second in
# this one file.
layout_markup = html_only(read(LAYOUT)) if os.path.isfile(LAYOUT) else ""
claim("the layout still derives the current page by slug, not by `contains`",
      os.path.isfile(LAYOUT) and "assign pageslug" in layout_markup
      and "page.url contains" not in layout_markup,
      "`page.url contains '/wiki/'` is true of every page and marked the index current "
      "everywhere")

# ---------------------------------------------------------------------------------- report
bad = [(label, detail) for label, ok, detail in CLAIMS if not ok]
for label, ok, detail in CLAIMS:
    print("%s  %s" % ("ok   " if ok else "FAIL!", label))
    if not ok and detail:
        print("       %s" % detail)
print("")
print("%d of %d claims hold" % (len(CLAIMS) - len(bad), len(CLAIMS)))
sys.exit(1 if bad else 0)
