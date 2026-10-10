# -*- coding: utf-8 -*-
"""Point the clean-up team at the shared supply table."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, 'src', 'RimroomsAsyncIndustries', 'Company', 'FacilityRelief.cs')
s = io.open(p, encoding='utf-8-sig').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:70]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:70]
    s = s.replace(old, new, 1)


sub(u"""        /// <summary>Basic supplies, in Core defs. A fresh start's worth, not a reward.</summary>
        private static readonly KeyValuePair<string, int>[] ReliefSupplies =
        {
            new KeyValuePair<string, int>("MealSurvivalPack", 30),
            new KeyValuePair<string, int>("MedicineIndustrial", 12),
            new KeyValuePair<string, int>("Steel", 300),
            new KeyValuePair<string, int>("ComponentIndustrial", 12),
            new KeyValuePair<string, int>("WoodLog", 200),
        };

""", u"""        /// <summary>
        /// The clean-up team drops the corporation's crate at **full scale**.
        ///
        /// The table itself lives in <see cref="CompanySupplyDrop"/> because the unsolicited
        /// courier drops the same crate smaller. Same corporation, same warehouse, one table.
        /// </summary>
        private const float ReliefSupplyScale = 1f;

""")

sub(u"            AddReliefSupplies(payload);",
    u"            CompanySupplyDrop.Fill(payload, ReliefSupplyScale);")

sub(u"""        private static void AddReliefSupplies(List<Thing> payload)
        {
            for (int index = 0; index < ReliefSupplies.Length; index++)
            {
                KeyValuePair<string, int> line = ReliefSupplies[index];
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(line.Key);
                if (def == null) { continue; }
                int remaining = line.Value;
                int limit = def.stackLimit > 0 ? def.stackLimit : remaining;
                while (remaining > 0)
                {
                    Thing stack = ThingMaker.MakeThing(def);
                    if (stack == null) { break; }
                    stack.stackCount = Math.Min(remaining, limit);
                    payload.Add(stack);
                    remaining -= stack.stackCount;
                }
            }
        }

""", u"")

io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)
print('FacilityRelief now reads the shared supply table')

# ------------------------------------------------------------------ the proof follows the code
p = os.path.join(REPO, '.local', 'register', 'proof-facility-relief.py')
s = io.open(p, encoding='utf-8').read()
old = u"""supply_block = re.search(r"ReliefSupplies\\s*=\\s*\\{(.*?)\\n        \\};", source, re.S)
supplies = re.findall(r'"(\\w+)"', supply_block.group(1)) if supply_block else []"""
new = u"""SUPPLY = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Company", "CompanySupplyDrop.cs")
supply_source = io.open(SUPPLY, encoding="utf-8-sig").read()
supply_block = re.search(r"Lines\\s*=\\s*\\{(.*?)\\n        \\};", supply_source, re.S)
supplies = re.findall(r'"(\\w+)"', supply_block.group(1)) if supply_block else []"""
assert old in s, 'proof supply anchor missing'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('proof-facility-relief now reads the shared table')
