# -*- coding: utf-8 -*-
"""Render the RimPLC wiki (RimPLC/docs/wiki/*.md) to standalone static HTML.

Owner, 2026-10-13, verbatim: *"and something i think is fucked is the RimPLC repo doesnt have it wiki
deployed.. i dont have the RimPLC address for its fully layed out wiki.. for some reason ther is a
RIMPLC section in the Rimrooms wiki,, this is an error"*.

So RimPLC has its own wiki source and its own site, rendered by the SAME engine as the Rimrooms
wiki (`tools/render-wiki-html.py`, imported, never copied) with its own reading order, its own
identity and its own cover: flat output, relative links, the shared stylesheet, no Jekyll. The
RimPLC export renders it into the published repository's `docs/`, which GitHub Pages serves as
the site root at https://g-fourteen.github.io/RimPLC/.

Usage
-----
    python tools/render-rimplc-wiki.py <output-directory>
    python tools/render-rimplc-wiki.py --check <output-directory>
"""
import importlib.util
import io
import os
import shutil
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
WIKI = os.path.join(REPO, "RimPLC", "docs", "wiki")
PREVIEW = os.path.join(REPO, "RimPLC", "About", "Preview.png")
SITE_TITLE = "RimPLC"
SITE_DESCRIPTION = "Colony logic as a PLC ladder: live sensors, editable rules and an in-game ladder window."
SECTIONS = [
    ("Start", ["index", "install", "window"]),
    ("Rules", ["ladder", "sensors"]),
    ("Programs", ["commands", "presets"]),
    ("About", ["links"]),
]
NL = chr(10)


def engine():
    """The Rimrooms renderer, pointed at this wiki: same markdown subset, same shell, same stylesheet."""
    spec = importlib.util.spec_from_file_location("rr_render_wiki", os.path.join(REPO, "tools", "render-wiki-html.py"))
    rw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rw)
    rw.WIKI = WIKI
    rw.SECTIONS = SECTIONS
    rw.BANNERS = {}                               # no slide art: the cover on the index is the only picture
    rw.PREVIEW_IMAGE = "assets/Preview.png"
    rw.site_identity = lambda: (SITE_TITLE, SITE_DESCRIPTION)
    return rw


def render_all():
    """Every output file as {relative path: text}, plus the one binary (the cover) as a source path."""
    rw = engine()
    out = rw.render_all()
    out[".nojekyll"] = ""                         # Pages must serve the files as they are, never build them
    return out, {"assets/Preview.png": PREVIEW}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    if not args:
        print("render-rimplc-wiki: give an output directory")
        return 1
    target = os.path.abspath(args[0])
    rendered, binaries = render_all()
    if check:
        problems = []
        for rel, text in sorted(rendered.items()):
            path = os.path.join(target, rel.replace("/", os.sep))
            if not os.path.isfile(path):
                problems.append("missing: %s" % rel)
            elif io.open(path, encoding="utf-8-sig").read() != text:
                problems.append("out of date: %s" % rel)
        for rel, source in binaries.items():
            path = os.path.join(target, rel.replace("/", os.sep))
            if not os.path.isfile(path) or open(path, "rb").read() != open(source, "rb").read():
                problems.append("missing or out of date: %s" % rel)
        for problem in problems:
            print("render-rimplc-wiki: %s" % problem)
        if problems:
            return 1
        print("render-rimplc-wiki: %d file(s) match the wiki source." % (len(rendered) + len(binaries)))
        return 0
    for rel, text in sorted(rendered.items()):
        path = os.path.join(target, rel.replace("/", os.sep))
        directory = os.path.dirname(path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)
        io.open(path, "w", encoding="utf-8", newline=NL).write(text)
    for rel, source in binaries.items():
        path = os.path.join(target, rel.replace("/", os.sep))
        directory = os.path.dirname(path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)
        shutil.copyfile(source, path)
    pages = len([r for r in rendered if r.endswith(".html")])
    print("render-rimplc-wiki: wrote %d page(s), the stylesheet, the cover and .nojekyll to %s" % (pages, target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
