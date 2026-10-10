import io

p = 'src/RimroomsAsyncIndustries/Portals/PortalCrossingService.cs'
s = io.open(p, encoding='utf-8').read()

old = """            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.InMentalState ||
                pawn.Faction != Faction.OfPlayer)
            { return "RR_PortalCrossing_PawnNotEligible"; }
            if (pawn.RaceProps != null && pawn.RaceProps.Animal) { return null; }
            if (pawn.Drafted || !pawn.IsColonist || pawn.IsPrisoner || pawn.IsSlave || pawn.IsQuestLodger())
            { return "RR_PortalCrossing_PawnNotEligible"; }
            return null;"""

new = """            // Drafted is checked for everything, not only for people. A colonist under direct
            // combat control has never been allowed to wander through a gate, and the reason
            // is the situation rather than the species.
            //
            // Vanilla cannot draft an animal, so this read as dead code until the register was
            // consulted retroactively: row 78, **Draftable Animals - Releashed**, is in the
            // owner's profile and does exactly that. A drafted animal could cross while a
            // drafted colonist could not, which is the kind of gap that only shows up on
            // somebody else's mod list. Found by the register check, not by reading this.
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.InMentalState ||
                pawn.Drafted || pawn.Faction != Faction.OfPlayer)
            { return "RR_PortalCrossing_PawnNotEligible"; }
            // The remaining conditions only mean something for a person: an animal is never a
            // prisoner, a slave or a quest lodger.
            if (pawn.RaceProps != null && pawn.RaceProps.Animal) { return null; }
            if (!pawn.IsColonist || pawn.IsPrisoner || pawn.IsSlave || pawn.IsQuestLodger())
            { return "RR_PortalCrossing_PawnNotEligible"; }
            return null;"""

assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('drafted animals are refused, like drafted colonists')

# The same rule at the policy, so the chokepoint agrees with the service.
p = 'src/RimroomsAsyncIndustries/Portals/PortalTraversalPolicy.cs'
s = io.open(p, encoding='utf-8').read()
old = """            if (traveller.RaceProps != null && traveller.RaceProps.Animal)
            {
                if (!traveller.Spawned || traveller.Dead || traveller.Downed || traveller.InMentalState)
                { return "RR_PortalCrossing_PawnNotEligible"; }
                return null;
            }"""
new = """            if (traveller.RaceProps != null && traveller.RaceProps.Animal)
            {
                // Drafted included. Vanilla cannot draft an animal, but **Draftable Animals -
                // Releashed** (register row 78) is in the owner's profile and can, and a pawn
                // under direct combat control does not walk through a gate whatever it is.
                if (!traveller.Spawned || traveller.Dead || traveller.Downed ||
                    traveller.InMentalState || traveller.Drafted)
                { return "RR_PortalCrossing_PawnNotEligible"; }
                return null;
            }"""
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('policy agrees with the service')
