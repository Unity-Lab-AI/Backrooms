# -*- coding: utf-8 -*-
"""Extend proof-remote-sites with company-to-site logistics."""
import ast
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, '.local', 'register', 'proof-remote-sites.py')
s = io.open(p, encoding='utf-8').read()

anchor = '''print("")
if failures:'''
assert anchor in s, 'tail anchor missing'

block = '''# --------------------------------------------------------------------------- deliveries
# Arc 5 names "company-to-site logistics". Procurement had the headquarters written into it in
# seven places, while `ProcurementOrderRecord.receivingMap` already existed and the DELIVERY path
# already honoured it -- so only the selection was pinned.
procurement = strip_comments(io.open(os.path.join(SRC, "Procurement",
                                                  "RimroomsProcurementComponent.cs"),
                                     encoding="utf-8-sig").read())
proc_ui = strip_comments(io.open(os.path.join(SRC, "UI", "OperationsProcurement.cs"),
                                 encoding="utf-8-sig").read())

print("")
check("the branch decides where it may receive", "CanReceiveDeliveryAt" in sites,
      "-- nothing would distinguish a site on the books from any map at all")
check("a delivery destination must be on the books",
      procurement.count('"RR_Proc_DestinationNotOnTheBooks"') >= 2,
      "-- quoting and redirecting must both refuse an unregistered place")
check("the quote takes its destination from the zone's own map",
      "Map destination = receivingZone == null ? null : receivingZone.Map;" in procurement,
      "-- passing a map separately lets the two disagree")
check("the quote no longer pins the destination to the headquarters",
      "receivingMap = campaign.Headquarters," not in procurement,
      "-- a site could be billed daily and never receive anything")
check("accepting validates against the quote's own destination",
      "IsReceivingZoneValid(quote.receivingMap, quote.receivingZone, itemDef)" in procurement,
      "-- a quote to a site would be refused at acceptance")
check("accepting checks the zone still sits on that destination",
      "quote.receivingZone.Map != quote.receivingMap" in procurement,
      "-- a zone moved between quoting and accepting would deliver into the wrong place")

# THE latent bug. The redirect updated the zone and not the map. Harmless while one map was
# allowed; the moment a second became legal, a cross-map redirect would leave the order pointing
# at the old map and the delivery check would refuse it on every attempt, for ever.
check("redirecting updates the receiving MAP, not only the zone",
      "order.receivingMap = redirectTo;" in procurement,
      "-- a cross-map redirect would stick awaiting a condition that can never come true")
redirect_assign = procurement.find("order.receivingMap = redirectTo;")
zone_assign = procurement.find("order.receivingZone = receivingZone;")
check("the map is set alongside the zone it belongs to",
      redirect_assign != -1 and zone_assign != -1 and abs(zone_assign - redirect_assign) < 200,
      "-- the two must move together or a later reader sees a mismatched pair")

# A site's map can be unloaded; the headquarters' cannot. The reason shown had to stop saying HQ.
check("an unloaded destination no longer blames the headquarters",
      '"RR_Proc_ReceivingMapUnavailable"' in procurement,
      "-- a site shipment would report the HQ as missing")

# Reachable at all: the menu has to offer site stockpiles or the feature is paperwork only.
check("the order menu lists stockpiles at every destination",
      "DeliveryStockpiles(campaign)" in proc_ui,
      "-- only headquarters stockpiles would be offered")
check("the headquarters-only listing is gone",
      "HeadquartersStockpiles(" not in proc_ui,
      "-- the old listing would still be the one in use")
check("a stockpile says where it is when there is more than one place",
      "StockpileLabel(" in proc_ui,
      "-- two stockpiles named Stockpile on different maps would be indistinguishable")

for key in ("RR_Proc_DestinationNotOnTheBooks", "RR_Proc_ReceivingMapUnavailable",
            "RR_Proc_AtHeadquarters", "RR_Proc_ZoneAtPlace"):
    check("%s has a keyed string" % key, ("<" + key + ">") in keyed,
          "-- the player would be shown the raw key")

''' + anchor

s = s.replace(anchor, block, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('proof-remote-sites extended with deliveries')
ast.parse(s)
print('proof-remote-sites.py parses clean')
