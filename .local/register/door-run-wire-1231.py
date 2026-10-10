# -*- coding: utf-8 -*-
"""Wire the bound door run into the width, provider, designation and save paths.

Four seams, and each one is the reason a run behaves like one gate instead of several:

  * `GateOccupiedRect` becomes the whole run's rectangle, so `GateEntryCells`, `GateWidth` and
    `GateCellCount` all report the run without any of them knowing a run exists. **Width is
    measured once**, which is invariant 47: per-endpoint measuring traps an animal.

  * `NativeDoorProvider` validates the **run's** footprint rather than the def's, so three 1x1
    doors are a legal 1x3 gate while one of them alone is a legal 1x1 gate.

  * `IsDesignated` refuses for an extension. Invariant 32: one gate, one spin-up, one address.

  * the save, because an unsaved run silently becomes three doors on reload.
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
    print('wired %s' % rel)


SRC = os.path.join('src', 'RimroomsAsyncIndustries')
FOOTPRINT = os.path.join(SRC, 'Gate', 'GateFootprint.cs')
BINDING = os.path.join(SRC, 'Gate', 'NativeGateBinding.cs')
COMP = os.path.join(SRC, 'Gate', 'CompRimroomsGate.cs')

# ------------------------------------------------------------------ 1. the rect is the run
edit(FOOTPRINT,
     u'''        /// <summary>Every cell this gate's door stands on.</summary>
        public CellRect GateOccupiedRect
        {
            get { return parent == null || !parent.Spawned ? CellRect.Empty : parent.OccupiedRect(); }
        }''',
     u'''        /// <summary>
        /// Every cell this gate's doorway stands on.
        ///
        /// **The whole run**, not just the parent door. A gate bound across a run of adjacent
        /// ordinary doors is one doorway that happens to be built out of several things, and
        /// everything downstream of this property -- the entry cells, the width, the cell count,
        /// the power draw and the spin-up work -- is derived from it without needing to know that.
        ///
        /// `RunRect` returns the parent's own rect for a single-door gate, which is every gate
        /// that has not been extended, so this is the same value it always was in that case.
        /// </summary>
        public CellRect GateOccupiedRect
        {
            get { return RunRect; }
        }''')

# ------------------------------------------------------------------ 2. cell count follows the run
edit(FOOTPRINT,
     u'''            get
            {
                if (parent == null || parent.def == null) { return 1; }
                int area = parent.def.size.x * parent.def.size.z;
                return area < 1 ? 1 : area;
            }''',
     u'''            get
            {
                // Measured off the occupied rectangle rather than the def's size, so a gate bound
                // across three ordinary doors costs three cells of machine to energise and to
                // bring up -- which is the owner's "costs more to run" applied to the fallback
                // exactly as it applies to a real wide door.
                CellRect rect = GateOccupiedRect;
                if (rect.Area > 0) { return rect.Area; }
                if (parent == null || parent.def == null) { return 1; }
                int area = parent.def.size.x * parent.def.size.z;
                return area < 1 ? 1 : area;
            }''')

# ------------------------------------------------------------------ 3. the provider sees the run
edit(BINDING,
     u'''        private bool NativeDoorProvider()
        { return parent is Building_Door && parent.def != null && LegalGateFootprint(parent.def.size); }''',
     u'''        /// <summary>
        /// Whether this door can be a gate at all.
        ///
        /// The footprint tested is the **run's**, not the def's, so three adjacent ordinary doors
        /// bound together are a legal 1x3 and any one of them alone is a legal 1x1. A door whose
        /// own def is already a legal shape stays legal with no run, which is every gate that has
        /// never been extended.
        ///
        /// An **extension** is deliberately still a provider by this test -- it is a door of a
        /// legal shape. What stops it being operated is `IsDesignated`, which refuses it outright.
        /// </summary>
        private bool NativeDoorProvider()
        {
            if (!(parent is Building_Door) || parent.def == null) { return false; }
            if (LegalGateFootprint(parent.def.size)) { return true; }
            CellRect run = RunRect;
            return run.Area > 0 && LegalGateFootprint(new IntVec2(run.Width, run.Height));
        }''')

# ------------------------------------------------------------------ 4. an extension is not a gate
edit(BINDING,
     u'        public bool IsDesignated { get { return NativeDoorProvider() && nativeBindingSchema == 1 && nativeDesignated; } }',
     u'''        /// <summary>
        /// This door is an operable gate.
        ///
        /// **False for a run extension**, which is what keeps invariant 32 true: exactly one way a
        /// laboratory gate opens, and every entry point routes into it. An extension has no
        /// spin-up, no address, no console, no window and no operator, because as far as every
        /// other system in this mod is concerned it is not a gate -- it is part of one.
        /// </summary>
        public bool IsDesignated
        {
            get
            {
                return !IsRunExtension && NativeDoorProvider() &&
                    nativeBindingSchema == 1 && nativeDesignated;
            }
        }''')

# ------------------------------------------------------------------ 5. the save
comp_path = os.path.join(REPO, COMP)
comp = io.open(comp_path, encoding='utf-8').read()
assert 'ExposeGateRun' not in comp, 'already wired'
anchor = u'            base.PostExposeData();'
assert anchor in comp, 'PostExposeData anchor missing in CompRimroomsGate'
assert comp.count(anchor) == 1
edit(COMP, anchor, anchor + u'\n            ExposeGateRun();')

print('door run wired into rect, cell count, provider, designation and save')
