# -*- coding: utf-8 -*-
"""Queue and audit updates for 0.12.34-dev.

Row 1266 closes and the coverage rows advance. **Status changes and appended closure notes only** --
never a rewritten description, per the standing rule that anyone reading the queue must see what
was done and where, not a checkmark.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


# ------------------------------------------------------------------ row 1266 closes
sub("docs/TODO.md",
    u"- [ ] **The eleven DLC container hauling givers** — open, and named rather than guessed at:",
    u"- [x] **The eleven DLC container hauling givers** — **BUILT 0.12.34-dev** as "
    u"`MachineLoadingProvider`, id `machine-loading`, nine routes covering all eleven. "
    u"**The custody question was already answered by Core and reading it was the work:** every "
    u"one of the eleven refuses to act unless the thing it moves is already on the worker's own "
    u"map — `WorkGiver_CarryToBuilding` returns false unless `selectedPawn.Map == pawn.Map`, "
    u"`FindGeneBank` requires `targetContainer.Map == genepack.Map`, "
    u"`TakeEntityToHoldingPlatform` requires `targetHolder.MapHeld == t.MapHeld`, and the rest "
    u"search `pawn.Map`. **So nothing ever crosses but the worker, and invariant 55 is never "
    u"engaged.** No expansion branch anywhere: the `MayRequire` DefOfs are null-checked and every "
    u"other route matches a group or a comp, so an absent expansion is an empty world rather than "
    u"a condition — which also covers a modded `Building_Enterable` with nothing naming it. "
    u"Record `implementation/MACHINE_LOADING_IMPLEMENTATION.md`, proof "
    u"`proof-machine-loading.py`. Was: open, and named rather than guessed at:")

# ------------------------------------------------------------------ the painting half
sub("docs/TODO.md",
    u"the **eleven DLC container hauling givers** (each needs a custody review before a worker "
    u"crosses for it), the **four painting givers** in `Art`, and any **mod-added work type**",
    u"the **eleven DLC container hauling givers** (each needs a custody review before a worker "
    u"crosses for it) — **BUILT 0.12.34-dev**, and the review found that Core forbids all eleven "
    u"from moving anything between maps — the **four painting givers** in `Art` — **BUILT "
    u"0.12.34-dev** as `PaintingProvider`; `Art` already had `bill-work-art` for sculpting, which "
    u"is why they were nearly lost, but a bill lives on a bench and paint lives on a "
    u"**designation**, so nobody would ever have crossed for any of it — and any **mod-added work "
    u"type**")

# The DEFERRED pointer on that row is stale: DEFERRED.md is closed with zero rows.
sub("docs/TODO.md", u"because the providers and their giver defs are shipped rather than derived. "
                    u"Recorded in `DEFERRED.md`.",
    u"because the providers and their giver defs are shipped rather than derived. **This is now "
    u"the only thing left on this row**, and it cannot be built against an unknown: a wholly new "
    u"work type from a mod nobody has named has no giver defs to write. `DEFERRED.md` is closed "
    u"with zero rows and this pointer to it was stale.")

sub("docs/TODO.md", u"eleven DLC container givers named and left open pending a custody review, "
                    u"and four built here.",
    u"eleven DLC container givers named and left open pending a custody review — **all eleven "
    u"BUILT 0.12.34-dev**, the review finding that Core forbids every one of them from moving "
    u"anything between maps — and four built here.")

# ------------------------------------------------------------------ the coverage audit
sub("docs/research/WORK_TYPE_COVERAGE_AUDIT.md",
    u"| Hauling | 30 | Core/Ideology/Biotech/Anomaly | carry families + `hauling-upkeep` "
    u"deployment | **Covered 0.6.7-dev** for Core; eleven DLC container givers named and open |",
    u"| Hauling | 30 | Core/Ideology/Biotech/Anomaly | carry families + `hauling-upkeep` and "
    u"`machine-loading` deployments | **Fully covered 0.12.34-dev** — the eleven DLC container "
    u"givers closed, and none of them can move anything between maps |")

sub("docs/research/WORK_TYPE_COVERAGE_AUDIT.md",
    u"| Art | 5 | Core | `bill-ingredients` carry + `bill-work-art` deployment | **Covered "
    u"0.6.5-dev** for sculpting; painting is designation work and belongs with `basic-worker`, "
    u"recorded below |",
    u"| Art | 5 | Core | `bill-ingredients` carry + `bill-work-art` and `painting` deployments | "
    u"**Fully covered 0.12.34-dev** — painting is designation work, so it needed its own family; "
    u"a bill lives on a bench and paint lives on a designation |")

sub("docs/research/WORK_TYPE_COVERAGE_AUDIT.md",
    u"What stays open is narrower and named: the eleven DLC *container* hauling givers, which each "
    u"need a custody review, and the four painting givers in `Art`. Two of the original four were "
    u"absent from the remembered list this audit replaced.",
    u"Two of the original four were absent from the remembered list this audit replaced.\n\n"
    u"**As of 0.12.34-dev both remaining named gaps are closed.** The eleven DLC container hauling "
    u"givers became `machine-loading`, and the custody review they were waiting on found that "
    u"**Core forbids every one of them from moving anything between maps** — so the worker crosses "
    u"and the subject is always already there. The four painting givers became `painting`, a second "
    u"`Art` family, because `bill-work-art` asks whether a bench has a deliverable bill and paint "
    u"is a designation on a floor or a wall.\n\n"
    u"**What remains is one thing and it is not buildable against an unknown:** a wholly mod-added "
    u"work type gets no provider, because the providers and their giver defs are shipped rather "
    u"than derived. The bill family already covers modded *benches* inside existing work types, and "
    u"every capability-matched route added since covers modded *content* inside covered types.")

print("queue and audit updated for 0.12.34-dev")
