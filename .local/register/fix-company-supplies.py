# -*- coding: utf-8 -*-
"""List what the COMPANY adds, read from our own def, so another mod cannot empty the list.

Owner, verbatim: *"like in the company start up that pop up should list all the equipemnet for the
gate that u get added to ur start on top of what u fill out in edb prepare carfully"*

THE SUPPLIES SECTION ASKED THE WRONG OBJECT. `SupplySummary` walks `Find.Scenario.AllParts` --
the LIVE scenario -- and EdB Prepare Carefully rewrites exactly those parts. Its assembly carries
`ReplaceScenarioPatch`, `ShouldReplaceScenarioPart`, `OriginalScenarioParts`,
`ReplacedScenarioParts`, `RestoreScenarioParts` and `CreateScenarioPartForCustomizedEquipment`:
**it swaps the scenario's starting-thing parts out for parts built from the player's edited
equipment list, and puts the originals back afterwards.** So at the moment this page draws, the
live scenario is not the company's scenario, and what the company contributes is unreportable
from it.

Register row [85] EdB Prepare Carefully is stance **Optional**, firmness **Provisional**, and its
review says in as many words: *"Check authored company starts, initial gear and limits"* and
*"never a runtime dependency"*. Both halves are honoured here -- nothing is patched, nothing is
named, nothing is required. The page simply stops asking a question the live scenario cannot
answer.

SO IT ASKS THE DEF. `CompanySupplies` finds the `ScenarioDef` whose scenario declares this very
start and reads the starting things from THERE. That is the shipped, authored list: it is the
same whether Prepare Carefully is installed, absent, or mid-edit.

PUBLIC API ONLY, NO REFLECTION. `ScenPart_ThingCount.thingDef`/`stuff`/`count` are `protected`,
and this package uses no Harmony and no reflection. `ScenPart.GetSummaryListEntries` is public and
already returns `GenLabel.ThingLabel(thingDef, stuff, count)` -- Core's own phrasing of exactly
this list. `PlayerStartingThings` is still never called: that one builds real objects.

AND BOTH LISTS ARE SHOWN, because the owner asked for *"on top of what u fill out"*. The company's
own contribution is named as such, and whatever the live scenario is carrying is listed under its
own heading beneath it. When the two differ, that is said plainly rather than left for the player
to work out from two lists that disagree.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPONENT = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Scenario",
                         "RimroomsStartupComponent.cs")

OLD = u'''        internal static List<string> SupplySummary()
        {
            // Never call PlayerStartingThings here: that API creates actual objects.
            var lines = new List<string>();
            if (Find.Scenario != null)
            {
                foreach (ScenPart part in Find.Scenario.AllParts)
                {
                    foreach (string entry in part.GetSummaryListEntries("PlayerStartsWith"))
                    { if (!string.IsNullOrEmpty(entry)) { lines.Add(entry); } }
                    if (!(part is ScenPart_StartingThing_Defined) && !(part is ScenPart_RimroomsStart) &&
                        !(part is ScenPart_ConfigPage_ConfigureStartingPawnsBase))
                    {
                        string summary = part.Summary(Find.Scenario);
                        if (!string.IsNullOrEmpty(summary) && !lines.Contains(summary)) { lines.Add(summary); }
                    }
                }
            }
            return lines;
        }'''

NEW = u'''        internal static List<string> SupplySummary()
        {
            // Never call PlayerStartingThings here: that API creates actual objects.
            var lines = new List<string>();
            if (Find.Scenario != null)
            {
                foreach (ScenPart part in Find.Scenario.AllParts)
                {
                    foreach (string entry in part.GetSummaryListEntries("PlayerStartsWith"))
                    { if (!string.IsNullOrEmpty(entry)) { lines.Add(entry); } }
                    if (!(part is ScenPart_StartingThing_Defined) && !(part is ScenPart_RimroomsStart) &&
                        !(part is ScenPart_ConfigPage_ConfigureStartingPawnsBase))
                    {
                        string summary = part.Summary(Find.Scenario);
                        if (!string.IsNullOrEmpty(summary) && !lines.Contains(summary)) { lines.Add(summary); }
                    }
                }
            }
            return lines;
        }

        /// <summary>
        /// The scenario this start is authored in, found by the start it declares.
        ///
        /// By the def rather than by `Find.Scenario`, because the live scenario is not reliably
        /// this one: a setup utility may have swapped its parts out for the player's edited
        /// equipment while its own page is open. Matching on `startDef` means a renamed or
        /// re-ordered scenario still resolves, and a start with no scenario returns null rather
        /// than guessing at the first one.
        /// </summary>
        internal static ScenarioDef AuthoredScenario(RimroomsStartDef start)
        {
            if (start == null) { return null; }
            foreach (ScenarioDef candidate in DefDatabase<ScenarioDef>.AllDefsListForReading)
            {
                if (candidate.scenario == null) { continue; }
                foreach (ScenPart part in candidate.scenario.AllParts)
                {
                    ScenPart_RimroomsStart ours = part as ScenPart_RimroomsStart;
                    if (ours != null && ours.startDef == start) { return candidate; }
                }
            }
            return null;
        }

        /// <summary>
        /// What the company itself adds to the start, as the shipped scenario declares it.
        ///
        /// Owner, verbatim: *"that pop up should list all the equipemnet for the gate that u get
        /// added to ur start on top of what u fill out in edb prepare carfully"*.
        ///
        /// **Read from the def, never from the live scenario.** A setup utility that rewrites the
        /// scenario's starting-thing parts makes `SupplySummary` report that utility's list
        /// instead of the company's -- which is why this page showed no supplies at all. This
        /// answers the question the owner actually asked, and answers it the same way whether
        /// such a utility is installed or not.
        ///
        /// `GetSummaryListEntries` is Core's own public phrasing of a starting thing and costs
        /// nothing. `PlayerStartingThings` is deliberately not used: it builds real objects.
        /// </summary>
        internal static List<string> CompanySupplies(RimroomsStartDef start)
        {
            var lines = new List<string>();
            ScenarioDef authored = AuthoredScenario(start);
            if (authored == null) { return lines; }
            foreach (ScenPart part in authored.scenario.AllParts)
            {
                foreach (string entry in part.GetSummaryListEntries("PlayerStartsWith"))
                { if (!string.IsNullOrEmpty(entry)) { lines.Add(entry); } }
            }
            return lines;
        }

        /// <summary>
        /// Whether the live scenario is carrying a different starting-equipment list from the one
        /// this company authored.
        ///
        /// Stated on the page rather than reconciled. Something else is managing the equipment --
        /// which is a legitimate thing for a player to have chosen -- and the honest report is
        /// that the two lists differ, not a guess about which one will win.
        /// </summary>
        internal static bool EquipmentManagedElsewhere(RimroomsStartDef start)
        {
            List<string> authored = CompanySupplies(start);
            if (authored.Count == 0) { return false; }
            var live = new List<string>();
            if (Find.Scenario != null)
            {
                foreach (ScenPart part in Find.Scenario.AllParts)
                {
                    foreach (string entry in part.GetSummaryListEntries("PlayerStartsWith"))
                    { if (!string.IsNullOrEmpty(entry)) { live.Add(entry); } }
                }
            }
            if (live.Count != authored.Count) { return true; }
            var remaining = new List<string>(live);
            foreach (string entry in authored)
            {
                if (!remaining.Remove(entry)) { return true; }
            }
            return false;
        }'''

text = io.open(COMPONENT, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(COMPONENT, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("CompanySupplies / AuthoredScenario / EquipmentManagedElsewhere added")
