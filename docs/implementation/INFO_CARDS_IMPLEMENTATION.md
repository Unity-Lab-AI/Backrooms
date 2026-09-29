# Everything you can look at says what it is (0.9.3-dev)

**Baseline:** `55fbe31` (0.9.2-dev, 156 C# files, 79 package files).

**This checkpoint — 0.9.3-dev:** **156 C# source files**, **79 approved package files**, **a fifth checker**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `BF66AC9770AC85F7A6471E95BD7DFB9DC2B2F30A8603B33DBA4786C3DAB26220`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"we also need to be making sure all mod ingame decriptions and informational informations for everything is properly in the cards like the game does currently"*

## "like the game does currently" is measurable, so it was measured

The tempting reading is *put a description on everything*. That would have been wrong, and the way to know is to count what RimWorld actually does across its own defs:

| Type | label | description |
|---|---|---|
| `WorkGiverDef` | 97% | **0%** |
| `ThoughtDef` | 0% | **0%** — its text lives in stages |
| `PawnKindDef` | 91% | **0%** |
| `TraderKindDef` | 87% | **0%** |
| `ThingCategoryDef` | 100% | **0%** |
| `JobDef` | 0% | 0% — the player reads `reportString` |
| `RecipeDef` | 100% | **100%** |
| `ThingDef` | 89% | 75% |
| `ScenarioDef` | 100% | 80% |
| `WorldObjectDef` | 100% | 80% |
| `MainButtonDef` | 100% | 92% |

**Core never describes a work giver, pawn kind, trader kind or thing category.** The first draft of the checker demanded one everywhere and reported **94 problems, 67 of them work givers** — which would have produced sixty-seven lines of text no player is ever shown. Matching the game meant writing *fewer* descriptions, in the right places.

After calibration: **17 real problems**, and every one of them genuine.

## Our own defs are held higher, because we render them

Core's rules are about Core's UI. Our def types appear in *our* windows, and there a bare noun is all a player gets.

So every `RimroomsAsyncIndustries.*Def` must carry a description — **and this checkpoint had to render them too**, because a description nothing displays is just text in a file. Before this, exactly one of our def types (`RimroomsProjectDef`) had its description shown anywhere.

- **The facilities overview** now explains what the chosen category is for and what goes wrong for a branch without it.
- **The procurement list** now says what a thing is actually *for*. Price and lead time were already on the row; what no number can say is why you would want it.

Nine facility categories and seven catalogue entries were written.

## One exemption, with its reason

`RimroomsStartDef` is exempt: it is branch setup data, and the `ScenarioDef` beside it is what a player reads at the scenario picker. Duplicating that text would show nobody anything. Every exemption in the checker carries a stated reason, because "it was missing so it must be fine" is how a rule quietly stops meaning anything.

## The checker caught itself failing, twice

**First**, a planted blank description was caught but a planted `TODO Structural steel…` **passed clean**. The placeholder test only matched a *whole* string, so a description that merely opened with TODO slipped by. Rule added.

**Second — and this is the one worth recording** — the added rule *still* passed the plant, while the regex tested correctly in isolation.

The cause: writing `\b` through a shell collapsed one escape level too far and put a **literal backspace byte** in the file. The pattern demanded a 0x08 character after the keyword and therefore matched nothing, and it looked right in every listing because a backspace renders as nothing.

**This is precisely the failure the standing warning describes** — every part correct in isolation, the assembly silently doing nothing — and it is the same shape as the unknown-def-field checker that was removed rather than shipped. The difference is that this one was *debugged* instead of abandoned: the word boundary is gone, replaced by a negative lookahead that survives being written through a shell.

Proved in both directions afterwards: exit code 1 with the plant in place, PASS with it removed.

## Five checkers now

`check-info-cards.py` joins the ritual. The checkpoint ritual in `NOW.md` says five.

## Not done, and named in `TODO.md`

- **Inspect-card text for things a player selects** — gates, the station, the beacon. The gate already explains itself in detail; the others have not been audited the same way.
- What a gate's size lets through; hostiles needing width; the adjacent-door-run fallback.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- **All five checkers pass.**
- The new checker was proved by planting three faults: an empty description, a placeholder-only one, and a placeholder-prefixed one. The third found a real bug **in the checker itself**.
- Compliance: **no new def, asset, patch operation or work type.** Sixteen descriptions and two rendering lines.

## For the post-completion test phase

Confirming the facilities overview shows the category explanation when a category is chosen and nothing when "all" is; that the procurement panel shows the selected item's description; that no info card belonging to this mod is blank; and that the thought's stages read correctly in the mood tab.
