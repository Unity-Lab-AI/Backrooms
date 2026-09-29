# A gate remembers where it has been (0.8.8-dev)

**Baseline:** `63b29f2` (0.8.7-dev, 152 C# files, 91 package files).

**This checkpoint — 0.8.8-dev:** **154 C# source files** (two new), **92 approved package files** (one new keyed file). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `5CFCA1C8EEEF139655B91ED421942FC58B33F683B03F1590F0607810A75C643B`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"we need a proper history list that lab gates are connected have connected to in a easily editable clear able and manage bench connected to the portal gates natural gates dont get to call a seed they are what they are"*

## The list belongs to the gate, not the branch

*"connected to the portal gates"* — so **two gates keep different address books.**

That is the right shape rather than a convenience. A branch running a gate at headquarters and another at an outpost is running **two different operations**, and merging their histories into one branch-wide list would lose the distinction that makes a second gate worth building at all.

## A natural gate has no address book, and that needed no new guard

*"natural gates dont get to call a seed they are what they are"* — a natural gate's destination is fixed at discovery and permanent. It may not dial, so it has nothing to remember.

**The existing architecture already guaranteed this.** Every gate gizmo sits behind `IsDesignated`, which is only ever true of a laboratory gate the player assembled. A natural threshold registers through `RegisterNaturalAddress`, has no gate behind it at all, and never reaches this code.

**Adding a second check would have implied the first one was unreliable.** The rule is enforced in one place and this is one more thing obeying it — the same reasoning that kept survivor recruitment from special-casing a gate.

Recording happens at exactly one point: the success branch of `RegisterLaboratoryAddress`. That is the single moment a laboratory gate dials a coordinate, which is precisely why the natural path cannot reach it.

## Editable, clearable, manageable — and why each verb earns its place

| Verb | Why |
|---|---|
| **Rename** | a coordinate id is not a name a person can navigate by |
| **Pin** | protects an address from eviction *and* from a clear |
| **Remove** | prune one mistake without losing the list |
| **Clear** | *"a history nobody can prune becomes unusable in a long game"* |

**Clear keeps pinned entries, deliberately.** In a long game "clear" means *get rid of the noise*, and a single button that also destroyed the handful of addresses somebody had explicitly marked would be a **trap rather than a convenience**.

The list caps at 32 and evicts the **least recently used unpinned** entry. Pinning is what makes that safe: the addresses a player cares about are the ones they marked, and those are never dropped to make room for somewhere they visited once by accident. If *everything* is pinned, a new address is simply not recorded — better than silently discarding something the player deliberately kept.

Repeat connections **update** an entry rather than appending, which keeps it an address book rather than a log, and the list orders most-recently-used first so it stays useful without anyone sorting it.

## Renaming reuses the game's own dialog

`GateHistoryEntry` implements `IRenameable`, so renaming goes through **RimWorld's own rename window** — the same one used for zones, caravans and storage groups, and already used by this mod for the company name.

`Dialog_Rename<T>` is abstract, so a concrete subclass is required even though it adds nothing. Worth it: the player gets an interaction they already know and there is **no second rename UI to keep consistent with the first**.

A blank name is accepted, unlike the company's, because the label falls back to the coordinate's own. **Clearing a name is how a player undoes a rename**, and refusing it would leave them stuck with a label they no longer want.

## No new window

A float menu per row rather than a bespoke management window. Everything asked for is four verbs on a short list; a window would be more code, more to keep consistent, and no easier to use. Each row opens **its own** actions rather than cramming rename, pin and remove onto one line **where a misclick destroys an address**.

## Not done, and named in `TODO.md`

- **Dialling from the history.** The list records and manages; selecting an entry to *re-open* that coordinate is the natural next step and is a separate interaction with its own permission checks.
- **Facilities** — larger functional spaces.
- **The unknown-def-field checker**, still open from 0.8.7-dev.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass; 1,194 keyed references all resolving.
- Compliance: one keyed file. **No new def of any kind, no asset, no patch operation, no new work type.**

## For the post-completion test phase

Confirming a laboratory gate records each coordinate it registers, once, with the count rising on repeats; confirming two gates keep separate lists; confirming **a natural portal offers no history gizmo at all**; confirming rename, pin, remove and clear each do exactly what they say; confirming a clear keeps pinned entries; confirming the list caps at 32 and evicts the least recently used unpinned entry; confirming a fully pinned list refuses new entries rather than dropping a pinned one; and confirming a renamed entry survives a save and reload.
