# Optional mod support policy

## Dependency contract

- RimWorld Core is the only requirement for the solo campaign.
- Harmony and RimWorld Together are additionally required for co-op.
- Royalty, Ideology, Biotech, Anomaly, and Odyssey are optional content layers.
- All remaining entries in the local 294-mod profile are optional. The full ordered profile is the research and test target, not a hidden launch requirement.
- Vanilla Gravship Expanded Chapters 1 and 2 are optional late-game integrations; verify their dependency chain before packaging any bridge.

## Per-mod disposition

Every profile row receives one evidence-backed disposition:

1. **Use native feature** — Rimrooms uses the mod's existing player-facing behavior without copying or replacing its content.
2. **Configuration only** — documented settings/load order are sufficient; no Rimrooms code patch is needed.
3. **Optional adapter** — a small isolated integration calls a documented, versioned extension point and fails cleanly when absent.
4. **Compatibility patch** — a narrowly scoped patch fixes a reproduced interaction and is guarded by exact package/version detection.
5. **Verified alongside / no touch** — the feature is outside Rimrooms' direct scope, but a named version has passed the recorded combined-profile checks.
6. **Unsupported / conflict** — a reproduced blocker or unsafe interaction exists; record the evidence, affected version, workaround if known, and do not claim support.

“Researched” does not mean “integrated”; “loads” does not mean “compatible”; “optional” does not mean tested. Do not claim compatibility for a version or load order not present in the evidence record.

## Maintenance and release policy

- Keep a supported-version matrix for RimWorld 1.6, each DLC combination actually verified, Harmony, RWT client/server builds, the exact full-profile order, and any adapter-specific mods.
- Treat each optional integration as opt-in. Missing mods must leave Core behavior intact; present mods must not trigger patches unless their package IDs are positively detected.
- Do not vendor or redistribute third-party code, textures, XML, audio, or other assets. Link to the upstream mod and record its author/license/version in the research register.
- Re-review a mod when its package ID, supported RimWorld version, declared dependency, relevant Def/API, or tested load order changes. Re-run only the affected isolation tests and the complete release smoke suite; update evidence before changing the compatibility claim.
- Prioritize QoL and content mods by player value and system overlap. Preserve normal vanilla workflows and keyboard bindings; add an adapter only when a documented, testable integration improves the Backrooms company loop.
- Public release notes list verified interactions, known conflicts, optional requirements, and the tested profile. Never say “works with all 294” solely because that profile is installed or its rows are mapped.
