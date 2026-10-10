import io

# --- CHANGELOG -------------------------------------------------------------
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = u"""# Changelog

## 0.9.0-dev - 2026-09-29 - a gate is a door and nothing else

- **The custom gate machine, control console, cutoff switch and generator are gone.** A gate is an ordinary door you designate, its controls are an ordinary comms console and machining table, and its power comes off your own grid like everything else.
- The unused site lamp, climate unit, analysis bench and floor carpet went with them. **Four of those had no code behind them at all** and had been shipping artwork nobody could see.
- The gate's control station no longer guesses which gate belongs to it. You choose, and only your choice counts.
- Nothing you can do in the game was removed. Every one of these had already been replaced by an ordinary object you designate.

Full record: [a gate is a door and nothing else](docs/implementation/LEGACY_GATE_RETIREMENT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
assert '0.9.0-dev' not in s
s = s.replace(u'# Changelog\n\n', entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('CHANGELOG.md updated')

# --- FINALIZED -------------------------------------------------------------
p = 'docs/FINALIZED.md'
s = io.open(p, encoding='utf-8').read()
block = u"""

---

## 0.9.0-dev - 2026-09-29 - a gate is a door and nothing else

### Owner direction, verbatim

> *"we are doing it all so order needs to be logical and your intelkligent educated choise based on logical programming order of operations"*

M2 existing-content replacement was chosen as the first of the four remaining majors, because it deletes defs and anything built against content about to be removed gets built twice. It also removes the gate component's second geometry model, so the multi-cell gate work that follows is written once rather than written and then rewritten.

### What shipped

Eight legacy defs retired to the historical archive: the custom gate machine, control console, emergency cutoff and generator, plus the unused site lamp, climate unit, field analysis bench and institutional carpet. Four of the eight had no C# consumer whatsoever. Thirteen package files removed, seven of them textures. The dead cutoff component was deleted outright, and the control station no longer guesses which gate is its own.

### Two checkers earned their place in the same checkpoint

Retiring the textures left three live C# references to textures that no longer shipped, and `check-package-integrity.py` passed clean: its texture check only read XML, and only asked the weaker "ships but unreferenced" question. It now scans C# for `ContentFinder<Texture2D>.Get` too - and it was validated not by planting a fault but by catching three real ones already in the tree. `audit-gate0.py` then caught seven documentation links pointing at the four files that had moved to the archive.

### Build evidence

0.9.0-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **155** C# source files (none added), **79** approved package files, down from 92. Assembly SHA-256 `72D0FF07B03FB90FE0DC31615281E2214A0C78ACFF82AF81947488108A12BD3D`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All four checkers pass; 1,207 keyed references all resolving. **Nothing was added: no new def, asset, patch operation or work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Defs retired: 8. Package files removed: 13. Source files reduced: 4. Docs updated: 9 (1 new).
**Checker gaps found and closed: 1** - C# texture references, proved by three real defects rather than a planted one.
**Broken documentation links caught by the audit: 7.**
Deliberately left for its own checkpoint: the sixty-odd now-unreachable `IsNativeProvider` branches, because a diff that says only "remove the dead branch" is reviewable in a way a mixed one is not.
Still open and named in `TODO.md`: the field gear, whose mechanics must be replaced before its defs can go; `RR_QuietPursuer`; the staff PawnKinds and their recipes.
"""
assert '0.9.0-dev' not in s
s = s.rstrip() + block
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('FINALIZED.md updated')

# --- TODO ------------------------------------------------------------------
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
pairs = [
 ('- [ ] **Legacy gate objects** `RR_MachineGate`, `RR_GateConsole`, `RR_EmergencyCutoff`, `RR_UtilityGenerator`',
  '- [x] **RETIRED 0.9.0-dev.** **Legacy gate objects** `RR_MachineGate`, `RR_GateConsole`, `RR_EmergencyCutoff`, `RR_UtilityGenerator`'),
 ('- [ ] **Legacy fixtures and terrain** `RR_SiteFluorescent`, `RR_SiteClimateUnit`, `RR_FadedInstitutionalCarpet`, plus `RR_FieldAnalysisBench` retirement.',
  '- [x] **RETIRED 0.9.0-dev.** **Legacy fixtures and terrain** `RR_SiteFluorescent`, `RR_SiteClimateUnit`, `RR_FadedInstitutionalCarpet`, plus `RR_FieldAnalysisBench` retirement. **All four had no C# consumer whatsoever** and had been shipping textures nobody could see. Archived to `historical-content/0.2.0/`.'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

anchor = '- [ ] **Remove the 14 historical gameplay PNGs from the package allowlist** once their references are gone.'
extra = (u'- [ ] **The remaining `IsNativeProvider` branches.** Sixty-odd sites whose else-side became unreachable when `RR_MachineGate` was retired in 0.9.0-dev. **Deliberately left for its own checkpoint** rather than mixed into the content retirement: the value is code clarity for the multi-cell gate work, and a diff that says only "remove the dead branch" is reviewable in a way a mixed one is not.\n')
assert anchor in s
s = s.replace(anchor, extra + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('TODO.md updated')
