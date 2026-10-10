import io

def patch(path, pairs):
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, path + ' :: ' + old[:70]
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('patched ' + path.split('/')[-1])

P = 'src/RimroomsAsyncIndustries/Portals/'

patch(P + 'PortalCrossingService.cs', [
 # The validation chokepoint permits whatever legitimately reached it. An animal only ever
 # reaches it through a player order; a work adapter still gates itself on the colonist-only
 # rule before it will plan anything.
 ('            string traveller = PortalTraversalPolicy.TravellerFailureKey(pawn);',
  '            string traveller = PortalTraversalPolicy.OrderedCrossingFailureKey(pawn);'),
 ('        /// <summary>\n'
  '        /// The single eligibility rule, shared with callers so an order can refuse\n'
  '        /// with the same reason the crossing itself would give. Mechs, subhumans and\n'
  '        /// non-colonists are deliberately out of scope.\n'
  '        /// </summary>\n'
  '        public static string EligibilityFailureKey(Pawn pawn)\n'
  '        {\n'
  '            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.Drafted || pawn.InMentalState ||\n'
  '                pawn.Faction != Faction.OfPlayer || !pawn.IsColonist || pawn.IsPrisoner || pawn.IsSlave || pawn.IsQuestLodger())\n'
  '            { return "RR_PortalCrossing_PawnNotEligible"; }\n'
  '            return null;\n'
  '        }',
  '        /// <summary>\n'
  '        /// The single eligibility rule, shared with callers so an order can refuse with the\n'
  '        /// same reason the crossing itself would give. Mechs and subhumans are deliberately\n'
  '        /// out of scope.\n'
  '        ///\n'
  '        /// **Owner direction, 2026-09-29:** a player-owned animal may cross freely, so one is\n'
  '        /// eligible here on the same terms a colonist is. The conditions that differ are the\n'
  '        /// ones that only mean something for a person: an animal is never a prisoner, a slave\n'
  '        /// or a quest lodger, and "drafted" is not a state it has.\n'
  '        /// </summary>\n'
  '        public static string EligibilityFailureKey(Pawn pawn)\n'
  '        {\n'
  '            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.InMentalState ||\n'
  '                pawn.Faction != Faction.OfPlayer)\n'
  '            { return "RR_PortalCrossing_PawnNotEligible"; }\n'
  '            if (pawn.RaceProps != null && pawn.RaceProps.Animal) { return null; }\n'
  '            if (pawn.Drafted || !pawn.IsColonist || pawn.IsPrisoner || pawn.IsSlave || pawn.IsQuestLodger())\n'
  '            { return "RR_PortalCrossing_PawnNotEligible"; }\n'
  '            return null;\n'
  '        }'),
])

patch(P + 'PortalTravelService.cs', [
 # Ordered crossings are the only path a non-colonist can take, so the fit rule lives where
 # the connection is known. A colonist is body size 1.0 and fits the narrowest gate there is,
 # so work-driven crossings need no second check.
 ('            if (crossings.HasUnresolvedCrossing(pawn))\n'
  '            { return CompanyActionResult.Refused("RR_PortalCrossing_PawnInTransit"); }',
  '            if (crossings.HasUnresolvedCrossing(pawn))\n'
  '            { return CompanyActionResult.Refused("RR_PortalCrossing_PawnInTransit"); }\n'
  '            string fit = PortalTraversalPolicy.FitFailureKey(pawn, DoorwayWidth(connection));\n'
  '            if (fit != null) { return CompanyActionResult.Refused(fit); }'),
 ('        /// <summary>Reconcile one interrupted crossing. Never invents a person or item.</summary>',
  '        /// <summary>\n'
  '        /// How wide the doorway of a connection is, in cells.\n'
  '        ///\n'
  '        /// Taken from the connection\'s **first** endpoint for every kind, which for a\n'
  '        /// laboratory connection is the gate. A connection has one width in both directions:\n'
  '        /// the gate is the machine that forms the aperture, and the doorway on the Backrooms\n'
  '        /// side is just where you arrive. Measuring each end separately would let a pack\n'
  '        /// animal walk in through a wide gate and then be unable to come home, because a\n'
  '        /// generated return threshold is always an ordinary one-cell door.\n'
  '        /// </summary>\n'
  '        public static int DoorwayWidth(PortalConnectionRecord connection)\n'
  '        {\n'
  '            Thing anchor = connection == null || connection.First == null ? null : connection.First.Anchor;\n'
  '            if (anchor == null) { return 1; }\n'
  '            CompRimroomsGate gate = anchor.TryGetComp<CompRimroomsGate>();\n'
  '            if (gate != null && gate.IsDesignated) { return gate.GateWidth; }\n'
  '            if (anchor.def == null) { return 1; }\n'
  '            int span = anchor.def.size.x > anchor.def.size.z ? anchor.def.size.x : anchor.def.size.z;\n'
  '            return span < 1 ? 1 : span;\n'
  '        }\n'
  '\n'
  '        /// <summary>Reconcile one interrupted crossing. Never invents a person or item.</summary>'),
])

# Keyed strings.
p = 'Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml'
s = io.open(p, encoding='utf-8-sig').read()
add = (u'  <RR_PortalTraversal_TooLargeForGate>Too large for this gate. Widen the opening: a one-cell '
       u'doorway passes people and working animals, a two-cell doorway passes pack animals like '
       u'muffalo and dromedaries, and three cells or more passes anything.</RR_PortalTraversal_TooLargeForGate>\n')
assert 'RR_PortalTraversal_TooLargeForGate' not in s
s = s.replace(u'</LanguageData>', add + u'</LanguageData>', 1)
# The old refusal text said colonists only, which is no longer true.
old = (u"<RR_PortalCrossing_PawnNotEligible>Only an available colonist of this company can cross. "
       u"Drafted, downed, dead, prisoner, enslaved, guest and distressed people cannot.</RR_PortalCrossing_PawnNotEligible>")
new = (u"<RR_PortalCrossing_PawnNotEligible>Only this company's own available people and animals can "
       u"cross. Drafted, downed, dead, prisoner, enslaved, guest and distressed people cannot, and "
       u"neither can a downed or panicking animal.</RR_PortalCrossing_PawnNotEligible>")
assert old in s
s = s.replace(old, new, 1)
old = (u"<RR_PortalTraversal_NotOurPerson>Only this company's own people walk through a gate. Anyone "
       u"or anything else comes back only by being carried through by one of them.</RR_PortalTraversal_NotOurPerson>")
new = (u"<RR_PortalTraversal_NotOurPerson>Only this company's own people and animals walk through a "
       u"gate. Anyone or anything else comes back only by being carried through by one of "
       u"them.</RR_PortalTraversal_NotOurPerson>")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('keyed strings updated')
