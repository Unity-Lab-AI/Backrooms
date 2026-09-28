# Phase 1 Core lifecycle and Operations source review

**Date:** 2026-09-28

**Evidence:** static inspection of the installed Core assembly and Core XML; no game launch, save test, profile change, or compatibility result.

**Scope:** profile row **4**, package **Ludeon.RimWorld**; feature routes **RR-SCEN**, **RR-ECO**, **RR-UI**, **RR-COMPAT**. The existing [Core review](../research/reviews/mods/official-4-Ludeon.RimWorld.md) supplies the publisher/source context.

## Task contract and boundaries

This review supplies the [Phase 1 build foundations](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md#phase-1--repository-build-and-content-foundations) and a bounded first step toward the Phase 2 state owner and Operations screen. Read it with the [Core source map](../research/FIRST_SLICE_CORE_API_SOURCE_MAP.md), [campaign state dictionary](../CAMPAIGN_STATE_DICTIONARY.md), [Operations action contracts](../OPERATIONS_ACTION_CONTRACTS.md), and [feature traceability map](../FEATURE_TRACEABILITY.md).

The approved foundation is a branch-local, initially inactive game component plus a read-only Operations tab. Loading the mod into an ordinary colony must not grant funds, create a branch, change a scenario, or add campaign objectives. A later explicit scenario initializer owns activation and one-time grants. The component owns its saved campaign data; the window owns presentation only. No Harmony, RWT, DLC, or optional mod reference is needed for the extension paths reviewed here.

The assigned review owns this document only. Build scripts, source classes, XML, translations, package files, and their task record belong to the lead implementation task. The remainder of Phase 1 and the complete first-playable loop remain tracked in the master TODO.

## Pinned input and reproduction

- Local input: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`.
- SHA-256 rechecked during this review: `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`.
- Assembly version: `1.6.9676.17735`, per the [pinned target](../research/RWT_AND_GRAVSHIP_FEASIBILITY.md#pinned-local-rimworld-test-target). The historical game-log `rev591` / static version-file `rev590` discrepancy is preserved there.
- Tool actually used: **ilspycmd 9.1.0.7988**, **ICSharpCode.Decompiler 9.1.0.7988**, installed locally at `.local/tools/ilspycmd.exe`.
- Decompiled reference text is held only in ignored `.local/inspection-agent/`. It is not source for redistribution and is not included in the package. This document contains original explanations and API identifiers, not copied game method bodies.
- Core XML inspected: `Data/Core/Defs/Misc/MainButtonDefs/MainButtons.xml` from the same install.

From the repository root, these commands reproduce the bounded inspection without starting RimWorld:

```powershell
$managed = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed'
$assemblyPath = Join-Path $managed 'Assembly-CSharp.dll'
Get-FileHash -LiteralPath $assemblyPath -Algorithm SHA256
& .local/tools/ilspycmd.exe --version
New-Item -ItemType Directory -Force .local/inspection-agent | Out-Null
$types = @(
  'Verse.Game', 'Verse.GameComponent', 'Verse.GameComponentUtility',
  'Verse.Mod', 'Verse.LoadedModManager', 'Verse.Scribe_Values',
  'Verse.Scribe_Deep', 'Verse.ScribeExtractor', 'Verse.Window',
  'Verse.ModsConfig', 'RimWorld.MainButtonDef', 'RimWorld.MainButtonWorker',
  'RimWorld.MainButtonWorker_ToggleTab',
  'RimWorld.MainButtonWorker_ToggleResearchTab',
  'RimWorld.MainTabWindow', 'RimWorld.MainTabsRoot'
)
foreach ($type in $types) {
  & .local/tools/ilspycmd.exe -r $managed -t $type $assemblyPath |
    Set-Content -Encoding utf8 ".local/inspection-agent/$type.cs"
}
```

Recheck the hash before applying the findings to a different installed build. The inspected members are public/protected extension surfaces in this assembly; that is not an upstream guarantee of stability across updates.

## Component construction and campaign ownership

| Verified member or path | Observed behavior | Foundation consequence |
| --- | --- | --- |
| `Verse.Game.Game()` → private `FillComponents()` | Discovers all nonabstract `GameComponent` subclasses; checks `GetComponent(Type)` and constructs missing types with the current `Game` argument. Constructor exceptions are logged. | The concrete Rimrooms component needs a public constructor accepting `Game`. It is created for ordinary colonies too. Do not depend on a Rimrooms scenario, map, or completed game initialization in that constructor. |
| `Verse.GameComponent` | Abstract `IExposable` base with the implicit parameterless base constructor. Its lifecycle hooks are virtual `void` methods. | Declare the concrete `(Game game)` constructor, but **do not call `base(game)`**. The base has no such constructor. Store the supplied game only if needed; never use a static mutable branch singleton. |
| `Game.GetComponent<T>() where T : GameComponent`; `GetComponent(Type)` | Searches existing components; returns null when none matches. It does not construct one. | Read the component through the current game and handle absence. UI must not create replacement campaign state. |
| `Game.ExposeSmallComponents()` | Scribes the component list with deep ownership and passes the current `Game` as construction argument. In `LoadingVars`, it then fills any missing component types. | A newly added mod also receives an inactive component when an older save lacks its data. Missing campaign data must not trigger a starting grant. |

The base exposes `ExposeData()`, `FinalizeInit()`, `StartedNewGame()`, `LoadedGame()`, `GameComponentTick()`, `GameComponentUpdate()`, `GameComponentOnGUI()`, and `AppendDebugString(StringBuilder)`. Each is public and virtual. `GameComponentUtility` dispatches lifecycle calls to the current game's components and catches/logs individual exceptions. A caught exception is not successful recovery; repeated failures can still produce repeated logs.

### Call order that matters

**New game:** `Game.InitNewGame()` generates the starting map, calls `Game.FinalizeInit()`, sets the current map, runs `Scenario.PostGameStart()`, applies starting research, then dispatches `GameComponentUtility.StartedNewGame()`.

**Load:** `Game.LoadGame()` exposes small components before loading the world and maps; it finalizes Scribe loading, finalizes maps and map parents, calls `Game.FinalizeInit()`, and then dispatches `GameComponentUtility.LoadedGame()`.

`Game.FinalizeInit()` dispatches component finalization in both paths, before setting program state to `Playing`. Therefore `FinalizeInit` is not a new-game-only hook, and `StartedNewGame` is still too broad to mean “start the Rimrooms scenario.” Keep all hooks inert until a later explicitly verified scenario route activates the branch. Do not recreate IDs, cash, quests, or objects when drawing UI, loading an existing game, or repairing a missing component.

## Scribe APIs and save pitfalls

| Verified signature/path | Meaning for Rimrooms |
| --- | --- |
| `Scribe_Values.Look<T>(ref T value, string label, T defaultValue = default(T), bool forceSave = false)` | Scalars are written in `Saving` and read in `LoadingVars`. Values matching their default may be omitted unless forced. Save schema/version fields explicitly or use a permanently stable missing-field sentinel; changing an omitted default in a future build must not silently relabel an older save. |
| `Scribe_Deep.Look<T>(ref T target, string label, params object[] ctorArgs)` | Deep-owned non-null data must implement `IExposable`. The serialized runtime class can determine the concrete type restored. Keep owned records separate from references to existing pawns, items, buildings, and maps. |
| `ScribeExtractor.SaveableFromNode<T>(XmlNode, object[])` | Constructs the saved object, registers reference resolution and post-load initialization, and invokes its `ExposeData` during variable loading. Reference-based validation belongs after resolution, not inside a constructor. |
| `ScribeExtractor.ValueFromNode<T>(XmlNode, T defaultValue)` | A missing node returns the supplied default; an explicit null returns the type default. Malformed scalar content may log and return the type default. Do not interpret a parse/default fallback as authorization to reset a live branch or create money. |

`Scribe_Values` explicitly rejects `Thing`, `IExposable`, and `Def` values as the wrong serialization route. Existing physical objects must retain their normal owner and eventually use the appropriate reference APIs; those reference paths are outside this scalar-only foundation review. A branch ID, initialization flag, stable scenario ID, and schema can be scalar fields. Full ledger transactions, receipts, migration, missing-object handling, and gameplay records still need their own implementation and save evidence.

No save round trip was performed here. Future acceptance must cover a normal colony remaining inactive, an explicitly initialized campaign retaining the same ID and money, an older save without the component, and successive loads that never repeat grants. An unsupported newer schema needs a readable non-mutating refusal, not a silent downgrade/reset.

## Mod bootstrap

`Verse.Mod` has a public `Mod(ModContentPack content)` constructor, a `Content` getter, and virtual settings methods. A concrete bootstrap can take that same argument and call `base(content)`.

The inspected `LoadedModManager.LoadAllActiveMods(bool hotReload = false)` sequence loads mod content, creates mod classes, and only then loads mod XML. `CreateModClasses()` locates the owning loaded assembly and activates each concrete `Mod` class with its `ModContentPack`. Thus a bootstrap constructor is an appropriate place for a restrained diagnostic message or settings setup, not for accessing the campaign, assuming Defs are resolved, creating a branch, or registering a duplicate game component.

`ModSettings` is stored outside individual game saves. It must not become the branch balance/research/scenario owner. The core bootstrap and component-discovery path require no Harmony patch.

## Read-only Operations tab and native navigation

| Verified member or Core data | Implementation guidance |
| --- | --- |
| `MainButtonDef.workerClass` defaults to `MainButtonWorker_ToggleTab`; `tabWindowClass` is a `Type`. | A new `MainButtonDef` can reference a Rimrooms `MainTabWindow` subclass without a custom worker or patch. Use the fully qualified class name and a unique Def name. |
| `MainButtonDef` fields include `order`, `buttonVisible`, `validWithoutMap`, `closesWorldView`, `defaultHotKey`, `iconPath`. | Choose an additive tab and preserve native tabs. A text button is possible without borrowing an icon. These inspected fields alone do not establish ordering/overflow behavior under the full UI mod profile. |
| `MainButtonDef.Worker` and `.TabWindow` | Lazily construct parameterless classes and assign their `def` afterward. The Def caches the window; map switches clear it. Avoid game/map access in the window constructor and avoid caching branch state across games. Read the current owner when the screen is drawn/opened. |
| `MainTabWindow()`; `virtual Vector2 RequestedTabSize`; overridden `InitialSize` | The native window clamps requested dimensions to screen bounds and anchors above the bottom button bar. Layout still needs scroll/wrapping behavior for small windows and UI scaling. |
| `Window.DoWindowContents(Rect inRect)` | Public abstract drawing entry point. The subclass implements it using localized text and current read-only state; drawing must not apply grants, perform migration, or create records. Restore shared GUI/font/color state after custom drawing. |
| `MainTabWindow.PostOpen()` | Calls the base hook and honors `def.closesWorldView`. Preserve the base call if overriding. |
| `MainTabsRoot.SetCurrentTab(MainButtonDef tab, bool playSound = true)` and `ToggleTab(MainButtonDef newTab, bool playSound = true)` | Manage closing/removing the old tab and adding the new one through the native window stack. They do not themselves run every worker/tutorial activation guard. |

Core XML confirms native Def names `Work` and `Research`. Raw type metadata confirms `MainButtonDefOf.Research` exists but **`MainButtonDefOf.Work` does not**. Resolve `Work` through a nullable Def lookup rather than inventing a static field; a missing Def must produce a localized refusal.

For a native shortcut, check the resolved target worker's `Visible` and `Disabled` properties, then use `InterfaceTryActivate()`. That keeps tutorial and mandatory tile-selection behavior in the native activation route. The base interface method does not check `Disabled` itself, so the caller must do so. `MainButtonWorker_ToggleTab.Activate()` delegates to `Find.MainTabsRoot.ToggleTab(def)`. `MainButtonWorker_ToggleResearchTab` only changes the progress percentage display; it inherits that activation behavior.

The first Operations panel should plainly report an inactive branch when the component has not been initialized. A Work/Research shortcut changes the selected native tab only. It must not imply gate, personnel, economy, scenario, or research systems have been implemented. Null current game, absent component, absent target Def, or disabled native worker must leave campaign data unchanged and explain the unavailable route.

## Optional-mod detection and framework evidence

`ModsConfig.IsActive(string id)` checks a lowercased ID against the configured active-mod hash set; it neither accepts null nor removes an extra `_steam` suffix. This indicates configured selection, not runtime compatibility. `ModsConfig`'s static constructor reads configuration and can reset/save it when it considers it invalid or outdated. Do not invoke that class in an external inspection script. This review read its code only and did not execute it.

For an in-game informational list, `LoadedModManager.RunningModsListForReading` / `RunningMods` exposes the loaded content packs. Treat this as read-only data and do not call profile mutation methods. A detected package never means a Rimrooms adapter or its runtime behavior is supported.

The Core assembly's metadata reports CLR image version **`v4.0.30319`** and references **mscorlib/System/System.Core `4.0.0.0`**, **netstandard `2.1.0.0`**, and **UnityEngine.CoreModule `0.0.0.0`**. Raw PE assembly-attribute inspection found **no `TargetFrameworkAttribute`**. Consequently a mod project targeting `net472` is a selected compilation baseline, not a framework value established by a game assembly attribute. Compile against the exact local managed references and record the result; only an owner-launched Unity/RimWorld session can establish runtime loading.

Metadata was read with `System.Reflection.PortableExecutable.PEReader` and `System.Reflection.Metadata.PEReaderExtensions.GetMetadataReader`, enumerating assembly custom attributes and `MainButtonDefOf` fields without executing game code. A preliminary `GetCustomAttributesData()` attempt could not resolve `Unity.Burst`; the raw PE read avoided that dependency and is the evidence for the attribute result.

## Result and remaining acceptance

**Source result:** the pinned Core assembly provides native hooks for the proposed inactive save component, minimal mod bootstrap, additive Operations window, and guarded Work/Research navigation. These exact paths need neither Harmony nor DLC. No method bodies or game binaries were copied into tracked source.

**Subsequent compile/package evidence:** see the [lead build record](PHASE_1_BUILD_RECORD.md). **Still unverified in game:** assembly loading, XML/class resolution, localization, runtime drawing/overflow, native shortcuts under the 294-mod profile, new/load/save behavior, schema recovery, performance, and all gameplay/co-op behavior. The lead records compilation/package checks separately. After a build exists, the owner launches through [RimSort](../research/RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md); [RimBridgeServer](../research/RIMBRIDGE_TEST_HARNESS.md) attaches only afterward. This source review cannot close those runtime acceptance cases.
