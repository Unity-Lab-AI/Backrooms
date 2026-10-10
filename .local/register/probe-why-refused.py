# -*- coding: utf-8 -*-
"""`RR_Generation_InvalidRoomGraph` covers a dozen rules. Make the probe say which one.

The key is shared by every structural refusal in `ValidateRooms` -- room count, duplicate indices,
family counts, span parity, bounds, overlap, link symmetry, grid adjacency. Knowing the key tells
you a candidate was refused and nothing about why.

So the probe reports **observations** about the refused layout: how many rooms, which unique
families are present and how many of each, the first overlapping pair, the first link whose
centres share no axis, the first odd or out-of-range span. These are facts read off the layout --
not a second implementation of the validator -- and any one of them points straight at the rule.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = os.path.join(REPO, ".local", "harness", "PlannerProbe", "Program.cs")

OLD = u"""                        object[] why = { built, null };
                        validateRooms.Invoke(null, why);
                        if (why[1] != null)
                        { reasons.Add("candidate refused: " + why[1]); }
                        else if (which == 0)
                        { reasons.Add("candidate refused: reachability or family rule"); }"""

NEW = u"""                        object[] why = { built, null };
                        validateRooms.Invoke(null, why);
                        string key = why[1] == null ? "reachability or a family rule" : why[1].ToString();
                        reasons.Add("candidate refused: " + key + " -- " + Describe((IList)built));"""

DESCRIBE = u'''        /// <summary>
        /// Facts about a refused layout, so `RR_Generation_InvalidRoomGraph` stops being a dozen
        /// rules wearing one name.
        ///
        /// **Observations, not a second validator.** Every line here reads the layout and
        /// reports; none of it decides whether the layout is acceptable. Re-implementing
        /// `ValidateRooms` in the probe would give two opinions about one question, which is the
        /// defect this whole harness exists to catch.
        /// </summary>
        private static string Describe(IList layout)
        {
            var families = new Dictionary<string, int>();
            foreach (object room in layout)
            {
                string family = Field<string>(room, "familyId") ?? "(null)";
                int seen;
                families[family] = families.TryGetValue(family, out seen) ? seen + 1 : 1;
            }
            var report = new List<string> { layout.Count + " rooms" };
            foreach (string unique in new[] { "threshold_room", "office_copy", "return_gallery",
                                              "service_passage" })
            {
                int seen;
                report.Add(unique + "=" + (families.TryGetValue(unique, out seen) ? seen : 0));
            }

            for (int index = 0; index < layout.Count; index++)
            {
                object room = layout[index];
                int width = Field<int>(room, "width");
                int height = Field<int>(room, "height");
                if (width % 2 != 0 || height % 2 != 0)
                { report.Add("odd span at room " + index + " (" + width + "x" + height + ")"); break; }
            }

            for (int index = 0; index < layout.Count; index++)
            {
                var a = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[index], null);
                if (a.minX < 1 || a.minZ < 1 || a.maxX > 298 || a.maxZ > 298)
                { report.Add("room " + index + " off the map " + a); break; }
            }

            bool overlapFound = false;
            for (int index = 0; index < layout.Count && !overlapFound; index++)
            {
                var a = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[index], null);
                for (int other = index + 1; other < layout.Count; other++)
                {
                    var b = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[other], null);
                    if (!a.Overlaps(b)) { continue; }
                    report.Add("rooms " + index + " and " + other + " overlap " + a + " / " + b);
                    overlapFound = true;
                    break;
                }
            }

            bool axisFound = false;
            for (int index = 0; index < layout.Count && !axisFound; index++)
            {
                var a = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[index], null);
                foreach (int linked in Field<List<int>>(layout[index], "links"))
                {
                    if (linked <= index || linked >= layout.Count) { continue; }
                    var b = (Verse.CellRect)roomType.GetProperty("Bounds").GetValue(layout[linked], null);
                    if (a.CenterCell.x == b.CenterCell.x || a.CenterCell.z == b.CenterCell.z) { continue; }
                    report.Add("link " + index + "-" + linked + " shares no axis "
                               + a.CenterCell + " / " + b.CenterCell);
                    axisFound = true;
                    break;
                }
            }

            return string.Join(", ", report.ToArray());
        }

'''

ANCHOR = u"        /// <summary>\n        /// Cells in this room that could hold a landmark"

text = io.open(PROBE, encoding="utf-8").read()
if text.count(OLD) != 1 or text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d / %d" % (text.count(OLD), text.count(ANCHOR)))
    raise SystemExit(1)
text = text.replace(OLD, NEW, 1)
text = text.replace(ANCHOR, DESCRIBE + ANCHOR, 1)
io.open(PROBE, "w", encoding="utf-8", newline="").write(text)
print("the probe describes a refused layout instead of naming a key")
