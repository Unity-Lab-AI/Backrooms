# -*- coding: utf-8 -*-
"""Stage five, part three: the door offers to re-open the place it led to."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

COMP = os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs")
text = io.open(COMP, encoding="utf-8").read()

OLD = """            bool marked = IsDesignated;
            yield return new Command_Action
            {
                defaultLabel = (marked ? "RR_Emergence_WithdrawLabel" : "RR_Emergence_MarkLabel").Translate(),
                defaultDesc = (marked ? "RR_Emergence_WithdrawDesc" : "RR_Emergence_MarkDesc").Translate(),
                icon = parent.def.uiIcon,
                action = delegate { Show(marked ? Withdraw() : Mark()); }
            };
        }"""

NEW = """            bool marked = IsDesignated;
            yield return new Command_Action
            {
                defaultLabel = (marked ? "RR_Emergence_WithdrawLabel" : "RR_Emergence_MarkLabel").Translate(),
                defaultDesc = (marked ? "RR_Emergence_WithdrawDesc" : "RR_Emergence_MarkDesc").Translate(),
                icon = parent.def.uiIcon,
                action = delegate { Show(marked ? Withdraw() : Mark()); }
            };

            // The place this door led to, while the company is not holding it open. Offered on
            // the door rather than only in Operations because this is where a player is standing
            // when they wonder why the door no longer goes anywhere.
            if (string.IsNullOrWhiteSpace(shelvedCoordinateId)) { yield break; }
            RimroomsCampaignComponent reopenCampaign = Campaign();
            CoordinateRecord shelved = reopenCampaign == null ? null
                : reopenCampaign.Coordinates.FirstOrDefault(record => record != null &&
                    record.Id == shelvedCoordinateId);
            if (shelved == null) { yield break; }
            bool room = OpenMapBudget.CanOpenAnother;
            yield return new Command_Action
            {
                defaultLabel = "RR_Release_ReopenLabel".Translate(),
                defaultDesc = (room ? "RR_Release_ReopenDesc" : "RR_Release_ReopenNoRoomDesc")
                    .Translate(OpenMapBudget.Describe()),
                icon = parent.def.uiIcon,
                // Disabled rather than hidden when there is no room: a player at their limit
                // needs to see that this is the thing they are at the limit of.
                Disabled = !room,
                disabledReason = room ? null : "RR_Release_ReopenNoRoomDesc".Translate(OpenMapBudget.Describe()),
                action = delegate { Show(Reopen(reopenCampaign, shelved)); }
            };
        }

        /// <summary>
        /// Open the shelved place again, through the same registration path that first created it.
        ///
        /// Nothing bespoke: `RegisterNaturalAddress` generates the site and registers the edge,
        /// exactly as it did at discovery. The coordinate record and its rooms were kept, so the
        /// place that comes back is the same place -- the same rooms in the same shape. **Its
        /// contents are not**, because the interior is generated from the seed, and the player was
        /// told that before they released it.
        /// </summary>
        private CompanyActionResult Reopen(RimroomsCampaignComponent campaign, CoordinateRecord shelved)
        {
            if (campaign == null || shelved == null) { return CompanyActionResult.Refused("RR_Release_UnknownPlace"); }
            if (!OpenMapBudget.CanOpenAnother)
            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }
            CompanyActionResult registered = PortalAddressService.RegisterNaturalAddress(
                parent, ApproachCell, shelved);
            // Only forgotten once the place is genuinely back. A failed re-open must leave the
            // door still offering to try, or a transient refusal would strand the place for ever.
            if (registered.Success) { ForgetShelvedPlace(); }
            return registered;
        }"""

if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
text = text.replace(OLD, NEW, 1)

# The file needs Linq and the campaign record type in scope.
if "using System.Linq;" not in text:
    text = text.replace("using System.Collections.Generic;",
                        "using System.Collections.Generic;\nusing System.Linq;", 1)
io.open(COMP, "w", encoding="utf-8", newline="").write(text)
print("re-open gizmo added")
