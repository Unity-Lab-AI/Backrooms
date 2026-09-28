# RimWorld mod review: Dependency Overdose Fix

- Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=3421951605
- Row 72; package `TheCafFiend.OverdoseDependencyFix`; local version blank; support 1.5–1.6; Harmony required. Local order lists Harmony, Core, Royalty, Ideology, Biotech.
- **Publisher/local mismatch:** Workshop states Biotech is required DLC; local `About.xml` declares Harmony as the only hard mod dependency and lists Biotech only in load-after metadata. Preserve both statements; do not treat local metadata as disproving the publisher requirement.
- Publisher states source is MIT. Reviewed 2026-09-27; Steam page direct request errored, exact-ID source text available. No runtime test.

## Source facts and Rimrooms use

The publisher says corresponding dependency genes prevent cumulative overdose severity for their matching substances; unrelated substances remain unaffected.

- **Provisional disposition:** optional Biotech-only drug-balance feature.
- **Feature mapping:** `RR-STA; RR-DLC; RR-COMPAT`.
- **Checks:** matching/unrelated substances, multiple dependency genes, and ordinary overdose with Biotech present. Verify it is safely absent from the Core-only profile and test selected medical/drug mods before any RWT pawn-state claim.

No Rimrooms staff-care path should require the mod.
