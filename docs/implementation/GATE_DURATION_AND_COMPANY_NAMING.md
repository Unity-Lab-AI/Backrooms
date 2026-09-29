# Gate duration ladder and company naming — four owner decisions implemented (0.5.4-dev)

**Baseline:** `1dc71a7` (0.5.3-dev, 93 C# files, 76 package files).

**This checkpoint — 0.5.4-dev:** **94 C# source files**, **76 approved package files**, zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `FA88C94730F13AB09CD49F52C5C1A39236D640BADC2533C6D4DE51209A17F3F9`. Evidence: [`evidence/gate-duration-and-naming-2026-09-28/`](evidence/gate-duration-and-naming-2026-09-28/), reference manifests recomputed, no drift.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The decisions, verbatim

Four questions were put to the owner. All four are answered and implemented; two of them had been sitting as owner-blocked rows since Gate 0.

> on gate duration question you should have the first opening be like 30 minutes of real time not game time there has to be time to acually do shit and it only greatly increases from there once u can re call seeds and better tech and levels to being able to open it indefintality at higherr tech and research and staff and power supplies

> but remember natural portals like in the not corporation secerio stay open indefinately as the player doesnt have a way to build a lab portal of their own yet

> hold up every scerio gets the same tech tree to research so each scernioro will be able to build a full corporation if they want

> and name it their own

Plus, from the multiple-choice round: **keep building and launch later** (no QA pass yet), **finish construction next via travel-to-work**, and for the inside start **configurable party, player chooses the exit**.

---

## 1. The laboratory duration ladder

### What was wrong

The recorded opening window was **833 ticks** — about fourteen real seconds at normal speed, or twenty in-game minutes. A previous agent had flagged it as unresolved and recorded it as a usability risk. It was worse than a usability risk: a colonist crossing a gate, walking to an object, picking it up, walking back, crossing again and delivering cannot happen in fourteen seconds. Every cross-map work family shipped in 0.5.0-dev through 0.5.3-dev would have been effectively unusable on a laboratory gate.

### What it is now

| | Ticks | ≈ real time at normal speed | ≈ in-game time |
|---|---|---|---|
| Tier 0 — first opening | **108,000** | ~30 minutes | ~1.8 days |
| Tier 1 | 324,000 | ~90 minutes | ~5.4 days |
| Tier 2 | 972,000 | ~4.5 hours | ~16 days |
| Tier *n* ≥ `portalIndefiniteTier` | **no countdown** | held while supported | — |

The base is 108,000 ticks because thirty real minutes at normal speed is 30 × 60 × 60 ticks. Each earned tier multiplies by three, so advancement increases duration sharply rather than incrementally, which is what "greatly increases from there" asks for.

### What drives a tier, and the trap avoided

Tier is the count of **completed** company projects named in `portalWindowTierProjects`.

It is deliberately *not* `researchInsights`. Insight is a spendable currency — `InvestigationServices` decrements it when a project is committed. Gating duration on it would mean **spending research to advance shrank your gate**, which is exactly backwards. Completed projects only ever accumulate, so a tier once earned cannot be lost.

### "Indefinite" means "while supported", not "free"

At and above `portalIndefiniteTier` the countdown stops, but nothing else relaxes. The tick still requires, every tick:

- power and headroom — losing it enters emergency, as before;
- the operator on station — losing them enters emergency, as before;
- the energy debit to succeed — running the supply dry enters emergency, exactly as losing power does.

That last one is what makes the word honest. A sustained 3,500 W draw needs real sustained generation behind it; one Core `GeothermalGenerator` at 3,600 W covers it, batteries alone will not. So "higher tech **and research and staff and power supplies**" is enforced by the machine rather than asserted in a description.

### The ladder is content, not code

`portalWindowTierProjects` defaults to the one company project that currently exists (`RR_GateTelemetry`). The research tree of tiers T0–T6 across nine branches is M3 work and does not exist yet, so **the top of the ladder is currently unreachable**: with one rung, the highest attainable tier is 1, giving ~90 real minutes. That is stated plainly rather than implied, and it is a content gap with a named owner — when the tree lands, its projects are appended to the def list and the ladder grows with no code change.

### Legacy behaviour untouched

`openingWindowTicks` is still 833 and still the window legacy expeditions run on. Nothing about the historical expedition path changed. Only portal sessions use the ladder, which keeps the project rule that legacy behaviour is never altered.

## 2. Natural gates were already right

The owner's reminder — that natural portals in the non-corporation scenarios stay open indefinitely, because the player has no way to build a laboratory gate yet — describes what the source already does, and this was verified rather than assumed:

- `RimroomsPortalNetwork.Availability` consults the gate window **only** for `PortalConnectionKind.Laboratory`. The natural branch is explicitly commented as having "no timeout, gate operator, mission completion, battery or close command dependency".
- A natural connection has no machine, no designated operator and no energy draw, so none of the tick logic above can touch it.

So the ladder is a laboratory-gate feature exclusively, and the starts that begin with only a natural gate are unaffected. No change was needed and none was made.

## 3. One tech tree for every scenario

The owner's clarification that every scenario researches the same tree and can build a full company is satisfied by construction rather than by a special case:

- The duration tier reads `campaign.Projects`, which is **per branch**, never per scenario. No scenario id is consulted anywhere in the ladder.
- The gate comp is patched onto Core's `Door` and `Autodoor`, which every start has access to.

So a lone-survivor or store start that researches the projects and builds a designated laboratory gate climbs the identical ladder. **This is now a binding constraint**: no research, project or duration rule may be gated on scenario identity, and M3's research tree must be authored as one tree available to all starts.

## 4. Every company is named by its player

There was no company name anywhere in the project — the corporate identity was implicit in the scenario. Since every start can now build a full company, every start names its own.

| Layer | What was added |
|---|---|
| `RimroomsStartDef` | `defaultCompanyName`, a per-scenario *suggestion* only |
| `Page_RimroomsCompanySetup` | a text field, pre-filled with the suggestion, editable on every start |
| `RimroomsStartupComponent` | carries the typed name through setup, saved, normalised |
| `BranchStartRequest` → `InitializeBranch` | accepts it; a rejected name is never fatal |
| `RimroomsCampaignComponent` | owns `companyName`, implements Core's `IRenameable` |
| `Dialog_RenameCompany` | subclasses Core's own `Verse.Dialog_Rename<T>` |
| Operations | the name on every pane, with a rename button |

The company renames through **the game's own rename dialog**, the same one zones, storage groups and caravans use, rather than a bespoke window. Validation is bounded at 64 characters and a blank entry is refused rather than silently clearing the name, so the company always has something to be called. `Async Industries` survives as the corporate start's suggested default, not as a hardcoded identity.

## 5. The inside-start decisions, resolved

Two rows that had been `[!]` owner-blocked since Gate 0 are now decided:

- **Party:** configurable — the player chooses solo or a small group. Unchanged from the provisional assumption.
- **First exit:** **the player chooses the destination settlement.** This *changes* the provisional assumption, which was a fixed discovered destination. Scenario work in M3 must implement a choice, not a reveal.

Both rows move from owner-blocked to decided in the register and the decision log.

## Saved state

| Owner | Key | Rule |
|---|---|---|
| `RimroomsCampaignComponent` | `rr_companyName` | Additive, no schema bump. A save from before naming loads with no name and falls back to a neutral label until renamed. |
| `RimroomsStartupComponent` | `rr_startupCompanyName` | Additive on the setup receipt. |

No existing key changed meaning. The duration ladder introduces **no saved state at all**: it is computed from the props and the branch's completed projects, so it cannot desync and an existing save picks up the new behaviour on load. A 0.5.3-dev save loads unchanged.

## Not done, and named

- **The remaining ladder rungs.** Only one company project exists, so the indefinite tier is unreachable until M3's research tree supplies more. Content gap with a named owner, recorded in the register.
- **Travel-to-work intents**, which is the owner's chosen next build and what construction *finishing* needs.
- The M3 scenario work that will consume the inside-start decisions.

## Owner-launched acceptance, deferred

Opening a laboratory gate at tier 0 and confirming the readout shows roughly thirty real minutes; completing `RR_GateTelemetry` and confirming the next opening is about three times longer; confirming a natural gate shows no countdown and ignores operator and power entirely; cutting power, pulling the operator, and letting the energy reserve run dry during a sustained session, each confirming an emergency rather than a silent close; naming a company at setup on each start and confirming the name appears in Operations and survives a save and reload; renaming through the dialog and confirming the activity feed records it; and confirming a blank or 65-character name is refused.
