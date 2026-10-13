using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimPLC
{
    /// <summary>One choice in a picker: what is shown, the value it inserts, and the requires entry it brings (DLC / mod gate).</summary>
    public sealed class PickItem
    {
        public string Label;
        public string Value;
        public string Requires;
        public string Group;
    }

    /// <summary>A searchable list (a FloatMenu cannot hold every thing def of a 294-mod profile).</summary>
    public sealed class Dialog_Pick : Window
    {
        private readonly string title;
        private readonly List<PickItem> items;
        private readonly Action<PickItem> picked;
        private string filter = string.Empty;
        private Vector2 scroll;

        public Dialog_Pick(string title, List<PickItem> items, Action<PickItem> picked)
        {
            this.title = title;
            this.items = items;
            this.picked = picked;
            doCloseX = true;
            closeOnClickedOutside = true;
            absorbInputAroundWindow = true;
        }

        public override Vector2 InitialSize => new Vector2(560f, 640f);

        public override void DoWindowContents(Rect inRect)
        {
            Text.Font = GameFont.Small;
            Widgets.Label(new Rect(inRect.x, inRect.y, inRect.width - 30f, 26f), title);
            filter = Widgets.TextField(new Rect(inRect.x, inRect.y + 30f, inRect.width, 26f), filter);
            string f = filter.Trim().ToLowerInvariant();
            List<PickItem> rows = f.Length == 0 ? items : items.Where(i => (i.Label + " " + i.Value + " " + i.Group).ToLowerInvariant().Contains(f)).ToList();
            var outRect = new Rect(inRect.x, inRect.y + 62f, inRect.width, inRect.height - 62f);
            var view = new Rect(0f, 0f, outRect.width - 16f, rows.Count * 22f);
            Widgets.BeginScrollView(outRect, ref scroll, view);
            Text.Font = GameFont.Tiny;
            for (int i = 0; i < rows.Count; i++)
            {
                float y = i * 22f;
                if (y + 22f < scroll.y || y > scroll.y + outRect.height) continue;
                var row = new Rect(0f, y, view.width, 22f);
                Widgets.DrawHighlightIfMouseover(row);
                PickItem it = rows[i];
                string text = (it.Group != null ? "[" + it.Group + "] " : string.Empty) + it.Label +
                              (it.Label != it.Value ? "   " + it.Value : string.Empty) + (it.Requires != null ? "   (" + it.Requires + ")" : string.Empty);
                Widgets.Label(row, text);
                if (Widgets.ButtonInvisible(row))
                {
                    picked(it);
                    Close();
                }
            }

            Text.Font = GameFont.Small;
            Widgets.EndScrollView();
        }

        /// <summary>The requires entry for a def: its DLC, mod:&lt;packageId&gt; for another mod, null for Core.</summary>
        public static string RequiresOf(Def def)
        {
            ModContentPack pack = def?.modContentPack;
            if (pack == null) return null;
            string id = (pack.PackageId ?? string.Empty).ToLowerInvariant();
            switch (id)
            {
                case "ludeon.rimworld": return null;
                case "ludeon.rimworld.royalty": return "Royalty";
                case "ludeon.rimworld.ideology": return "Ideology";
                case "ludeon.rimworld.biotech": return "Biotech";
                case "ludeon.rimworld.anomaly": return "Anomaly";
                case "ludeon.rimworld.odyssey": return "Odyssey";
            }

            return pack.IsOfficialMod ? null : "mod:" + pack.PackageId;
        }

        /// <summary>Every key a condition can name: the catalogue, what is measured now, marks, tags and the def families.</summary>
        public static List<PickItem> Keys(RimPLCGameComponent plc, string family)
        {
            var o = new List<PickItem>();
            Ladder book = RimPLCMod.Book;
            switch (family)
            {
                case "sensor":
                    var seen = new HashSet<string>();
                    foreach (var kv in book.Sensors)
                    {
                        if (kv.Key.Contains("<") || !seen.Add(kv.Key)) continue;
                        o.Add(new PickItem { Label = kv.Key, Value = kv.Key, Group = "catalogue" });
                    }

                    foreach (string k in (plc.Last?.State.Keys ?? Enumerable.Empty<string>()).OrderBy(k => k, StringComparer.Ordinal))
                    {
                        if (k == "tags" || k.StartsWith("mark_", StringComparison.Ordinal) || !Validate.KeyRule.IsMatch(k) || !seen.Add(k)) continue;
                        o.Add(new PickItem { Label = k, Value = k, Group = "measured" });
                    }

                    break;
                case "mark":
                    var marks = new HashSet<string>(plc.Marks.Select(kv => kv.Key));
                    foreach (var kv in book.MarkDefaults) marks.Add(kv.Key);
                    foreach (Rung r in Engine.Merge(book, plc.MyRungs))
                    {
                        foreach (var leaf in Engine.Leaves(r.When))
                        {
                            if (leaf.Key.StartsWith("mark_", StringComparison.Ordinal)) marks.Add(leaf.Key.Substring(5));
                        }
                    }

                    o.AddRange(marks.OrderBy(m => m, StringComparer.Ordinal).Select(m => new PickItem { Label = "mark_" + m, Value = "mark_" + m, Group = "mark" }));
                    break;
                case "tag":
                    o.AddRange(book.Variables.Select(kv => new PickItem { Label = kv.Key, Value = kv.Key, Group = "variable" }));
                    o.AddRange(book.Constants.Select(kv => new PickItem { Label = kv.Key, Value = kv.Key, Group = "constant" }));
                    break;
                case "item":
                case "building":
                    foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading.OrderBy(d => d.defName, StringComparer.Ordinal))
                    {
                        bool want = family == "item" ? d.category == ThingCategory.Item : d.category == ThingCategory.Building && d.BuildableByPlayer;
                        string k = want ? Sensors.CountKey(d) : null;
                        if (k == null) continue;
                        o.Add(new PickItem { Label = d.LabelCap.RawText ?? d.defName, Value = k, Requires = RequiresOf(d), Group = family });
                    }

                    break;
                case "research":
                    foreach (ResearchProjectDef d in DefDatabase<ResearchProjectDef>.AllDefsListForReading.OrderBy(d => d.defName, StringComparer.Ordinal))
                    {
                        string k = "research_" + d.defName.ToLowerInvariant();
                        if (!Validate.KeyRule.IsMatch(k)) continue;
                        o.Add(new PickItem { Label = d.LabelCap.RawText ?? d.defName, Value = k, Requires = RequiresOf(d), Group = "research" });
                    }

                    break;
                case "alert":
                    foreach (Type t in typeof(Alert).AllSubclassesNonAbstract().OrderBy(t => t.Name, StringComparer.Ordinal))
                    {
                        string k = Sensors.AlertKey(t.Name);
                        if (!Validate.KeyRule.IsMatch(k)) continue;
                        o.Add(new PickItem { Label = t.Name, Value = k, Group = "alert" });
                    }

                    break;
            }

            return o;
        }
    }

    /// <summary>
    /// The rung editor (docs/RIMPLC_DESIGN.md 6): id, priority, conditions (key + operator + value, with key, def and
    /// {TAG} pickers), nested instructions as JSON (any / not / ton / tof / ctu / ons templates), then lines, notice,
    /// why, requires. Save runs the rimplc-check rules (Validate) through the same upsert path as the AI API, as a
    /// player rung: a new rung is player-&lt;id&gt;, editing a book rung makes a player copy with the book's id.
    /// </summary>
    public sealed class Dialog_RungEditor : Window
    {
        private sealed class Cond
        {
            public string Key = string.Empty;
            public string Op = "=";
            public string Value = string.Empty;
            public string Raw;   // a nested instruction, edited as JSON
        }

        private static readonly string[] OpChoices = { "is true", "is false", "=", "<", ">", "<=", ">=", "!=", "text" };

        private readonly RimPLCGameComponent plc;
        private readonly bool editingBook;
        private string id;
        private string priority;
        private readonly List<Cond> conds = new List<Cond>();
        private string thenText;
        private string notice;
        private string why;
        private readonly List<string> requires = new List<string>();
        private JsonObject extra;   // fields the form does not edit (latch, never, chain, check, coils, family) kept as they were
        private List<string> errors = new List<string>();
        private List<string> notes = new List<string>();
        private Vector2 scroll;

        public Dialog_RungEditor(RimPLCGameComponent plc, Rung rung)
        {
            this.plc = plc;
            doCloseX = true;
            absorbInputAroundWindow = true;
            forcePause = false;
            if (rung == null)
            {
                id = "player-";
                priority = "50";
                thenText = string.Empty;
                notice = string.Empty;
                why = string.Empty;
                extra = new JsonObject();
                conds.Add(new Cond());
                return;
            }

            editingBook = rung.Source == "book";
            id = rung.Id;
            priority = Json.Num(rung.Priority);
            thenText = string.Join("\n", rung.Then.ToArray());
            notice = rung.Notice ?? string.Empty;
            why = rung.Why ?? string.Empty;
            requires.AddRange(rung.Requires);
            extra = rung.Raw?.Copy() ?? new JsonObject();
            foreach (string k in new[] { "id", "priority", "when", "then", "notice", "why", "requires", "source", "mode", "disabled" }) extra.RemoveKey(k);
            foreach (var kv in rung.When) conds.Add(FromCondition(kv.Key, kv.Value));
        }

        public override Vector2 InitialSize => new Vector2(980f, 720f);

        private static Cond FromCondition(string key, object want)
        {
            var c = new Cond { Key = key };
            if (want is JsonObject e) { c.Raw = Json.Write(e); return c; }
            if (want is bool b) { c.Op = b ? "is true" : "is false"; return c; }
            if (want is double d) { c.Op = "="; c.Value = Json.Num(d); return c; }
            string s = want as string ?? string.Empty;
            foreach (string op in new[] { ">=", "<=", "!=", ">", "<" })
            {
                if (s.StartsWith(op, StringComparison.Ordinal)) { c.Op = op; c.Value = s.Substring(op.Length); return c; }
            }

            c.Op = "text";
            c.Value = s;
            return c;
        }

        private static object ToCondition(Cond c, out string error)
        {
            error = null;
            if (c.Raw != null)
            {
                try { return Json.ParseObject(c.Raw); }
                catch (FormatException e) { error = c.Key + ": " + e.Message; return null; }
            }

            switch (c.Op)
            {
                case "is true": return true;
                case "is false": return false;
                case "=":
                    if (double.TryParse(c.Value.Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out double d)) return d;
                    error = c.Key + ": = needs a number (use text for words)";
                    return null;
                case "text": return c.Value;
                default: return c.Op + c.Value.Trim();
            }
        }

        private JsonObject Build(out List<string> buildErrors)
        {
            buildErrors = new List<string>();
            var o = new JsonObject();
            o.Set("id", id.Trim());
            if (double.TryParse(priority.Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out double p)) o.Set("priority", p);
            else buildErrors.Add("priority is not a number");
            var when = new JsonObject();
            foreach (Cond c in conds)
            {
                if (c.Key.Trim().Length == 0) continue;
                object v = ToCondition(c, out string err);
                if (err != null) buildErrors.Add(err);
                else when.Set(c.Key.Trim(), v);
            }

            o.Set("when", when);
            o.Set("then", thenText.Split('\n').Select(s => s.TrimEnd('\r')).Where(s => s.Trim().Length > 0).Cast<object>().ToList());
            if (why.Trim().Length > 0) o.Set("why", why.Trim());
            if (notice.Trim().Length > 0) o.Set("notice", notice.Trim());
            if (requires.Count > 0) o.Set("requires", requires.Cast<object>().ToList());
            foreach (var kv in extra) o.Set(kv.Key, kv.Value);
            o.Set("source", "player");
            return o;
        }

        public override void DoWindowContents(Rect inRect)
        {
            Text.Font = GameFont.Small;
            float y = inRect.y;
            Widgets.Label(new Rect(inRect.x, y, 600f, 26f), editingBook ? "Edit book rung (saved as your copy; Revert removes it)" : "Rung editor");
            y += 30f;
            Widgets.Label(new Rect(inRect.x, y, 40f, 26f), "id");
            if (editingBook) Widgets.Label(new Rect(inRect.x + 45f, y, 300f, 26f), id);
            else id = Widgets.TextField(new Rect(inRect.x + 45f, y, 300f, 26f), id);
            Widgets.Label(new Rect(inRect.x + 360f, y, 70f, 26f), "priority");
            priority = Widgets.TextField(new Rect(inRect.x + 430f, y, 80f, 26f), priority);
            Widgets.Label(new Rect(inRect.x + 525f, y, 70f, 26f), "requires");
            Widgets.Label(new Rect(inRect.x + 600f, y, 260f, 26f), requires.Count == 0 ? "-" : string.Join(", ", requires.ToArray()));
            if (Widgets.ButtonText(new Rect(inRect.xMax - 110f, y, 110f, 26f), "Requires..."))
            {
                var opts = new List<FloatMenuOption>();
                foreach (string q in new[] { "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey" })
                {
                    string qq = q;
                    opts.Add(new FloatMenuOption((requires.Contains(q) ? "remove " : "add ") + q, () => Toggle(qq)));
                }

                foreach (string q in requires.Where(r => r.StartsWith("mod:", StringComparison.Ordinal)).ToList())
                {
                    string qq = q;
                    opts.Add(new FloatMenuOption("remove " + q, () => requires.Remove(qq)));
                }

                Find.WindowStack.Add(new FloatMenu(opts));
            }

            y += 34f;
            Widgets.Label(new Rect(inRect.x, y, 600f, 24f), "when (all must hold; a missing key never fires)");
            if (Widgets.ButtonText(new Rect(inRect.x + 620f, y, 110f, 24f), "+ condition")) conds.Add(new Cond());
            if (Widgets.ButtonText(new Rect(inRect.x + 735f, y, 130f, 24f), "+ instruction"))
            {
                var opts = new List<FloatMenuOption>
                {
                    Template("any (OR)", "either", "{\"any\":[{\"hostiles_on_map\":\">0\"},{\"mark_combat_paused\":true}]}"),
                    Template("not", "not_this", "{\"not\":{\"hostile_threat\":true}}"),
                    Template("ton (on-delay)", "held", "{\"ton\":{\"outdoor_temp\":\"<-10\"},\"hours\":2}"),
                    Template("tof (off-delay)", "cooling", "{\"tof\":{\"hostile_threat\":true},\"ticks\":2500}"),
                    Template("ctu (counter)", "raids", "{\"ctu\":{\"hostile_threat\":true},\"preset\":3,\"reset\":{\"mark_raids_reset\":true}}"),
                    Template("ons (one-shot)", "first_time", "{\"ons\":{\"bleeding_count\":\">0\"}}"),
                };
                Find.WindowStack.Add(new FloatMenu(opts));
            }

            y += 28f;
            float condH = Mathf.Min(260f, conds.Count * 28f + 4f);
            var condOut = new Rect(inRect.x, y, inRect.width, condH);
            var condView = new Rect(0f, 0f, condOut.width - 16f, conds.Count * 28f);
            Widgets.BeginScrollView(condOut, ref scroll, condView);
            Cond remove = null;
            for (int i = 0; i < conds.Count; i++)
            {
                if (DrawCond(new Rect(0f, i * 28f, condView.width, 26f), conds[i])) remove = conds[i];
            }

            Widgets.EndScrollView();
            if (remove != null) conds.Remove(remove);
            y += condH + 6f;

            Widgets.Label(new Rect(inRect.x, y, 400f, 24f), "then (one step per line, at most 8 lines of 300 characters)");
            y += 24f;
            thenText = Widgets.TextArea(new Rect(inRect.x, y, inRect.width, 110f), thenText);
            y += 114f;
            Widgets.Label(new Rect(inRect.x, y, 60f, 26f), "notice");
            notice = Widgets.TextField(new Rect(inRect.x + 65f, y, inRect.width - 65f, 26f), notice);
            y += 30f;
            Widgets.Label(new Rect(inRect.x, y, 60f, 26f), "why");
            why = Widgets.TextField(new Rect(inRect.x + 65f, y, inRect.width - 65f, 26f), why);
            y += 32f;

            Text.Font = GameFont.Tiny;
            var msg = errors.Select(e => "error: " + e).Concat(notes.Select(n => "note: " + n)).ToList();
            GUI.color = errors.Count > 0 ? new Color(1f, 0.5f, 0.5f) : new Color(0.8f, 0.8f, 0.6f);
            Widgets.Label(new Rect(inRect.x, y, inRect.width, inRect.yMax - y - 34f), string.Join("\n", msg.Take(6).ToArray()));
            GUI.color = Color.white;
            Text.Font = GameFont.Small;

            float by = inRect.yMax - 30f;
            if (Widgets.ButtonText(new Rect(inRect.x, by, 120f, 30f), "Check")) Check();
            if (Widgets.ButtonText(new Rect(inRect.xMax - 250f, by, 120f, 30f), "Save") && Check()) Save();
            if (Widgets.ButtonText(new Rect(inRect.xMax - 120f, by, 120f, 30f), "Cancel")) Close();
        }

        private FloatMenuOption Template(string label, string key, string json)
        {
            return new FloatMenuOption(label, () =>
            {
                string k = key;
                int n = 2;
                while (conds.Any(c => c.Key == k)) k = key + "_" + n++;
                conds.Add(new Cond { Key = k, Raw = json });
            });
        }

        private void Toggle(string q)
        {
            if (!requires.Remove(q)) requires.Add(q);
        }

        /// <summary>One condition row; returns true when its remove button was pressed.</summary>
        private bool DrawCond(Rect row, Cond c)
        {
            Text.Font = GameFont.Tiny;
            c.Key = Widgets.TextField(new Rect(row.x, row.y, 220f, row.height), c.Key);
            if (Widgets.ButtonText(new Rect(row.x + 224f, row.y, 60f, row.height), "key...")) KeyMenu(c);
            if (c.Raw != null)
            {
                c.Raw = Widgets.TextField(new Rect(row.x + 290f, row.y, row.width - 330f, row.height), c.Raw);
            }
            else
            {
                if (Widgets.ButtonText(new Rect(row.x + 290f, row.y, 80f, row.height), c.Op))
                {
                    Find.WindowStack.Add(new FloatMenu(OpChoices.Select(op => new FloatMenuOption(op, () => c.Op = op)).ToList()));
                }

                if (c.Op != "is true" && c.Op != "is false")
                {
                    c.Value = Widgets.TextField(new Rect(row.x + 375f, row.y, 200f, row.height), c.Value);
                    if (Widgets.ButtonText(new Rect(row.x + 580f, row.y, 70f, row.height), "{TAG}"))
                    {
                        Find.WindowStack.Add(new Dialog_Pick("Compare with a tag", Dialog_Pick.Keys(plc, "tag"), it => c.Value = "{" + it.Value + "}"));
                    }

                    if (Widgets.ButtonText(new Rect(row.x + 655f, row.y, 70f, row.height), "key"))
                    {
                        Find.WindowStack.Add(new Dialog_Pick("Compare with a measured key", Dialog_Pick.Keys(plc, "sensor"), it => c.Value = it.Value));
                    }
                }
            }

            bool removed = Widgets.ButtonText(new Rect(row.xMax - 34f, row.y, 30f, row.height), "x");
            Text.Font = GameFont.Small;
            return removed;
        }

        private void KeyMenu(Cond c)
        {
            var opts = new List<FloatMenuOption>();
            foreach (var fam in new[]
                     {
                         new[] { "sensor", "Sensor (catalogue and measured now)" }, new[] { "mark", "Mark" }, new[] { "tag", "Tag" },
                         new[] { "item", "Thing: items in store (count_)" }, new[] { "building", "Thing: buildings (count_)" },
                         new[] { "research", "Research finished (research_)" }, new[] { "alert", "Alert active (alert_)" },
                     })
            {
                string family = fam[0];
                opts.Add(new FloatMenuOption(fam[1], () => Find.WindowStack.Add(new Dialog_Pick(fam[1], Dialog_Pick.Keys(plc, family), it =>
                {
                    c.Key = it.Value;
                    if (it.Requires != null && !requires.Contains(it.Requires)) requires.Add(it.Requires);
                    if (family == "research" || family == "alert") c.Op = "is true";
                    else if (family == "item" || family == "building") c.Op = ">";
                }))));
            }

            opts.Add(new FloatMenuOption("letter_matches (a letter label contains)", () => { c.Key = "letter_matches"; c.Op = "text"; }));
            Find.WindowStack.Add(new FloatMenu(opts));
        }

        private bool Check()
        {
            JsonObject o = Build(out List<string> buildErrors);
            var live = plc.Last == null ? null : new HashSet<string>(plc.Last.State.Keys);
            errors = buildErrors.Concat(Validate.Rung(o, RimPLCMod.Book, live, out List<string> n)).ToList();
            notes = n;
            if (!editingBook && plc.MyRungs.All(r => r.Id != o.GetString("id")) && RimPLCMod.Book.Rungs.Any(r => r.Id == o.GetString("id")))
            {
                errors.Add("that id is a book rung: use Edit on the book rung to override it");
            }

            return errors.Count == 0;
        }

        private void Save()
        {
            JsonObject o = Build(out _);
            if (plc.UpsertRung(o, "player", out string note, true))
            {
                plc.AddLog(Find.TickManager?.TicksGame ?? 0, note.Split(' ')[0], editingBook ? "player copy of the book rung saved" : "player rung saved", "player");
                Close();
            }
            else
            {
                errors = new List<string> { note };
            }
        }
    }

    /// <summary>The import diff: every change listed before anything is applied; Apply runs the plan, Cancel drops it.</summary>
    public sealed class Dialog_ImportDiff : Window
    {
        private readonly RimPLCGameComponent plc;
        private readonly ImportPlan plan;
        private readonly string file;
        private Vector2 scroll;

        public Dialog_ImportDiff(RimPLCGameComponent plc, ImportPlan plan, string file)
        {
            this.plc = plc;
            this.plan = plan;
            this.file = file;
            doCloseX = true;
            absorbInputAroundWindow = true;
        }

        public override Vector2 InitialSize => new Vector2(860f, 640f);

        public override void DoWindowContents(Rect inRect)
        {
            Text.Font = GameFont.Small;
            Widgets.Label(new Rect(inRect.x, inRect.y, inRect.width, 26f), "Import " + file + ": " + plan.Changes + " changes   (+ new  ~ changed  = unchanged  ! refused)");
            var outRect = new Rect(inRect.x, inRect.y + 30f, inRect.width, inRect.height - 70f);
            var view = new Rect(0f, 0f, outRect.width - 16f, plan.Lines.Count * 22f);
            Widgets.BeginScrollView(outRect, ref scroll, view);
            Text.Font = GameFont.Tiny;
            for (int i = 0; i < plan.Lines.Count; i++)
            {
                DiffLine l = plan.Lines[i];
                GUI.color = l.Kind == '+' ? new Color(0.5f, 1f, 0.5f) : l.Kind == '~' ? new Color(1f, 0.85f, 0.4f) :
                            l.Kind == '!' ? new Color(1f, 0.5f, 0.5f) : new Color(0.7f, 0.7f, 0.7f);
                Widgets.Label(new Rect(0f, i * 22f, view.width, 22f), l.Kind + "  " + l.Text);
            }

            GUI.color = Color.white;
            Text.Font = GameFont.Small;
            Widgets.EndScrollView();
            float by = inRect.yMax - 32f;
            if (plan.Changes > 0 && Widgets.ButtonText(new Rect(inRect.xMax - 250f, by, 120f, 32f), "Apply"))
            {
                foreach (Action a in plan.Actions) a();
                plc.AddLog(Find.TickManager?.TicksGame ?? 0, "-", "import " + file + ": " + plan.Changes + " changes", "player");
                Close();
            }

            if (Widgets.ButtonText(new Rect(inRect.xMax - 120f, by, 120f, 32f), "Cancel")) Close();
        }
    }
}
