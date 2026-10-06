# -*- coding: utf-8 -*-
"""Generate the published wiki's index from the pages themselves.

Why this exists
---------------
**Owner direction, verbatim:** *"and docs and pages when we deploy the wiki and docs on github"*,
*"docs/ root on this repo, github.io for now"*, and the one that decides the shape:
*"the beautiful and masterfully way paossible so the thing needs to NOT pop like a text wall"*.
The queue row adds the rule that matters here: **"Generated, never hand-maintained."**

A hand-written list of pages is a second place the truth lives. Add a page and the list is wrong;
rename one and the list is a broken link. So `docs/_includes/nav.html` is written from whatever is
actually in `docs/wiki/`, and `_layouts/default.html` includes it.

**This is NOT the internal ledger renderer and must never become it.** `tools/make-readable-html.py`
renders `TODO.html` and `NOW.html` into `outputs/readable/` as a reading convenience. The queue row
is explicit that it *"stays an internal reading convenience and is never wired to the published
tree"* -- the work ledger is not public. The two tools share no output directory, and
`check-doc-conformance.py` refuses a published copy of either ledger.

What it writes
--------------
**Two generated artefacts, and neither is prose.**

`docs/_includes/nav.html` -- the index. It never touches a page's prose: the title comes from the
page's own first `# ` heading and the one-line summary from its `summary:` front matter, so the
page remains the source of truth and this file remains derived.

`docs/_config.yml`'s `exclude:` block, between markers. **This was added because the hand-written
version was not merely unmaintained, it was wrong.** The file said *"everything else under docs/ is
project working material and is deliberately excluded"* while naming four directories, two of
which (`evidence`, `reviews`) do not exist. **Jekyll publishes every entry in its source directory
that it is not told to exclude**, and fifty-four markdown files sit at `docs/` root -- `TODO.md`,
`NOW.md`, `FINALIZED.md`, `DECOMPOSED.md` among them. Enabling Pages would have put the entire work
ledger on the public internet, which is the exact outcome the queue row calls *"never published"*.

The list is written **explicitly, entry by entry, never as a glob.** Jekyll's exact-name and
directory-prefix rules behave identically in every version; `*` crossing a path separator is a
subtlety of Ruby's `File.fnmatch` that cannot be verified from here, and a pattern that silently
fails to exclude is the one failure mode this must not have. Completeness is guaranteed by
`--check` instead -- add a document, and the battery fails until it is excluded.

Order is declared in SECTIONS rather than alphabetical, because a reader arriving at a wiki wants
*install* before *credits*, and alphabetical would put `backrooms` first and `troubleshooting`
last by accident rather than on purpose. A page not named in SECTIONS still appears, under
"More" -- a new page is never silently dropped from the index.

Usage
-----
    python tools/build-site.py          # write the include and the exclude block
    python tools/build-site.py --check  # fail if either is out of date, for the battery
"""
import io
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DOCS = os.path.join(REPO, "docs")
WIKI = os.path.join(DOCS, "wiki")
INCLUDE = os.path.join(DOCS, "_includes", "nav.html")
SITE_CONFIG = os.path.join(DOCS, "_config.yml")
NL = chr(10)

# **What the published site actually is.** Everything else at `docs/` root is working material.
#
# `assets` is here because the stylesheet has to be served or the layout is a text wall again, and
# `CNAME` is here because GitHub Pages reads it out of the published root -- excluding it would
# make the custom domain silently never work, which is the same class of quiet failure as
# `CNAME.example` going live. `CNAME.example` itself is working material and is excluded; the
# prefix rule is safe in that direction, because `docs/CNAME` does not start with
# `docs/CNAME.example`.
#
# Entries beginning `_` or `.` are never listed: Jekyll treats those as special and never
# publishes them, which is why `_config.yml`, `_layouts/` and `_includes/` need no exclusion.
PUBLISHED_ENTRIES = ("wiki", "assets", "CNAME", "index.html")

EXCLUDE_BEGIN = "  # BEGIN GENERATED EXCLUDE LIST -- written by tools/build-site.py."
EXCLUDE_END = "  # END GENERATED EXCLUDE LIST"

# The reading order a newcomer needs, which is not alphabetical. Any page not listed here is
# still published and still indexed, under the last group.
SECTIONS = [
    ("Start", ["index", "install", "first-hour", "scenarios"]),
    ("Playing", ["company", "gates", "backrooms", "interface"]),
    ("Running it", ["mods", "mods-list", "multiplayer", "troubleshooting"]),
    ("About", ["credits", "links"]),
]

# ---------------------------------------------------------------------------- the art
#
# **Owner direction, 2026-10-05, verbatim:** *"and use our slide art as a banner or something
# /background to where text writing is not fighting the art to be read ,, in the wiki pages"*, and
# on which image leads: *"make sure the preview image is prominate becasue thats what mod loaders
# see"*.
#
# These are the **only** art in the package -- twelve menu slides and the preview, the approved
# exception to shipping no art.
#
# ## THE ART IS COPIED INTO THE SITE, AND THE FIRST ATTEMPT NOT TO WAS BROKEN ON THE LIVE SITE
#
# The obvious saving is to reference the slides where the mod already puts them -- the export
# carries all thirteen as package files, so `../1.6/Textures/UI/Menu/<file>` costs **zero extra
# bytes**. That shipped, the export audit verified every path against the assembled tree, and
# **every banner was a 404 in the browser.**
#
# Why: **Pages serves `/docs` AS THE SITE ROOT.** `docs/gates.html` is published at
# `<site>/gates.html`, so `../1.6/...` resolves to `<host>/1.6/...` -- above the project entirely.
# Anything outside `docs/` is never served at all, at any URL. The path was correct on disk and
# unreachable over HTTP, which is why the audit passed and the site was wrong.
#
# So the art is **copied into the site directory** and referenced site-relative. Twenty-one
# megabytes are published twice in the export repository, and that is the honest price of the
# direction. The rule it leaves behind is the general one: **a published page may never reference a
# path that climbs out of the site directory**, and `export-public-repo.py` now refuses one.
#
# ## Assigned by subject, never at random
#
# Twelve slides against thirteen pages, so a slide may serve more than one page. The alternative --
# rotating them, or leaving a page blank -- would put a cinema behind the install instructions.
#
# ## The readability rule lives in the markup, not here
#
# The owner's direction carries its own acceptance test: *"to where text writing is not fighting
# the art to be read"*. The answer is structural rather than a matter of opacity -- **no text is
# ever drawn over a banner.** The band sits above the prose, the heading sits below it, and the
# image is marked decorative so a screen reader skips it instead of reading out a filename.
# Where the art lives in the package, and where the site serves its own copy from. The second is
# site-relative with no leading `..`, which is the whole point.
BANNER_SOURCE_DIRECTORY = "1.6/Textures/UI/Menu"
PREVIEW_SOURCE = "About/Preview.png"
SITE_ART_DIRECTORY = "assets/art"
PREVIEW_IMAGE = "assets/art/Preview.png"

# **All twelve are used.** Thirteen pages and twelve slides means exactly one repeat, and it is the
# honest one: the two pages about the gate carry the gate slide. Leaving a slide unused would be
# the same fault as a def nobody wired -- it was made for this and nothing else uses it.
BANNERS = {
    "index": "RR_Menu_FacilityThreshold_v2.png",      # the way in
    "install": "RR_Menu_LaboratoryOperations.png",    # getting it running
    "first-hour": "RR_Menu_IndustrialGateLogistics.png",
    "gates": "RR_Menu_IndustrialGateLogistics.png",   # the one repeat, and the reason for it
    "scenarios": "RR_Menu_EmptyCinema.png",           # choosing an opening
    "company": "RR_Menu_BreachedVault.png",           # the account, the bonds
    "backrooms": "RR_Menu_LightsOut.png",             # deep levels
    "interface": "RR_Menu_SilentRecovery.png",        # reading the panels
    "mods": "RR_Menu_FamiliarStranger.png",           # other people's content
    "multiplayer": "RR_Menu_CorridorEncounter.png",   # meeting somebody
    "troubleshooting": "RR_Menu_PanicJunction.png",   # when it goes wrong
    "credits": "RR_Menu_FieldSurvey_v2.png",
    "links": "RR_Menu_RedTrail.png",                  # a trail to follow
}

# Every slide is this size, checked rather than assumed, so the markup can carry `width` and
# `height` and the page does not jump while the image loads.
BANNER_WIDTH = 1672
BANNER_HEIGHT = 941


def page_title(text, slug):
    """The page's own first heading. Falls back to the slug rather than inventing a title."""
    match = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    return match.group(1).strip() if match else slug.replace("-", " ").capitalize()


def page_summary(text):
    """The `summary:` front matter line, or empty.

    Read from front matter rather than guessed from the first paragraph: a guess would put
    half a sentence in the index the first time somebody opened a page with a note at the top.
    """
    if not text.startswith("---"):
        return ""
    end = text.find(NL + "---", 3)
    if end < 0:
        return ""
    match = re.search(r"^summary:\s*(.+?)\s*$", text[:end], re.M)
    if not match:
        return ""
    return match.group(1).strip().strip('"').strip("'")


def esc(value):
    return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def pages():
    found = {}
    for name in sorted(os.listdir(WIKI)):
        if not name.endswith(".md"):
            continue
        slug = name[:-3]
        text = io.open(os.path.join(WIKI, name), encoding="utf-8-sig").read()
        found[slug] = (page_title(text, slug), page_summary(text))
    return found


def render(found):
    lines = []
    lines.append("<!-- GENERATED by tools/build-site.py. Do not edit: edit the pages, then run it.")
    lines.append("     Owner: \"Generated, never hand-maintained.\" `--check` fails the battery")
    lines.append("     when this file and docs/wiki/ disagree. -->")
    placed = set()
    groups = list(SECTIONS)
    extra = [slug for slug in sorted(found) if not any(slug in names for _, names in SECTIONS)]
    if extra:
        groups.append(("More", extra))
    for heading, slugs in groups:
        listed = [slug for slug in slugs if slug in found]
        if not listed:
            continue
        lines.append("")
        lines.append("<h2>%s</h2>" % esc(heading))
        lines.append("<ul>")
        for slug in listed:
            placed.add(slug)
            title, summary = found[slug]
            # `index` is the wiki root, so it is linked as the directory rather than as a file.
            href = "/wiki/" if slug == "index" else "/wiki/%s" % slug
            title_attr = (' title="%s"' % esc(summary)) if summary else ""
            # **Compared against a SLUG, not with `contains`.** `page.url contains '/wiki/'` is
            # true on every page in the wiki, so the index would have been marked as the current
            # page everywhere. The layout derives `pageslug` once from `page.url`; this only has
            # to match it.
            lines.append(
                '  <li><a href="{{ \'%s\' | relative_url }}"%s'
                '{%% if pageslug == \'%s\' %%} aria-current="page"{%% endif %%}>%s</a></li>'
                % (href, title_attr, slug, esc(title)))
        lines.append("</ul>")
    lines.append("")
    return NL.join(lines)


def working_material():
    """Every entry at `docs/` root that is not part of the published site.

    Read off the directory rather than listed, for the same reason the index is: a hand-written
    list is a second place the truth lives, and this one was already wrong in the direction that
    publishes a ledger.
    """
    found = []
    for name in sorted(os.listdir(DOCS)):
        if name.startswith("_") or name.startswith("."):
            continue        # Jekyll treats these as special and never publishes them.
        if name in PUBLISHED_ENTRIES:
            continue
        found.append(name)
    return found


def render_excludes(names):
    """The `exclude:` block, with the reason it exists written where it is read."""
    lines = [
        EXCLUDE_BEGIN,
        "  #",
        "  # Jekyll publishes every entry in its source directory that it is not told to",
        "  # exclude. This list named four directories until 0.12.93-dev -- two of which",
        "  # (evidence, reviews) do not exist -- while fifty-four documents sat at docs/ root,",
        "  # TODO.md and NOW.md among them. Enabling Pages would have published the whole work",
        "  # ledger. The owner's rule is that it is never published, so the rule is now a list",
        "  # that cannot fall behind the directory: `tools/build-site.py --check` fails the",
        "  # battery when a new document appears and is not named here.",
        "  #",
        "  # Explicit names, never globs: Jekyll's exact-name and directory-prefix rules behave",
        "  # identically in every version, and a glob that silently fails to exclude is the one",
        "  # failure mode a ledger guard must not have.",
    ]
    for name in names:
        lines.append("  - %s" % name)
    lines.append(EXCLUDE_END)
    return NL.join(lines)


def splice_excludes(text, block):
    """Replace the generated region, or refuse rather than guess where it goes."""
    begin = text.find(EXCLUDE_BEGIN)
    end = text.find(EXCLUDE_END)
    if begin < 0 or end < 0 or end < begin:
        return None
    return text[:begin] + block + text[end + len(EXCLUDE_END):]


def excludes_up_to_date(names):
    """(ok, message). False whenever the config does not hold exactly this list."""
    if not os.path.isfile(SITE_CONFIG):
        return False, "docs/_config.yml is missing"
    text = io.open(SITE_CONFIG, encoding="utf-8").read()
    begin = text.find(EXCLUDE_BEGIN)
    end = text.find(EXCLUDE_END)
    if begin < 0 or end < 0:
        return False, ("docs/_config.yml has no generated exclude block. Run "
                       "tools/build-site.py.")
    region = text[begin:end]
    listed = [line.strip()[2:].strip() for line in region.split(NL)
              if line.strip().startswith("- ")]
    missing = [name for name in names if name not in listed]
    extra = [name for name in listed if name not in names]
    if missing:
        return False, ("docs/_config.yml does not exclude %d entry(s) that are working "
                       "material: %s" % (len(missing), ", ".join(missing)))
    if extra:
        return False, ("docs/_config.yml excludes %d entry(s) that are not at docs/ root "
                       "any more: %s" % (len(extra), ", ".join(extra)))
    return True, "the exclude list matches %d working-material entry(s)" % len(listed)


def main():
    if not os.path.isdir(WIKI):
        print("build-site: %s does not exist" % WIKI)
        return 1
    found = pages()
    if not found:
        print("build-site: no pages found in docs/wiki")
        return 1
    rendered = render(found)
    existing = (io.open(INCLUDE, encoding="utf-8").read()
                if os.path.isfile(INCLUDE) else None)
    material = working_material()

    if "--check" in sys.argv:
        failures = []
        if existing is None:
            failures.append("docs/_includes/nav.html is missing. Run tools/build-site.py.")
        elif existing != rendered:
            failures.append("docs/_includes/nav.html is out of date against docs/wiki/. "
                            "Run tools/build-site.py and commit the result.")
        ok, message = excludes_up_to_date(material)
        if not ok:
            failures.append(message)
        if failures:
            for failure in failures:
                print("build-site: %s" % failure)
            return 1
        print("build-site: the generated index matches %d page(s)." % len(found))
        print("            %s" % message)
        return 0

    directory = os.path.dirname(INCLUDE)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    io.open(INCLUDE, "w", encoding="utf-8", newline=NL).write(rendered)
    unlisted = [slug for slug in found if slug not in set(
        s for _, names in SECTIONS for s in names)]
    print("build-site: wrote docs/_includes/nav.html for %d page(s)." % len(found))
    if unlisted:
        print("            indexed under \"More\": %s" % ", ".join(sorted(unlisted)))

    if not os.path.isfile(SITE_CONFIG):
        print("build-site: docs/_config.yml is missing; wrote no exclude list.")
        return 1
    config = io.open(SITE_CONFIG, encoding="utf-8").read()
    spliced = splice_excludes(config, render_excludes(material))
    if spliced is None:
        print("build-site: docs/_config.yml has no %r .. %r region, so there is nowhere to"
              % (EXCLUDE_BEGIN.strip(), EXCLUDE_END.strip()))
        print("            write the exclude list. Add the two marker lines under `exclude:`")
        print("            rather than letting this guess where the block belongs.")
        return 1
    io.open(SITE_CONFIG, "w", encoding="utf-8", newline=NL).write(spliced)
    print("build-site: wrote docs/_config.yml exclude list for %d working-material entry(s)."
          % len(material))
    print("            published: %s" % ", ".join(PUBLISHED_ENTRIES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
