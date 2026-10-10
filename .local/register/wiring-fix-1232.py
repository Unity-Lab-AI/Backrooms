# -*- coding: utf-8 -*-
"""Resolve the two unwired action methods the new checker found, each on its own merits.

**`RenameCompany` is retired.** It duplicates a path that already works: `Dialog_RenameCompany`
uses Core's `Dialog_Rename<T>`, whose accept sets `RenamableLabel`, whose setter calls the very
same `TrySetCompanyName` -- and `OnRenamed` then calls `NoteRenamed()`, which records the same
`RR_Event_CompanyRenamed` event. So the live path validates identically and records identically.
**Two entry points to one state change is how two validations drift apart**, and the one nobody
uses is the one that drifts unnoticed.

**`TriggerEmergencyCutoff` is wired.** It is not a duplicate: the kill switch is a *persistent
thrown state* that must be cleared before the next opening, while a cutoff **ends this opening and
starts the return window without disabling the gate.** Those are different things, and the second
one is the safety action a player wants while watching a crew get into trouble -- end it now, keep
the gate for next time. It had no surface at all.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def edit(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding='utf-8').read()
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    print('edited %s' % rel)


SERVICES = os.path.join('src', 'RimroomsAsyncIndustries', 'Company', 'CampaignServices.cs')
COMP = os.path.join('src', 'RimroomsAsyncIndustries', 'Gate', 'CompRimroomsGate.cs')

# ------------------------------------------------------------------ 1. retire the duplicate
edit(SERVICES,
     u'''        /// <summary>
        /// Rename the company. Available at any time and to every start, because every
        /// start can build a full company of its own.
        /// </summary>
        public CompanyActionResult RenameCompany(string proposed)
        {
            if (!CanOperate) { return CompanyActionResult.Refused(stateFaultKey ?? "RR_Company_Inactive"); }
            if (proposed != null && proposed.Trim() == CompanyName) { return CompanyActionResult.Existing(); }
            if (!TrySetCompanyName(proposed)) { return CompanyActionResult.Refused("RR_Company_InvalidName"); }
            RecordEvent("RR_Event_CompanyRenamed", branchId, CompanyName);
            return CompanyActionResult.Applied();
        }

''',
     u'''        // RenameCompany was retired in 0.12.32-dev, by the wiring checker that found it had no
        // caller. It was not a missing feature -- it was a SECOND path to a change that already
        // works. `Dialog_RenameCompany` uses Core's `Dialog_Rename<T>`, whose accept sets
        // `RenamableLabel`, whose setter calls the same `TrySetCompanyName`; and its `OnRenamed`
        // calls `NoteRenamed()`, which records the same RR_Event_CompanyRenamed event. Identical
        // validation, identical record, one of them unreachable.
        //
        // Two entry points to one state change is how two validations drift apart, and the one
        // nobody uses is the one that drifts without anybody noticing.

''')

# ------------------------------------------------------------------ 2. wire the real capability
edit(COMP,
     u'''            yield return new Command_Action
            {
                defaultLabel = "RR_Gate_KillSwitchLabel".Translate(),''',
     u'''            // Ending this opening now, without disabling the gate.
            //
            // NOT the same as the kill switch below it, which is a persistent thrown state that
            // has to be cleared before the next opening. A cutoff starts the emergency return
            // window and leaves the gate usable, which is what a player wants while watching a
            // crew get into trouble. It had no surface at all until the wiring checker found the
            // method with no caller, at 0.12.32-dev.
            if (IsOpening && !IsEmergency)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RR_Gate_CutoffLabel".Translate(),
                    defaultDesc = "RR_Gate_CutoffDesc".Translate(),
                    icon = parent.def.uiIcon,
                    action = delegate { ShowOrderResult(TriggerEmergencyCutoff()); }
                };
            }

            yield return new Command_Action
            {
                defaultLabel = "RR_Gate_KillSwitchLabel".Translate(),''')

print('RenameCompany retired; TriggerEmergencyCutoff wired to a gizmo')
