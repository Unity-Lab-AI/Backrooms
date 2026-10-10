# -*- coding: utf-8 -*-
"""Prepend the 0.12.95-dev entry. CHANGELOG.md has no BOM and must keep none."""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"
HEADING = "# Changelog"

ENTRY = NL.join([
"## 0.12.95-dev - 2026-10-05 - One deploy, no build-repo references, and the dependency lie is out",
"",
"- **ONE PAGES DEPLOY, AND IT IS THE PUBLIC MOD REPOSITORY.** Owner: *\"the only page deploy will be",
"  on the new github mod and wiki and public docs ONLY!!! DO YOU UNDERSTAND!!!!?????\"*, then naming",
"  the supersession itself: *\"but wait there are supper seeding rules that only the mod and public",
"  docs go into the new mod repo as the deployable repo for the wiki\"*.",
"- **It was already the live state, measured not assumed:** Pages on this repository returns **404**",
"  and has never been enabled. **What was wrong was the documents.** `TODO.md`, `NOW.md` and",
"  `PUBLIC_RELEASE_PLAN.md` each still told a reader to switch Pages on here, and one named a",
"  `github.io` address this repository does not serve. **A queue row instructing a forbidden action",
"  is worse than a stale one: somebody does it.**",
"- **So the rule is enforced rather than written down.** `check_only_one_pages_deploy` refuses any",
"  living document that instructs a deploy from this repository or names that address. It allows a",
"  sentence about the public repository and is negation-aware, so a document *recording* the rule",
"  passes while one *instructing* the forbidden action fails. It caught two documents written",
"  earlier in the same session.",
"- **The address rule scans RAW LINES, not stripped prose.** `readable_prose` removes code spans,",
"  which is right for claims -- and `PUBLIC_RELEASE_PLAN.md` was carrying the address **inside a",
"  code span**, in a table saying that is what gets built. A hostname being advertised is a hostname",
"  being advertised whatever punctuation is around it.",
"- **NOTHING WAS DELETED.** Owner: *\"without losing capability and functioning and documentiaons\"*.",
"  `_config.yml`, `_layouts/default.html`, `_includes/nav.html` and `docs/index.html` all stay, and",
"  `build-site.py` and `check-site-generated.py` keep maintaining them. **The exclude list stays as",
"  a guard** -- it is the only thing standing between an accidental Pages switch and the work",
"  ledger. Two renderers of one source is not duplication while the source is single, and it is:",
"  the static renderer **imports** the reading order rather than copying it.",
"- **NOTHING REFERENCES THE BUILD REPOSITORIES ANY MORE.** Owner: *\"nothing should refrence the",
"  build repos anywhere\"* -- and it was live when the rule was given. `docs/wiki/links.md` pointed",
"  its **Repository** and **Issues** rows at the working repository, so the published site sent",
"  every reader who wanted the source, or who wanted to report a bug, to the repository that holds",
"  the work ledger. Re-pointed, and the exporter now refuses any export that references one.",
"- **Matched on repository forms only, never the bare word.** *Backrooms* is the name of the setting",
"  and appears all over the wiki as prose; a rule banning the word would be unusable and would be",
"  scrolled past. So the patterns are owner/repo pairs and hostnames.",
"- **The Links page is reoriented on the Steam Workshop**, per *\"the links we wiull use later are",
"  the stewam mod collection and mod listing in the workshops\"* -- both still pending publication,",
"  with one row for source and issues so a bug report has somewhere to go. A dangling",
"  `../../CHANGELOG.md` link was removed: it escaped the site root and pointed at a file the export",
"  deliberately does not carry.",
"",
"### The dependency lie, out of five documents",
"",
"- **Owner: *\"that needs ficxing because i inaccuratly told u evry mod was required, when that is in",
"  no way the case and needs rectify, with that major major task i told you about\"*.** The **code**",
"  half of that major task shipped at 0.12.86-dev -- `About.xml` declares **zero**",
"  `modDependencies`. **The documents never followed it**, and five were still telling players the",
"  opposite, in the places it does the most damage.",
"- **`docs/wiki/install.md`** had a Requirements table listing all five expansions, the full",
"  collection and **Harmony** as *Required* -- on the one page a player reads to find out what to",
"  install.",
"- **`docs/wiki/mods.md`** was built on the premise end to end: *\"This build is authored against a",
"  specific collection and declares every member of it\"*, with a table of required expansions.",
"- **`About.xml`'s own description** said it *\"declares every member of it as a dependency\"* -- the",
"  text in the mod list itself.",
"- **`README.md`** said *\"RimWorld 1.6, all five expansions, and the collection this build is",
"  authored against. Every requirement is declared.\"*",
"- **`docs/PLAYING.md`** said *\"It declares hard dependencies\"*.",
"- **All five corrected, and the rule is enforced in three places** -- reader-facing documents,",
"  `About.xml`, and the public export -- so it cannot come back quietly.",
"- **The rule was narrowed after scoring one out of four.** Turned loose on reader prose it flagged",
"  *\"Nothing special is required\"* (a denial), a table label and a heading, and caught one real",
"  claim. A finding now needs an assertion phrase, a subject that is actually a mod or an expansion,",
"  and no negator -- and it runs on **paragraphs**, because an assertion lives in prose and a table",
"  cell is a label.",
"- **The negator must be in the SAME CLAUSE, and a comma ends a clause.** `install.md` said *\"This",
"  build declares every one of its requirements, so your mod manager will tell you what is missing",
"  before the game loads rather than failing later\"* -- and a sentence-wide negator test saw",
"  *\"rather than\"*, about failing later, and excused a false claim on the install page. This file",
"  already records the identical defect in `retirement_covers`. **A false negative here is worse",
"  than a false positive: the finding is simply never made.**",
"",
"### Instruments, and five of my own mistakes they caught",
"",
"- **A CHECKER THAT CRASHES WHILE REPORTING CANNOT REPORT.** The Pages rule quotes the offending",
"  sentence; one contained an arrow, and on a cp1252 console `print` raised `UnicodeEncodeError`",
"  **after** finding six real problems and before naming five of them. Findings that are correct and",
"  invisible are the worst outcome an instrument can produce. `say()` replaces what it cannot",
"  encode.",
"- **MY OWN RULE WAS A NO-OP AND A STRENGTHENED CLAIM FOUND IT.** The subject guard held",
"  `re.search(r\"\\\\b\" + subject + ...)` -- a doubled backslash from a shell heredoc, matching a",
"  literal backslash, so `any(...)` was always false and **the whole reader-dependency rule did",
"  nothing**. The repair attempt then wrote a real **backspace character**: invisible in a diff and",
"  equally dead. Then the claim written to guard it used `r\"\\\\b\"` inside a non-raw string, which is",
"  the backspace escape. **One backslash broke one line three times**, so both the fix and the claim",
"  are now assembled from `chr(92)` where no shell and no literal can reach them -- and the rule was",
"  then **proved alive** by planting a false claim into a reader page and watching it refuse.",
"- **Six claims were too weak in one identical way**, every one caught by its plant: asserting that",
"  a **name exists** rather than that it **does something**. One passed because",
"  `PAGES_NEGATORS_UNUSED` contains `PAGES_NEGATORS` as a substring; another because",
"  `def check_reader_dependency_assertions(rel, prose, problems):` contains the call text it was",
"  looking for. **Assert the call, the anchored statement, or the condition -- never the identifier.**",
"- **One plant was testing something the instrument cannot see.** Renaming a constant produces a",
"  runtime `NameError`, which a proof that reads source text will never notice; the plant was",
"  re-aimed at a use site, where a source claim can catch it.",
"- `proof-public-export.py` **79 of 79**, `plant-public-export.py` **44 of 44**. Totals unchanged at",
"  **21 checkers, 58 proofs, 32 plant suites**.",
"- Build 0.12.95-dev, **232 C# files, 103 package files, 0 warnings, 0 errors**. Six rows closed and",
"  archived with `VERBATIM TRANSFER CONFIRMED`; queue **48 open / 20 partial / 38 test / 0",
"  completed**. **No game was launched, and nothing here has been played.**",
"",
])

raw = io.open(PATH, "rb").read()
if raw.startswith(b"\xef\xbb\xbf"):
    print("CHANGELOG.md has a BOM and should not; refusing")
    sys.exit(1)
text = raw.decode("utf-8")
if "0.12.95-dev" in text:
    print("already present; nothing written")
    sys.exit(1)
rest = text[len(HEADING):].lstrip(NL)
io.open(PATH, "wb").write((HEADING + NL + NL + ENTRY + NL + rest).encode("utf-8"))
if io.open(PATH, "rb").read().startswith(b"\xef\xbb\xbf"):
    print("a BOM was added -- ABORT")
    sys.exit(1)
print("prepended %d lines; no BOM added" % ENTRY.count(NL))
