# Menu controller source preparation

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**2026-09-28 — native source inspection.** RR-UI/RR-STYLE, later Phase 5 implementation. This follow-up extends the [earlier menu audit](../research/MENU_BACKGROUND_EXTENSION_AUDIT.md) while the owner-launched first-loop acceptance is pending. This file records engine source facts; the implementation is tracked separately in [PHASE_5_MENU_IMPLEMENTATION.md](PHASE_5_MENU_IMPLEMENTATION.md). No profile change, game launch or runtime result was produced. The [original art candidate](PHASE_5_MENU_ART_PREPARATION.md) remains outside the loadable package.

## Exact local source

Core row 4, `Ludeon.RimWorld`; reviewed assembly SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`. ILSpy 9.1 inspection files remain ignored under `.local/inspection-menu/`: `Verse.UIMenuBackground.cs`, `Verse.UIRoot_Entry.cs`, `Verse.UIRoot.cs`, `RimWorld.UI_BackgroundMain.cs`, `RimWorld.MainMenuDrawer.cs`. No game source is copied into this document or distributed.

| Native surface | Source fact | Implementation implication |
| --- | --- | --- |
| `Verse.Root.Start()` / static startup runner | `Root` is a `MonoBehaviour`; `CheckGlobalInit()` enqueues `StaticConstructorOnStartupUtility.CallAll` with `doAsynchronously: false`. `Root.Update()` advances synchronous long events. `CallAll()` invokes marked type constructors with `RuntimeHelpers.RunClassConstructor`. | The marked constructor is run in RimWorld's normal Unity startup path; source establishes a main-thread startup callback path without using the mod content constructor. |
| `LongEventHandler.ExecuteWhenFinished(Action)` | Adds the callback to a list, but invokes the list immediately when there is no current event or when the current event should wait until displayed. Otherwise the callback is drained when the synchronous event finishes. | It is not by itself a worker-to-main-thread dispatcher. Call it from the marked startup runner's synchronous main-thread event; never use it as the sole recovery for a worker-thread callback. |
| `Verse.UIMenuBackground` | Abstract class with abstract `BackgroundOnGUI()` | An original background renderer can implement the native drawing contract. |
| `UIRoot_Entry.Init()` | Assigns a new `UI_BackgroundMain` to `UIMenuBackgroundManager.background`, then calls `MainMenuDrawer.Init()` | Returning to entry mode resets the owner. A controller must detect that lifecycle rather than installing once and assuming permanence. |
| `UIRoot_Entry.DoMainMenu()` | Draws the current background before normal menu controls when the world view is not selected | The background should use the native surface, preserving normal controls and draw order. |
| `MainMenuDrawer.BackgroundMain` | Casts the manager's background to `UI_BackgroundMain` | Replacing it with an arbitrary `UIMenuBackground` subclass would break this cast. Any replacement candidate must derive from `UI_BackgroundMain`. |
| `UI_BackgroundMain.overrideBGImage` | Public **instance** `Texture2D` field | It is not a static global-image API. Keep a reference to the actual menu instance and its prior image. |
| `SetupExpansionFadeData()` | Public method populates private fade state from `ModLister.AllExpansions` | A newly installed derived background must initialize this state before native hover handling reaches it. |
| `Notify_Hovered(ExpansionDef)` | Public nonvirtual method; only updates the private fade dictionary on repaint | Shadowing this method in a subclass will not intercept `MainMenuDrawer` calls. Do not assume a virtual hover hook. |
| Native draw | Chooses a centered aspect-preserving cover rectangle, draws the current image, then applies native expansion hover fades | Own transitions must preserve crop behavior and DLC preview semantics. A second full-screen draw after the native method can cover the hover preview; that is an unresolved design/implementation detail. |

## Startup route and remaining source questions

The implementation uses an internal `[StaticConstructorOnStartup]` bootstrap type. Its static constructor queues controller creation through `ExecuteWhenFinished`; the Unity-main-thread check remains immediately before any `GameObject` creation. The source path is `Root.Start()` → synchronous `QueueLongEvent(CallAll, doAsynchronously: false)` → `RuntimeHelpers.RunClassConstructor` → bootstrap static constructor → post-event callback. The `RimroomsMod` content constructor does not touch Unity or schedule this work. This ordering is derived from the pinned source and has not been observed in a game session.

An original `UI_BackgroundMain` subclass managed by a narrowly scoped Unity component avoids a mandatory Harmony dependency or fake DLC definition. The implementation follows the public types above; preserving native DLC hover previews during a two-second crossfade still requires owner-launched acceptance. It does not copy the native renderer or read its private fade dictionary.

The candidate must claim only an ordinary native background instance, preserve its previous owner/image for disable and missing-asset fallback, restore only an instance it still owns, and yield if another mod has installed its own renderer. It must not alter `Prefs` or rewrite the owner's chosen vanilla background. Its settings belong to Rimrooms ModSettings; no company save field or simulation tick should drive menu transitions.

Planned files, once the source questions and current phase gate are resolved: `src/RimroomsAsyncIndustries/UI/Menu/` for controller/renderer; original menu texture exports under `1.6/Textures/UI/Menu/`; settings and English text additions; explicit package allowlist/provenance updates. These paths are **planned**, not present in the package.

## Acceptance boundary

Use the existing menu audit's exact mod rows and present/absent cases. Required observations include first entry, return from a save, native fixed/random preferences, DLC hover preview, missing asset, disable/reenable, reduced-motion still selection, slow crossfade, another background owner, no audio, supported crop/UI scale and the full profile's menu overlays. No static source result closes these cases.
