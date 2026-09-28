# RimWorld mod review: Death Rattle Continued [1.2+]

- Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=2896207870
- Source: https://github.com/kittycat2002/Death-Rattle-Continued
- Row 71; package `Troopersmith1.DeathRattle`; local version blank; local support declaration 1.3–1.6 despite title text “1.2+”. Harmony required and ordered before it; conditional load-after target `vat.epoeforked` is not selected.
- Selected repository is a fork with no visible license statement. Reviewed 2026-09-27; no runtime test.

## Source facts and Rimrooms use

The publisher describes a short rescue window after some vital-organ injuries, with possible lasting brain injury; the page says it incorporates Comatose functionality, has an EPOE: Forked patch, claims Biotech compatibility, and works well with Life Support. Row 272 locally requires this package; consider the pair optional together.

- **Provisional disposition:** optional injury-severity rule; expeditions must not rely on its rescue window.
- **Feature mapping:** `RR-STA; RR-EXP; RR-THREAT; RR-COMPAT`.
- **Checks:** organ injury timing, surgery/rescue, lasting injury, and saves; then Life Support, Biotech, selected surgery/race mods, and RWT pawn recovery if in scope.

Publisher statements are not profile results; no copying or asset reuse.
