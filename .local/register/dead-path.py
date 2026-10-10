import io, re

# --- 1. The cutoff component is entirely dead ------------------------------
# Its only host def was RR_EmergencyCutoff, now retired, and its own gate lookup searched
# for RR_MachineGate, also retired. The native path has had its own kill switch since the
# native binding landed (NativeGateKillSwitch.cs), which is what a player actually uses.
p = 'src/RimroomsAsyncIndustries/Gate/WorkGiver_RimroomsGate.cs'
s = io.open(p, encoding='utf-8').read()
start = s.index('    public sealed class CompProperties_RimroomsGateCutoff : CompProperties')
end = s.rindex('}\n')            # closing brace of the namespace
removed = s[start:end]
assert 'CompRimroomsGateCutoff' in removed and 'RR_EmergencyCutoff' in removed
s = s[:start] + s[end:]
s = s.rstrip() + '\n'
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('removed the dead cutoff component (%d chars)' % len(removed))

# --- 2. Gate console: the non-native branches are unreachable --------------
p = 'src/RimroomsAsyncIndustries/Gate/CompRimroomsGateConsole.cs'
s = io.open(p, encoding='utf-8').read()

old = """            if (nativeProvider)
            {
                if (!typeof(Building_WorkTable).IsAssignableFrom(parentDef.thingClass) &&
                    !typeof(Building_CommsConsole).IsAssignableFrom(parentDef.thingClass))
                { yield return "Native Rimrooms station requires an existing worktable or communications console."; }
                yield break;
            }
            if (parentDef.thingClass != typeof(Building_WorkTable))
            { yield return "RR_GateConsole must use Building_WorkTable for native bills."; }
            if (parentDef.size.x != 1 || parentDef.size.z != 1)
            { yield return "RR_GateConsole must use a 1x1 footprint."; }"""
new = """            // Only existing Core objects carry this component now. The custom RR_GateConsole
            // it used to also describe was retired in 0.9.0-dev, so there is no second shape
            // left to validate.
            if (!typeof(Building_WorkTable).IsAssignableFrom(parentDef.thingClass) &&
                !typeof(Building_CommsConsole).IsAssignableFrom(parentDef.thingClass))
            { yield return "Native Rimrooms station requires an existing worktable or communications console."; }"""
assert old in s
s = s.replace(old, new, 1)

old = """                if (linkedGate != null && linkedGate.Spawned && linkedGate.Map == parent.Map)
                { return linkedGate.TryGetComp<CompRimroomsGate>(); }
                if (NativeProvider) { return null; }
                ThingDef gateDef = DefDatabase<ThingDef>.GetNamedSilentFail("RR_MachineGate");
                if (gateDef == null) { return null; }
                linkedGate = parent.Map.listerBuildings.AllBuildingsColonistOfDef(gateDef)
                    .OrderBy(t => t.Position.DistanceToSquared(parent.Position)).FirstOrDefault();
                return linkedGate == null ? null : linkedGate.TryGetComp<CompRimroomsGate>();"""
new = """                if (linkedGate != null && linkedGate.Spawned && linkedGate.Map == parent.Map)
                { return linkedGate.TryGetComp<CompRimroomsGate>(); }
                // A station is bound to its gate explicitly, by the player, through the
                // designation UI. It used to fall back to hunting for the nearest
                // RR_MachineGate on the map; that def was retired in 0.9.0-dev and the guess
                // it made was never the right answer anyway once two gates could exist.
                return null;"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('gate console: dead branches removed')

# --- 3. Gate properties: the 3x3 footprint rule described a retired def ----
p = 'src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs'
s = io.open(p, encoding='utf-8').read()
old = """            if (!nativeProvider && (parentDef.size.x != 3 || parentDef.size.z != 3))
            { yield return "RR_MachineGate must use a 3x3 footprint."; }
"""
assert old in s
s = s.replace(old, '', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('gate properties: retired footprint rule removed')
