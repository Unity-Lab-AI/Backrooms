# -*- coding: utf-8 -*-
"""Render the wiki to standalone static HTML, with no Jekyll and no build step.

Why this exists
---------------
**Owner direction, 2026-10-05, verbatim:** *"which should include only public facing documents and
wiki htmls for deploying the github.io static page"*, and when asked whether that meant Jekyll
source or committed HTML, the answer was **pre-rendered static HTML, no Jekyll**.

So this is the other half of the site story. `docs/` in the Backrooms repository keeps its Jekyll
source, because that is what a working repository should hold. The **published** repository gets
HTML that needs nothing: no gem, no `_config.yml`, no build on push, no network. It opens from
disk, and it would serve from any static host on earth.

Where the shape comes from, and the one rule it must not break
--------------------------------------------------------------
`SECTIONS`, `page_title` and `page_summary` are **imported from `tools/build-site.py`**, not copied.
The queue row says why in its own words: the two indexes must not be *"a second place the truth
lives"*. A copied reading order drifts the first time somebody adds a page, and then the Jekyll
site and the static site disagree about what the wiki is.

FLAT OUTPUT, DELIBERATELY. Every page is a sibling of every other, so each link is a bare
filename and the stylesheet is `assets/css/rimrooms.css` from everywhere. A nested `wiki/`
directory would mean `..` in some links and not others, which is the kind of thing that works
locally and 404s on a project subpath.

Nothing here hard-codes the site's own address, which is the same rule `CNAME.example` sets: links
are relative, so they follow whatever domain serves them.

The markdown subset
-------------------
Deliberately a subset, and matched to what the thirteen pages actually use rather than to a
specification: fenced code, tables with a header rule, headings, horizontal rules, blockquotes as
callouts, bulleted and numbered lists, and paragraphs that **join wrapped lines**.

That last one is why `tools/make-readable-html.py` could not be used as-is. It emits one `<p>` per
source line, and every wiki page is hard-wrapped at roughly ninety characters -- so a four-line
paragraph would have rendered as four paragraphs. It also has no blockquote, and the wiki uses
blockquote as its callout. The internal reader and the published site want different renderers;
pretending one tool does both is how the published site would quietly look wrong.

Usage
-----
    python tools/render-wiki-html.py <output-directory>
    python tools/render-wiki-html.py --check <output-directory>
"""
import io
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))

# **IMPORTED, NEVER COPIED.** One reading order, one title rule, one summary rule.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("rr_build_site", os.path.join(REPO, "tools", "build-site.py"))
_bs = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_bs)
SECTIONS = _bs.SECTIONS
page_title = _bs.page_title
page_summary = _bs.page_summary
BANNERS = _bs.BANNERS
SITE_ART_DIRECTORY = _bs.SITE_ART_DIRECTORY
BANNER_WIDTH = _bs.BANNER_WIDTH
BANNER_HEIGHT = _bs.BANNER_HEIGHT
PREVIEW_IMAGE = _bs.PREVIEW_IMAGE

# EVERY PATH A PAGE EMITS IS SITE-RELATIVE, AND THERE IS NO `..` ANYWHERE.
#
# Pages serves `/docs` **as the site root**, so `docs/gates.html` is published at
# `<site>/gates.html`. A `../` in any reference climbs out of the published site and 404s, which is
# precisely what happened the first time the banners pointed at the package copies of the slides:
# correct on disk, unreachable over HTTP, and the on-disk audit could not see it.
#
# This is the same rule the flat output already follows for links and the stylesheet. The art now
# obeys it too, and `export-public-repo.py` refuses any published page that breaks it.
ART_PREFIX = ""

WIKI = os.path.join(REPO, "docs", "wiki")
CSS = os.path.join(REPO, "docs", "assets", "css", "rimrooms.css")
CONFIG = os.path.join(REPO, "docs", "_config.yml")
NL = chr(10)


def read(path):
    return io.open(path, encoding="utf-8-sig").read()


def site_identity():
    """The site's name and one-line description, from the file that already curates them.

    Read out of `docs/_config.yml` rather than retyped here. The export does not ship that file,
    but the generator may read it: it is the existing single definition, and a second copy in this
    module is the drift this whole file is written to avoid.
    """
    text = read(CONFIG)
    title = re.search(r"(?m)^title:\s*(.+?)\s*$", text)
    description = re.search(r"(?m)^description:\s*(.+?)\s*$", text)
    return (title.group(1).strip() if title else "Rimrooms",
            description.group(1).strip() if description else "")


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def strip_front_matter(text):
    if not text.startswith("---"):
        return text
    end = text.find(NL + "---", 3)
    if end < 0:
        return text
    rest = text[end + 4:]
    return rest.lstrip(NL)


LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def rewrite_target(target):
    """`install.md` -> `install.html`, and a bare anchor or absolute URL is left alone.

    Written as a rewrite rather than by generating `.html` links in the source, because the source
    is markdown that has to keep working as markdown in the Jekyll site and on any viewer that
    renders the repository directly.
    """
    if target.startswith(("http://", "https://", "#", "mailto:")):
        return target
    anchor = ""
    if "#" in target:
        target, anchor = target.split("#", 1)
        anchor = "#" + anchor
    # **`lstrip("./")` USED TO FLATTEN AN ESCAPE PATH INTO A LIE, and it shipped one.** It strips
    # the characters `.` and `/` from the front, so `../../LICENSE` came out as `LICENSE` -- a
    # perfectly site-relative-looking href for a file that is not at the site root. The licence
    # link on the published credits page was **404 on the live site**, read back over HTTP, with
    # every instrument green: the on-disk path resolved, and the escape guard added at 0.12.97-dev
    # covers image sources only.
    #
    # So the two cases are now separated rather than collapsed. A `./` prefix is noise and is
    # stripped; a `..` is a page reaching outside the published site and is **carried through
    # intact**, so `check_links_resolve` in the exporter refuses it instead of inheriting a
    # flattened href that looks correct.
    if target.startswith("./"):
        target = target[2:]
    if target.split("#")[0].rsplit("/", 1)[-1] == "LICENSE" and ".." in target.split("/"):
        # The one escape that is answered by publishing the file twice rather than by rewording
        # the page -- the same answer the slide art got, for the same reason. A credits page that
        # cites a licence has to be able to link it, and the export copies `LICENSE` into the
        # site directory so this href resolves at the site root.
        return "LICENSE" + anchor
    if target.endswith(".md"):
        target = target[:-3] + ".html"
    return target + anchor


def inline(text):
    """The inline markdown the pages use. Escaped first, so no source can inject markup."""
    out = esc(text)
    # Code spans first: their contents must not then be read as emphasis.
    spans = []

    def stash(match):
        spans.append(match.group(1))
        return "\x00%d\x00" % (len(spans) - 1)

    out = re.sub(r"`([^`]+)`", stash, out)
    out = re.sub(r"\*\*\*([^*]+)\*\*\*", r"<strong><em>\1</em></strong>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", out)
    out = LINK.sub(lambda m: '<a href="%s">%s</a>'
                   % (esc(rewrite_target(m.group(2))), m.group(1)), out)
    for index, span in enumerate(spans):
        out = out.replace("\x00%d\x00" % index, "<code>%s</code>" % span)
    return out


TABLE_RULE = re.compile(r"^\s*\|?[\s:\-|]+\|?\s*$")


def render_blocks(text):
    """Block-level markdown, written as an explicit state machine over blank-line-separated runs.

    A line-at-a-time renderer is what produced one paragraph per source line in the internal
    reader. Grouping into blocks first is what makes a hard-wrapped paragraph render as one
    paragraph, which is the whole reason the published site needed its own renderer.
    """
    out = []
    lines = text.split(NL)
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith("```"):
            index += 1
            block = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                block.append(lines[index])
                index += 1
            index += 1
            out.append("<pre><code>%s</code></pre>" % esc(NL.join(block)))
            continue

        if not stripped:
            index += 1
            continue

        if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", line):
            out.append("<hr>")
            index += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            out.append("<h%d>%s</h%d>" % (level, inline(heading.group(2).strip()), level))
            index += 1
            continue

        # A table: a run of pipe rows. The separator row is what makes the first row a header,
        # so a pipe table without one is rendered as an all-body table rather than guessed at.
        if stripped.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(lines[index].strip())
                index += 1
            header = len(rows) > 1 and TABLE_RULE.match(rows[1]) is not None

            def cells(row):
                return [c.strip() for c in row.strip().strip("|").split("|")]

            # **AN ALL-EMPTY HEADER ROW IS NOT A HEADER.** The wiki writes its two-column link
            # tables as `| | |` with a rule under them, which is valid markdown and renders a
            # header of empty cells. A screen reader announces those as column headers and gets
            # nothing, which is worse than having no header row at all -- so the cells are kept
            # as ordinary ones and the table is left headerless.
            if header and not any(c.strip() for c in cells(rows[0])):
                header = False
                # Dropped, not demoted. Keeping it as a body row leaves a visibly empty first
                # row in the table, which was the first attempt and looked like a rendering bug.
                rows = rows[2:]

            out.append("<table>")
            if header:
                out.append("<thead><tr>%s</tr></thead>"
                           % "".join("<th>%s</th>" % inline(c) for c in cells(rows[0])))
                body = rows[2:]
            else:
                body = rows
            out.append("<tbody>")
            for row in body:
                out.append("<tr>%s</tr>"
                           % "".join("<td>%s</td>" % inline(c) for c in cells(row)))
            out.append("</tbody></table>")
            continue

        if stripped.startswith(">"):
            block = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                block.append(lines[index].strip()[1:].strip())
                index += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(block).strip()))
            continue

        bullet = re.match(r"^\s*[-*+]\s+(.*)$", line)
        number = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if bullet or number:
            ordered = number is not None
            items = []
            while index < len(lines):
                current = lines[index]
                start = (re.match(r"^\s*\d+[.)]\s+(.*)$", current) if ordered
                         else re.match(r"^\s*[-*+]\s+(.*)$", current))
                if start:
                    items.append([start.group(1).strip()])
                    index += 1
                    continue
                # A wrapped list item: indented continuation with an item already open.
                if items and current.strip() and re.match(r"^\s{2,}\S", current):
                    items[-1].append(current.strip())
                    index += 1
                    continue
                break
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (
                tag, "".join("<li>%s</li>" % inline(" ".join(item)) for item in items), tag))
            continue

        # A paragraph: every following line until a blank one or a line that starts a new block.
        block = []
        while index < len(lines):
            current = lines[index]
            if not current.strip():
                break
            if (current.strip().startswith(("|", ">", "```", "#"))
                    or re.match(r"^\s*[-*+]\s+", current)
                    or re.match(r"^\s*\d+[.)]\s+", current)
                    or re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", current)):
                break
            block.append(current.strip())
            index += 1
        if block:
            out.append("<p>%s</p>" % inline(" ".join(block)))
    return NL.join(out)


def nav_html(found, current):
    """The index, in the order `build-site.py` declares, with the current page marked.

    Marked by `aria-current` exactly as the Jekyll layout does, so `rimrooms.css` styles both
    sites identically from one stylesheet and the current page is signalled by weight and an
    inset rule rather than by colour alone.
    """
    out = []
    listed = set(s for _, names in SECTIONS for s in names)
    groups = list(SECTIONS)
    extra = [slug for slug in sorted(found) if slug not in listed]
    if extra:
        groups.append(("More", extra))
    for heading, slugs in groups:
        present = [slug for slug in slugs if slug in found]
        if not present:
            continue
        out.append("<h2>%s</h2>" % esc(heading))
        out.append("<ul>")
        for slug in present:
            title = found[slug][0]
            summary = found[slug][1]
            href = "index.html" if slug == "index" else "%s.html" % slug
            mark = ' aria-current="page"' if slug == current else ""
            hint = ' title="%s"' % esc(summary) if summary else ""
            out.append('  <li><a href="%s"%s%s>%s</a></li>'
                       % (href, hint, mark, esc(title)))
        out.append("</ul>")
    return NL.join(out)


def banner_html(slug):
    """The page's decorative band, or nothing when no slide is assigned.

    **Nothing is ever written across it.** The band is a sibling of the prose and sits above it,
    so the owner's test -- *"to where text writing is not fighting the art to be read"* -- is
    satisfied by the structure rather than by a colour choice somebody could later tune away.

    `alt=""` plus `aria-hidden` is the correct pair for decoration: a screen reader skips it
    entirely instead of announcing `RR_Menu_PanicJunction.png`, which is not information.

    `width` and `height` are the real pixel dimensions so the browser reserves the space before
    the bytes arrive and the heading does not jump down the page as it loads.
    """
    name = BANNERS.get(slug)
    if not name:
        return ""
    return NL.join([
        '    <div class="banner" role="presentation">',
        '      <img src="%s%s/%s" alt="" aria-hidden="true" loading="lazy" decoding="async"'
        % (ART_PREFIX, SITE_ART_DIRECTORY, esc(name)),
        '           width="%d" height="%d">' % (BANNER_WIDTH, BANNER_HEIGHT),
        "    </div>",
    ])


def preview_html(site_title):
    """The front page's cover, and the one image that is NOT decoration.

    **Owner, verbatim:** *"make sure the preview image is prominate becasue thats what mod loaders
    see"*. That is exactly why it leads: a mod manager already renders this file in its list, so a
    reader arriving at the wiki sees the same picture they will see in their launcher.

    It carries a real `alt` rather than being hidden, because unlike the banners this one is
    **content** -- it is the mod's cover, and a reader who cannot see it should still be told that
    is what they are missing.
    """
    return NL.join([
        '    <div class="cover">',
        '      <img src="%s%s" alt="%s cover art" loading="eager" decoding="async"'
        % (ART_PREFIX, PREVIEW_IMAGE, esc(site_title)),
        '           width="%d" height="%d">' % (BANNER_WIDTH, BANNER_HEIGHT),
        "    </div>",
    ])


def shell(site_title, site_description, page_name, summary, nav, body, slug=""):
    """The same structure as `_layouts/default.html`, so one stylesheet serves both sites."""
    head_title = ("%s — %s" % (page_name, site_title)) if page_name != site_title else site_title
    return NL.join([
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % esc(head_title),
        '<meta name="description" content="%s">' % esc(summary or site_description),
        '<link rel="stylesheet" href="assets/css/rimrooms.css">',
        "</head>",
        "<body>",
        "",
        "<!-- GENERATED by tools/render-wiki-html.py from docs/wiki/. Do not edit: edit the page.",
        "     Owner: \"wiki htmls for deploying the github.io static page\". No Jekyll, no build",
        "     step, no external request. The reading order and the per-page summary come from",
        "     tools/build-site.py, imported rather than copied, so the two sites cannot disagree",
        "     about what the wiki is. -->",
        "",
        '<a class="skip" href="#content">Skip to content</a>',
        "",
        '<header class="masthead">',
        '  <div class="masthead-inner">',
        '    <a class="brand" href="index.html">%s</a>' % esc(site_title),
        '    <p class="tagline">%s</p>' % esc(site_description),
        "  </div>",
        "</header>",
        "",
        '<div class="shell">',
        "",
        '  <nav class="sidebar" aria-label="Pages">',
        nav,
        "  </nav>",
        "",
        '  <main id="content" class="prose">',
        preview_html(site_title) if slug == "index" else banner_html(slug),
        ('    <p class="summary">%s</p>' % esc(summary)) if summary else "",
        body,
        "  </main>",
        "",
        "</div>",
        "",
        '<footer class="footer">',
        "  <p>%s. A development build; nothing here is a balance, performance or" % esc(site_title),
        "     compatibility report.</p>",
        "</footer>",
        "",
        "</body>",
        "</html>",
        "",
    ])


def pages():
    found = {}
    for name in sorted(os.listdir(WIKI)):
        if not name.endswith(".md"):
            continue
        slug = name[:-3]
        text = read(os.path.join(WIKI, name))
        found[slug] = (page_title(text, slug), page_summary(text), text)
    return found


def render_all():
    """Every output file as {relative path: text}. Nothing is written here."""
    site_title, site_description = site_identity()
    found = pages()
    meta = dict((slug, (title, summary)) for slug, (title, summary, _) in found.items())
    out = {}
    for slug, (title, summary, text) in sorted(found.items()):
        body = render_blocks(strip_front_matter(text))
        # The page's own `# ` heading is the title the shell already shows in <title>, and the
        # layout prints the summary above the content. The heading stays in the body because a
        # reader landing mid-site needs to see what page they are on.
        name = "index.html" if slug == "index" else "%s.html" % slug
        out[name] = shell(site_title, site_description, title, summary,
                          nav_html(meta, slug), body, slug)
    out[os.path.join("assets", "css", "rimrooms.css").replace(os.sep, "/")] = read(CSS)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    if not args:
        print("render-wiki-html: give an output directory")
        return 1
    target = os.path.abspath(args[0])
    rendered = render_all()

    if check:
        problems = []
        for rel, text in sorted(rendered.items()):
            path = os.path.join(target, rel.replace("/", os.sep))
            if not os.path.isfile(path):
                problems.append("missing: %s" % rel)
            elif read(path) != text:
                problems.append("out of date: %s" % rel)
        if problems:
            for problem in problems:
                print("render-wiki-html: %s" % problem)
            print("render-wiki-html: re-run without --check.")
            return 1
        print("render-wiki-html: %d file(s) match the wiki source." % len(rendered))
        return 0

    for rel, text in sorted(rendered.items()):
        path = os.path.join(target, rel.replace("/", os.sep))
        directory = os.path.dirname(path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)
        io.open(path, "w", encoding="utf-8", newline=NL).write(text)
    pagecount = len([r for r in rendered if r.endswith(".html")])
    print("render-wiki-html: wrote %d page(s) + the stylesheet to %s" % (pagecount, target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
