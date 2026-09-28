# Performance benchmark plan

**Status:** pre-build engineering targets, recorded 2026-09-28. No performance measurements or game runs were made for this plan. Feature coverage: `RR-SPACE`, `RR-GATE`, `RR-EXP`, `RR-OUT`, `RR-UI`, `RR-COMPAT`.

This plan completes the performance-budget requirement in the [acceptance standard](PREPRODUCTION_ACCEPTANCE_STANDARD.md). The thresholds below are initial development budgets. Keep them until measurements justify a documented change; do not silently relax a failed limit. They are not minimum system requirements or measured claims.

## Named reference machine

Use identifier **RR-DEV-01** for the owner's current workstation. Read-only Windows CIM inspection on 2026-09-28 reported:

| Component | Recorded value |
| --- | --- |
| CPU | AMD Ryzen 7 5800X, 8 cores / 16 logical processors |
| RAM | 127.91 GiB reported usable physical memory |
| GPU | NVIDIA GeForce RTX 4070 Ti SUPER |
| Graphics driver | 32.0.16.1692 |
| OS | Windows 11 Home, 10.0.26200, build 26200 |

This identifier avoids publishing the computer's hostname or serial numbers. Repeat the hardware/version capture for a changed machine; record game-install drive type, display resolution, UI scale, graphics settings and power mode with the actual run. Its large RAM capacity must not hide uncontrolled memory growth.

Read-only capture commands: `Get-CimInstance Win32_Processor`, `Get-CimInstance Win32_ComputerSystem`, `Get-CimInstance Win32_OperatingSystem`, and `Get-CimInstance Win32_VideoController`. Select only the fields in the table when retaining output. The game and multiplayer binary identities come from the [pinned target audit](RWT_AND_GRAVSHIP_FEASIBILITY.md#pinned-local-rimworld-test-target).

## Profiles and launch sequence

The [RimSort launch plan](RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md) controls every launch. A Rimrooms package must exist first. The owner performs the first full-target startup: existing 294 entries plus Rimrooms, with RimBridgeServer separately counted as the test overlay (normally 296 loaded entries). This startup is an observation, not the benchmark or a compatibility pass.

After that startup, the owner uses disposable RimSort profiles for these matched comparisons. Never change the owner's active list or remove a mod to offset the bridge count.

| Comparison | Baseline | Candidate |
| --- | --- | --- |
| Core campaign | Core, with identical QA overlay recorded | Core + Rimrooms, same overlay |
| Full selected profile | Frozen 294 entries, same overlay | Same 294 + Rimrooms, same overlay |
| Co-op overhead | Pinned Core + Harmony + RWT, same overlay | Same stack + Rimrooms, same overlay |

Use fresh paired saves with the same seed, map dimensions, pawn/animal/thing counts, stock and work conditions. Do not remove Rimrooms from a live save to create a baseline. For native-vs-Rimrooms features without equivalent content, compare against the previous Rimrooms build and report that limitation. RWT includes both clients and server versions/settings; network latency is recorded separately from local simulation cost.

## Initial budgets

| Case | Procedure and initial acceptance budget |
| --- | --- |
| Idle and active tick cost | Warm up for 2 real minutes, record 10 real minutes at normal game speed, repeat 3 times. Measure tick work time excluding intentional sleep and achieved ticks/second. Added mean tick cost must be at most 10% of matched baseline and at most 1 ms/tick; added p95 at most 2 ms/tick. Also report absolute candidate p50/p95 so a slow baseline cannot conceal unusable performance. Separate idle facility, staffed work/hauling, active expedition, and later outpost cases. |
| Map generation | Freeze 100 seeds per supported map/room-size band and record total generation time, route-validation time, attempts and failures. For the first 6–8-room survey, target p95 at most 10 seconds and no case above 30 seconds. Allow at most 3 failed layout attempts before the documented safe fallback/refusal. Every successful graph must retain its return route; speed cannot excuse an invalid layout. The broader 1,000-seed correctness suite remains in the acceptance standard. |
| Operations UI | Capture 1,000 frames each with Operations closed/open at the same camera and simulation state. Added p95 UI draw time at most 2 ms/frame; a command must display acknowledgement or its refusal within 250 ms. Include large staff, atlas and ledger lists, using paging/virtualization rather than drawing every historical record. |
| Repeated visits and unload | Warm 5 visit/return cycles, then measure 20 revisits to the same site, with the same fixed content. Sample private process memory at the same quiescent checkpoint each cycle. Final-five median minus first-five median must be at most 128 MiB and at most 5% of the post-warmup baseline. Record resident maps, objects and references to distinguish caches from retained live maps. Repeat 20 new-coordinate visits separately; expected saved discoveries may grow, active-map memory must respect the map budget. Never delete a visited site's history to meet the limit. |
| Save/load | Perform 10 paired save/load cycles at the same fixed-content checkpoint. Candidate p95 duration at most baseline ×1.20 + 1 second. Capture save size, warning/error logs and reference counts; no duplicate grants/items/pawns/receipts or orphaned required references. New discoveries may legitimately increase save size; fixed-content replays must not append duplicate records. |
| Main-menu slideshow | Compare disabled, static/reduced-motion and rotating modes at the same menu/display settings. Added p95 frame time at most 2 ms; keep at most 2 full-resolution slide textures resident and target incremental memory at most 128 MiB. A 30-minute rotation must show no accumulating textures or audio sources; disabled mode restores native behavior. |

For tick and UI metrics, collect timings through documented profiler/counter access available to the pinned build or development-only instrumentation. RimBridgeServer controls the case and captures state/evidence; do not assume it supplies every profiler counter. If a metric is unavailable, record **not measured** and add the instrumentation before claiming that budget passed.

## Expansion and evidence

The [procedural space contract](../PROCEDURAL_SPACE_CONTRACT.md) sets candidate room bands of 6–8, 8–16, 16–32 and 24–48. The first implementation tests the smallest band. Later bands, simultaneous staffed sites, additional maps and outpost counts need measured limits before being enabled for release. The campaign can continue discovering coordinates; it must not allocate all potential destinations at once. Archive inactive state through the proven save path and restore visited sites without rerolling them.

Save each result under `docs/research/runtime-evidence/performance/<run-id>/` (planned until a run exists): manifest with hardware ID, exact build/profile/overlay order and settings; paired saves; seed list; raw timings/memory samples; logs; summary table with p50/p95, differences and pass/failure; recovery observations. Keep proprietary binaries out of Git. Record file hashes instead. The feature implementer owns instrumentation and collection, the lead reviews comparability and results, and the owner controls launch.

**Phase 1 follow-up:** establish paired baselines after the first package and owner-operated launch; then enforce these budgets during each feature's implementation. Measured baselines cannot exist before the game tests the owner has explicitly scheduled after the build. Gate 0 closes the plan, named machine and initial thresholds only.
