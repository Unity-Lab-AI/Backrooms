# -*- coding: utf-8 -*-
"""Ledger for 0.12.24-dev: the recorder became the book.

Written as a file rather than piped through a heredoc because that has now broken on an
apostrophe eleven times in this project. The gotcha is recorded; reaching for the heredoc
anyway is the part that keeps repeating.
"""
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


# ---------------------------------------------------------------- CHANGELOG
sub('CHANGELOG.md', u'## 0.12.23-dev', u"""## 0.12.24-dev - 2026-09-29 - the recorder became the book

- **Field crews now write straight into the record book they carry.** The separate field recorder is gone from every start and can no longer be built or bought. One item does both jobs, so the record and the thing that made it can no longer get separated.
- **Nothing in your save breaks.** A recorder you already own still loads, still weighs the same, and can still be recovered from a coordinate. It is simply never issued again.
- **The company now sells blank record books.** Books burn, and the base game only sells them to you by chance, so a branch that loses its book can order more instead of being unable to send anyone out.
- **Surveying and recording now follow the same rule:** somebody on the crew has to be carrying the book. Before, a book left on the floor still counted for one of the two.
- **Losing the book is now the thing that stops a survey**, rather than losing a second piece of equipment nobody could see the point of.

Full record: [the recorder became the book](docs/implementation/RECORD_BOOK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.23-dev""")

# ---------------------------------------------------------------- FINALIZED
sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the recorder became the book (0.12.24-dev)

**Verbatim user quote:** *"read now.md to continue the working count of the remain doable work of the build whicvh shall be ALL build work completed 100% no exceptions!!! perfectly and masterfully for exactly how Rimworld requires it in order to work. and we need to make sure we are refrenceing the lore and prep when building out all the content and ingame information and items and benches and quests and all of that that might need updated per the guidace on the mods in the columns of the mod registar"*

**Owner decision carried out, verbatim:** *"Fold it into the record book crews already carry"*

### What shipped

`RR_FieldRecorder` job folded into Core `TextBook`, which closes the def half of invariant 10 and the last of the four field-gear replacements. Plus the two register queries that made the guidance readable at all.

### Files touched

`tools/register-query.py`, `src/.../Expedition/ExpeditionCargo.cs`, `src/.../Threats/FirstSliceSiteComponent.cs`, `src/.../Company/EvidenceObservations.cs`, `1.6/Defs/ThingDefs_Items/RR_FieldEquipment.xml`, `1.6/Defs/ScenarioDefs/RR_Scenarios.xml`, `1.6/Defs/RimroomsProcurementCatalogDefs/RR_ProcurementCatalog.xml`, `1.6/Languages/English/Keyed/RR_Expedition.xml`, `1.6/Defs/RecipeDefs/RR_FieldEquipmentRecipes.xml` **deleted**, `tools/package-files.json`, `.local/register/proof-record-book.py` **new**, `docs/implementation/RECORD_BOOK_IMPLEMENTATION.md` **new**, `EXISTING_CONTENT_REPLACEMENT_MAP.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `SCENARIOS.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **THE ANSWER HAD BEEN WRITTEN DOWN FOURTEEN CHECKPOINTS EARLIER.** The 0.9.9-dev plan table of four answers already said *"**Field recorder** | **the book** | One Core `TextBook`: carried in blank, written in the field, carried home as the evidence. The recorder and the record stop being two things that can get separated."* Three of the four shipped - beacon 0.9.9, survey tag 0.10.7, sealed case 0.10.9 - and the recorder sat with its answer already recorded. **No proof mentioned it, which is exactly how a decided piece of work stays undone while every sweep stays green.**
- **THE REGISTER GUIDANCE WAS UNREACHABLE FROM ITS OWN TOOL.** `register-query.py row 4` printed `card : open card`, which is a hyperlink label. Every real instruction - Planned Use, Integration Approach, Compatibility Watch, FinalDisposition - lives in the register `#cards` section and in **294 review records on disk**, and the tool read none of it. **A LAW that points at a document its own tool cannot open is a LAW satisfied by reading four short columns and calling it consulted.** Added `card <id|text>` (one mod full card, and whether the review record it names is actually on disk) and **`use <trace>`** (for every mod bearing on the feature being built, how this mod is supposed to use it - the question the LAW actually asks).
- **Three register instructions applied, and all three supported the design.** [26] Adaptive Simple Storage: *"Keep custody and evidence records separate from the containers"* - the record is a carried book, no container owns it. The materials and cargo family: *"Preserve each mod normal material and weight behavior"* - the loadout reads mass off the item, and a Core book weighs **0.50** where our recorder declared **1.6**. [4] Core: *"do not make a DLC feature the sole route through the campaign"* - `TextBook` is Core. A register search for `book` returns **zero rows**, so nothing in the 294 is recorded as touching Core books.
- **The kit is resolved, never named.** `KitDefs`/`KitCounts` - two parallel arrays, with a comment on them warning that arrays disagreeing about their own length are a bug waiting to happen - are gone. The kit comes from `CompRouteEvidence.NativeCarrierDef`, which is strict where a def name is not: Core own book, a `Book` subclass, **exactly one** of our comps, `CompBook` and `CompQuality`. **And it can return null, so both callers refuse visibly** - a silent null would make the kit check pass for a crew carrying nothing, the same failure shape as `Named<TerrainDef>("Carpet")`.
- **Two gates that had never agreed now ask one question.** Surveying needed the recorder **in an inventory**; recording an observation needed the book **anywhere on the map**. Both now require the book in a crew member inventory. A book on the floor two rooms back is not being written in.
- **The observation was crediting the wrong object.** `TryFindFieldRecorder` hunted for a **second** object when the caller had already established `record.item` is a bound route-evidence book held on this map. It now credits the record itself. **Saved field names untouched** - `recorder`, `recorderLoadId`, `recorderCarrier`, `recorderCarrierName` are what old saves contain, and renaming a saved field is a save break for a cosmetic gain.
- **NO SAVE BREAK.** The def still loads, still weighs 1.6, still recovers from a failed site, and `FailedSiteRecovery` deliberately keeps naming it. Retirement is achieved entirely by removing every way to **get** one: recipe retired with its whole file (the abstract base had no other child), both scenario grants now `TextBook`, `tradeability` `None` overriding `ResourceBase` `Buyable`, and a description that says plainly it is superseded. Recipe retirement follows precedent set three times here already.
- **THE REPLACEMENT WOULD HAVE CREATED A DEAD END.** Core gives books `Flammability 1` and `DeteriorationRate 5`, and sells `TextBook` only as random outlander stock at nought to two a visit. A branch whose only book burned would have failed every future dispatch for ever. **This was not in the row, the plan, or the owner answer** - it came out of reading what Core actually does with the object. `RR_Procurement_RecordBooks` fixes it, priced the way glow pods are priced and for the same reason: the company is buying its own paperwork.
- **The build caught my own XML.** An em-dash habit put a double hyphen inside an XML comment, which is illegal, and `BuildCommon.ps1` refused the file before the compiler saw it. **That validation is not one of the nine checkers** - it is the build own XML parse.
- **Twenty-second proof, 28 claims, fault-planted four ways and caught 4 of 4**: a start granting a recorder again, the recipe coming back, tradeability restored, and the site tick name-matching an item again. Comments are stripped before every source claim, because this change is documented at length in the files it changes and those comments name the def repeatedly while explaining why nothing reads it.
- Build 0.12.24-dev, **174 C# files, 86 package files**, **0 warnings, 0 errors**. Assembly `B382E45C0ADF918FFF8BBAAC643C88DAB1B7CF8F0E9CDA74D60ABB22617030BE`, identical across **three** clean rebuilds. Nine checkers pass, **twenty-two** proofs exit zero. **No game was launched, so every claim is structural and nobody has ever carried one of these books anywhere.**

---

## Completed sessions""")

# ---------------------------------------------------------------- ARCHITECTURE: the Open row
sub('docs/ARCHITECTURE.md',
    u'`RR_FieldRecorder`/`RR_SurveyTag`/`RR_ReturnBeacon`/`RR_SealedEvidenceCase` (no portable Core '
    u'equivalents; `MedicineIndustrial` explicitly unsafe), `RR_RouteRecording` (→ `TextBook`/`Schematic`), '
    u'`RR_ReturnAnchor` (→ `Door`), `RR_QuietPursuer` (→ `Megascarab` reskin or removal), '
    u'five `RR_*Staff` PawnKinds (→ `Colonist`, already used by new starts), five recipes',
    u'**all four field items CLOSED** — `RR_ReturnBeacon` retired 0.9.9-dev, `RR_SurveyTag` → '
    u'`GlowPod` 0.10.7-dev, `RR_SealedEvidenceCase` → designated `Shelf` 0.10.9-dev, '
    u'`RR_FieldRecorder` → Core `TextBook` 0.12.24-dev (**def kept loadable, never granted again**); '
    u'`RR_RouteRecording` **superseded** by `CompRouteEvidence.NativeCarrierDef` resolving `TextBook`, '
    u'kept only so old saves load; `RR_ReturnAnchor` **kept** — generator-placed infrastructure, which '
    u'invariant 10 permits; `RR_QuietPursuer` → Core `Things/Mote/Black` 0.12.22-dev (**the '
    u'`Megascarab` reskin was declined**: an insect where a figure belongs); five `RR_*Staff` PawnKinds '
    u'**wired** as the clean-up team relief crew 0.11.7-dev; **one recipe left of five**, '
    u'`RR_AssembleMachineGate`, live and kept')

# ---------------------------------------------------------------- ROADMAP
sub('docs/ROADMAP.md',
    u'**Still custom:** three field items (`RR_FieldRecorder`, `RR_SurveyTag`, `RR_SealedEvidenceCase`) '
    u'plus `RR_RouteRecording`, `RR_ReturnAnchor`, the `RR_QuietPursuer` presentation, five `RR_*Staff` '
    u'PawnKinds and the remaining gameplay PNGs. Replacements are decided and recorded in `TODO.md`: the '
    u'survey tag becomes a Core `GlowPod`, the recorder merges into the evidence book, and custody '
    u'completes at a designated Core `Shelf`.',
    u'**Nothing is still custom that invariant 10 forbids, as of 0.12.24-dev.** Every replacement named '
    u'here was decided, then built: the survey tag became a Core `GlowPod` (0.10.7-dev), custody '
    u'completes at a designated Core `Shelf` (0.10.9-dev), the recorder merged into the record book '
    u'(0.12.24-dev), and `RR_QuietPursuer` presents as Core `Things/Mote/Black` (0.12.22-dev). '
    u'**Zero gameplay art or audio ships.** What remains authored is what the invariant permits: '
    u'mechanics defs, a generator-placed marker, `FactionDef`s, and the `RR_FieldRecorder` def itself '
    u'— **kept loadable on purpose** so saves containing one still open, and never granted or sold again.')

# ---------------------------------------------------------------- SCENARIOS: the solo kit
sub('docs/SCENARIOS.md',
    u'Start with five meals, two medical supplies, a field recorder, a light source, a basic repair '
    u'tool, a short-range radio with one damaged battery, and one clearly marked personal item.',
    u'Start with five meals, two medical supplies, **a blank record book** (Core `TextBook` — the '
    u'field recorder folded into it at 0.12.24-dev, so the thing you write in is the thing that '
    u'remembers), a light source, a basic repair tool, a short-range radio with one damaged battery, '
    u'and one clearly marked personal item.')

print('ledger written for 0.12.24-dev')
