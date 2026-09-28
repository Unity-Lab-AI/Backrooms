# RimWorld mod review: Prisoners Need Recruiting

- Steam Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=2076235181
- Publisher-linked releases: https://github.com/MadaraUchiha/RimWorldMod-PrisonersNeedRecruiting/releases
- Workshop ID: `2076235181`
- Package ID: `MadaraUchiha.PrisonersNeedRecruiting`
- Review date: 2026-09-27; Workshop page and local metadata reviewed
- Installed version: no `modVersion`; local `About.xml` lists RimWorld 1.1–1.6; SHA-256 `6D486C4E3AA8DE6BBF6BB6AD046E3877C94D2F692FCC07BB448488DD04DFDAD3`
- Dependencies: none declared locally
- Source examined: Workshop description and publisher-linked release page; a reuse license or public extension API was not established

## Verified source facts

- The publisher describes a reminder for prisoners marked `No interaction`, which can be dismissed until prisoner status changes.
- A Steam comment reports interaction with Custom Prisoner Interactions when a hemogen farm is set to maintain. This is not a reproduced result.

## Rimrooms integration decision

- **Provisional disposition:** leave the native reminder optional; no adapter planned unless the company case system introduces distinct statuses that the vanilla alert does not cover.
- Related systems: `RR-STA`, `RR-COMPAT`.
- Do not make recruitment or case progression depend on this reminder.

## Runtime evidence

- Not runtime tested. Check alert show/dismiss/reset behavior with prisoner recruitment settings, Custom Prisoner Interactions, Prison Labor, and hemogen maintenance; verify alerts recover correctly after save/load.
