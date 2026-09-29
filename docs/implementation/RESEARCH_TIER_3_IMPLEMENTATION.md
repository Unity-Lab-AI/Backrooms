# The third rung of every branch — 0.12.18-dev, 2026-09-29

**Dated record.** Never rewritten. Reverses nothing in `BUILD_ORDER_CORRECTION.md` (0.12.5-dev) —
it is what that record said would eventually become possible.

---

## The register, checked first — because it was skipped first

The owner caught this mid-build:

> *"make sure you are use the prep docs and mod register as a guide in all you build"*

Correct, and the LAW says **before** designing, not after. Done properly:

| Row | Mod | Stance | What it meant |
|---|---|---|---|
| **191** | ResearchTree (Eheieh Version) | **Settled** | replaces the research **tree UI**, operating on `ResearchProjectDef` |
| **279** | Research Whatever | Optional | removes research prerequisites, on `ResearchProjectDef` |
| **76** | Do Your F\*\*\*\*\*\* Research | Configuration only | gates research by pawn skill |
| **123 / 129** | Mad Skills / Misc. Training | Optional | make skill thresholds easier to reach |

**Our company projects are `RimroomsProjectDef`, a separate type.** Neither 191 nor 279 can see
them, which is the same structural reason this mod never collided with the native quest system.
Row 76's idea is already ours — these require `minimumIntellectual` 6 — and 123/129 make that
threshold easier rather than harder, so the requirement is not a wall for players running them.

---

## Why this tier was deleted before it was written

At 0.12.5-dev the knob sweep found **nothing to move** for four of seven branches, and four
projects were **deleted rather than shipped**. That was right. The systems a tier-3 unlock would
modify did not exist.

**Arc 5 wrote them** — remote sites on the books and billed daily (0.12.6), company-to-site
logistics (0.12.7), staffing (0.12.8), a gate at a site (0.12.9). So the sweep was run again, and
this time it found a real, observable read site for **all seven** branches:

| Branch | Knob | What a player watches change |
|---|---|---|
| Facilities | `MaximumRemoteSites` 8 → **12** | the Sites pane reads *"3 of 12"*; `RR_Site_TooMany` stops |
| Commerce | overhead divisor 4 → **6** | the Sites pane's daily figure drops |
| Logistics | `CanUnloadAt` staffing bypass | a shipment is **left** at a site with nobody there |
| Spatial | `FrontierRarity` 12 → **8** | a way onward turns up sooner |
| Fieldcraft | `EmergenceShare` 3 → **2** | a way **out to the world** comes up more often |
| Measurement | `SurveyTicks` 600 → **420** | the survey progress bar is visibly shorter |
| Entities | `BestShelterRate` 0.20 → **0.12** | a built room holds the place back better |

### The two branches that looked empty had the best knobs

An hour before this checkpoint my own survey said **five of seven** and named Fieldcraft and
Entities as having nothing. Reading the code rather than the summary changed both:

- **`EmergenceShare` belongs to Fieldcraft, not Spatial.** How often a survey produces a way *out
  to the world* rather than a way deeper is not about reading a space — it is about **coming back
  out of one**, which is the same subject as the return drill and the relief watch.
- **`BestShelterRate` belongs to Entities.** Knowing what is in a space changes how a room is built
  against it: sightlines, thresholds, what is left in the open.

Neither was invented. Both were sitting in the code with real read sites.

---

## Two restraints kept, and both asserted

### The per-coordinate frontier cap is not a research knob

`MaximumFrontiersPerCoordinate`'s own summary says it plainly:

> *Raising this is a design decision, not a tuning knob; the cap is what keeps a chain of spaces
> finite.*

So Spatial's unlock moves **rarity**, making the two a branch may find arrive **sooner**. It never
makes them three. The proof asserts the `Cap` assignment is the bare constant and that **no second
per-coordinate cap constant exists to switch to**.

### Shelter never reaches zero

`BestShelterRate`'s summary is equally clear: *never zero — a coordinate is always wearing, just
slowly, so a player cannot build a room that makes the place ordinary.* `DisciplinedShelterRate` is
**0.12**, and the proof asserts it is above zero and that the interpolation still runs toward a
floor rather than removing one.

**A restraint is only a restraint if breaking it fails.** Both were fault-planted.

---

## My own first version of the cap restraint was wrong

It searched for the capability name **within 400 characters** of the cap assignment — and broke the
instant the capability-aware **rarity** line was legitimately written directly above it.

**Proximity is not the thing that happens.** That is the same mistake this project has now caught
five times: keyed off a variable's spelling, a refusal string, a nonexistent method name, a grep
phrasing, and now nearness. Rewritten to key off the **assignment itself**.

---

## One number, one source

The site cap had two readers: the service refusal and the Sites pane. Both now go through
`RemoteSiteCap`, so **the number a player is shown and the number that refuses them cannot
disagree** — the same discipline as the gate's `IdlePowerDrawWatts`. `proof-remote-sites.py`
asserts the pane no longer reads the raw constant.

That proof also **failed on the divisor change and was retargeted**, which is the proof working:
the literal moved into `OverheadDivisorInForce` while the property — a ratio of the branch's own
overhead, never an absolute — is unchanged. Two claims were **added**, including that a tier-3
unlock may not swap in a flat discount.

---

## Two of my own errors, corrected not excused

- **The vocabulary checker caught *"doorway"* twice in my descriptions.** This mod says **door**;
  the far-side arrival point is a **threshold**. My text was corrected, not the rule.
- **The heredoc backslash trap, tenth time.** It mangled a regex into a syntax error. The gotcha
  line exists for exactly this and I reached for a heredoc anyway. The count is corrected rather
  than rounded down.

---

## Fault-planted four ways

| Planted fault | Exit | Caught |
|---|---|---|
| the per-coordinate cap becomes a research knob | 1 | ✓ |
| shelter reduced to zero — the Backrooms becomes livable | 1 | ✓ |
| a tier-3 capability read that no project grants | 1 | ✓ |
| a branch left without a tier-3 project | 1 | ✓ |
| *restored* | **0** | — |

---

## Receipts

| | |
|---|---|
| Version | 0.12.18-dev |
| Build | 173 C# files, 91 package files, **0 warnings, 0 errors** |
| Project defs | **32** — tiers 0–3 complete across seven branches, plus four gate projects |
| Branches with a tier-3 project | **7 of 7**, up from a surveyed 3 at 0.12.5-dev |
| Capabilities granted with no read site | **zero**, asserted |
| Design restraints asserted | **2** |
| Checkers | **eight**, all passing |
| Proofs | **nineteen**, all exiting zero |
| Planted faults caught | **4 of 4** |
| Game launched | **no**, and nothing in this mod has ever been played |
