import io, re

OLD_BRANCH = 'feature/preproduction-handoff'
NEW_BRANCH = 'feature/connected-colony-portals'
CLOSED = ('**`DEFERRED.md` is CLOSED** as of 0.7.x: it holds zero open rows, nothing is ever '
          'deferred, and no row may be added to it. Build it, queue it in `TODO.md`, or ask.')


def edit(path, pairs, must_all=True):
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        if old not in s:
            if must_all:
                raise AssertionError(path + ' :: ' + old[:70])
            continue
        s = s.replace(old, new)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('updated ' + path)


# --- the working branch ----------------------------------------------------
for path in ['AGENTS.md', 'CONTRIBUTING.md', 'docs/HOWTO.md', 'docs/PUBLISHING.md',
             'docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md']:
    s = io.open(path, encoding='utf-8').read()
    assert OLD_BRANCH in s, path
    s = s.replace(OLD_BRANCH, NEW_BRANCH)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('rebranched ' + path)


# --- DEFERRED is closed, said where it is mentioned ------------------------
edit('docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md', [
 ('- The faction rows in [`DEFERRED.md`](DEFERRED.md) now carry rules 1–4 as authoring constraints, not just as content-policy notes.',
  '- The faction rows that were in [`DEFERRED.md`](DEFERRED.md) carry rules 1–4 as authoring '
  'constraints, not just as content-policy notes. ' + CLOSED + ' Those rows were migrated to '
  '[`TODO.md`](TODO.md) and the constraints travelled with them.'),
])

edit('docs/HOWTO.md', [
 ('| [`DEFERRED.md`](DEFERRED.md) | Every deferment with a named owner step. A step cannot close while it still owns an open row here | `TODO.md`, the implementation records |',
  '| ~~[`DEFERRED.md`](DEFERRED.md)~~ | **CLOSED.** Zero open rows, and no row may ever be added. '
  'Every row it held was migrated into `TODO.md`. Nothing in this project is deferred: build it, '
  'queue it, or ask | `TODO.md` |'),
])

edit('docs/REGRESSION_CONTAINMENT.md', [
 ('- `DEFERRED.md` had two residual owner-blocked phrasings.',
  '- `DEFERRED.md` had two residual owner-blocked phrasings. That file has since been **closed** '
  'entirely: zero open rows, no row may be added, and everything it held was migrated to '
  '`TODO.md`.'),
])

edit('docs/SKILL_TREE.md', [
 ('**Design** (owned by resume step 5, spec in `DEFERRED.md`)',
  '**Built** (0.8.0-dev, the escalation ladder; its specification moved to `TODO.md` when '
  '`DEFERRED.md` was closed)'),
 ('**Design** (step 5, spec in `DEFERRED.md`)',
  '**Built** (0.8.0-dev; spec moved to `TODO.md`, `DEFERRED.md` is closed)'),
])


# --- the roadmap's "still custom" list is no longer what is still custom ---
edit('docs/ROADMAP.md', [
 ('  **Still custom:** gate objects (`RR_MachineGate`, `RR_GateConsole`, `RR_EmergencyCutoff`, '
  '`RR_UtilityGenerator`), `RR_FieldAnalysisBench`, four field items + `RR_RouteRecording`, '
  '`RR_SiteFluorescent`, `RR_SiteClimateUnit`, `RR_FadedInstitutionalCarpet`, `RR_ReturnAnchor`, '
  '`RR_QuietPursuer` presentation, five `RR_*Staff` PawnKinds, 14 gameplay PNGs.',
  '  **Retired 0.9.0-dev:** the four legacy gate objects, the field analysis bench, the site '
  'lamp and climate unit, and the institutional carpet — eight defs and seven textures, archived '
  'under `implementation/historical-content/0.2.0/`. **Retired 0.9.9-dev:** the return beacon and '
  'its recipe, whose job the gate\'s own address book had already taken over.\n\n'
  '  **Still custom:** three field items (`RR_FieldRecorder`, `RR_SurveyTag`, '
  '`RR_SealedEvidenceCase`) plus `RR_RouteRecording`, `RR_ReturnAnchor`, the `RR_QuietPursuer` '
  'presentation, five `RR_*Staff` PawnKinds and the remaining gameplay PNGs. Replacements are '
  'decided and recorded in `TODO.md`: the survey tag becomes a Core `GlowPod`, the recorder '
  'merges into the evidence book, and custody completes at a designated Core `Shelf`.'),
])


# --- the master TODO's replacement inventory -------------------------------
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
line = s.split('\n')[110]
assert 'Already replaced in source' in line
s = s.replace(line, line + ' **Retired outright since: the four legacy gate objects, the field '
              'analysis bench, the site lamp and climate unit, and the institutional carpet '
              '(0.9.0-dev); the return beacon and its recipe (0.9.9-dev).** All are archived '
              'under `implementation/historical-content/0.2.0/` rather than deleted.', 1)
s = s.replace(
 '- [ ] **Five recipes** (`RR_MakeFieldRecorder`, `RR_MakeSurveyTags`, `RR_MakeReturnBeacon`, `RR_MakeEvidenceCase`, `RR_AssembleMachineGate`).',
 '- [~] **Five recipes.** `RR_MakeReturnBeacon` was **retired with its item in 0.9.9-dev**, and '
 '`RR_AssembleMachineGate` is **live and kept**: it is the bill a branch runs on a Core machining '
 'table to assemble a gate, and only its name still refers to the retired machine. Remaining: '
 '`RR_MakeFieldRecorder`, `RR_MakeSurveyTags`, `RR_MakeEvidenceCase`.', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('updated docs/TODO.md')
