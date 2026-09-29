# Contributing

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](docs/CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


Start with [AGENTS.md](AGENTS.md), the [AI handoff](docs/AI_BUILD_HANDOFF.md), [master TODO](docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md), and [build instructions](docs/BUILDING.md). Keep owner decisions D1–D9 and S1/B; do not expand deferred named threats or introduce a mandatory optional-mod dependency. **D1 was changed by the owner on 2026-09-29** — public Steam Workshop is now the first distribution target, replacing the private RimWorld Together prototype; see [D1 superseded](docs/GATE_0_DECISIONS.md#d1-superseded-2026-09-29--public-workshop-is-the-first-distribution-target). D2–D9 and S1/B are unchanged.

Read [regression containment](docs/REGRESSION_CONTAINMENT.md) before extending an implemented path. Keep the baseline, impact list, deliberate changes, preserved behavior and remaining verification in the task record, then update the master TODO to match actual evidence.

## Task and source ownership

Each task gets a record under `docs/implementation/` naming its TODO items, feature IDs, canonical contracts, exact reviewed mod rows/package IDs, source facts, saved-state owner, player route, failure/recovery, file scope and acceptance evidence. Use the [foundation task](docs/implementation/PHASE_1_FOUNDATION_TASK.md) as an example. Mark future paths **planned**. Agents receive exclusive file/row scopes; the lead reconciles changes to shared contracts. Do not copy game/mod source or assets.

## Code and identifiers

- Namespace root: `RimroomsAsyncIndustries`; folders group ownership (`Core`, `Company`, `UI`, then feature folders as implemented). Use C# 7.3, four spaces, block namespaces, explicit braces and clear names. Follow [.editorconfig](.editorconfig).
- Def names and language keys start `RR_`. Prefix an asset name by its purpose; keep texture/audio references extensionless within the package's `Textures/` or `Sounds/` tree. Use forward slashes in XML asset paths. Do not rename shipped Defs casually.
- Scribe keys start `rr_`. Force-save schema versions. Once written, a key, stable ID or class full name is a save contract; migrations must precede changes. See the [migration policy](docs/SAVE_MIGRATION_POLICY.md) and [state dictionary](docs/CAMPAIGN_STATE_DICTIONARY.md).
- Later branch/project/coordinate/case/transaction IDs follow the state dictionary. Never use mutable labels, list positions, wall-clock names or a static cross-save counter as identity. IDs and owner references survive reload; display text is separate.
- Keep mutable campaign state in the owning game's component. Constructors and UI drawing do not initialize scenarios, grant funds, generate rooms, reserve stock or complete research. UI calls validated services once those services exist.
- Optional integrations are guarded by their documented package/API boundary. The Core foundation has no Harmony, RWT or DLC assembly reference. Do not add global patches for functionality supported by normal Core extension points.
- UI text uses keyed English translations; Def labels/descriptions also receive DefInjected entries. Match format arguments; preserve no-audio and non-color warning routes. Diagnostics may remain plain technical text.

## XML, assets and package checks

Use UTF-8 and consistent two-space XML indentation. Keep unique Def names/keys, valid document roots, resolvable class/Def references, matching translation arguments and explicit optional-content guards. Well-formed XML alone does not validate RimWorld Def loading. Record static checks separately from runtime results.

Only approved game-loadable files enter `Mod/Rimrooms - Async Industries/`. Extend the explicit [package allowlist](tools/package-files.json), enforced by [BuildCommon.ps1](tools/BuildCommon.ps1) alongside the feature. No docs, source, caches, tests, logs, dependencies' DLLs or private settings belong there. Track every original asset in the [provenance register](docs/research/provenance-register.csv) and follow the [production specification](docs/research/VISUAL_AUDIO_STYLE_BRIEF.md#existing-content-bindings-and-presentation).

## Versions, changes and review

Use semantic `major.minor.patch` versions. `0.x` is private development and does not promise save compatibility. Update project/About metadata, entry-point version, identity-card version where shown, changelog and package evidence together. Version numbers do not replace the integer save schema or the [migration policy](docs/SAVE_MIGRATION_POLICY.md).

Preserve user edits. Keep diffs scoped; update all contracts affected by a new decision. Do not add/run tests without owner direction; build/metadata evidence must be described accurately. Only the owner starts the game through RimSort. Report failures and unobserved runtime behavior plainly.

**One scoped exception to the no-tests rule exists, and only one** — owner decision 20, recorded 2026-09-29 in [Gate 0 decisions](docs/GATE_0_DECISIONS.md). It authorises **automated fixtures** for the single Phase 6 row covering deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs and schema migration, and **defers every line of it until after the owner's first launch** so the fixtures follow observed failures rather than guessed ones. It is not permission for a general test suite, it does not extend to any other row, and nothing for it may be written before that launch. Everywhere else in this repository the rule above is unchanged: verification is compiling against the pinned Core references, reading the compiler output, inspecting the package manifest and reviewing neighbouring callers.

Authorized publication uses `feature/preproduction-handoff` → `Prep` → `Develop` → `Main` separately on `forgejo` and `github`. Inspect remote refs, preserve divergent work with normal merge/review, and verify each resulting ref. Never force-push. A branch update is not a Workshop release.
