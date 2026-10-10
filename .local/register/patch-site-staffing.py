# -*- coding: utf-8 -*-
"""Extend proof-remote-sites with staffing."""
import ast
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, '.local', 'register', 'proof-remote-sites.py')
s = io.open(p, encoding='utf-8').read()

anchor = '''print("")
if failures:'''
assert anchor in s, 'tail anchor missing'

block = '''# --------------------------------------------------------------------------- staffing
# Arc 5: "remote sites need people". The consequence is that a shipment bound for an empty place
# WAITS -- a supplier does not unload with nobody to sign for it.
print("")
check("the branch can tell whether anybody is at a site", "IsSiteStaffed" in sites,
      '-- "remote sites need people" would be a sentence in a document')

staffed = re.search(r"public bool IsSiteStaffed\\(Map map\\).*?\\n        \\}", sites, re.S)
staffed_text = staffed.group(0) if staffed else ""
check("the staffing check was found", bool(staffed_text))
check("staffing requires somebody present on that map",
      "pawn.Map != map" in staffed_text,
      "-- staff anywhere at all would count as staffing every site")
check("staffing does not count the downed",
      "pawn.Downed" in staffed_text,
      "-- somebody unconscious on the floor cannot take delivery of anything")
check("staffing does not count prisoners or slaves",
      "pawn.IsPrisoner" in staffed_text and "pawn.IsSlave" in staffed_text,
      "-- neither is staff, and neither chose to be there")
check("staffing counts only the employed and living",
      "member.employed" in staffed_text and "pawn.Dead" in staffed_text)

# THE design. Two predicates, and the split is the point: the address is acceptable if the place
# is on the books, and the ARRIVAL needs somebody there. Ordering ahead must stay possible.
check("unloading is a separate question from addressing", "public bool CanUnloadAt" in sites,
      "-- one predicate would either punish ordering ahead or make staffing mean nothing")
unload = re.search(r"public bool CanUnloadAt\\(Map map\\).*?\\n        \\}", sites, re.S)
unload_text = unload.group(0) if unload else ""
check("unloading builds on the address check",
      "CanReceiveDeliveryAt(map)" in unload_text,
      "-- an unregistered place could be unloaded into by a staffed crew")
check("the headquarters is never held to the staffing rule",
      "if (map == headquarters) { return true; }" in unload_text,
      "-- a branch with nobody at home has a bigger problem and the clean-up team owns it")

# The order path must gate ARRIVAL, not the quote. Gating the quote punishes planning.
check("arrival waits when nobody is there",
      'SetAwaiting(order, "RR_Proc_SiteUnstaffed", now)' in procurement,
      "-- a shipment would land in an empty field")
check("arrival uses the unload check, not the address check",
      "campaign.CanUnloadAt(order.receivingMap)" in procurement,
      "-- staffing would not be consulted at the moment it matters")
check("ordering is NOT gated on staffing",
      "CanUnloadAt" not in procurement.split("private int TryDeliver")[0]
      if "private int TryDeliver" in procurement else "CanUnloadAt" in procurement,
      "-- a player could not order ahead while the crew was still walking there")
check("a waiting shipment is not a lost one",
      "SetAwaiting" in procurement and "SetRecovery(order, \\"RR_Proc_SiteUnstaffed\\")" not in procurement,
      "-- an unstaffed site must never turn a paid order into a recovery case")

# The player has to be able to see which site is holding their shipments.
check("the pane distinguishes unstaffed from unreachable",
      '"RR_Sites_RowUnstaffed"' in pane,
      "-- the state that quietly holds shipments would look identical to a healthy one")

for key in ("RR_Proc_SiteUnstaffed", "RR_Sites_RowUnstaffed"):
    check("%s has a keyed string" % key, ("<" + key + ">") in keyed,
          "-- the player would be shown the raw key")

''' + anchor

s = s.replace(anchor, block, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('proof extended with staffing')
ast.parse(s)
print('proof-remote-sites.py parses clean')
