# Every surface the game speaks through — 0.10.5-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## The direction

> *"read now.md to continue the work completing the mod, and also real quick did we finish up
> that doc regress work and the later stuff i said about cleaning up text walls for everything
> making them a pleasure to read, lets make sure the docs and informations displays in game are
> proper to backrrooms universe and rimworld gameplay style of all displayed informations of
> varying types to include all."*

Four items. This checkpoint builds the fourth — the in-game half. The first two were
questions, answered with measurements and written into `TODO.md` rather than into a reply that
scrolls away. The third, the document half, is queued behind this one and named there.

---

## The register, checked first

Per the standing LAW, before designing anything.

| Query | Result |
|---|---|
| `register-query.py family interface` | 12 rows. Loading Progress, Character Editor, DragSelect, Dubs Mint Menus, EdB Prepare Carefully, Name Your Entities, NamesGalore, Numbers, Quality Colors, Recipe icons, Show Me Your Hands, Ding On Game Loaded. **None touches the alerts readout, the letter stack, float menus or the message feed.** Nothing applied. |
| `register-query.py find alert` | **One row, 146 — *No Hemogen Farm Medical Alert*.** |
| `register-query.py find letter` | Zero rows. |

Row 146 turned out to be the only genuinely applicable thing in the register, and it applied
in a way that changed the code.

Its review (`research/reviews/mods/2887053053-Dark.NoHemogenFarmMedicalAlert.md`) records the
author's own note about *"a possible small alert-check cost with many prisoners"*. That mod
exists to suppress **one** Core alert, and even it warns about the per-check cost of the
alerts readout. Core calls `GetReport()` on a rotating one-in-twenty-four schedule, so three
new alerts each doing their own building sweep would be three sweeps forever.

That produced `GateAlertScan`, below: at most one building sweep per game tick no matter how
many alerts ask. **A real register finding that changed a design, not a box ticked.**

Also worth recording: that mod achieves its filtering with Harmony. This one adds to the
readout with neither Harmony nor a def, because adding is a supported extension point and
removing is not.

---

## What was actually wrong

RimWorld does not have one voice for displayed text. It has **a different convention per
surface**, and it is consistent about them to a degree that is easy to violate without
noticing. Core's own keyed files are organised by surface — `Alerts.xml`, `Letters.xml`,
`Messages.xml`, `FloatMenu.xml`, `GameplayCommands.xml`, `Designators.xml`. Ours are organised
by system, which is normal for a mod and is not the problem. Losing the conventions along the
way is.

Measured over Core 1.6's English keyed strings by `.local/register/measure-core-surfaces.py`:

| Surface | n | median | p90 | max | ends with punctuation |
|---|---|---|---|---|---|
| Message | 363 | 42 | 88 | 156 | 85% |
| FloatMenu option | 290 | 19 | 38 | 76 | **7%** |
| Letter label | 74 | 15 | 24 | 45 | 2% |
| Letter body | 264 | 62 | 198 | 666 | 62% |
| Alert label | 77 | 21 | 87 | 363 | 14% |
| Alert explanation | 60 | 141 | 298 | 372 | 70% |
| Command label | 188 | 15 | 52 | 162 | 28% |
| Explanatory `*Desc` | 430 | 70 | 178 | 894 | **93%** |

Two of those numbers carry it. A **float menu row ends with a full stop 7% of the time** — it
is a thing a player picks. An **explanatory tooltip does 93% of the time** — it is prose.
Writing either in the other's register is the specific mistake.

Six of our strings were written in the wrong register:

| Key | Was | Now |
|---|---|---|
| `RR_GateHistory_Empty` | "This gate has not connected anywhere yet." | "No connections yet" |
| `RR_Supply_NoTiers` | "No catalogue tiers are defined." | "No catalogue tiers open" |
| `RR_Bond_BelowSmallest` | "That is less than the smallest bond denomination." | "Below the smallest bond denomination" |
| `RR_Generation_GateAccessOnly` | "Enter this coordinate through the gate." | "Reachable only through a gate" |
| `RR_Gate_NoKillSwitchCandidates` | 98 characters carrying an instruction | "No power switch on this gate's circuit" |
| `RR_Gate_KillSwitchDesc` | — | gained the instruction the row above lost |

The last pair is the interesting one. The kill-switch row was not merely too long: it was a
**row doing a tooltip's job**. Shortening it would have thrown the instruction away, so the
instruction moved to the surface that exists for instructions. `RR_Bond_BelowSmallest` is used
in three positions — a refusal reason, a `Command.Disable` reason and a float menu row — and
all three want a fragment rather than a sentence, so one rewrite fixed all three.

---

## The surface that was empty

`check-display-style.py` prints a census: every place RimWorld displays text, and how many of
our strings reach each one, **including the ones at zero**. That is the only way to act on
*"to include all"*, and on the first run it came back like this:

    alert-label    alerts readout down the right edge           0   <- this mod displays nothing here
    alert-desc     alert explanation on hover                   0   <- this mod displays nothing here

Every warning this mod had was either a **letter**, which a player can dismiss and then no
longer have, or an **inspect line**, which a player only sees if already looking at that
thing. RimWorld reserves the alerts readout for a thing that is **still wrong right now**, and
it was unused.

### How an alert is added

No def, no asset, no patch operation, no Harmony. Verified by decompiling
`RimWorld.AlertsReadout`:

```csharp
foreach (Type item2 in typeof(Alert).AllLeafSubclasses())
```

A mod joins the readout by subclassing `Alert` and nothing else. `AlertPriority` is
`{ Medium, High, Critical }`; `GetReport()` is abstract and returns `AlertReport.CulpritsAre`
so that clicking the alert jumps the camera to the thing.

### The three

| Alert | Priority | Fires when | The countermeasure |
|---|---|---|---|
| **Recovery overdue** | Critical | `gate.IsAwaitingRecovery` | Bring the gate back up, send a recovery run |
| **Return window closing** | High | `gate.IsEmergency && EmergencyReturnTicksRemaining > 0` | Get everyone to the threshold now |
| **No gate operator** | Medium | a gate is calibrated and **no** gate anywhere has an operator | Assign one |

The first two are a pair: the High one is the warning you can still act on, the Critical one
is what it becomes if you do not. Both read the gate's **own** state rather than recomputing
the condition, so an alert can never disagree with the inspect pane about whether somebody is
stranded.

The third is deliberately **colony-wide rather than per-gate**. Firing on each unassigned gate
would nag a player who runs one gate properly and keeps a second door designated for later,
which is a reasonable thing to do. Being told off for it teaches a player to scroll past the
alerts, and an alert readout that gets scrolled past is worse than one warning fewer. Firing
only when no finished gate anywhere has an operator says something unambiguously true and
unambiguously a problem.

### The cache, which the register asked for

```csharp
if (now == cachedTick && ReferenceEquals(game, cachedGame) && now >= 0) { return Cached; }
```

Keying on the tick alone looks sufficient and is not. Load one save at tick 500000, let an
alert scan, then load a **different** save that also sits at tick 500000: the cache hands back
the first game's components, every one of them despawned. A load always constructs a new
`Game`, so comparing the reference closes it off completely.

---

## The seventh checker

`tools/check-display-style.py`. It classifies each key by **where it is used**, never by its
name — `RR_GateHistory_Empty` could be a message, a tooltip or a float menu row, and only the
C# that passes it says which. Patterns match argument positions (`Messages.Message(`,
`new FloatMenuOption(`, `defaultLabel =`, `ReceiveLetter(`), the two def fields that name
letter keys in XML, and the body of every `CompInspectStringExtra()` override, found by brace
matching rather than by regex so that a lambda inside one does not truncate the scan.

135 of 1,272 keys are classified. The other 1,137 are reached indirectly and the report
**prints that number** rather than implying a coverage it does not have.

### The first run reported seven faults that were not faults

Every one came from measuring a **file** instead of a **surface**:

* Letter bodies were measured from `Letters.xml` alone, giving a maximum of 385. Core's
  incident letters live in `Incidents.xml` and reach **666**. The welcome letter — 474
  characters across four paragraphs, already reflowed in 0.10.4-dev — was reported as longer
  than anything Core writes. It is not.
* Tooltips were measured from `GameplayCommands.xml` alone, giving a maximum of 204. Core's
  explanatory strings across every keyed file reach **894**, p95 at 221 and p99 at 345. Six
  ordinary tooltips were reported for exceeding a ceiling that was never real — one of them by
  four characters.

**The baselines were corrected, not the text.** A rule that would have had somebody trimming
four characters off a good sentence could not justify itself, and a checker that cries wolf is
one people learn to scroll past.

### Sanity-tested in both directions

Per the standing warning that a checker which silently passes everything manufactures
confidence:

| Planted | Result |
|---|---|
| A full stop on the alert label `RR_Alert_NoGateOperator` | **FAIL**, named the key and the 14% |
| The full stop removed from the tooltip `RR_Gate_KillSwitchDesc` | **FAIL**, named the key and the 93% |
| Both reverted | **PASS** |

### One surface is counted and not ruled on

The inspect pane. Core builds inspect lines from stat and need strings scattered across its
keyed files, so there is no clean population to measure against. It is counted — 19 of our
keys reach it — and the report says in words that no rule is applied there. A stated limit is
not a forgotten one.

---

## Receipts

| | |
|---|---|
| Version | 0.10.5-dev |
| Build | 160 C# files, 80 package files, **0 warnings, 0 errors** |
| New source | `src/RimroomsAsyncIndustries/Presentation/RimroomsAlerts.cs` |
| New package file | `1.6/Languages/English/Keyed/RR_Alerts.xml`, added to the allowlist |
| New tool | `tools/check-display-style.py` |
| Checkers | **seven**, all passing |
| New defs | **none** |
| New art, audio or texture | **none** |
| Harmony | **none**, as always |
| Game launched | **no** |

Two live facts were taken from decompiled Core rather than remembered:
`AlertsReadout` discovering alerts through `typeof(Alert).AllLeafSubclasses()`, and
`AlertPriority` having exactly three members.
