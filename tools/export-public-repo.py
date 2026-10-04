# -*- coding: utf-8 -*-
"""Build the public repository: the mod exactly as the game loads it, plus the public face.

Why this exists
---------------
**Owner direction, 2026-10-05, verbatim:** *"the repo for the mod only is
:https://git.unityailab.com/GFourteen/Rimrooms-AsyncIndustries.git which should include only public
facing documents and wiki htmls for deploying the github.io static page but for forgejo, and the
same thing for a github repo of the same name that you will make and set up to have only the mod
and only the public facing docs and wiki htmls for deployment to pages"*.

And, asked what *the mod* means, three times in a row: *"make sure as far as what goes in it is only
what the game need to run the mod"*, *"ie what we stage"*, *"what goes into the game as the mod, idk
, idk how to say it"*.

It was said clearly enough, and it was already machine-readable.

ONE DEFINITION OF "THE MOD", AND IT IS NOT IN THIS FILE
-------------------------------------------------------
`artifacts/build/package-manifest.json` is written by the build and holds every package file with
its size and SHA256. `tools/stage-mod.ps1` copies exactly that set into the game folder. **This
reads the same manifest**, so "what we stage" and "what we publish" cannot drift apart: there is
one list, produced by the build, and two consumers.

**Every hash is verified on the way out.** The stager refuses a package edited after the build, by
hash, for the reason that a staged mod must be the one that was built and checked. Publishing has
the same requirement and a worse failure mode -- a wrong file in the game folder is one machine, a
wrong file in a public repository is everybody's.

THE DENYLIST REFUSES; IT DOES NOT TRUST
---------------------------------------
The queue row's words: the repository *"should include only public facing documents and wiki
htmls"*. An allowlist decides what goes in. A **denylist then refuses the result**, and both run,
because 0.12.93-dev learned this the expensive way: `docs/_config.yml` *described* an exclusion
policy it did not implement, and enabling Pages would have published the whole work ledger.

So the export is assembled from an explicit allowlist, and then the assembled tree is scanned for
anything that must never be in it. The second pass is not redundant: it is the one that catches a
mistake in the first.

FRESH HISTORY, AND DELIBERATELY NOT A SUBTREE SPLIT
---------------------------------------------------
`git subtree split` was offered to the owner and argued against; the owner agreed. Backrooms'
history contains the ledger in essentially every commit, and a split carries the history of the
paths it keeps -- so a public repository would have ended up holding hundreds of commits of
`docs/TODO.md`. The export repository starts its own history here and gains one commit per
publication. Nothing from Backrooms' past travels.

Usage
-----
    python tools/export-public-repo.py              # build the tree, report, change no remote
    python tools/export-public-repo.py --commit     # also commit it in the export repository
    python tools/export-public-repo.py --push       # also push to forgejo and github
"""
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MANIFEST = os.path.join(REPO, "artifacts", "build", "package-manifest.json")
PACKAGE = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
EXPORT = os.path.join(REPO, ".local", "export", "Rimrooms-AsyncIndustries")
RENDERER = os.path.join(REPO, "tools", "render-wiki-html.py")
NL = chr(10)

# The two remotes, by the owner's own words. Forgejo already exists and is empty; GitHub is on the
# owner's personal account -- *"itylab ai but my personal"* -- mirroring the Forgejo path exactly.
REMOTES = [
    ("forgejo", "ssh://git@git.unityailab.com/GFourteen/Rimrooms-AsyncIndustries.git"),
    ("github", "https://github.com/G-Fourteen/Rimrooms-AsyncIndustries.git"),
]

# Copied verbatim. **Only the licence**, and that is not an oversight.
#
# `README.md` is NOT copied. The working repository's readme is clean of internal vocabulary -- it
# is in the reader-facing set and checked -- but **every link in it is wrong here**: it points at
# `docs/wiki/*.md`, which this export renders to `docs/*.html`, and at `CONTRIBUTING.md` and
# `docs/BUILDING.md`, which are development documents that do not ship. Copying it would publish a
# readme of dead links. So the export gets its own, generated below from `About.xml` -- the text
# that already describes this mod to a player, in the game itself.
#
# `CHANGELOG.md` is NOT copied either, and the audit is what forced the decision: it refused the
# export because the changelog contains *"VERBATIM TRANSFER CONFIRMED"*. That is correct. The
# changelog is a **development log** -- queue counts, proof and plant tallies, instrument names --
# and the owner's standing rule for public documents is explicit: *"public facing docs are concise
# easy to read and have no in house dev names and no todo numbering and no actual work
# information"*. A player-facing *what is new* is worth having and is **authoring work**, not a
# transformation of this one; filtering it automatically would be guessing at what a player cares
# about. Left out and recorded rather than shipped dressed up.
PUBLIC_FILES = [
    ("LICENSE", "LICENSE"),
]

ABOUT = os.path.join(PACKAGE, "About", "About.xml")

# Where the rendered site goes. Pages serves either the repository root or `/docs` and nothing
# else, and the root is the mod folder, so `/docs` is the only arrangement that satisfies both
# halves of the direction at once.
SITE_DIRECTORY = "docs"

# Anything matching these must never reach the export. Checked against the assembled tree, after
# the allowlist has had its say.
#
# **This is the pass that catches a mistake in the allowlist**, so it names the hazards by
# category rather than by the paths the allowlist happens to use.
FORBIDDEN_NAMES = {
    "TODO.md", "TODO.html", "NOW.md", "NOW.html", "FINALIZED.md", "FINALIZED.html",
    "DECOMPOSED.md", "DECOMPOSED.html", "ROADMAP.md", "ROADMAP.html", "DEFERRED.md",
    "PREPRODUCTION_AND_IMPLEMENTATION_TODO.md", "AI_BUILD_HANDOFF.md", "PUBLISHING.md",
    "GATE_0_DECISIONS.md", "SOURCE_REGISTER.md", "MOD_INTEGRATION_PLAN.md",
    "REGRESSION_CONTAINMENT.md", "ADMIN-ONBOARDING.md", "user.json", ".env",
}
FORBIDDEN_PARTS = (".claude", ".local", "implementation", "research", "reviews", "evidence",
                   "artifacts", "src", "tools", "outputs", "node_modules")
# Text that would mean working material got in even under an innocent filename. A task marker and
# the archive's own transfer banner are both unmistakable.
FORBIDDEN_TEXT = (
    "VERBATIM TRANSFER CONFIRMED",
    "archived-queue:begin",
    "LAW #0",
)

# **NOTHING IN THE PUBLIC REPOSITORY MAY REFERENCE THE BUILD REPOSITORIES.**
#
# Owner direction, 2026-10-05, verbatim: *"nothing should refrence the build repos anywhere"*.
#
# This was live when the rule was given. `docs/wiki/links.md` pointed its **Repository** and
# **Issues** rows at the working repository, so the published site sent every reader who wanted the
# source, or who wanted to report a bug, to the repository that holds the work ledger.
#
# Matched on the **repository forms only**, never on the bare word: *Backrooms* is the name of the
# setting and appears all over the wiki as prose, which it must. A rule that banned the word would
# be unusable, and this battery has five recorded cases of a check that cried wolf being scrolled
# past. So the patterns are owner/repo pairs and hostnames -- things that can only be a repository.
FORBIDDEN_REFERENCES = (
    "Unity-Lab-AI/Backrooms",
    "unity-lab-ai.github.io",
    "git.unityailab.com",
    "GFourteen/Backrooms",
    "Unity-Lab-AI/backrooms",
)
TEXT_SUFFIXES = (".md", ".html", ".htm", ".txt", ".xml", ".json", ".yml", ".css", ".js")


def read_bytes(path):
    return io.open(path, "rb").read()


def sha256(path):
    return hashlib.sha256(read_bytes(path)).hexdigest().upper()


def load_manifest():
    if not os.path.isfile(MANIFEST):
        return None, "no build manifest at artifacts/build/package-manifest.json -- build first"
    data = json.load(io.open(MANIFEST, encoding="utf-8-sig"))
    files = data.get("Files") or []
    if not files:
        return None, "the build manifest names no files"
    return data, None


def copy_mod(problems):
    """The mod, from the manifest, hash-verified. Returns how many files were copied."""
    data, error = load_manifest()
    if error:
        problems.append(error)
        return 0, None
    copied = 0
    for entry in data["Files"]:
        rel = entry["Path"].replace("\\", "/")
        source = os.path.join(PACKAGE, rel.replace("/", os.sep))
        if not os.path.isfile(source):
            problems.append("the manifest names a file the package does not have: %s" % rel)
            continue
        actual = sha256(source)
        if actual != entry["SHA256"].upper():
            problems.append("%s does not match the build manifest (edited after the build?); "
                            "rebuild, then export" % rel)
            continue
        target = os.path.join(EXPORT, rel.replace("/", os.sep))
        directory = os.path.dirname(target)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)
        shutil.copyfile(source, target)
        if sha256(target) != entry["SHA256"].upper():
            problems.append("%s did not read back identical after the copy" % rel)
            continue
        copied += 1
    return copied, data


def copy_public(problems):
    copied = []
    for source_rel, target_rel in PUBLIC_FILES:
        source = os.path.join(REPO, source_rel)
        if not os.path.isfile(source):
            problems.append("a public-facing file is missing: %s" % source_rel)
            continue
        target = os.path.join(EXPORT, target_rel)
        shutil.copyfile(source, target)
        copied.append(target_rel)
    return copied


def write_readme(problems):
    """The export's own readme, from the mod's own words.

    Built from `About.xml` rather than written here, for the same reason the mod payload comes from
    the build manifest: the description a player reads in the mod list and the description they
    read on the repository should be the same sentence, and the only way to guarantee that is to
    have one copy of it.

    **No link in it points at anything the export does not contain**, which is the rule the working
    repository's readme cannot satisfy here. The wiki links go to the rendered pages; there is no
    link to a changelog, a contributing guide or a build document, because none of those ship.

    **It does not name the published site's address.** Same rule `CNAME.example` sets: a document
    must not claim a URL that may not serve. The wiki is linked by relative path, which works on
    the repository's own file view and from a clone alike.
    """
    import xml.etree.ElementTree as ET
    if not os.path.isfile(ABOUT):
        problems.append("About.xml is missing, so the readme cannot be generated")
        return None
    root = ET.parse(ABOUT).getroot()

    def value(tag):
        node = root.find(tag)
        return (node.text or "").strip() if node is not None else ""

    name = value("name")
    versions = ", ".join((li.text or "").strip()
                         for li in root.findall("supportedVersions/li"))
    description = value("description")

    # The description uses `--- SECTION ---` as its own heading form, because that is all a mod
    # list can render. Promoted to real headings here and left alone otherwise.
    body = []
    for block in re.split(r"\n\s*\n", description):
        block = " ".join(block.split())
        if not block:
            continue
        heading = re.match(r"^-{2,}\s*(.+?)\s*-{2,}$", block)
        if heading:
            body.append("## %s" % heading.group(1).strip().title())
        else:
            body.append(block)

    order = [("index", "Start here"), ("install", "Install"), ("first-hour", "Your first hour"),
             ("scenarios", "The three starts"), ("gates", "Gates and connections"),
             ("backrooms", "Beyond the gate"), ("company", "The company"),
             ("interface", "The interface"), ("mods", "Mods and expansions"),
             ("multiplayer", "Multiplayer"), ("troubleshooting", "Troubleshooting"),
             ("links", "Links"), ("credits", "Credits")]
    site = os.path.join(EXPORT, SITE_DIRECTORY)
    links = []
    for slug, label in order:
        target = "%s/%s.html" % (SITE_DIRECTORY, slug)
        if os.path.isfile(os.path.join(site, "%s.html" % slug)):
            links.append("- [%s](%s)" % (label, target))
        else:
            problems.append("the readme would link to a page the export does not have: %s"
                            % target)

    text = NL.join([
        "# %s" % name,
        "",
        "**%s** for RimWorld %s. Needs no other mod and no expansion." % (value("modVersion"),
                                                                         versions),
        "",
        "> **Development build.** Gameplay acceptance is pending; this is not a finished campaign",
        "> release, and nothing here is a balance, performance or compatibility report.",
        "",
    ] + body + [
        "",
        "## Install",
        "",
        "Download or clone this repository into RimWorld's `Mods` folder, so that `About/` and",
        "`1.6/` sit directly inside it. Enable it in the mod list. The folder's name does not",
        "matter: the game identifies a mod by the `packageId` in `About/About.xml`, which is",
        "`%s`." % value("packageId"),
        "",
        "This repository holds the mod exactly as the game loads it. Nothing has to be built.",
        "",
        "## Documentation",
        "",
        "The full wiki is in [`%s/`](%s/index.html) and is plain static HTML, so it reads from a"
        % (SITE_DIRECTORY, SITE_DIRECTORY),
        "clone with no build step and no network.",
        "",
    ] + links + [
        "",
        "## Licence",
        "",
        "MIT. See [LICENSE](LICENSE).",
        "",
    ])
    io.open(os.path.join(EXPORT, "README.md"), "w", encoding="utf-8", newline=NL).write(text)
    return "README.md"


def render_site(problems):
    target = os.path.join(EXPORT, SITE_DIRECTORY)
    code = subprocess.call([sys.executable, RENDERER, target], cwd=REPO,
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    if code != 0:
        problems.append("the wiki renderer failed (exit %d)" % code)
        return 0

    # **`.nojekyll` OR PAGES BUILDS IT ANYWAY.** GitHub Pages runs Jekyll over the published
    # folder by default, and the owner's answer was explicitly *pre-rendered static HTML, no
    # Jekyll*. Without this marker the deploy quietly reintroduces the build step this export
    # exists to remove -- and a Jekyll build that finds no `_config.yml` can fail the deployment
    # outright rather than falling back to serving the files.
    #
    # Empty by design: Pages tests for the file's presence, never its contents.
    io.open(os.path.join(target, ".nojekyll"), "w", encoding="utf-8", newline=NL).write("")
    return len([n for n in os.listdir(target) if n.endswith(".html")])


def audit(problems):
    """Refuse the assembled tree if anything in it must not be published.

    Walks what is actually on disk rather than what the allowlist intended to put there, because
    the whole value of this pass is catching the difference between those two.
    """
    seen = 0
    for base, dirs, names in os.walk(EXPORT):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in names:
            path = os.path.join(base, name)
            rel = os.path.relpath(path, EXPORT).replace(os.sep, "/")
            seen += 1
            if name in FORBIDDEN_NAMES:
                problems.append("WORKING MATERIAL IN THE EXPORT: %s" % rel)
                continue
            if any(part in FORBIDDEN_PARTS for part in rel.split("/")[:-1]):
                problems.append("WORKING DIRECTORY IN THE EXPORT: %s" % rel)
                continue
            if not rel.lower().endswith(TEXT_SUFFIXES):
                continue
            try:
                text = io.open(path, encoding="utf-8-sig").read()
            except (UnicodeDecodeError, OSError):
                continue
            for marker in FORBIDDEN_TEXT:
                if marker in text:
                    problems.append("LEDGER TEXT IN THE EXPORT: %s contains %r" % (rel, marker))
                    break
            for marker in FORBIDDEN_REFERENCES:
                if marker.lower() in text.lower():
                    problems.append("A BUILD REPOSITORY IS REFERENCED IN THE EXPORT: %s names "
                                    "%r -- owner: nothing should reference the build repos "
                                    "anywhere" % (rel, marker))
                    break
            # A queue row carries its own shape, and it is unmistakable at the start of a line.
            if re.search(r"(?m)^\s*- \[[ x~T]\] ", text):
                problems.append("A QUEUE ROW IN THE EXPORT: %s" % rel)
    check_images_resolve(problems)
    return seen


def check_images_resolve(problems):
    """Every `<img src>` in the published site must name a file that is actually in the export.

    **This is the one failure mode the art work could have had, and it is silent.** The banners
    reference the slides where the *mod* puts them -- `../1.6/Textures/UI/Menu/...` -- precisely so
    that twenty-one megabytes are not duplicated into the site directory. The cost of that choice
    is that the link crosses from the site into the package, so a renamed texture, a manifest that
    stops carrying the menu art, or a change to `SITE_DIRECTORY` would publish **pages full of
    broken images with every instrument still green.**

    Resolved against the assembled tree on disk rather than against the mapping that generated it,
    for the same reason the rest of this audit walks the tree: the point is to catch the difference
    between what was intended and what is there.
    """
    site = os.path.join(EXPORT, SITE_DIRECTORY)
    if not os.path.isdir(site):
        return
    checked = 0
    for name in sorted(os.listdir(site)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(site, name)
        try:
            text = io.open(path, encoding="utf-8-sig").read()
        except (UnicodeDecodeError, OSError):
            continue
        for src in re.findall(r"<img[^>]+src=\"([^\"]+)\"", text):
            if src.startswith(("http://", "https://", "data:")):
                continue
            checked += 1
            target = os.path.normpath(os.path.join(site, src.replace("/", os.sep)))
            if not os.path.isfile(target):
                problems.append("A PUBLISHED PAGE REFERENCES AN IMAGE THAT IS NOT IN THE EXPORT: "
                                "%s/%s names %r" % (SITE_DIRECTORY, name, src))
    # An absence rule over an empty set is satisfied by construction, which is the trap this
    # project keeps meeting. The art is not optional, so finding none is itself the fault.
    if checked == 0:
        problems.append("NO PAGE IN THE PUBLISHED SITE REFERENCES AN IMAGE. The owner's direction "
                        "is that the slide art is the wiki's banner and the preview leads; a site "
                        "with no image means the banners stopped being generated.")


def git(*args):
    return subprocess.call(["git"] + list(args), cwd=EXPORT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def git_out(*args):
    try:
        return subprocess.check_output(["git"] + list(args), cwd=EXPORT,
                                       stderr=subprocess.STDOUT).decode("utf-8", "replace").strip()
    except subprocess.CalledProcessError:
        return ""


def ensure_repo(problems):
    if not os.path.isdir(os.path.join(EXPORT, ".git")):
        if git("init", "-q") != 0:
            problems.append("could not initialise the export repository")
            return
        git("symbolic-ref", "HEAD", "refs/heads/main")
    for name, url in REMOTES:
        current = git_out("remote", "get-url", name)
        if not current:
            git("remote", "add", name, url)
        elif current != url:
            git("remote", "set-url", name, url)


def main():
    problems = []
    data, error = load_manifest()
    if error:
        print("export-public-repo: %s" % error)
        return 1
    version = data.get("Version", "unknown")

    # **The tree is rebuilt from scratch every time, except for `.git`.** An incremental copy
    # leaves a file behind the day its source is deleted, and a published repository holding a
    # page that no longer exists is the stale-index failure with a worse blast radius.
    if os.path.isdir(EXPORT):
        for name in sorted(os.listdir(EXPORT)):
            if name == ".git":
                continue
            path = os.path.join(EXPORT, name)
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    else:
        os.makedirs(EXPORT)

    mod_files, data = copy_mod(problems)
    public = copy_public(problems)
    # The site is rendered before the readme, because the readme refuses to link to a page that
    # is not there and can only know that once the pages exist.
    pages = render_site(problems)
    readme = write_readme(problems)
    if readme:
        public = public + [readme + " (generated from About.xml)"]
    total = audit(problems)

    print("export-public-repo")
    print("  version                  : %s" % version)
    print("  mod files (from manifest) : %d, every SHA256 verified" % mod_files)
    print("  public-facing documents   : %d (%s)" % (len(public), ", ".join(public)))
    print("  rendered wiki pages       : %d, into %s/" % (pages, SITE_DIRECTORY))
    print("  files in the export       : %d" % total)
    print("  export tree               : %s" % os.path.relpath(EXPORT, REPO))
    print("")

    if problems:
        print("REFUSED: %d problem(s)" % len(problems))
        for problem in sorted(set(problems)):
            print("  - %s" % problem)
        return 1
    print("CLEAN: the export holds the staged mod, the public documents and the rendered wiki.")

    if "--commit" in sys.argv or "--push" in sys.argv:
        ensure_repo(problems)
        git("add", "-A")
        if not git_out("diff", "--cached", "--name-only"):
            print("")
            print("nothing to commit: the export already matches the last one.")
        else:
            message = ("Rimrooms - Async Industries %s" % version + NL + NL +
                       "The mod exactly as the game loads it, from the build manifest with every "
                       "SHA256" + NL +
                       "verified, plus the public documents and the wiki rendered to static HTML." +
                       NL + NL +
                       "Generated by tools/export-public-repo.py in the working repository. Do not "
                       "commit" + NL + "here by hand: the next export rebuilds this tree." + NL)
            if git("commit", "-q", "-m", message) != 0:
                print("the export commit failed")
                return 1
            print("")
            print("committed %s in the export repository" % git_out("rev-parse", "--short", "HEAD"))

    if "--push" in sys.argv:
        print("")
        for name, _ in REMOTES:
            code = git("push", "-u", name, "main")
            print("  push %-8s %s" % (name, "ok" if code == 0 else "FAILED (exit %d)" % code))
            if code != 0:
                problems.append("push to %s failed" % name)

        # **THE PUSH RECEIPTS ITSELF.** Owner, 2026-10-05: *"and remember staging now includeds
        # pushes to the mod only repo"* -- so this is part of publication rather than something
        # somebody remembers to do afterwards, and a step that is part of publication has to prove
        # it happened the same way the ten-ref cascade does: by reading the refs back.
        #
        # `git push` exiting zero is not the same statement as *the remote holds this commit*. A
        # push can report success having sent nothing when the local branch is behind, and the
        # whole reason `PUBLISHING.md` §5 insists on a read-back is that nobody noticed an
        # eight-ref publish was missing a branch for forty-five checkpoints.
        head = git_out("rev-parse", "HEAD")
        print("")
        print("  export HEAD              : %s" % (head[:7] if head else "unknown"))
        level = 0
        for name, _ in REMOTES:
            listed = git_out("ls-remote", "--heads", name, "main")
            at = listed.split()[0] if listed else ""
            ok = bool(head) and at == head
            level += 1 if ok else 0
            print("  %-8s refs/heads/main : %s" % (name, (at[:7] + " ok") if ok else
                                                   ("%s MISMATCH" % (at[:7] or "absent"))))
            if not ok:
                problems.append("%s does not hold the export commit; the mod-only repository is "
                                "not published" % name)
        print("  PUBLIC RECEIPT           : %d of %d remote(s) at the export commit"
              % (level, len(REMOTES)))

        if problems:
            print("")
            print("REFUSED: %d problem(s)" % len(problems))
            for problem in sorted(set(problems)):
                print("  - %s" % problem)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
