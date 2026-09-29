# Who you find down there (0.8.2-dev)

**Baseline:** `30c7054` (0.8.1-dev, 142 C# files, 86 package files).

**This checkpoint — 0.8.2-dev:** **145 C# source files** (three new), **88 approved package files** (two new). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `6CF7DD15383596B41C85A36039CDC1C9F3383147569F13040FE814268CE2901B`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"alla trhings are possible finding random pawns of disappering, findeding dead ones pasycholitc ones lost pawns all kinds of crazy variations as per the lore"*

All six, no shortcuts. This is what the escalation ladder in 0.8.0-dev was built to pace.

| Owner's words | Family | When |
|---|---|---|
| *"random pawns"* | wanderer | arrival, Unsettled+ |
| *"of disappering"* | missing person | arrival, Unsettled+ |
| *"lost pawns"* | survivor | arrival, Unsettled+ |
| *"pasycholitc ones"* | unstable inhabitant, and a pack of them | arrival, Active+ / Hostile |
| *"findeding dead ones"* | three body families | **generation** |
| *"all kinds of crazy variations"* | counts, chances, identities rolled from seed | — |

## The split that makes the ladder's promises true

**Bodies are placed at generation. Living things are placed on arrival.**

A corpse is discoverable content — finding one should not wait on a danger band, and a body does not act. But if *living* inhabitants were baked in at generation, **"a first visit is always quiet" would be a lie the moment somebody walked in**, and a band that rose later would never show. So anything that acts is placed on arrival, against the band as it stands at that moment.

## "Of disappering" lands because the name is one you know

When a coordinate produces a *missing* person, the name it carries is drawn from the branch's own register of people it lost inside a coordinate. **A stranger called nothing in particular is atmosphere; somebody you lost is a story.**

The register is bounded at 24, drops the oldest when full, and **consumes** a name when it is used — so the same colonist is never found twice, which is both better and the only honest reading of "missing".

Losses are recorded by **sampling corpses** on the sweep that already runs, not by hooking death. Same reason the construction echo samples: bounded cost, and it is also correct for a body carried in from elsewhere and left there.

## No new pawn kinds, and that constraint was load-bearing

M2 is currently **deleting** this mod's five legacy `RR_*Staff` PawnKindDefs under the existing-content policy. Authoring new ones here would reopen the exact category being closed.

Every inhabitant generates from a `PawnKindDef` the loaded game already ships, via a **fallback chain** — so a Core-only install and a 274-mod profile both work, and neither needs this mod to know what it has. A family whose kinds are all absent is **skipped rather than substituted**: a wanderer rendered as the wrong kind of person is worse than an empty room.

## Held to rules frozen long before this was written

- **Only `Psychotic` families are hostile, and it is enforced in code**, not trusted in data. A `ConfigErrors` check rejects any hostile family that is not Psychotic, because **a hostile family that does not read as hostile breaks the warning-first rule**.
- **Hostiles get a defend-point lord, not an assault lord.** A player who backs off is not pursued across the whole space — that is what makes withdrawal a real countermeasure rather than a delayed death.
- **Every announced family sends a letter that points at the pawn**, so the warning arrives before the encounter.
- **The ladder's absolute cap of three** clamps hostile counts whatever the defs say.
- **Quiet rooms are never used for people**, so the guaranteed-empty half of a coordinate stays empty of inhabitants too.
- **The threshold room is never used**, so nothing is ever standing between the player and the way back.
- **Nothing here touches gates.** `PortalTraversalPolicy` remains the single chokepoint; an inhabitant may never decide anything about one.

## Bodies carry what they had

A body generated and then **killed**, rather than spawned dead, so it has a real cause, a real age and real belongings. *"Findeding dead ones"* is a discovery, and **a body with nothing on it is a prop rather than a find**. One family is deliberately stripped — an old one, long since picked over.

Corpses are marked odd, so a body found down there is consistent with everything else a coordinate produces and can be sold as odd goods.

## A checker gap closed in the same checkpoint

The integrity checker flagged every letter key as an unresolved def reference. **The package was right and the checker was incomplete** — a def may legitimately name a keyed string. It now loads keyed names and accepts them, verified by planting a genuinely missing key, confirming it still fails, and restoring.

That is the third checker gap this session found by a real change rather than by inspection.

## Not done, and named in `TODO.md`

- **Recruiting a survivor.** They exist, are neutral and can be carried out; a dedicated recovery interaction does not exist yet.
- **Raising an encounter cap as a recorded progression step.**
- **Anomalous events**, as distinct from anomalous rooms and inhabitants.
- **Echoed room shapes**, still outstanding from 0.8.1-dev.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass; the integrity checker's new behaviour sanity-tested by breaking it.
- Compliance: two def/keyed files. **No new PawnKindDef, no new gameplay ThingDef, no asset, no patch operation, no new work type.**

## For the post-completion test phase

Confirming a first visit places no living inhabitant at any depth or wealth; confirming bodies are present from the first visit; confirming hostiles never exceed three; confirming a hostile does not pursue across the space when the player withdraws; confirming letters arrive before contact; confirming no inhabitant is ever in a quiet room or the threshold room; confirming a missing person carries the name of somebody the branch actually lost, once; confirming no inhabitant ever crosses a gate on its own; and confirming a Core-only install still produces every family.
