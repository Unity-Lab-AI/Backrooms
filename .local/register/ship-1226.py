# -*- coding: utf-8 -*-
"""Ledger for 0.12.26-dev: the in-game text stops naming things that do not exist."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def sub(rel, old, new):
    s = read(rel)
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    write(rel, s.replace(old, new, 1))


sub('CHANGELOG.md', u'## 0.12.25-dev', u"""## 0.12.26-dev - 2026-09-29 - the in-game text stops naming things that do not exist

- **Fourteen pieces of in-game text told you to use equipment this mod no longer has.** The objectives panel, the contract terms, three room clues and the what-to-do-next readouts were all naming a return beacon, a survey tag, a sealed evidence case or a field recorder - gear retired between four and fifteen checkpoints ago.
- **They now name what the game actually gives you:** the record book you carry, glow pods designated as numbered route markers, and the shelf designated as your records archive.
- **Two of those are different instructions, not different words.** Custody is a place now, so a crew brings the book home to a shelf rather than returning it inside a case. And a marker is still numbered - the numbering survived the tag.
- **Three dead labels were removed** - text describing two fixtures that stopped existing long ago.
- **A check now refuses to ship text that names retired equipment**, so this cannot come back.

Full record: [the in-game text stops naming things that do not exist](docs/implementation/RETIRED_VOCABULARY_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.25-dev""")

sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the in-game text stops naming things that do not exist (0.12.26-dev)

**Verbatim user quote:** *"read now.md to continue the working count of the remain doable work of the build whicvh shall be ALL build work completed 100% no exceptions!!! perfectly and masterfully for exactly how Rimworld requires it in order to work. and we need to make sure we are refrenceing the lore and prep when building out all the content and ingame information and items and benches and quests and all of that that might need updated per the guidace on the mods in the columns of the mod registar"*

### What shipped

Fourteen pieces of player-facing text corrected, three dead keys deleted, and the **tenth checker** so it cannot rot again.

### Files touched

`tools/check-retired-content.py` **new**, `tools/retired-vocabulary.json` **new**, five Keyed XML files, `1.6/Defs/ThingDefs_Items/RR_FieldEquipment.xml`, `1.6/Defs/RimroomsProjectDefs/RR_CompanyProjects.xml`, `docs/implementation/historical-content/0.9.9-dev/**` **new archive**, `docs/implementation/historical-content/0.12.24-dev/**` **new archive**, `docs/implementation/RETIRED_VOCABULARY_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **THIS IS THE WORST KIND OF STALE.** A stale document misleads somebody reading the repository; a stale tutorial string tells a **player** to go and do something the game will not let them do. The objectives panel, the contract terms, three room clues and the what-to-do-next readouts were naming a **return beacon** (retired 0.9.9-dev), a **survey tag** (0.10.7-dev), a **sealed evidence case** (0.10.9-dev), a **field recorder** (0.12.24-dev) and a **route recording** (legacy only).
- **Nothing caught it, and the reason is exact.** `check-keyed-strings.py` verifies that every key **resolves** and that every used key **exists**. Both were true. The text was well-formed, translated, referenced, and wrong.
- **I found nine by eye. The check found fourteen, then two more.** The five I missed were all `route recording` mentions, which I had not thought to look for because the phrase still *sounds* current. The last two came out of def descriptions: `RR_RouteRecording` still said *"return it with the field evidence case"*, and `RR_GateTelemetry`, a live research project, described *"Compare recovered route recordings"*.
- **MY FIRST VERSION OF THE CHECK WOULD HAVE PASSED WHILE THE DEFECT SAT IN A RESEARCH PROJECT.** Its def-block pattern listed Core def types and **not this mod's own namespaced ones**, so it was blind to `RimroomsProjectDef`, `RimroomsRequestDef` and the procurement catalogue - most of what this mod actually authors.
- **The rule is derived, not listed.** Invariant 214: a checker holding four names is stale the next time something is retired, which is the failure it exists to prevent. **Retired** = a def labelled in `historical-content/` that the package no longer declares, which maintains itself because invariant 37 already requires archiving. **Superseded but loadable** = a live item def that is untradeable, unbuilt and ungranted - which catches `RR_FieldRecorder` with no rule naming it, because that is exactly how it was retired.
- **THE ARCHIVE HAD A HOLE, SO THE ARCHIVE WAS REPAIRED FIRST.** `RR_ReturnBeacon` was retired at 0.9.9-dev and **never archived** - an invariant 37 breach sitting in history - which meant the derivation missed the very item whose stale text started this. Recovered from `578df5d^` and archived; derived retired defs went from **12 to 15**. **A derived list is only as complete as what it derives from**, and it would have been quietly partial and passed.
- **The one judgement that cannot be derived is whether the CONCEPT survived the item.** A pure phrase rule produced **25 hits, most of them false positives**: *"emergency return cutoff"* is retired but an emergency return is a live mechanic; *"legacy field analysis bench"* is retired but the analysis bench is live; *"gate control console"* is retired but a gate console is live. So `tools/retired-vocabulary.json` holds **decisions with reasons**, and the check enforces the shape around them - every derived phrase must be dispositioned (**a new retirement fails the build until somebody says whether its words survived it**), every disposition must carry a reason, every `stale` phrase must appear nowhere player-facing, and **every entry must still be derived so the file cannot rot either.**
- **A def may name itself.** `RR_FieldRecorder` is labelled *"field recorder and radio"* and has to be able to say so; what it may not do is instruct somebody to use some *other* retired thing.
- **Two substitutions are not rewords.** Custody is a **place** now, so *"return it with the evidence case"* became *"bring it to the shelf designated as the records archive"* - the player does something different. And **a marker is still numbered**: `CompRimroomsMarker.Number` is live, so *"numbered tag"* became *"numbered marker"*, never nothing.
- **Replacement vocabulary was taken from strings already shipped**, not invented. `RR_Event_CorridorUnmarked` was already the modern voice for the same situation `RR_Event_CorridorMismatch` was describing in retired words.
- **Three keys were simply dead.** `RR_Generation_ClimateUnitLabel`, `RR_Generation_FluorescentLabel` and `RR_Generation_FluorescentDescription` labelled two long-retired fixtures and grep confirms nothing references them. Deleted rather than reworded: nothing is left for them to describe.
- **Fault-planted four ways, caught 4 of 4**, including both directions the data can rot: a derived phrase with no disposition, and a disposition no longer derived from any label.
- Build 0.12.26-dev, **174 C# files, 86 package files**, **0 warnings, 0 errors**, **no C# changed**. Assembly `0E265705F23D1CC907E25CF48C767B5548ED99F8EB3588FD992DD9488DD68EA5`, identical across two clean rebuilds. **TEN checkers** pass, twenty-three proofs exit zero. **No game was launched, so nobody has read one of these strings on a screen.**

---

## Completed sessions""")

print('ledger written for 0.12.26-dev')
