# Declared relationship gap audit

**Snapshot:** 2026-09-27 local profile inventory. **Scope:** reconcile every selected-profile directed Requires, LoadAfter, LoadBefore, and IncompatibleWith declaration against its originating mod review and the priority interaction map. The relationship CSVs remain unchanged; this audit does not establish compatibility.

## Finding

The source files are not a single 294-row relationship table: the mod inventory and metadata register each contain 294 profile entries, while [installed-mod-relationships-2026-09-27.csv](installed-mod-relationships-2026-09-27.csv) contains 914 declared relationship records, including external targets and ordering metadata. Of those, **602 records point to an in-profile target**: **226 Requires, 371 LoadAfter, 5 LoadBefore, and 0 IncompatibleWith**. They represent **443 unique directed source/target pairs**. The narrower Requires/LoadAfter/IncompatibleWith subset is 597 records across 438 pairs; the five LoadBefore records add five distinct pairs.

The prose-coverage check finds **285 records explicitly described in the originating per-mod review** (including four of the five LoadBefore declarations), **37 additional records explicitly represented in the declared-edge portion of the priority map**, and **280 records whose exact directed relationship is not repeated in either prose artifact**. The prose-uncovered set is **13 Requires records and 267 LoadAfter records**, across **269 unique endpoint pairs**; none of the five LoadBefore records remains uncovered after the source/map reconciliation below. These are not missing relationship rows: every record has exact installed-metadata provenance and a conservative proposed disposition in the complete matrix. The 280 prose omissions remain explicitly classified as installed local metadata only where no review explains the edge; no publisher-intent, source-code, or runtime claim is inferred.

The priority map explicitly names **188 of the 294 profile row numbers**; **106 entries do not appear by row number** there. Those entries still have a populated inventory ReviewRecord, non-empty feature trace IDs, disposition, and acceptance-evidence field; all **294/294 review paths exist**, and all 294 inventory review statuses say “Reviewed—source facts recorded”. Priority-map omission is not a missing per-mod review.

## Full-record conservative disposition matrix

The [914-row declared-relationship disposition matrix](declared-relationship-disposition-matrix-2026-09-27.csv) is a static register with one row for each relationship CSV record. Stable IDs (`RIMREL-20260927-0001` through `RIMREL-20260927-0914`) follow the source CSV record ordinal. The matrix was generated using only the exact relationship export and the 294-row inventory. It retains each export record’s source/target load-order numbers, names, package IDs, relationship type, in-profile flag, About.xml evidence path, and hash. It copies endpoint feature tags and review-record paths from the inventory when that endpoint is in profile; target inventory fields are blank for targets outside the selected profile.

The matrix keeps source facts and project policy in separate columns. `SourceFactClassification` identifies every row as installed relationship-export metadata only. `ProjectDispositionBasis` and `ProjectDisposition` apply conservative design handling by relation type and profile presence; they do not assert that any per-mod review or upstream source confirmed the relation. Requires entries preserve the declared dependency for the source mod when it is enabled without turning either optional endpoint into a Rimrooms hard dependency. LoadAfter and LoadBefore entries preserve order only when both endpoints are active and infer no API or feature integration. IncompatibleWith entries keep the declared target out of the selected profile and prohibit automatically pulling it in.

`InteractionTestCandidate` is `Yes` only where both endpoints are in the 294-row profile and share at least one inventory feature tag other than `RR-COMPAT`; this static rule flags **266 candidates**. It is a test queue hint, not proof of code interaction. All **914 rows** have `RuntimeTestStatus=Pending; not run; no compatibility claim.` The full-export counts are 914 records (226 Requires, 616 LoadAfter, 12 LoadBefore, 60 IncompatibleWith), split into 602 in-profile and 312 out-of-profile targets. The in-profile subset remains 226 Requires, 371 LoadAfter, 5 LoadBefore, and 0 IncompatibleWith across 443 unique directed pairs.

The complete matrix closes the record-level inventory gap: every exported relationship now has a stable ID, preserved local metadata evidence, endpoint context when present in profile, and an explicit proposed project disposition. The **280 prose omissions** remain useful as a list of relationships not explained by an originating review or curated interaction note; they are not evidence that the relationship export is incomplete. Where publisher intent or code behavior matters to a proposed integration, cite and reconcile that separate source claim before relying on it. The matrix and 266 feature-overlap flags do not establish runtime support, conflict, or acceptance evidence.

## Evidence labels and counting rule

- **Local metadata fact:** the relationship CSV records relation type, load-order rows, package IDs, TargetInProfile, source About.xml path, and its SHA-256. The CSV proves what the installed metadata declares in this snapshot; it does not by itself prove publisher intent beyond that metadata, a code dependency, conflict, feature interaction, or runtime support.
- **Per-mod review coverage:** counted when the originating review names the exact target and directly states the same relationship type: a requirement/dependency; “after <target>” for LoadAfter; “before <target>” for LoadBefore; or a target-specific incompatibility/conflict. This is a documentation-coverage count only: it does not upgrade local About.xml metadata into a publisher or code claim. A generalized statement such as “supported DLC”, an unverified user report, or a different relation type does not explain this edge.
- **Priority-map explanation:** counted only when the exact source/target row pair is explicitly listed in the map’s “Remaining declared in-profile relationship leads” section. A functional cluster containing multiple mods is not treated as proof of every cross-pair metadata edge.
- **Inference:** a LoadAfter ordering is not evidence of a patch or functional interaction. The missing-edge rows below do not assert a conflict. No in-profile incompatibility edge was found in this snapshot; the 60 IncompatibleWith declarations in the CSV all target mods outside the selected profile.

### LoadBefore reconciliation

The five in-profile LoadBefore records are each accounted for below. Four originating reviews directly record the target-specific order; the Adaptive Storage Framework review does not discuss its declared target, so that relationship remains local metadata only. The priority map now lists that metadata pair as a test lead. The More Beautiful Bodies pair is already stated in an earlier priority-map interaction heading, while Non uno Pinata is in the declared-edge supplement. These documentation references do not establish runtime compatibility.

| From row | LoadBefore target | Exact package IDs (From → To) | Local metadata and originating review | Priority-map location / status |
| ---: | --- | --- | --- | --- |
| 1 — Harmony | 4 — Core | `brrainz.harmony` → `Ludeon.RimWorld` | Local metadata and the [Harmony review](reviews/mods/2009463077-brrainz.harmony.md) state to load before Core; the review attributes the order to the Workshop page. | New startup-order entry in [priority map](PRIORITY_PROFILE_INTERACTIONS.md); source-documented metadata, runtime pending. |
| 3 — Loading Progress | 4 — Core | `ilyvion.LoadingProgress` → `ludeon.rimworld` | Local metadata and the [Loading Progress review](reviews/mods/3535481557-ilyvion.LoadingProgress.md) state before Core; the review also records after Harmony. | New startup-order entry in [priority map](PRIORITY_PROFILE_INTERACTIONS.md); source-documented metadata, runtime pending. |
| 10 — Adaptive Storage Framework | 14 — Vanilla Expanded Framework | `adaptive.storage.framework` → `OskarPotocki.VanillaFactionsExpanded.Core` | Relationship CSV declares the order; the [originating review](reviews/mods/3033901359-adaptive.storage.framework.md) does not name this target or explain the edge. | New framework-order entry in [priority map](PRIORITY_PROFILE_INTERACTIONS.md); installed metadata only, source intent unresolved, runtime pending. |
| 130 — More Beautiful Bodies | 268 — Beautiful Bodies | `Burpee.MoreBeautifulBodies` → `mireia.bodies` | The [originating review](reviews/mods/3341372760-Burpee.MoreBeautifulBodies.md) records local metadata order before selected row 268. | Already recorded in the body-texture interaction headings of the [priority map](PRIORITY_PROFILE_INTERACTIONS.md); runtime pending. |
| 152 — Non uno Pinata (don't drop items) | 270 — Hospitality (Continued) | `avilmask.NonUnoPinata` → `orion.hospitality` | The [originating review](reviews/mods/1778821244-avilmask.NonUnoPinata.md) says the local package loads before Hospitality. | Already listed in the declared-edge supplement of the [priority map](PRIORITY_PROFILE_INTERACTIONS.md); runtime pending. |

### Reproduce the counts

Use the two CSVs and the review paths in the inventory’s ReviewRecord field. The scope filter is Relationship in {Requires, LoadAfter, LoadBefore, IncompatibleWith} and TargetInProfile = True. For a review-note coverage check, target aliases are the relationship row ToName/ToPackageID and target inventory ModName/ModID. Requires is explained only when a target alias and requirement/dependency marker (require, dependency/depend, hard dependency, need, must be present) occur on the same line within 80 characters. LoadAfter and LoadBefore require the exact target after/before marker, respectively, on that line (within the preceding 90 characters), or a line explicitly saying the load-after list includes all five DLCs; this grouped phrase applies only to DLC targets. IncompatibleWith requires the exact target and an incompatibility/conflict marker on the same line. The priority-map comparison uses exact endpoint row pairs in its declared-edge section. The map now lists **41 endpoint pairs** there: the 37-pair prior Requires/LoadAfter comparison delta, the previously listed row 152 LoadBefore pair, and the three other LoadBefore pairs absent from earlier interaction headings. The fifth LoadBefore pair, row 130 → 268, is already stated in the earlier body-texture heading.

~~~powershell
$inventory = Import-Csv docs/research/rimworld-server-mod-inventory.csv
$relations = Import-Csv docs/research/installed-mod-relationships-2026-09-27.csv
$inProfile = $relations | Where-Object {
  $_.TargetInProfile -eq "True" -and
  $_.Relationship -in @("Requires", "LoadAfter", "LoadBefore", "IncompatibleWith")
}
$relations | Group-Object Relationship | Sort-Object Name | Select-Object Name, Count # full-export type counts
$relations | Group-Object TargetInProfile | Sort-Object Name | Select-Object Name, Count # 602 in-profile; 312 outside
$inProfile | Group-Object Relationship | Select-Object Name, Count
($inventory | Measure-Object).Count       # 294
($relations | Measure-Object).Count       # 914
(($inProfile | ForEach-Object { "$($_.FromPackageID)`t$($_.ToPackageID)" } | Sort-Object -Unique).Count) # 443 unique directed pairs
~~~

## Priority map coverage of the 294 entries

The priority interaction map cites **188** inventory rows by explicit load-order row number. Of the other 106, it identifies **30 more** by exact inventory mod name or profile ModID in its text/links. Under that reproducible identity rule, **76 entries have no row-number, exact-name, or ModID reference in the priority map**; they are listed below. This is a measure of the selective priority map’s item coverage, not of the per-mod review register.

All 294 inventory entries still have a per-mod ReviewRecord path, populated FeatureTraceIDs, disposition, and acceptance-evidence field; all 294 linked review files exist, and all 294 review statuses are “Reviewed—source facts recorded”. The 76 unreferenced entries are therefore mapped through their accepted per-mod review and inventory feature tags, even though the current priority interaction map does not name them.

### No identifiable priority-map reference (76 entries)

| Profile row | Inventory mod name | Feature trace IDs | Per-mod review |
| ---: | --- | --- | --- |
| 2 | SF Grim Reality | RR-STA;RR-COMPAT | [1543063349-SF.Grim.Reality.md](reviews/mods/1543063349-SF.Grim.Reality.md) |
| 12 | XML Extensions | RR-COMPAT | [2574315206-imranfish.xmlextensions.md](reviews/mods/2574315206-imranfish.xmlextensions.md) |
| 13 | HugsLib | RR-COMPAT | [818773962-UnlimitedHugs.HugsLib.md](reviews/mods/818773962-UnlimitedHugs.HugsLib.md) |
| 14 | Vanilla Expanded Framework | RR-SPACEFLIGHT;RR-COMPAT | [2023507013-OskarPotocki.VanillaFactionsExpanded.Core.md](reviews/mods/2023507013-OskarPotocki.VanillaFactionsExpanded.Core.md) |
| 15 | [ARY] Automatic Stump Chopping [1.5 - 1.6] | RR-FAC;RR-OUT;RR-COMPAT | [3357749890-Arylice.Rimworld.AutomaticStumpChopping.md](reviews/mods/3357749890-Arylice.Rimworld.AutomaticStumpChopping.md) |
| 16 | [Kit] Graze up | RR-OUT;RR-FAC;RR-COMPAT | [2302739121-kittahkhan.grazeup.md](reviews/mods/2302739121-kittahkhan.grazeup.md) |
| 18 | [Ling]Move Steam Geyser | RR-FAC;RR-OUT;RR-COMPAT | [1547361568-LingLuo.MoveSteamGeyser.md](reviews/mods/1547361568-LingLuo.MoveSteamGeyser.md) |
| 19 | [Og] Automatic Power Switch | RR-FAC;RR-GATE;RR-COMPAT | [3031634496-Og.AutomaticPowerSwitch.md](reviews/mods/3031634496-Og.AutomaticPowerSwitch.md) |
| 20 | [SR]Factional War (fork) | RR-MSN;RR-THREAT;RR-COMPAT | [3423264477-SR.ModRimworld.FactionalWarContinued.md](reviews/mods/3423264477-SR.ModRimworld.FactionalWarContinued.md) |
| 22 | [XND] Visible Pants | RR-STYLE;RR-STA;RR-COMPAT | [2264108215-XeoNovaDan.VisiblePants.md](reviews/mods/2264108215-XeoNovaDan.VisiblePants.md) |
| 26 | Adaptive Simple Storage | RR-FAC;RR-EVD;RR-COMPAT | [3297307747-Adaptive.SimpleStorage.md](reviews/mods/3297307747-Adaptive.SimpleStorage.md) |
| 27 | Age Reversing Mech Serum | RR-STA;RR-MSN;RR-COMPAT | [1826684801-LegendaryMinuteman.AgeRMechSerum.md](reviews/mods/1826684801-LegendaryMinuteman.AgeRMechSerum.md) |
| 28 | All Memories Fade | RR-STA;RR-COMPAT | [2800155563-Mlie.AllMemoriesFade.md](reviews/mods/2800155563-Mlie.AllMemoriesFade.md) |
| 30 | Allow Tool | RR-FAC;RR-EXP;RR-OUT;RR-COMPAT | [761421485-UnlimitedHugs.AllowTool.md](reviews/mods/761421485-UnlimitedHugs.AllowTool.md) |
| 35 | Animal Sarcophagus | RR-FAC;RR-STA;RR-COMPAT | [2876565401-overpl.AnimalSarcophagus.md](reviews/mods/2876565401-overpl.AnimalSarcophagus.md) |
| 40 | Architect Icons | RR-UI;RR-STYLE;RR-COMPAT | [1195427067-com.bymarcin.ArchitectIcons.md](reviews/mods/1195427067-com.bymarcin.ArchitectIcons.md) |
| 43 | Auto links | RR-UI;RR-FAC;RR-GATE;RR-EVD;RR-COMPAT | [2059389912-automatic.autolinks.md](reviews/mods/2059389912-automatic.autolinks.md) |
| 44 | Auto-Cut Blight - 1.6 | RR-FAC;RR-STA;RR-COMPAT | [3520167264-Defi.AutoCutBlight.md](reviews/mods/3520167264-Defi.AutoCutBlight.md) |
| 45 | Bad Can Be Good (Continued) | RR-STA;RR-COMPAT | [2889440091-Mlie.BadCanBeGood.md](reviews/mods/2889440091-Mlie.BadCanBeGood.md) |
| 52 | BetterWeight | RR-EXP;RR-OUT;RR-SPACEFLIGHT;RR-COMPAT | [2221387317-ArchieV.BetterWeight.md](reviews/mods/2221387317-ArchieV.BetterWeight.md) |
| 56 | Bo's Milkable Animals | RR-COMPAT | [841092540-Bos.MilkableAnimals.md](reviews/mods/841092540-Bos.MilkableAnimals.md) |
| 61 | Carryalls \| Intercontinental Transport (Continued) | RR-EXP;RR-OUT;RR-SPACEFLIGHT;RR-COMPAT | [3642349335-Mlie.CarryallsIntercontinentalTransport.md](reviews/mods/3642349335-Mlie.CarryallsIntercontinentalTransport.md) |
| 65 | CM Color Coded Mood Bar [1.1+] | RR-STA;RR-UI;RR-COMPAT | [2006605356-CrashM.ColorCodedMoodBar.11.md](reviews/mods/2006605356-CrashM.ColorCodedMoodBar.11.md) |
| 70 | Damage Indicators [1.6] | RR-THREAT;RR-EXP;RR-STYLE;RR-COMPAT | [2016331497-CaesarV6.DamageIndicators.md](reviews/mods/2016331497-CaesarV6.DamageIndicators.md) |
| 78 | Draftable Animals - Releashed | RR-STA;RR-THREAT;RR-EXP;RR-COMPAT | [3534629428-Wolfcub05.DraftableAnimals.md](reviews/mods/3534629428-Wolfcub05.DraftableAnimals.md) |
| 79 | DragSelect | RR-UI;RR-ECO;RR-STA;RR-EXP;RR-COMPAT | [2599942235-telardo.DragSelect.md](reviews/mods/2599942235-telardo.DragSelect.md) |
| 82 | Dubs Mint Minimap | RR-UI;RR-EXP;RR-OUT;RR-MP;RR-COMPAT | [1662119905-dubwise.dubsmintminimap.md](reviews/mods/1662119905-dubwise.dubsmintminimap.md) |
| 89 | Explosive Implant (Continued) | RR-STA;RR-THREAT;RR-EVD;RR-COMPAT | [2162909284-Mlie.ExplosiveImplant.md](reviews/mods/2162909284-Mlie.ExplosiveImplant.md) |
| 95 | FrameRateControl | RR-MP;RR-COMPAT | [1591142767-notfood.FrameRateControl.md](reviews/mods/1591142767-notfood.FrameRateControl.md) |
| 101 | Gold & Silver Ingots | RR-ECO;RR-FAC;RR-COMPAT | [2527544142-kongkim.GSingots.md](reviews/mods/2527544142-kongkim.GSingots.md) |
| 106 | Harvest When Butchering | RR-THREAT;RR-ECO;RR-EXP;RR-STA;RR-COMPAT | [2898826891-Mlie.HarvestWhenButchering.md](reviews/mods/2898826891-Mlie.HarvestWhenButchering.md) |
| 108 | Healer Mech Serum Choice | RR-STA;RR-COMPAT | [2714095848-Syrus.HMSChoice.md](reviews/mods/2714095848-Syrus.HMSChoice.md) |
| 120 | Live With The Pain | RR-STA;RR-EXP;RR-COMPAT | [2659985388-Mlie.LiveWithThePain.md](reviews/mods/2659985388-Mlie.LiveWithThePain.md) |
| 128 | MinifyEverything | RR-FAC;RR-OUT;RR-SPACEFLIGHT;RR-COMPAT | [872762753-erdelf.MinifyEverything.md](reviews/mods/872762753-erdelf.MinifyEverything.md) |
| 134 | More Linkables | RR-FAC;RR-STA;RR-GATE;RR-COMPAT | [1103809207-4loris4.MoreLinkables.md](reviews/mods/1103809207-4loris4.MoreLinkables.md) |
| 136 | More Vanilla Biomes | RR-SPACE;RR-OUT;RR-DLC;RR-COMPAT | [1931453053-zylle.MoreVanillaBiomes.md](reviews/mods/1931453053-zylle.MoreVanillaBiomes.md) |
| 141 | NamesGalore (Continued) | RR-STA;RR-STYLE;RR-COMPAT | [3263018536-zal.namesgalore.md](reviews/mods/3263018536-zal.namesgalore.md) |
| 144 | No Burn Metal | RR-FAC;RR-THREAT;RR-COMPAT | [1923990111-Unon.NoBurnMetal.md](reviews/mods/1923990111-Unon.NoBurnMetal.md) |
| 145 | No Death Cooties On Armour | RR-STA;RR-ECO;RR-COMPAT | [914638336-cucumpear.cooties.md](reviews/mods/914638336-cucumpear.cooties.md) |
| 147 | No Infestation | RR-THREAT;RR-SPACE;RR-COMPAT | [2890080496-walkingproblem.noinfestation.md](reviews/mods/2890080496-walkingproblem.noinfestation.md) |
| 149 | No Royal Clothing Reqs (1.6) | RR-STA;RR-DLC;RR-COMPAT | [2558797536-No.Royal.Clothing.Reqs.md](reviews/mods/2558797536-No.Royal.Clothing.Reqs.md) |
| 150 | No Solar Flares | RR-FAC;RR-COMPAT | [2879659174-laura7z.noflares.md](reviews/mods/2879659174-laura7z.noflares.md) |
| 153 | Not My Fault | RR-OUT;RR-ECO;RR-STA;RR-COMPAT | [2870045856-Vesper.NotMyFault.md](reviews/mods/2870045856-Vesper.NotMyFault.md) |
| 166 | Plasteel Surgery (Continued) | RR-STA;RR-FAC;RR-COMPAT | [2018276375-Mlie.PlasteelSurgery.md](reviews/mods/2018276375-Mlie.PlasteelSurgery.md) |
| 172 | Prisoner Jumpsuits | RR-STA;RR-COMPAT | [3402467889-ocarina.prisonerjumpsuits.md](reviews/mods/3402467889-ocarina.prisonerjumpsuits.md) |
| 180 | Quality Colors (Continued) | RR-UI;RR-ECO;RR-STYLE;RR-COMPAT | [3513846773-DawnsGlow.qualcolor.md](reviews/mods/3513846773-DawnsGlow.qualcolor.md) |
| 184 | Realistic Rooms Rewritten | RR-FAC;RR-STA;RR-COMPAT | [2558042766-Lucifer.RealisticRooms.md](reviews/mods/2558042766-Lucifer.RealisticRooms.md) |
| 186 | Recipe icons (Continued) | RR-UI;RR-FAC;RR-EXP;RR-COMPAT | [2904906618-Mlie.RecipeIcons.md](reviews/mods/2904906618-Mlie.RecipeIcons.md) |
| 188 | Removable Mt.Rock Roof Patch | RR-FAC;RR-SPACE;RR-THREAT;RR-COMPAT;RR-DLC | [1541438898-Proxyer.RemovableMtRockRoofPatche.md](reviews/mods/1541438898-Proxyer.RemovableMtRockRoofPatche.md) |
| 190 | Replantable Anima Trees (Continued) | RR-DLC;RR-FAC;RR-STA;RR-COMPAT | [3503586725-Spuffy.AnimaReplant.md](reviews/mods/3503586725-Spuffy.AnimaReplant.md) |
| 192 | Restraints | RR-STA;RR-THREAT;RR-COMPAT | [1578234826-BDew.Restraints.md](reviews/mods/1578234826-BDew.Restraints.md) |
| 193 | ReTend | RR-STA;RR-EXP;RR-COMPAT | [3523724230-temmie3754.retend.1.md](reviews/mods/3523724230-temmie3754.retend.1.md) |
| 199 | Safely Hidden Away (Continued) | RR-OUT;RR-MSN;RR-THREAT;RR-COMPAT | [3546378186-Mlie.SafelyHiddenAway.md](reviews/mods/3546378186-Mlie.SafelyHiddenAway.md) |
| 202 | Sentience Catalyst Filth Rate Reducer | RR-FAC;RR-STA;RR-THREAT;RR-DLC;RR-COMPAT | [3525790312-FlyingSloth.SCFilthReducer.md](reviews/mods/3525790312-FlyingSloth.SCFilthReducer.md) |
| 206 | Slave Outfit Fix | RR-STA;RR-COMPAT | [2926945131-NightKosh.SlaveOutfitFix.md](reviews/mods/2926945131-NightKosh.SlaveOutfitFix.md) |
| 208 | Smaller radius for Anima Trees, Shrines and Animus Stones | RR-FAC;RR-COMPAT | [2812513517-Longman.SmallerRadiusForAnimaTreesAndShrines.md](reviews/mods/2812513517-Longman.SmallerRadiusForAnimaTreesAndShrines.md) |
| 210 | Smart Meditation | RR-STA;RR-FAC;RR-COMPAT | [2800676538-PureMJ.MjRimMods.SmartMeditation.md](reviews/mods/2800676538-PureMJ.MjRimMods.SmartMeditation.md) |
| 220 | Stop, Drop, And Roll! [BAL] | RR-STA;RR-THREAT;RR-COMPAT | [2362707956-balistafreak.StopDropAndRoll.md](reviews/mods/2362707956-balistafreak.StopDropAndRoll.md) |
| 222 | Stuff on Tables Forked | RR-FAC;RR-UI;RR-COMPAT | [3289533061-moistestWhale.stuffOnTablesForked.md](reviews/mods/3289533061-moistestWhale.stuffOnTablesForked.md) |
| 223 | Surrogate Mechanoid | RR-STA;RR-COMPAT | [3246748490-sov.det.surrogatemech.md](reviews/mods/3246748490-sov.det.surrogatemech.md) |
| 224 | TakeCover | RR-THREAT;RR-EXP;RR-COMPAT | [3749200746-rabiosus.TakeCover.md](reviews/mods/3749200746-rabiosus.TakeCover.md) |
| 226 | The Cooler | RR-FAC;RR-SPACE;RR-COMPAT | [3221592105-GodlyAnnihilator.TheLowCooler.md](reviews/mods/3221592105-GodlyAnnihilator.TheLowCooler.md) |
| 228 | Toggle Harvest | RR-ECO;RR-OUT;RR-COMPAT | [1499848654-Jaxe.ToggleHarvest.md](reviews/mods/1499848654-Jaxe.ToggleHarvest.md) |
| 229 | Tradable Meals | RR-FAC;RR-ECO;RR-COMPAT | [1506931205-Meow.TradableMeals.md](reviews/mods/1506931205-Meow.TradableMeals.md) |
| 230 | Tradable Stone Blocks | RR-ECO;RR-OUT;RR-EXP;RR-COMPAT | [1522257424-Meow.TradableStoneBlocks.md](reviews/mods/1522257424-Meow.TradableStoneBlocks.md) |
| 233 | Trait Rarity Colors | RR-STA;RR-UI;RR-COMPAT | [1751884355-CarnySenpai.TraitRarityColors.md](reviews/mods/1751884355-CarnySenpai.TraitRarityColors.md) |
| 239 | Undraft After Tucking | RR-STA;RR-EXP;RR-COMPAT | [2157495459-madarauchiha.undraftaftertucking.md](reviews/mods/2157495459-madarauchiha.undraftaftertucking.md) |
| 240 | Unsterilize Animals | RR-ECO;RR-COMPAT | [2895378449-BlackFranky.UnsterilizeAnimals.md](reviews/mods/2895378449-BlackFranky.UnsterilizeAnimals.md) |
| 241 | Use Your Gun! | RR-THREAT;RR-EXP;RR-COMPAT | [3229291869-dd.useyourgun.md](reviews/mods/3229291869-dd.useyourgun.md) |
| 245 | Vanilla Fix: Haul After Slaughter | RR-FAC;RR-ECO;RR-COMPAT | [2801452324-PureMJ.MjRimMods.VanillaFixHaulAfterSlaughter.md](reviews/mods/2801452324-PureMJ.MjRimMods.VanillaFixHaulAfterSlaughter.md) |
| 253 | Walkable Solar Panels | RR-FAC;RR-GATE;RR-OUT;RR-COMPAT | [2511096015-Mlie.WalkableSolarPanels.md](reviews/mods/2511096015-Mlie.WalkableSolarPanels.md) |
| 254 | Wall Heater | RR-FAC;RR-OUT;RR-SPACE;RR-COMPAT | [3286518227-Xercaine.WallHeater.md](reviews/mods/3286518227-Xercaine.WallHeater.md) |
| 260 | While You Are Nearby | RR-FAC;RR-STA;RR-COMPAT | [2784585275-PureMJ.MjRimMods.WhileYouAreNearby.md](reviews/mods/2784585275-PureMJ.MjRimMods.WhileYouAreNearby.md) |
| 261 | Who shot my leg off? | RR-STA;RR-EVD;RR-THREAT;RR-COMPAT | [3491552121-Tixiv.WhoShotMyLegOff.md](reviews/mods/3491552121-Tixiv.WhoShotMyLegOff.md) |
| 264 | Zone To Schedule | RR-STA;RR-FAC;RR-OUT;RR-COMPAT | [2436086611-Mlie.ZoneToSchedule.md](reviews/mods/2436086611-Mlie.ZoneToSchedule.md) |
| 294 | Vehicles Wrecks Expanded - Revisited | RR-STYLE;RR-COMPAT | [3348827283-VehiclesWrecksExpanded.Revisited.md](reviews/mods/3348827283-VehiclesWrecksExpanded.Revisited.md) |

### Identified by name or ModID, but not by row number (30 entries)

These entries do appear by exact name or ModID in the map text or linked path; they are excluded from the 76-entry no-reference list above.

| Profile row | Inventory mod name | Map identity reference | Per-mod review |
| ---: | --- | --- | --- |
| 1 | Harmony | exact mod name | [2009463077-brrainz.harmony.md](reviews/mods/2009463077-brrainz.harmony.md) |
| 4 | Core | exact mod name and ModID | [official-4-Ludeon.RimWorld.md](reviews/mods/official-4-Ludeon.RimWorld.md) |
| 5 | Royalty | exact mod name and ModID | [official-5-Ludeon.RimWorld.Royalty.md](reviews/mods/official-5-Ludeon.RimWorld.Royalty.md) |
| 6 | Ideology | exact mod name and ModID | [official-6-Ludeon.RimWorld.Ideology.md](reviews/mods/official-6-Ludeon.RimWorld.Ideology.md) |
| 7 | Biotech | exact mod name and ModID | [official-7-Ludeon.RimWorld.Biotech.md](reviews/mods/official-7-Ludeon.RimWorld.Biotech.md) |
| 8 | Anomaly | exact mod name and ModID | [official-8-Ludeon.RimWorld.Anomaly.md](reviews/mods/official-8-Ludeon.RimWorld.Anomaly.md) |
| 9 | Odyssey | exact mod name and ModID | [official-9-Ludeon.RimWorld.Odyssey.md](reviews/mods/official-9-Ludeon.RimWorld.Odyssey.md) |
| 32 | Animal Apparel: Vac Belt | ModID in linked/reference text | [3525740284-Ingendum.AnimalArmorVacBelt.md](reviews/mods/3525740284-Ingendum.AnimalArmorVacBelt.md) |
| 37 | Animals are fun! (Continued) | ModID in linked/reference text | [3245454244-ColossalFossil.AnimalsAreFunContinued.md](reviews/mods/3245454244-ColossalFossil.AnimalsAreFunContinued.md) |
| 87 | Egg Incubator | exact mod name and ModID | [2505566813-Mlie.EggIncubator.md](reviews/mods/2505566813-Mlie.EggIncubator.md) |
| 91 | Flickable Storage | exact mod name and ModID | [2497907804-Mlie.FlickableStorage.md](reviews/mods/2497907804-Mlie.FlickableStorage.md) |
| 112 | Inject Genes | exact mod name and ModID | [2918091446-Zaf.InjectGene.md](reviews/mods/2918091446-Zaf.InjectGene.md) |
| 139 | Muzzle Flash | exact mod name and ModID | [2917732219-IssacZhuang.MuzzleFlash.md](reviews/mods/2917732219-IssacZhuang.MuzzleFlash.md) |
| 148 | No Quests Without Comms | exact mod name and ModID | [2557302879-eBae.NoQuestsWithoutComms.md](reviews/mods/2557302879-eBae.NoQuestsWithoutComms.md) |
| 156 | Offspring Inherit Xenogenes (Continued) | ModID in linked/reference text | [3266000468-Mlie.OffspringInheritXenogenes.md](reviews/mods/3266000468-Mlie.OffspringInheritXenogenes.md) |
| 170 | Prisoner Arena (Continued) | ModID in linked/reference text | [2022581505-Mlie.PrisonerArena.md](reviews/mods/2022581505-Mlie.PrisonerArena.md) |
| 181 | QualityBuilder Unofficial 1.6 | exact mod name and ModID | [3512466087-hatti.qualitybuilder.md](reviews/mods/3512466087-hatti.qualitybuilder.md) |
| 187 | Remote Doors (Continued) | ModID in linked/reference text | [2243274070-Mlie.RemoteDoors.md](reviews/mods/2243274070-Mlie.RemoteDoors.md) |
| 196 | RimWorld Together | exact mod name and ModID | [3005289691-nova.rimworldtogether.md](reviews/mods/3005289691-nova.rimworldtogether.md) |
| 197 | Romance On The Rim | exact mod name and ModID | [2654432921-telardo.RomanceOnTheRim.md](reviews/mods/2654432921-telardo.RomanceOnTheRim.md) |
| 201 | Secret Passage Doors (Continued) | ModID in linked/reference text | [2412682633-Mlie.SecretPassageDoors.md](reviews/mods/2412682633-Mlie.SecretPassageDoors.md) |
| 211 | Smart Turret Covering | exact mod name and ModID | [2636621800-denev.SmartTurretCovering.md](reviews/mods/2636621800-denev.SmartTurretCovering.md) |
| 212 | Smarter Construction | exact mod name and ModID | [2202185773-dhultgren.smarterconstruction.md](reviews/mods/2202185773-dhultgren.smarterconstruction.md) |
| 216 | Sparkling Worlds - Full Mod | ModID in linked/reference text | [1123043922-Albion.SparklingWorlds.Full.md](reviews/mods/1123043922-Albion.SparklingWorlds.Full.md) |
| 232 | Trade Ships No Matter What | exact mod name and ModID | [2296557502-WindowsXP.TradeShipsNoMatterWhat.md](reviews/mods/2296557502-WindowsXP.TradeShipsNoMatterWhat.md) |
| 235 | TV is Educational | exact mod name and ModID | [2921021769-Mlie.TVIsEducational.md](reviews/mods/2921021769-Mlie.TVIsEducational.md) |
| 252 | Vault Walls and Doors | exact mod name and ModID | [2000708343-SickBoyWi.Vault.OnePointOne.md](reviews/mods/2000708343-SickBoyWi.Vault.OnePointOne.md) |
| 267 | Animal Apparel: Basic Armor | ModID in linked/reference text | [3513849448-Ingendum.AnimalArmorBasic.md](reviews/mods/3513849448-Ingendum.AnimalArmorBasic.md) |
| 281 | Vanilla Gravship Expanded - Chapter 2 | ModID in linked/reference text | [3799737423-vanillaexpanded.gravship2.md](reviews/mods/3799737423-vanillaexpanded.gravship2.md) |
| 286 | Hospitality: Storefront | ModID in linked/reference text | [2952321484-Adamas.Storefront.md](reviews/mods/2952321484-Adamas.Storefront.md) |

## Reconciliation issue in the existing map

The priority-map supplement now enumerates 41 declared endpoint pairs: 37 from the prior Requires/LoadAfter comparison delta and four LoadBefore pairs, including row 152 → 270 and the three startup/framework pairs added for this reconciliation. The fifth in-profile LoadBefore pair, row 130 → 268, is already named in an earlier body-texture heading. The FrozenSnowFox Tweaks subsection now lists all 17 in-profile LoadAfter targets for row 284, including row 12 XML Extensions; that same endpoint pair also has a Requires record, so it is 17 endpoint pairs but 18 relationship records. One Hospitality supplement pair is LoadBefore, which was previously excluded from the 597-record subtotal. This audit now counts all four declared relationship types.

The word “pair” in the map is not the same as a relationship record: one endpoint pair can have separate Requires and LoadAfter records. This audit preserves each declared relation type independently.

## Unexplained in-profile relationship records

All rows below are local metadata declarations lacking a target-specific, relation-matched explanation in the originating review or exact-pair priority-map section. For Requires, run a clean pinned RimWorld 1.6 profile with the declared target present, capture mod-list/dependency diagnostics and startup/Defs logs, then repeat with the source mod excluded when validating the Core/DLC-optional route. For LoadAfter, run a disposable minimal pair in the selected order, capture the resolved order and startup/Defs logs, then exercise the mod’s reviewed behavior only if it shares a relevant system; ordering alone is not a conflict. For DLC targets, include the corresponding absent-DLC profile and exclude any DLC-hard-dependent optional mod. Record exact game/DLC/mod/RWT versions, save, logs, and result before calling a profile supported.

Each table row below is one uncovered directed relationship record. The source review is linked in that source-row heading; package IDs match the corresponding row of the relationship CSV.

### Row 10 — Adaptive Storage Framework ([per-mod review](reviews/mods/3033901359-adaptive.storage.framework.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 10 | LoadAfter | 1 — Harmony | adaptive.storage.framework → brrainz.harmony |
| 10 | LoadAfter | 4 — Core | adaptive.storage.framework → Ludeon.RimWorld |

### Row 11 — Vehicle Framework ([per-mod review](reviews/mods/3014915404-SmashPhil.VehicleFramework.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 11 | LoadAfter | 1 — Harmony | SmashPhil.VehicleFramework → brrainz.harmony |

### Row 13 — HugsLib ([per-mod review](reviews/mods/818773962-UnlimitedHugs.HugsLib.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 13 | LoadAfter | 1 — Harmony | UnlimitedHugs.HugsLib → brrainz.harmony |
| 13 | LoadAfter | 5 — Royalty | UnlimitedHugs.HugsLib → Ludeon.RimWorld.Royalty |
| 13 | LoadAfter | 6 — Ideology | UnlimitedHugs.HugsLib → Ludeon.RimWorld.Ideology |
| 13 | LoadAfter | 7 — Biotech | UnlimitedHugs.HugsLib → Ludeon.RimWorld.Biotech |
| 13 | LoadAfter | 8 — Anomaly | UnlimitedHugs.HugsLib → Ludeon.RimWorld.Anomaly |

### Row 14 — Vanilla Expanded Framework ([per-mod review](reviews/mods/2023507013-OskarPotocki.VanillaFactionsExpanded.Core.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 14 | LoadAfter | 1 — Harmony | OskarPotocki.VanillaFactionsExpanded.Core → brrainz.harmony |
| 14 | LoadAfter | 4 — Core | OskarPotocki.VanillaFactionsExpanded.Core → Ludeon.RimWorld |
| 14 | LoadAfter | 5 — Royalty | OskarPotocki.VanillaFactionsExpanded.Core → Ludeon.RimWorld.Royalty |
| 14 | LoadAfter | 6 — Ideology | OskarPotocki.VanillaFactionsExpanded.Core → Ludeon.RimWorld.Ideology |
| 14 | LoadAfter | 7 — Biotech | OskarPotocki.VanillaFactionsExpanded.Core → Ludeon.RimWorld.Biotech |
| 14 | LoadAfter | 8 — Anomaly | OskarPotocki.VanillaFactionsExpanded.Core → Ludeon.RimWorld.Anomaly |
| 14 | LoadAfter | 9 — Odyssey | OskarPotocki.VanillaFactionsExpanded.Core → Ludeon.RimWorld.Odyssey |

### Row 15 — [ARY] Automatic Stump Chopping [1.5 - 1.6] ([per-mod review](reviews/mods/3357749890-Arylice.Rimworld.AutomaticStumpChopping.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 15 | LoadAfter | 1 — Harmony | Arylice.Rimworld.AutomaticStumpChopping → brrainz.harmony |
| 15 | LoadAfter | 4 — Core | Arylice.Rimworld.AutomaticStumpChopping → Ludeon.RimWorld |
| 15 | LoadAfter | 5 — Royalty | Arylice.Rimworld.AutomaticStumpChopping → Ludeon.RimWorld.Royalty |
| 15 | LoadAfter | 6 — Ideology | Arylice.Rimworld.AutomaticStumpChopping → Ludeon.RimWorld.Ideology |
| 15 | LoadAfter | 7 — Biotech | Arylice.Rimworld.AutomaticStumpChopping → Ludeon.RimWorld.Biotech |
| 15 | LoadAfter | 8 — Anomaly | Arylice.Rimworld.AutomaticStumpChopping → Ludeon.RimWorld.Anomaly |
| 15 | LoadAfter | 9 — Odyssey | Arylice.Rimworld.AutomaticStumpChopping → Ludeon.RimWorld.Odyssey |

### Row 21 — [XND] Profitable Weapons (Continued) ([per-mod review](reviews/mods/2269697598-Mlie.XNDProfitableWeapons.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 21 | LoadAfter | 1 — Harmony | Mlie.XNDProfitableWeapons → brrainz.harmony |

### Row 22 — [XND] Visible Pants ([per-mod review](reviews/mods/2264108215-XeoNovaDan.VisiblePants.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 22 | LoadAfter | 1 — Harmony | XeoNovaDan.VisiblePants → brrainz.harmony |
| 22 | LoadAfter | 5 — Royalty | XeoNovaDan.VisiblePants → Ludeon.RimWorld.Royalty |

### Row 23 — A Dog Said... Animal Prosthetics 2 ([per-mod review](reviews/mods/3238353862-SamBucher.ADogSaidAnimalProsthetics2.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 23 | LoadAfter | 12 — XML Extensions | SamBucher.ADogSaidAnimalProsthetics2 → imranfish.xmlextensions |

### Row 24 — Adaptive Ideology Storage ([per-mod review](reviews/mods/3301337278-Adaptive.Ideology.Storage.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 24 | LoadAfter | 4 — Core | Adaptive.Ideology.Storage → Ludeon.RimWorld |
| 24 | LoadAfter | 6 — Ideology | Adaptive.Ideology.Storage → Ludeon.RimWorld.Ideology |
| 24 | LoadAfter | 10 — Adaptive Storage Framework | Adaptive.Ideology.Storage → adaptive.storage.framework |

### Row 25 — Adaptive Primitive Storage ([per-mod review](reviews/mods/3400037215-Adaptive.PrimitiveStorage.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 25 | Requires | 1 — Harmony | Adaptive.PrimitiveStorage → brrainz.harmony |
| 25 | LoadAfter | 4 — Core | Adaptive.PrimitiveStorage → Ludeon.RimWorld |
| 25 | LoadAfter | 6 — Ideology | Adaptive.PrimitiveStorage → Ludeon.RimWorld.Ideology |
| 25 | LoadAfter | 10 — Adaptive Storage Framework | Adaptive.PrimitiveStorage → adaptive.storage.framework |

### Row 26 — Adaptive Simple Storage ([per-mod review](reviews/mods/3297307747-Adaptive.SimpleStorage.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 26 | LoadAfter | 4 — Core | Adaptive.SimpleStorage → Ludeon.RimWorld |
| 26 | LoadAfter | 10 — Adaptive Storage Framework | Adaptive.SimpleStorage → adaptive.storage.framework |

### Row 30 — Allow Tool ([per-mod review](reviews/mods/761421485-UnlimitedHugs.AllowTool.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 30 | LoadAfter | 13 — HugsLib | UnlimitedHugs.AllowTool → UnlimitedHugs.HugsLib |

### Row 36 — Animal Tab (Continued 1.6) ([per-mod review](reviews/mods/3575480305-Fluffy.AnimalTab.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 36 | LoadAfter | 1 — Harmony | Fluffy.AnimalTab → brrainz.harmony |

### Row 39 — Anomaly Research Asteroid ([per-mod review](reviews/mods/3527726648-zoarak.anomalyplat.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 39 | LoadAfter | 5 — Royalty | zoarak.anomalyplat → Ludeon.RimWorld.Royalty |
| 39 | LoadAfter | 6 — Ideology | zoarak.anomalyplat → Ludeon.RimWorld.Ideology |
| 39 | LoadAfter | 7 — Biotech | zoarak.anomalyplat → Ludeon.RimWorld.Biotech |
| 39 | LoadAfter | 8 — Anomaly | zoarak.anomalyplat → Ludeon.RimWorld.Anomaly |
| 39 | LoadAfter | 9 — Odyssey | zoarak.anomalyplat → Ludeon.RimWorld.Odyssey |

### Row 40 — Architect Icons ([per-mod review](reviews/mods/1195427067-com.bymarcin.ArchitectIcons.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 40 | LoadAfter | 1 — Harmony | com.bymarcin.ArchitectIcons → brrainz.harmony |

### Row 41 — Area Unlocker (Continued) ([per-mod review](reviews/mods/3550817577-Mlie.AreaUnlocker.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 41 | LoadAfter | 1 — Harmony | Mlie.AreaUnlocker → brrainz.harmony |

### Row 49 — Better Electronics ([per-mod review](reviews/mods/1555743957-AdamBucior.BetterElectronics.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 49 | LoadAfter | 13 — HugsLib | AdamBucior.BetterElectronics → UnlimitedHugs.HugsLib |

### Row 51 — Better Gene Inheritance ([per-mod review](reviews/mods/3046776238-RedMattis.BetterGeneInheritance.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 51 | LoadAfter | 1 — Harmony | RedMattis.BetterGeneInheritance → brrainz.harmony |
| 51 | LoadAfter | 5 — Royalty | RedMattis.BetterGeneInheritance → Ludeon.RimWorld.Royalty |
| 51 | LoadAfter | 6 — Ideology | RedMattis.BetterGeneInheritance → Ludeon.RimWorld.Ideology |
| 51 | LoadAfter | 7 — Biotech | RedMattis.BetterGeneInheritance → Ludeon.RimWorld.Biotech |

### Row 52 — BetterWeight ([per-mod review](reviews/mods/2221387317-ArchieV.BetterWeight.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 52 | LoadAfter | 1 — Harmony | ArchieV.BetterWeight → brrainz.harmony |
| 52 | LoadAfter | 4 — Core | ArchieV.BetterWeight → Ludeon.RimWorld |
| 52 | LoadAfter | 5 — Royalty | ArchieV.BetterWeight → Ludeon.RimWorld.Royalty |
| 52 | LoadAfter | 6 — Ideology | ArchieV.BetterWeight → Ludeon.Rimworld.Ideology |
| 52 | LoadAfter | 7 — Biotech | ArchieV.BetterWeight → Ludeon.Rimworld.Biotech |
| 52 | LoadAfter | 8 — Anomaly | ArchieV.BetterWeight → Ludeon.Rimworld.Anomaly |
| 52 | LoadAfter | 9 — Odyssey | ArchieV.BetterWeight → Ludeon.Rimworld.Odyssey |

### Row 54 — Blood Animations ([per-mod review](reviews/mods/3228047321-Fuu.BloodAnimations.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 54 | LoadAfter | 1 — Harmony | Fuu.BloodAnimations → brrainz.harmony |
| 54 | LoadAfter | 4 — Core | Fuu.BloodAnimations → Ludeon.RimWorld |
| 54 | LoadAfter | 5 — Royalty | Fuu.BloodAnimations → Ludeon.RimWorld.Royalty |
| 54 | LoadAfter | 6 — Ideology | Fuu.BloodAnimations → Ludeon.RimWorld.Ideology |
| 54 | LoadAfter | 7 — Biotech | Fuu.BloodAnimations → Ludeon.RimWorld.Biotech |
| 54 | LoadAfter | 8 — Anomaly | Fuu.BloodAnimations → Ludeon.RimWorld.Anomaly |
| 54 | LoadAfter | 9 — Odyssey | Fuu.BloodAnimations → Ludeon.RimWorld.Odyssey |

### Row 59 — Call A Trader ([per-mod review](reviews/mods/2784149999-arakos.callatrader.acat.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 59 | LoadAfter | 1 — Harmony | arakos.callatrader.acat → brrainz.harmony |
| 59 | LoadAfter | 4 — Core | arakos.callatrader.acat → Ludeon.RimWorld |
| 59 | LoadAfter | 5 — Royalty | arakos.callatrader.acat → Ludeon.RimWorld.Royalty |
| 59 | LoadAfter | 6 — Ideology | arakos.callatrader.acat → Ludeon.RimWorld.Ideology |

### Row 61 — Carryalls \| Intercontinental Transport (Continued) ([per-mod review](reviews/mods/3642349335-Mlie.CarryallsIntercontinentalTransport.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 61 | LoadAfter | 1 — Harmony | Mlie.CarryallsIntercontinentalTransport → brrainz.harmony |

### Row 62 — Cash Register (Continued) ([per-mod review](reviews/mods/3509487668-Orion.CashRegister.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 62 | LoadAfter | 1 — Harmony | Orion.CashRegister → brrainz.harmony |

### Row 64 — Character Editor ([per-mod review](reviews/mods/1874644848-void.charactereditor.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 64 | LoadAfter | 1 — Harmony | void.charactereditor → brrainz.harmony |
| 64 | LoadAfter | 4 — Core | void.charactereditor → Ludeon.RimWorld |
| 64 | LoadAfter | 5 — Royalty | void.charactereditor → Ludeon.RimWorld.Royalty |
| 64 | LoadAfter | 6 — Ideology | void.charactereditor → Ludeon.RimWorld.Ideology |
| 64 | LoadAfter | 7 — Biotech | void.charactereditor → Ludeon.RimWorld.Biotech |
| 64 | LoadAfter | 8 — Anomaly | void.charactereditor → Ludeon.RimWorld.Anomaly |
| 64 | LoadAfter | 13 — HugsLib | void.charactereditor → UnlimitedHugs.HugsLib |

### Row 66 — Common Sense ([per-mod review](reviews/mods/1561769193-avilmask.CommonSense.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 66 | LoadAfter | 13 — HugsLib | avilmask.CommonSense → UnlimitedHugs.HugsLib |

### Row 67 — Compact Work Tab (Continued) ([per-mod review](reviews/mods/3250322299-Mlie.CompactWorkTab.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 67 | LoadAfter | 1 — Harmony | Mlie.CompactWorkTab → brrainz.harmony |

### Row 68 — Corpse info ([per-mod review](reviews/mods/2913588675-arl85.CorpseInfo.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 68 | LoadAfter | 1 — Harmony | arl85.CorpseInfo → brrainz.harmony |

### Row 71 — Death Rattle Continued [1.2+] ([per-mod review](reviews/mods/2896207870-Troopersmith1.DeathRattle.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 71 | LoadAfter | 1 — Harmony | Troopersmith1.DeathRattle → brrainz.harmony |

### Row 72 — Dependency Overdose Fix ([per-mod review](reviews/mods/3421951605-TheCafFiend.OverdoseDependencyFix.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 72 | LoadAfter | 1 — Harmony | TheCafFiend.OverdoseDependencyFix → brrainz.harmony |
| 72 | LoadAfter | 4 — Core | TheCafFiend.OverdoseDependencyFix → Ludeon.RimWorld |
| 72 | LoadAfter | 5 — Royalty | TheCafFiend.OverdoseDependencyFix → Ludeon.RimWorld.Royalty |
| 72 | LoadAfter | 6 — Ideology | TheCafFiend.OverdoseDependencyFix → Ludeon.RimWorld.Ideology |
| 72 | LoadAfter | 7 — Biotech | TheCafFiend.OverdoseDependencyFix → Ludeon.RimWorld.Biotech |

### Row 76 — Do Your F****** Research ([per-mod review](reviews/mods/3523205869-MD.PrioritizeResearch.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 76 | LoadAfter | 1 — Harmony | MD.PrioritizeResearch → brrainz.harmony |
| 76 | LoadAfter | 4 — Core | MD.PrioritizeResearch → Ludeon.RimWorld |

### Row 87 — Egg Incubator ([per-mod review](reviews/mods/2505566813-Mlie.EggIncubator.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 87 | LoadAfter | 1 — Harmony | Mlie.EggIncubator → brrainz.harmony |

### Row 91 — Flickable Storage ([per-mod review](reviews/mods/2497907804-Mlie.FlickableStorage.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 91 | LoadAfter | 1 — Harmony | Mlie.FlickableStorage → brrainz.harmony |

### Row 93 — Food Poisoning Stack Fix (Continued) ([per-mod review](reviews/mods/2843483188-Mlie.FoodPoisoningStackFix.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 93 | LoadAfter | 1 — Harmony | Mlie.FoodPoisoningStackFix → brrainz.harmony |

### Row 102 — Graying Hair ([per-mod review](reviews/mods/2807132773-Arkymn.AgingVisuals.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 102 | LoadAfter | 1 — Harmony | Arkymn.AgingVisuals → brrainz.harmony |
| 102 | LoadAfter | 4 — Core | Arkymn.AgingVisuals → Ludeon.RimWorld |
| 102 | LoadAfter | 5 — Royalty | Arkymn.AgingVisuals → Ludeon.RimWorld.Royalty |
| 102 | LoadAfter | 6 — Ideology | Arkymn.AgingVisuals → Ludeon.RimWorld.Ideology |
| 102 | LoadAfter | 7 — Biotech | Arkymn.AgingVisuals → Ludeon.RimWorld.Biotech |
| 102 | LoadAfter | 8 — Anomaly | Arkymn.AgingVisuals → Ludeon.RimWorld.Anomaly |

### Row 104 — Hardened Armor ([per-mod review](reviews/mods/3515052580-Sirprook.HardenedArmor.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 104 | LoadAfter | 1 — Harmony | Sirprook.HardenedArmor → brrainz.harmony |

### Row 107 — Haul to Stack ([per-mod review](reviews/mods/949498803-jkluch.HaulToStack.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 107 | LoadAfter | 1 — Harmony | jkluch.HaulToStack → brrainz.harmony |
| 107 | LoadAfter | 5 — Royalty | jkluch.HaulToStack → Ludeon.RimWorld.Royalty |

### Row 108 — Healer Mech Serum Choice ([per-mod review](reviews/mods/2714095848-Syrus.HMSChoice.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 108 | LoadAfter | 1 — Harmony | Syrus.HMSChoice → brrainz.harmony |

### Row 111 — I Clearly Have Enough! (Continued) ([per-mod review](reviews/mods/2023661266-Mlie.IClearlyHaveEnough.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 111 | LoadAfter | 1 — Harmony | Mlie.IClearlyHaveEnough → brrainz.harmony |

### Row 115 — InterRim Ballistic Missile ([per-mod review](reviews/mods/3682304832-kazepsi.irbm.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 115 | LoadAfter | 4 — Core | kazepsi.irbm → Ludeon.RimWorld |

### Row 116 — Just Put It Over There ([per-mod review](reviews/mods/2856471776-Mlie.JustPutItOverThere.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 116 | LoadAfter | 1 — Harmony | Mlie.JustPutItOverThere → brrainz.harmony |

### Row 117 — Keep Converting ([per-mod review](reviews/mods/3461478214-Linnun.KeepConverting.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 117 | LoadAfter | 1 — Harmony | Linnun.KeepConverting → brrainz.harmony |
| 117 | LoadAfter | 4 — Core | Linnun.KeepConverting → Ludeon.RimWorld |

### Row 118 — Ladies Can Flirt Too! (Continued) ([per-mod review](reviews/mods/3559816908-Mlie.LadiesCanFlirtToo.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 118 | LoadAfter | 1 — Harmony | Mlie.LadiesCanFlirtToo → brrainz.harmony |

### Row 119 — Less Stupid Romance Attempt (Continued) ([per-mod review](reviews/mods/2014603702-Mlie.LessStupidRomanceAttempt.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 119 | LoadAfter | 1 — Harmony | Mlie.LessStupidRomanceAttempt → brrainz.harmony |

### Row 120 — Live With The Pain ([per-mod review](reviews/mods/2659985388-Mlie.LiveWithThePain.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 120 | LoadAfter | 1 — Harmony | Mlie.LiveWithThePain → brrainz.harmony |

### Row 122 — LWM's Adaptive Deep Storage ([per-mod review](reviews/mods/3373064575-ASF.DeepStorage.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 122 | LoadAfter | 10 — Adaptive Storage Framework | ASF.DeepStorage → adaptive.storage.framework |

### Row 124 — Map Preview ([per-mod review](reviews/mods/2800857642-m00nl1ght.MapPreview.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 124 | LoadAfter | 1 — Harmony | m00nl1ght.MapPreview → brrainz.harmony |
| 124 | LoadAfter | 5 — Royalty | m00nl1ght.MapPreview → Ludeon.RimWorld.Royalty |
| 124 | LoadAfter | 6 — Ideology | m00nl1ght.MapPreview → Ludeon.RimWorld.Ideology |
| 124 | LoadAfter | 7 — Biotech | m00nl1ght.MapPreview → Ludeon.RimWorld.Biotech |
| 124 | LoadAfter | 8 — Anomaly | m00nl1ght.MapPreview → Ludeon.RimWorld.Anomaly |
| 124 | LoadAfter | 9 — Odyssey | m00nl1ght.MapPreview → Ludeon.RimWorld.Odyssey |

### Row 126 — Medical IVs Fork ([per-mod review](reviews/mods/3480177412-cantaloupetheclown.MedicalIVsFork.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 126 | LoadAfter | 1 — Harmony | cantaloupetheclown.MedicalIVsFork → brrainz.harmony |

### Row 127 — Mine Sight ([per-mod review](reviews/mods/3769804600-rabiosus.minesight.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 127 | LoadAfter | 1 — Harmony | rabiosus.minesight → brrainz.harmony |

### Row 132 — More Faction Interaction (Continued) ([per-mod review](reviews/mods/2379076640-Mlie.MoreFactionInteraction.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 132 | LoadAfter | 1 — Harmony | Mlie.MoreFactionInteraction → brrainz.harmony |

### Row 138 — Move Your Monolith ([per-mod review](reviews/mods/3221480525-ferny.moveyourmonolith.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 138 | LoadAfter | 5 — Royalty | ferny.moveyourmonolith → Ludeon.Rimworld.Royalty |
| 138 | LoadAfter | 6 — Ideology | ferny.moveyourmonolith → Ludeon.Rimworld.Ideology |
| 138 | LoadAfter | 7 — Biotech | ferny.moveyourmonolith → Ludeon.Rimworld.Biotech |
| 138 | LoadAfter | 8 — Anomaly | ferny.moveyourmonolith → Ludeon.Rimworld.Anomaly |

### Row 139 — Muzzle Flash ([per-mod review](reviews/mods/2917732219-IssacZhuang.MuzzleFlash.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 139 | LoadAfter | 4 — Core | IssacZhuang.MuzzleFlash → Ludeon.RimWorld |

### Row 140 — Name Your Entities ([per-mod review](reviews/mods/3229905841-ferny.NameYourEntities.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 140 | LoadAfter | 8 — Anomaly | ferny.NameYourEntities → Ludeon.RimWorld.Anomaly |

### Row 142 — Need Bar Overflow ([per-mod review](reviews/mods/2566316158-AmCh.NeedBarOverflow.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 142 | LoadAfter | 4 — Core | AmCh.NeedBarOverflow → Ludeon.RimWorld |

### Row 147 — No Infestation ([per-mod review](reviews/mods/2890080496-walkingproblem.noinfestation.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 147 | LoadAfter | 7 — Biotech | walkingproblem.noinfestation → Ludeon.RimWorld.Biotech |

### Row 148 — No Quests Without Comms ([per-mod review](reviews/mods/2557302879-eBae.NoQuestsWithoutComms.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 148 | LoadAfter | 1 — Harmony | eBae.NoQuestsWithoutComms → brrainz.harmony |

### Row 151 — No Sympathy For Prisoners ([per-mod review](reviews/mods/3533769253-sk.noprisonersympathy.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 151 | LoadAfter | 1 — Harmony | sk.noprisonersympathy → brrainz.harmony |

### Row 156 — Offspring Inherit Xenogenes (Continued) ([per-mod review](reviews/mods/3266000468-Mlie.OffspringInheritXenogenes.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 156 | LoadAfter | 1 — Harmony | Mlie.OffspringInheritXenogenes → brrainz.harmony |

### Row 158 — Oops All Gene Banks ([per-mod review](reviews/mods/2883683444-redundant.oopsallgenepacks.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 158 | LoadAfter | 7 — Biotech | redundant.oopsallgenepacks → ludeon.rimworld.biotech |

### Row 162 — Pawn Target Fix ([per-mod review](reviews/mods/2014789938-fed1sPlay.PawnTargetFix.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 162 | LoadAfter | 1 — Harmony | fed1sPlay.PawnTargetFix → brrainz.harmony |

### Row 169 — Prison Commons (Continued) ([per-mod review](reviews/mods/2898000489-Mlie.PrisonCommons.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 169 | LoadAfter | 1 — Harmony | Mlie.PrisonCommons → brrainz.harmony |

### Row 172 — Prisoner Jumpsuits ([per-mod review](reviews/mods/3402467889-ocarina.prisonerjumpsuits.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 172 | LoadAfter | 4 — Core | ocarina.prisonerjumpsuits → Ludeon.RimWorld |

### Row 174 — Prisoners Can Read ([per-mod review](reviews/mods/3409290110-divineDerivative.PrisonerReading.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 174 | LoadAfter | 1 — Harmony | divineDerivative.PrisonerReading → brrainz.harmony |

### Row 175 — Prisoners Dont Have Keys ([per-mod review](reviews/mods/2595360307-Mlie.PrisonersDontHaveKeys.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 175 | LoadAfter | 1 — Harmony | Mlie.PrisonersDontHaveKeys → brrainz.harmony |

### Row 177 — Prisoners Should Fear Turrets ([per-mod review](reviews/mods/2602436826-Mlie.PrisonersShouldFearTurrets.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 177 | LoadAfter | 1 — Harmony | Mlie.PrisonersShouldFearTurrets → brrainz.harmony |

### Row 179 — Prosthetic No Missing Body Parts (Continued) ([per-mod review](reviews/mods/2739055353-Mlie.ProstheticNoMissingBodyParts.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 179 | LoadAfter | 1 — Harmony | Mlie.ProstheticNoMissingBodyParts → brrainz.harmony |

### Row 180 — Quality Colors (Continued) ([per-mod review](reviews/mods/3513846773-DawnsGlow.qualcolor.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 180 | LoadAfter | 1 — Harmony | DawnsGlow.qualcolor → brrainz.harmony |
| 180 | LoadAfter | 5 — Royalty | DawnsGlow.qualcolor → Ludeon.RimWorld.Royalty |
| 180 | LoadAfter | 6 — Ideology | DawnsGlow.qualcolor → Ludeon.RimWorld.Ideology |
| 180 | LoadAfter | 7 — Biotech | DawnsGlow.qualcolor → Ludeon.RimWorld.Biotech |
| 180 | LoadAfter | 8 — Anomaly | DawnsGlow.qualcolor → Ludeon.RimWorld.Anomaly |
| 180 | LoadAfter | 9 — Odyssey | DawnsGlow.qualcolor → Ludeon.RimWorld.Odyssey |

### Row 181 — QualityBuilder Unofficial 1.6 ([per-mod review](reviews/mods/3512466087-hatti.qualitybuilder.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 181 | LoadAfter | 1 — Harmony | hatti.qualitybuilder → brrainz.harmony |

### Row 182 — Questionable Ethics Enhanced (Continued) ([per-mod review](reviews/mods/2850854272-Mlie.QuestionableEthicsEnhanced.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 182 | LoadAfter | 1 — Harmony | Mlie.QuestionableEthicsEnhanced → brrainz.harmony |

### Row 183 — Real Faction Guest (Continued) ([per-mod review](reviews/mods/2886929245-Mlie.RealFactionGuest.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 183 | LoadAfter | 1 — Harmony | Mlie.RealFactionGuest → brrainz.harmony |

### Row 185 — ReBuild: Doors and Corners ([per-mod review](reviews/mods/3262718980-ReBuild.COTR.DoorsAndCorners.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 185 | LoadAfter | 1 — Harmony | ReBuild.COTR.DoorsAndCorners → brrainz.harmony |
| 185 | LoadAfter | 5 — Royalty | ReBuild.COTR.DoorsAndCorners → Ludeon.RimWorld.Royalty |
| 185 | LoadAfter | 6 — Ideology | ReBuild.COTR.DoorsAndCorners → Ludeon.RimWorld.Ideology |
| 185 | LoadAfter | 7 — Biotech | ReBuild.COTR.DoorsAndCorners → Ludeon.RimWorld.Biotech |
| 185 | LoadAfter | 8 — Anomaly | ReBuild.COTR.DoorsAndCorners → Ludeon.RimWorld.Anomaly |
| 185 | LoadAfter | 14 — Vanilla Expanded Framework | ReBuild.COTR.DoorsAndCorners → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 186 — Recipe icons (Continued) ([per-mod review](reviews/mods/2904906618-Mlie.RecipeIcons.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 186 | LoadAfter | 1 — Harmony | Mlie.RecipeIcons → brrainz.harmony |

### Row 187 — Remote Doors (Continued) ([per-mod review](reviews/mods/2243274070-Mlie.RemoteDoors.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 187 | LoadAfter | 1 — Harmony | Mlie.RemoteDoors → brrainz.harmony |

### Row 188 — Removable Mt.Rock Roof Patch ([per-mod review](reviews/mods/1541438898-Proxyer.RemovableMtRockRoofPatche.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 188 | LoadAfter | 5 — Royalty | Proxyer.RemovableMtRockRoofPatche → Ludeon.RimWorld.Royalty |
| 188 | LoadAfter | 6 — Ideology | Proxyer.RemovableMtRockRoofPatche → Ludeon.RimWorld.Ideology |
| 188 | LoadAfter | 7 — Biotech | Proxyer.RemovableMtRockRoofPatche → Ludeon.RimWorld.Biotech |
| 188 | LoadAfter | 8 — Anomaly | Proxyer.RemovableMtRockRoofPatche → Ludeon.RimWorld.Anomaly |

### Row 191 — ResearchTree (Eheieh Version) ([per-mod review](reviews/mods/3569150345-eheieh.researchtree.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 191 | LoadAfter | 1 — Harmony | eheieh.researchtree → brrainz.harmony |

### Row 192 — Restraints ([per-mod review](reviews/mods/1578234826-BDew.Restraints.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 192 | LoadAfter | 13 — HugsLib | BDew.Restraints → UnlimitedHugs.HugsLib |

### Row 196 — RimWorld Together ([per-mod review](reviews/mods/3005289691-nova.rimworldtogether.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 196 | LoadAfter | 1 — Harmony | nova.rimworldtogether → brrainz.harmony |
| 196 | LoadAfter | 4 — Core | nova.rimworldtogether → Ludeon.RimWorld |
| 196 | LoadAfter | 5 — Royalty | nova.rimworldtogether → Ludeon.RimWorld.Royalty |
| 196 | LoadAfter | 6 — Ideology | nova.rimworldtogether → Ludeon.Rimworld.Ideology |
| 196 | LoadAfter | 7 — Biotech | nova.rimworldtogether → Ludeon.Rimworld.Biotech |
| 196 | LoadAfter | 9 — Odyssey | nova.rimworldtogether → Ludeon.Rimworld.Odyssey |

### Row 199 — Safely Hidden Away (Continued) ([per-mod review](reviews/mods/3546378186-Mlie.SafelyHiddenAway.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 199 | LoadAfter | 1 — Harmony | Mlie.SafelyHiddenAway → brrainz.harmony |

### Row 200 — Search and Destroy (Continued) ([per-mod review](reviews/mods/3232242247-MemeGoddess.SearchAndDestroy.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 200 | LoadAfter | 14 — Vanilla Expanded Framework | MemeGoddess.SearchAndDestroy → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 201 — Secret Passage Doors (Continued) ([per-mod review](reviews/mods/2412682633-Mlie.SecretPassageDoors.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 201 | LoadAfter | 1 — Harmony | Mlie.SecretPassageDoors → brrainz.harmony |

### Row 202 — Sentience Catalyst Filth Rate Reducer ([per-mod review](reviews/mods/3525790312-FlyingSloth.SCFilthReducer.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 202 | LoadAfter | 1 — Harmony | FlyingSloth.SCFilthReducer → brrainz.harmony |
| 202 | LoadAfter | 5 — Royalty | FlyingSloth.SCFilthReducer → Ludeon.RimWorld.Royalty |
| 202 | LoadAfter | 6 — Ideology | FlyingSloth.SCFilthReducer → Ludeon.RimWorld.Ideology |
| 202 | LoadAfter | 7 — Biotech | FlyingSloth.SCFilthReducer → Ludeon.RimWorld.Biotech |
| 202 | LoadAfter | 9 — Odyssey | FlyingSloth.SCFilthReducer → Ludeon.RimWorld.Odyssey |

### Row 204 — Show Me Your Hands ([per-mod review](reviews/mods/2475965842-Mlie.ShowMeYourHands.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 204 | LoadAfter | 1 — Harmony | Mlie.ShowMeYourHands → brrainz.harmony |

### Row 205 — Simple sidearms ([per-mod review](reviews/mods/927155256-PeteTimesSix.SimpleSidearms.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 205 | LoadAfter | 1 — Harmony | PeteTimesSix.SimpleSidearms → brrainz.harmony |

### Row 211 — Smart Turret Covering ([per-mod review](reviews/mods/2636621800-denev.SmartTurretCovering.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 211 | LoadAfter | 1 — Harmony | denev.SmartTurretCovering → brrainz.harmony |
| 211 | LoadAfter | 5 — Royalty | denev.SmartTurretCovering → Ludeon.RimWorld.Royalty |
| 211 | LoadAfter | 6 — Ideology | denev.SmartTurretCovering → Ludeon.RimWorld.Ideology |
| 211 | LoadAfter | 8 — Anomaly | denev.SmartTurretCovering → Ludeon.RimWorld.Anomaly |

### Row 218 — Stargates! ([per-mod review](reviews/mods/2831698056-ccyt.stargatesmod.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 218 | LoadAfter | 14 — Vanilla Expanded Framework | ccyt.stargatesmod → oskarpotocki.vanillafactionsexpanded.core |

### Row 219 — Stonecutting Extended ([per-mod review](reviews/mods/2571676542-Scherub.StonecuttingExtended.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 219 | LoadAfter | 1 — Harmony | Scherub.StonecuttingExtended → brrainz.harmony |
| 219 | LoadAfter | 4 — Core | Scherub.StonecuttingExtended → Ludeon.RimWorld |
| 219 | LoadAfter | 5 — Royalty | Scherub.StonecuttingExtended → Ludeon.RimWorld.Royalty |
| 219 | LoadAfter | 6 — Ideology | Scherub.StonecuttingExtended → Ludeon.RimWorld.Ideology |
| 219 | LoadAfter | 8 — Anomaly | Scherub.StonecuttingExtended → Ludeon.RimWorld.Anomaly |
| 219 | LoadAfter | 9 — Odyssey | Scherub.StonecuttingExtended → Ludeon.RimWorld.Odyssey |

### Row 223 — Surrogate Mechanoid ([per-mod review](reviews/mods/3246748490-sov.det.surrogatemech.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 223 | LoadAfter | 5 — Royalty | sov.det.surrogatemech → Ludeon.RimWorld.Royalty |
| 223 | LoadAfter | 6 — Ideology | sov.det.surrogatemech → Ludeon.RimWorld.Ideology |
| 223 | LoadAfter | 7 — Biotech | sov.det.surrogatemech → Ludeon.RimWorld.Biotech |

### Row 232 — Trade Ships No Matter What ([per-mod review](reviews/mods/2296557502-WindowsXP.TradeShipsNoMatterWhat.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 232 | LoadAfter | 1 — Harmony | WindowsXP.TradeShipsNoMatterWhat → brrainz.harmony |

### Row 233 — Trait Rarity Colors ([per-mod review](reviews/mods/1751884355-CarnySenpai.TraitRarityColors.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 233 | LoadAfter | 1 — Harmony | CarnySenpai.TraitRarityColors → brrainz.harmony |

### Row 234 — Turrets Shoot Hunting Predators ([per-mod review](reviews/mods/3221646589-archie.turrettargetpatch.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 234 | LoadAfter | 1 — Harmony | archie.turrettargetpatch → brrainz.harmony |

### Row 235 — TV is Educational ([per-mod review](reviews/mods/2921021769-Mlie.TVIsEducational.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 235 | LoadAfter | 7 — Biotech | Mlie.TVIsEducational → Ludeon.Rimworld.Biotech |

### Row 239 — Undraft After Tucking ([per-mod review](reviews/mods/2157495459-madarauchiha.undraftaftertucking.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 239 | LoadAfter | 1 — Harmony | madarauchiha.undraftaftertucking → brrainz.harmony |

### Row 241 — Use Your Gun! ([per-mod review](reviews/mods/3229291869-dd.useyourgun.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 241 | LoadAfter | 13 — HugsLib | dd.useyourgun → UnlimitedHugs.HugsLib |

### Row 242 — Vanilla Apparel Expanded ([per-mod review](reviews/mods/1814987817-VanillaExpanded.VAPPE.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 242 | LoadAfter | 14 — Vanilla Expanded Framework | VanillaExpanded.VAPPE → OskarPotocki.VanillaFactionsExpanded.Core |
| 242 | Requires | 14 — Vanilla Expanded Framework | VanillaExpanded.VAPPE → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 243 — Vanilla Apparel Expanded — Accessories ([per-mod review](reviews/mods/2521176396-VanillaExpanded.VAEAccessories.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 243 | LoadAfter | 14 — Vanilla Expanded Framework | VanillaExpanded.VAEAccessories → OskarPotocki.VanillaFactionsExpanded.Core |
| 243 | Requires | 14 — Vanilla Expanded Framework | VanillaExpanded.VAEAccessories → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 244 — Vanilla Armour Expanded ([per-mod review](reviews/mods/1814988282-VanillaExpanded.VARME.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 244 | LoadAfter | 14 — Vanilla Expanded Framework | VanillaExpanded.VARME → OskarPotocki.VanillaFactionsExpanded.Core |
| 244 | Requires | 14 — Vanilla Expanded Framework | VanillaExpanded.VARME → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 245 — Vanilla Fix: Haul After Slaughter ([per-mod review](reviews/mods/2801452324-PureMJ.MjRimMods.VanillaFixHaulAfterSlaughter.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 245 | LoadAfter | 1 — Harmony | PureMJ.MjRimMods.VanillaFixHaulAfterSlaughter → brrainz.harmony |

### Row 246 — Vanilla Furniture Expanded - Factory ([per-mod review](reviews/mods/3686924415-VanillaExpanded.VFEFactory.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 246 | LoadAfter | 14 — Vanilla Expanded Framework | VanillaExpanded.VFEFactory → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 247 — Vanilla Gravship Expanded - Chapter 1 ([per-mod review](reviews/mods/3609835606-vanillaexpanded.gravship.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 247 | LoadAfter | 14 — Vanilla Expanded Framework | vanillaexpanded.gravship → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 249 — Vanilla Vehicles Expanded ([per-mod review](reviews/mods/3014906877-OskarPotocki.VanillaVehiclesExpanded.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 249 | LoadAfter | 1 — Harmony | OskarPotocki.VanillaVehiclesExpanded → brrainz.harmony |
| 249 | LoadAfter | 4 — Core | OskarPotocki.VanillaVehiclesExpanded → Ludeon.RimWorld |
| 249 | LoadAfter | 5 — Royalty | OskarPotocki.VanillaVehiclesExpanded → Ludeon.RimWorld.Royalty |
| 249 | LoadAfter | 14 — Vanilla Expanded Framework | OskarPotocki.VanillaVehiclesExpanded → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 250 — Vanilla Weapons Expanded - Non-Lethal ([per-mod review](reviews/mods/2454918354-VanillaExpanded.VWENL.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 250 | LoadAfter | 14 — Vanilla Expanded Framework | VanillaExpanded.VWENL → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 251 — Various Space Ship Chunk (Continued) ([per-mod review](reviews/mods/2014616487-Mlie.VariousSpaceShipChunk.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 251 | LoadAfter | 1 — Harmony | Mlie.VariousSpaceShipChunk → brrainz.harmony |

### Row 256 — Wall Televisions ([per-mod review](reviews/mods/3582096423-Xercaine.WallTelevisions.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 256 | LoadAfter | 1 — Harmony | Xercaine.WallTelevisions → brrainz.harmony |

### Row 259 — Warehouse Storage ([per-mod review](reviews/mods/3519963835-vin.warehouse.storage.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 259 | LoadAfter | 4 — Core | vin.warehouse.storage → Ludeon.RimWorld |
| 259 | LoadAfter | 10 — Adaptive Storage Framework | vin.warehouse.storage → adaptive.storage.framework |

### Row 260 — While You Are Nearby ([per-mod review](reviews/mods/2784585275-PureMJ.MjRimMods.WhileYouAreNearby.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 260 | LoadAfter | 1 — Harmony | PureMJ.MjRimMods.WhileYouAreNearby → brrainz.harmony |

### Row 261 — Who shot my leg off? ([per-mod review](reviews/mods/3491552121-Tixiv.WhoShotMyLegOff.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 261 | LoadAfter | 4 — Core | Tixiv.WhoShotMyLegOff → Ludeon.RimWorld |

### Row 263 — You Drive, I Sleep ([per-mod review](reviews/mods/3324430833-Spacemoth.YouDriveISleep.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 263 | LoadAfter | 1 — Harmony | Spacemoth.YouDriveISleep → brrainz.harmony |

### Row 264 — Zone To Schedule ([per-mod review](reviews/mods/2436086611-Mlie.ZoneToSchedule.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 264 | LoadAfter | 1 — Harmony | Mlie.ZoneToSchedule → brrainz.harmony |

### Row 270 — Hospitality (Continued) ([per-mod review](reviews/mods/3509486825-Orion.Hospitality.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 270 | LoadAfter | 1 — Harmony | Orion.Hospitality → brrainz.harmony |
| 270 | LoadAfter | 5 — Royalty | Orion.Hospitality → Ludeon.RimWorld.Royalty |
| 270 | LoadAfter | 14 — Vanilla Expanded Framework | Orion.Hospitality → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 271 — Jewelry ([per-mod review](reviews/mods/3203280763-kikohi.jewelry.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 271 | LoadAfter | 1 — Harmony | kikohi.jewelry → brrainz.harmony |
| 271 | LoadAfter | 5 — Royalty | kikohi.jewelry → Ludeon.RimWorld.Royalty |

### Row 272 — Life Support Continued [1.1+] ([per-mod review](reviews/mods/2937012139-Troopersmith1.LifeSupport.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 272 | LoadAfter | 1 — Harmony | Troopersmith1.LifeSupport → brrainz.harmony |
| 272 | LoadAfter | 71 — Death Rattle Continued [1.2+] | Troopersmith1.LifeSupport → Troopersmith1.DeathRattle |

### Row 273 — Locks ([per-mod review](reviews/mods/1157085076-avius.locks.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 273 | LoadAfter | 77 — Doors Expanded | avius.locks → jecrell.doorsexpanded |

### Row 274 — Medical Dissection ([per-mod review](reviews/mods/1328216966-Heremeus.MedicalDissection.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 274 | LoadAfter | 1 — Harmony | Heremeus.MedicalDissection → brrainz.harmony |
| 274 | LoadAfter | 5 — Royalty | Heremeus.MedicalDissection → Ludeon.RimWorld.Royalty |
| 274 | LoadAfter | 105 — Harvest Organs Post Mortem Continued | Heremeus.MedicalDissection → Smuffle.HarvestOrgansPostMortem |

### Row 275 — Non-Lethal: Re-Examined ([per-mod review](reviews/mods/3455926746-Smxrez.nonlethalreexamined.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 275 | LoadAfter | 250 — Vanilla Weapons Expanded - Non-Lethal | Smxrez.nonlethalreexamined → vanillaexpanded.vwenl |
| 275 | Requires | 250 — Vanilla Weapons Expanded - Non-Lethal | Smxrez.nonlethalreexamined → vanillaexpanded.vwenl |

### Row 276 — Power Poles Extended ([per-mod review](reviews/mods/3339142899-gy.ppextend.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 276 | LoadAfter | 167 — Power Poles | gy.ppextend → co.uk.epicguru.rimforgepoles |

### Row 278 — Replace Stuff: Cooler And Vent Placement Fix ([per-mod review](reviews/mods/3093303048-Deadmano.ReplaceStuffCoolerVentPlacementFix.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 278 | LoadAfter | 189 — Replace Stuff - Continued | Deadmano.ReplaceStuffCoolerVentPlacementFix → Memegoddess.ReplaceStuff |

### Row 280 — Van's Retexture : Misc. Training ([per-mod review](reviews/mods/2848956469-SirVan.MiscTrainingRetexture.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 280 | LoadAfter | 5 — Royalty | SirVan.MiscTrainingRetexture → Ludeon.RimWorld.Royalty |
| 280 | LoadAfter | 6 — Ideology | SirVan.MiscTrainingRetexture → Ludeon.RimWorld.Ideology |

### Row 281 — Vanilla Gravship Expanded - Chapter 2 ([per-mod review](reviews/mods/3799737423-vanillaexpanded.gravship2.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 281 | LoadAfter | 14 — Vanilla Expanded Framework | vanillaexpanded.gravship2 → OskarPotocki.VanillaFactionsExpanded.Core |
| 281 | LoadAfter | 247 — Vanilla Gravship Expanded - Chapter 1 | vanillaexpanded.gravship2 → vanillaexpanded.gravship |
| 281 | Requires | 247 — Vanilla Gravship Expanded - Chapter 1 | vanillaexpanded.gravship2 → vanillaexpanded.gravship |

### Row 282 — Vanilla Vehicles Expanded - Tier 3 ([per-mod review](reviews/mods/3047892432-OskarPotocki.VanillaVehiclesExpandedTier3.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 282 | LoadAfter | 1 — Harmony | OskarPotocki.VanillaVehiclesExpandedTier3 → brrainz.harmony |
| 282 | LoadAfter | 4 — Core | OskarPotocki.VanillaVehiclesExpandedTier3 → Ludeon.RimWorld |
| 282 | LoadAfter | 5 — Royalty | OskarPotocki.VanillaVehiclesExpandedTier3 → Ludeon.RimWorld.Royalty |
| 282 | LoadAfter | 249 — Vanilla Vehicles Expanded | OskarPotocki.VanillaVehiclesExpandedTier3 → OskarPotocki.VanillaVehiclesExpanded |
| 282 | Requires | 249 — Vanilla Vehicles Expanded | OskarPotocki.VanillaVehiclesExpandedTier3 → OskarPotocki.VanillaVehiclesExpanded |

### Row 283 — Vanilla Vehicles Expanded - Upgrades ([per-mod review](reviews/mods/3302208420-OskarPotocki.VanillaVehiclesExpandedUpgrades.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 283 | LoadAfter | 1 — Harmony | OskarPotocki.VanillaVehiclesExpandedUpgrades → brrainz.harmony |
| 283 | LoadAfter | 4 — Core | OskarPotocki.VanillaVehiclesExpandedUpgrades → Ludeon.RimWorld |
| 283 | LoadAfter | 5 — Royalty | OskarPotocki.VanillaVehiclesExpandedUpgrades → Ludeon.RimWorld.Royalty |
| 283 | LoadAfter | 249 — Vanilla Vehicles Expanded | OskarPotocki.VanillaVehiclesExpandedUpgrades → OskarPotocki.VanillaVehiclesExpanded |
| 283 | Requires | 249 — Vanilla Vehicles Expanded | OskarPotocki.VanillaVehiclesExpandedUpgrades → OskarPotocki.VanillaVehiclesExpanded |

### Row 285 — Hospitality - Invite to Stay ([per-mod review](reviews/mods/3783522506-gatoviejo.hospitality.invitetostay.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 285 | LoadAfter | 1 — Harmony | gatoviejo.hospitality.invitetostay → brrainz.harmony |
| 285 | LoadAfter | 270 — Hospitality (Continued) | gatoviejo.hospitality.invitetostay → Orion.Hospitality |
| 285 | Requires | 270 — Hospitality (Continued) | gatoviejo.hospitality.invitetostay → Orion.Hospitality |

### Row 286 — Hospitality: Storefront ([per-mod review](reviews/mods/2952321484-Adamas.Storefront.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 286 | LoadAfter | 62 — Cash Register (Continued) | Adamas.Storefront → Orion.CashRegister |
| 286 | Requires | 62 — Cash Register (Continued) | Adamas.Storefront → Orion.CashRegister |
| 286 | LoadAfter | 270 — Hospitality (Continued) | Adamas.Storefront → Orion.Hospitality |

### Row 287 — Imprisonment On The Go! (Continued) ([per-mod review](reviews/mods/3358620558-AgentBlac.MakePawnsPrisoners.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 287 | LoadAfter | 1 — Harmony | AgentBlac.MakePawnsPrisoners → brrainz.harmony |

### Row 288 — Prison Labor ([per-mod review](reviews/mods/1899474310-avius.prisonlabor.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 288 | LoadAfter | 1 — Harmony | avius.prisonlabor → brrainz.harmony |
| 288 | LoadAfter | 273 — Locks | avius.prisonlabor → avius.locks |

### Row 289 — Simple Ivory ([per-mod review](reviews/mods/1724270693-LegendaryMinuteman.SimpleIvory.fork.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 289 | LoadAfter | 5 — Royalty | LegendaryMinuteman.SimpleIvory.fork → Ludeon.RimWorld.Royalty |
| 289 | LoadAfter | 9 — Odyssey | LegendaryMinuteman.SimpleIvory.fork → Ludeon.RimWorld.Odyssey |

### Row 290 — Vehicles Wrecks Expanded ([per-mod review](reviews/mods/3299034372-Explorern11.VehiclesWrecksExpanded.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 290 | LoadAfter | 1 — Harmony | Explorern11.VehiclesWrecksExpanded → brrainz.harmony |
| 290 | LoadAfter | 4 — Core | Explorern11.VehiclesWrecksExpanded → Ludeon.RimWorld |
| 290 | LoadAfter | 5 — Royalty | Explorern11.VehiclesWrecksExpanded → Ludeon.RimWorld.Royalty |
| 290 | LoadAfter | 249 — Vanilla Vehicles Expanded | Explorern11.VehiclesWrecksExpanded → OskarPotocki.VanillaVehiclesExpanded |
| 290 | Requires | 249 — Vanilla Vehicles Expanded | Explorern11.VehiclesWrecksExpanded → OskarPotocki.VanillaVehiclesExpanded |
| 290 | LoadAfter | 282 — Vanilla Vehicles Expanded - Tier 3 | Explorern11.VehiclesWrecksExpanded → OskarPotocki.VanillaVehiclesExpandedTier3 |
| 290 | Requires | 282 — Vanilla Vehicles Expanded - Tier 3 | Explorern11.VehiclesWrecksExpanded → OskarPotocki.VanillaVehiclesExpandedTier3 |

### Row 291 — VVE - Secondary Weapons ([per-mod review](reviews/mods/3459650108-tgbm.vve.secondary.weapons.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 291 | Requires | 14 — Vanilla Expanded Framework | tgbm.vve.secondary.weapons → OskarPotocki.VanillaFactionsExpanded.Core |

### Row 292 — Custom Prisoner Interactions ([per-mod review](reviews/mods/2841231775-Mlie.CustomPrisonerInteractions.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 292 | LoadAfter | 1 — Harmony | Mlie.CustomPrisonerInteractions → brrainz.harmony |
| 292 | LoadAfter | 288 — Prison Labor | Mlie.CustomPrisonerInteractions → avius.prisonlabor |

### Row 293 — Dismantle Ancient Junk ([per-mod review](reviews/mods/2871064871-proxyer.dismantleancientjunk.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 293 | LoadAfter | 1 — Harmony | proxyer.dismantleancientjunk → brrainz.harmony |
| 293 | LoadAfter | 4 — Core | proxyer.dismantleancientjunk → Ludeon.RimWorld |
| 293 | LoadAfter | 5 — Royalty | proxyer.dismantleancientjunk → Ludeon.RimWorld.Royalty |
| 293 | LoadAfter | 6 — Ideology | proxyer.dismantleancientjunk → Ludeon.Rimworld.Ideology |
| 293 | LoadAfter | 7 — Biotech | proxyer.dismantleancientjunk → Ludeon.RimWorld.Biotech |
| 293 | LoadAfter | 8 — Anomaly | proxyer.dismantleancientjunk → Ludeon.RimWorld.Anomaly |
| 293 | LoadAfter | 14 — Vanilla Expanded Framework | proxyer.dismantleancientjunk → OskarPotocki.VanillaFactionsExpanded.Core |
| 293 | LoadAfter | 290 — Vehicles Wrecks Expanded | proxyer.dismantleancientjunk → Explorern11.VehiclesWrecksExpanded |

### Row 294 — Vehicles Wrecks Expanded - Revisited ([per-mod review](reviews/mods/3348827283-VehiclesWrecksExpanded.Revisited.md))

| From row | Declared relation | To row | Exact package IDs (From → To) |
| ---: | --- | ---: | --- |
| 294 | LoadAfter | 4 — Core | VehiclesWrecksExpanded.Revisited → Ludeon.RimWorld |
| 294 | LoadAfter | 5 — Royalty | VehiclesWrecksExpanded.Revisited → Ludeon.RimWorld.Royalty |
| 294 | LoadAfter | 290 — Vehicles Wrecks Expanded | VehiclesWrecksExpanded.Revisited → Explorern11.VehiclesWrecksExpanded |

## Gate consequence

These 280 rows are an auditable declaration-coverage gap, not a claim that 280 conflicts exist. The mod inventory’s individual source reviews preserve provisional disposition, feature mapping, and known follow-up; the priority interaction map remains a selective high-overlap and named-pair checklist. Before Gate 0 can close, the master graph still needs an owner-reviewed disposition for each uncovered relationship, including whether the declaration is merely load ordering, a required optional stack, a DLC gate, or a meaningful system overlap, followed by pinned-profile evidence for any compatibility claim. The five LoadBefore records are counted and linked above, but they also remain metadata/test leads rather than runtime evidence. Do not treat this audit as a green light for Rimrooms implementation.

## Source files

- [rimworld-server-mod-inventory.csv](rimworld-server-mod-inventory.csv) — 294 profile rows, review paths, feature IDs, disposition, review status, and acceptance evidence.
- [installed-mod-metadata-2026-09-27.csv](installed-mod-metadata-2026-09-27.csv) — 294 installed metadata rows.
- [installed-mod-relationships-2026-09-27.csv](installed-mod-relationships-2026-09-27.csv) — 914 relationship declaration records, package IDs, in-profile flags, local About paths, and hashes.
- [PRIORITY_PROFILE_INTERACTIONS.md](PRIORITY_PROFILE_INTERACTIONS.md) — selected interaction map; not a complete relationship graph.
- [../FEATURE_TRACEABILITY.md](../FEATURE_TRACEABILITY.md) — stable feature IDs referenced by per-mod reviews.
