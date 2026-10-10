# -*- coding: utf-8 -*-
"""Make the refusal name the real cause. A flat battery said the address was not open.

Owner, 2026-10-01, from a running game: *"its the same problem as before: the laboratory address
for that is not open.... thats just clicking on the portal and trying to send them through not
working"*, and *"which i think is a power porblem"*.

**They were right, and the message sent them the wrong way.** `HasUsablePortalWindow` collapses
seven different conditions into one bool; `RimroomsPortalNetwork` turns a false into
`PortalNetworkResult.Closed`; `PortalTravelService` renders that as *"The laboratory connection for
that address is not open."* So a drained battery, a missing operator and a cut connection all read
as an address fault.

**This is the same correction already made twice in this project** -- `CalibrationBlockerKey` and
`StaffConsoleBlockerKey` exist because *"one `RR_Gate_JobUnavailable` covered four different
problems with four different fixes."* The gate gets a third blocker key, and the crossing path asks
it before falling back to the generic text.

**One authority.** `HasUsablePortalWindow` now asks the blocker key rather than restating the
conditions, so the predicate that gates the crossing and the message the player reads cannot
disagree. Two derivations of one rule is the defect this project keeps meeting.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPENING = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Gate", "PortalGateOpening.cs")
TRAVEL = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals", "PortalTravelService.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed", "RR_Portals.xml")

OLD = u"""        public bool HasUsablePortalWindow(string connectionId, string openingId)
        {
            return !portalOwnerFault && !string.IsNullOrEmpty(portalOpeningId) &&
                portalConnectionId == connectionId && portalOpeningId == openingId &&
                string.IsNullOrEmpty(activeExpeditionId) && !IsEmergency &&
                (openingTicksRemaining > 0 || PortalOpeningIsIndefinite) &&
                CheckStationReadiness(assignedOperator).Success &&
                NativeStoredEnergy >= OpeningPowerDrawWatts * CompPower.WattsToWattDaysPerTick;
        }"""

NEW = u"""        /// <summary>
        /// Why a crossing cannot use this window right now, as a keyed reason, or null when it
        /// can.
        ///
        /// **Seven conditions used to collapse into one bool**, and the one message a player got
        /// was *"The laboratory connection for that address is not open."* So a drained battery
        /// reported an address fault, which cost the owner a session in a running game:
        /// *"its the same problem as before: the laboratory address for that is not open"*, and
        /// *"which i think is a power porblem"* -- they were right, and the text had sent them
        /// looking at the address.
        ///
        /// Third of its kind, after <c>CalibrationBlockerKey</c> and
        /// <c>StaffConsoleBlockerKey</c>, both added because one generic refusal covered several
        /// problems with several different fixes.
        /// </summary>
        public string PortalWindowBlockerKey(string connectionId, string openingId)
        {
            if (portalOwnerFault) { return "RR_PortalTravel_OwnerFault"; }
            if (string.IsNullOrEmpty(portalOpeningId) ||
                portalConnectionId != connectionId || portalOpeningId != openingId)
            { return "RR_PortalTravel_SessionClosed"; }
            if (!string.IsNullOrEmpty(activeExpeditionId))
            { return "RR_PortalTravel_ExpeditionHolds"; }
            if (IsEmergency) { return "RR_PortalTravel_InEmergency"; }
            if (openingTicksRemaining <= 0 && !PortalOpeningIsIndefinite)
            { return "RR_PortalTravel_WindowExpired"; }
            CompanyActionResult station = CheckStationReadiness(assignedOperator);
            if (!station.Success) { return station.MessageKey ?? "RR_Gate_OperatorLost"; }
            // **The one that was invisible.** Reported in watt-days so the number matches the
            // gate's own power readout rather than being a second unit nobody can compare.
            float needed = OpeningPowerDrawWatts * CompPower.WattsToWattDaysPerTick;
            if (NativeStoredEnergy < needed) { return "RR_PortalTravel_NoCharge"; }
            return null;
        }

        /// <summary>
        /// **Asks the blocker key rather than restating the conditions.** One authority, so the
        /// predicate that gates a crossing and the message a player reads cannot disagree.
        /// </summary>
        public bool HasUsablePortalWindow(string connectionId, string openingId)
        {
            return PortalWindowBlockerKey(connectionId, openingId) == null;
        }"""

text = io.open(OPENING, encoding="utf-8-sig").read()
if text.count(OLD) != 1:
    print("OPENING ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(OPENING, "w", encoding="utf-8-sig", newline="").write(text.replace(OLD, NEW, 1))

# ---------------------------------------------------------------- the crossing path asks it
OLD_TRAVEL = u"""            PortalNetworkResult availability = network.ValidateRouteStep(step);
            if (availability != PortalNetworkResult.Success)
            { return CompanyActionResult.Refused(AvailabilityKey(availability)); }"""

NEW_TRAVEL = u"""            PortalNetworkResult availability = network.ValidateRouteStep(step);
            if (availability != PortalNetworkResult.Success)
            {
                // **Ask the gate why before falling back to the generic text.** `Closed` covers
                // seven conditions, and the one the owner hit -- no stored charge -- read as an
                // address fault. A refusal that names the wrong thing is worse than a vague one,
                // because it sends somebody to fix something that is not broken.
                CompRimroomsGate blocked = connection.First == null || connection.First.Anchor == null
                    ? null : connection.First.Anchor.TryGetComp<CompRimroomsGate>();
                if (availability == PortalNetworkResult.Closed && blocked != null)
                {
                    string why = blocked.PortalWindowBlockerKey(connection.Id, connection.OpeningId);
                    if (why != null) { return CompanyActionResult.Refused(why); }
                }
                return CompanyActionResult.Refused(AvailabilityKey(availability));
            }"""

text = io.open(TRAVEL, encoding="utf-8-sig").read()
if text.count(OLD_TRAVEL) != 1:
    print("TRAVEL ANCHOR PROBLEM: %d" % text.count(OLD_TRAVEL))
    raise SystemExit(1)
io.open(TRAVEL, "w", encoding="utf-8-sig", newline="").write(text.replace(OLD_TRAVEL, NEW_TRAVEL, 1))

# ---------------------------------------------------------------- the words
ADDITION = u"""  <RR_PortalTravel_NoCharge>The gate has no stored charge to hold the aperture. Its circuit needs power in the batteries, not just a generator running — check the batteries on the same net as the gate. Any number of them count.</RR_PortalTravel_NoCharge>
  <RR_PortalTravel_OwnerFault>This gate is not the one that holds that connection.</RR_PortalTravel_OwnerFault>
  <RR_PortalTravel_ExpeditionHolds>An expedition is using that connection. Recall or close it first.</RR_PortalTravel_ExpeditionHolds>
  <RR_PortalTravel_InEmergency>That connection is in emergency. The crew have a return window; nobody else goes through.</RR_PortalTravel_InEmergency>
  <RR_PortalTravel_WindowExpired>That opening has run out of time.</RR_PortalTravel_WindowExpired>
"""
keyed = io.open(KEYED, encoding="utf-8-sig").read()
CLOSE = u"</LanguageData>"
if keyed.count(CLOSE) != 1:
    print("KEYED ANCHOR PROBLEM: %d" % keyed.count(CLOSE))
    raise SystemExit(1)
io.open(KEYED, "w", encoding="utf-8-sig", newline="").write(
    keyed.replace(CLOSE, ADDITION + CLOSE, 1))

after_open = io.open(OPENING, encoding="utf-8-sig").read()
after_travel = io.open(TRAVEL, encoding="utf-8-sig").read()
after_keyed = io.open(KEYED, encoding="utf-8-sig").read()
failures = []
if u"public string PortalWindowBlockerKey(" not in after_open:
    failures.append("the blocker key was not defined")
if u"return PortalWindowBlockerKey(connectionId, openingId) == null;" not in after_open:
    failures.append("HasUsablePortalWindow does not delegate -- two derivations of one rule")
if u"blocked.PortalWindowBlockerKey(connection.Id, connection.OpeningId)" not in after_travel:
    failures.append("THE BLOCKER KEY IS DEFINED AND NEVER CALLED")
for key in ("RR_PortalTravel_NoCharge", "RR_PortalTravel_OwnerFault",
            "RR_PortalTravel_ExpeditionHolds", "RR_PortalTravel_InEmergency",
            "RR_PortalTravel_WindowExpired"):
    if (u"<%s>" % key) not in after_keyed:
        failures.append("%s has no string" % key)
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("the refusal names the real cause; five new reasons, all with strings")
