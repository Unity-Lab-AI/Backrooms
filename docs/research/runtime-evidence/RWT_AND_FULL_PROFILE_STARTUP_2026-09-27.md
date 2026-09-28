# Rimrooms pre-build runtime smoke evidence — 2026-09-27

**Purpose:** preserve bounded startup observations from disposable local profiles. These checks do not establish Rimrooms behavior, multiplayer support, or compatibility of the 294-mod profile.

## A. Core + Harmony + RimWorld Together startup

- **Run:** one disposable client profile with Core, Harmony, and RimWorld Together; launched with `-batchmode -quicktest` and a temporary save-data folder.
- **Observed:** RimWorld reported `1.6.4871 rev591`; RWT created its dispatcher for `26.8.31.1`; the new-game log listed exactly `brrainz.harmony`, `Ludeon.RimWorld`, and `nova.rimworldtogether`.
- **Saved raw log:** [2026-09-27-core-rwt-startup-smoke.log](2026-09-27-core-rwt-startup-smoke.log), SHA-256 `DE1509229F7EBA6A3064996758B548F3D341293C880C86338A6E72A565ACCC78`.
- **Limit:** one headless client startup only. No second player/server session, join, visit, trade, aid, reconnect, save recovery, or selected optional-mod candidate was exercised. The global user `ModsConfig.xml` was not changed (SHA-256 `D80C797B6DC41B0D8C44F5E0BAA28E9670656E36637D7E16885680DDDA0F38B1`).

## B. Full 294-profile startup

- **Run:** copied the current 294-entry client profile into a disposable directory and launched `-batchmode -quicktest` with a temporary save-data folder. No live configuration was edited.
- **Observed:** RimWorld reported `1.6.4871 rev591`; RWT 26.8.31.1 initialized; the startup log reached new-game/map generation with all 294 selected entries, including `Ogre.OgreStack`. OgreStack logged `Modify Stack Sizes Complete`.
- **Saved raw log:** [2026-09-27-full-profile-quicktest.log](2026-09-27-full-profile-quicktest.log), SHA-256 `7D017596D99F44B0B6AF60622B5EDD17DE7DB1CAF28CF00980CED8D0EDC7B46E`.
- **Diagnostics:** the batch-mode run logged `DivineFramework.OnStartup` GUI calls to `Verse.Text`/`GUI.skin` outside `OnGUI`, a denied `UpdateLog` write under the Workshop folder, two English translation errors, a duplicate `Z` key binding, and invalid `AncientJunkClusters` scattering-location output. These are recorded as test leads; this headless run does not determine which persist in a normal interactive launch or whether they are harmless.
- **Limit:** a successful startup/map-generation path is not a compatibility pass. It did not exercise normal menu behavior, gameplay, save/reload, RWT sessions, visits, item transfer, DLC-specific play, or Rimrooms code.

## Runtime target identity and next evidence

Both saved runs report RimWorld `1.6.4871 rev591` and launch from the same Steam install. The current executable SHA-256 is `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D`; the Core `Assembly-CSharp.dll` SHA-256 is `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`. Their on-disk last-write times predate both saved logs, associating these installed binaries with the startup evidence; the raw logs do not themselves contain hashes. Steam app manifest build ID is `23969874`. The installed `Version.txt` and profile snapshot label still say `rev590`; the cause of this static-label mismatch is unknown and remains documented. For the two-client baseline, verify both hashes and capture the runtime-reported build on each client, then run the cases in [RWT_BASELINE_TEST_PLAN.md](../RWT_BASELINE_TEST_PLAN.md), including rows 182 and 274 separately and together. The full-profile run also needs a normal interactive start and targeted save/reload checks; do not infer support from `-quicktest`.
