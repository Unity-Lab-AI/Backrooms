using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimPLC
{
    /// <summary>
    /// The ladder window (docs/RIMPLC_DESIGN.md 6). Tabs: Ladder (rungs live, every contact coloured: green true,
    /// dark false, amber unmeasured, red unresolved; switch on/off; mode advise/auto), Tags (overrides), Marks (set,
    /// clear, add), Sensors (the input image, read only). The window reads the last scan; while the game is paused the
    /// component rescans once a second, so it stays live.
    /// </summary>
    public sealed class MainTabWindow_RimPLC : MainTabWindow
    {
        private enum Tab { Ladder, Tags, Marks, Sensors, Log }

        private static readonly Color Green = new Color(0.25f, 0.65f, 0.3f);
        private static readonly Color Dark = new Color(0.22f, 0.22f, 0.22f);
        private static readonly Color Amber = new Color(0.85f, 0.6f, 0.15f);
        private static readonly Color Red = new Color(0.8f, 0.2f, 0.2f);
        private static readonly Color LiveRow = new Color(0.2f, 0.45f, 0.2f, 0.35f);
        private static readonly Color OffRow = new Color(0f, 0f, 0f, 0.35f);
        private static readonly Color NaRow = new Color(0.4f, 0.4f, 0.4f, 0.25f);

        private const float RowH = 24f;

        private Tab tab = Tab.Ladder;
        private Vector2 scroll;
        private string selected;
        private bool liveOnly;
        private readonly Dictionary<string, string> buffers = new Dictionary<string, string>();
        private string newMarkName = string.Empty;
        private string newMarkValue = string.Empty;

        public override Vector2 RequestedTabSize => new Vector2(1100f, 700f);

        public override void DoWindowContents(Rect inRect)
        {
            RimPLCGameComponent plc = RimPLCGameComponent.Get();
            Text.Font = GameFont.Small;
            if (plc == null)
            {
                Widgets.Label(inRect, "RimPLC: no game loaded.");
                return;
            }

            if (RimPLCMod.Book.LoadError != null)
            {
                Widgets.Label(inRect, "RimPLC: the book preset did not load: " + RimPLCMod.Book.LoadError);
                return;
            }

            ScanResult r = plc.Last ?? plc.Scan(false);
            float y = inRect.y;
            DrawHeader(new Rect(inRect.x, y, inRect.width, 28f), plc, r);
            y += 32f;
            DrawTabs(new Rect(inRect.x, y, inRect.width, 28f));
            y += 34f;
            var body = new Rect(inRect.x, y, inRect.width, inRect.yMax - y);
            if (r == null)
            {
                Widgets.Label(body, "No scan yet.");
                return;
            }

            switch (tab)
            {
                case Tab.Ladder: DrawLadder(body, plc, r); break;
                case Tab.Tags: DrawTags(body, plc, r); break;
                case Tab.Marks: DrawMarks(body, plc); break;
                case Tab.Sensors: DrawSensors(body, r); break;
                case Tab.Log: DrawLog(body, plc); break;
            }

            Text.Font = GameFont.Small;
            Text.Anchor = TextAnchor.UpperLeft;
            GUI.color = Color.white;
        }

        private void DrawHeader(Rect rect, RimPLCGameComponent plc, ScanResult r)
        {
            string live = r == null ? "-" : string.Join(" + ", Engine.LiveRung(r).Select(h => h.Rung.Id).ToArray());
            string head = "RimPLC   scan every " + plc.ScanTicks + "t   " +
                          (r == null ? string.Empty : r.Ms.ToString("0.00", CultureInfo.InvariantCulture) + " ms" + (plc.OverBudget ? " (over budget)" : string.Empty)) +
                          "   live: " + (live.Length > 0 ? live : "none") + (r != null && r.PausedScan ? "   [paused: advice only]" : string.Empty);
            Widgets.Label(new Rect(rect.x, rect.y, rect.width - 330f, rect.height), head);
            float x = rect.xMax - 325f;
            bool notify = plc.Notify;
            Widgets.CheckboxLabeled(new Rect(x, rect.y, 120f, 24f), "Notices", ref notify);
            plc.Notify = notify;
            x += 130f;
            if (Widgets.ButtonText(new Rect(x, rect.y, 30f, 24f), "-")) plc.ScanTicks = Mathf.Clamp(plc.ScanTicks / 2, 60, 2500);
            Widgets.Label(new Rect(x + 34f, rect.y, 90f, 24f), "scan " + plc.ScanTicks + "t");
            if (Widgets.ButtonText(new Rect(x + 125f, rect.y, 30f, 24f), "+")) plc.ScanTicks = Mathf.Clamp(plc.ScanTicks * 2, 60, 2500);
        }

        private void DrawTabs(Rect rect)
        {
            float w = 110f;
            int i = 0;
            foreach (Tab t in Enum.GetValues(typeof(Tab)))
            {
                var b = new Rect(rect.x + i * (w + 4f), rect.y, w, rect.height);
                if (tab == t) Widgets.DrawBoxSolid(b, new Color(1f, 1f, 1f, 0.12f));
                if (Widgets.ButtonText(b, t.ToString()))
                {
                    tab = t;
                    scroll = Vector2.zero;
                }

                i++;
            }
        }

        // ------------------------------------------------------------------------------------------- ladder

        private void DrawLadder(Rect rect, RimPLCGameComponent plc, ScanResult r)
        {
            Widgets.CheckboxLabeled(new Rect(rect.x, rect.y, 140f, 24f), "Live rungs only", ref liveOnly);
            float bx = rect.x + 150f;
            if (Widgets.ButtonText(new Rect(bx, rect.y, 100f, 24f), "Letters seen")) plc.MarkLettersSeen();
            bx += 104f;
            if (Widgets.ButtonText(new Rect(bx, rect.y, 90f, 24f), "New rung")) Find.WindowStack.Add(new Dialog_RungEditor(plc, null));
            bx += 94f;
            Rung sel = selected == null ? null : plc.MyRungs.FirstOrDefault(x => x.Id == selected) ?? RimPLCMod.Book.Rungs.FirstOrDefault(x => x.Id == selected);
            if (sel != null && Widgets.ButtonText(new Rect(bx, rect.y, 60f, 24f), "Edit")) Find.WindowStack.Add(new Dialog_RungEditor(plc, sel));
            bx += 64f;
            bool layered = sel != null && plc.MyRungs.Any(x => x.Id == sel.Id);
            bool overridesBook = layered && RimPLCMod.Book.Rungs.Any(x => x.Id == sel.Id);
            if (layered && Widgets.ButtonText(new Rect(bx, rect.y, 70f, 24f), overridesBook ? "Revert" : "Remove"))
            {
                string rid = sel.Id;
                if (plc.RemoveRung(rid, out string note, true)) plc.AddLog(Find.TickManager.TicksGame, rid, overridesBook ? "reverted to the book" : "removed", "player");
                else Messages.Message("RimPLC: " + note, MessageTypeDefOf.RejectInput, false);
            }

            bx += 74f;
            if (Widgets.ButtonText(new Rect(bx, rect.y, 70f, 24f), "Export"))
            {
                string path = Transfer.ExportFile(plc);
                plc.AddLog(Find.TickManager.TicksGame, "-", "exported to " + path, "player");
                Messages.Message("RimPLC: exported to " + path, MessageTypeDefOf.NeutralEvent, false);
            }

            bx += 74f;
            if (Widgets.ButtonText(new Rect(bx, rect.y, 70f, 24f), "Import")) ImportMenu(plc);
            bx += 78f;
            Text.Font = GameFont.Tiny;
            Widgets.Label(new Rect(bx, rect.y + 4f, rect.xMax - bx, 22f), "green true / dark false / amber unmeasured / red unresolved");
            Text.Font = GameFont.Small;

            float detailH = selected != null ? 150f : 0f;
            var outRect = new Rect(rect.x, rect.y + 28f, rect.width, rect.height - 28f - detailH);
            List<RungEval> rows = liveOnly ? r.Rungs.Where(e => e.Live).ToList() : r.Rungs;
            var view = new Rect(0f, 0f, outRect.width - 16f, rows.Count * RowH);
            Widgets.BeginScrollView(outRect, ref scroll, view);
            for (int i = 0; i < rows.Count; i++)
            {
                float top = i * RowH;
                if (top + RowH < scroll.y || top > scroll.y + outRect.height) continue;
                DrawRung(new Rect(0f, top, view.width, RowH), plc, rows[i]);
            }

            Widgets.EndScrollView();

            if (selected != null)
            {
                RungEval ev = r.Rungs.FirstOrDefault(e => e.Rung.Id == selected);
                if (ev != null) DrawDetail(new Rect(rect.x, rect.yMax - detailH + 4f, rect.width, detailH - 4f), ev);
            }
        }

        private static void ImportMenu(RimPLCGameComponent plc)
        {
            List<string> files = Transfer.ImportFiles();
            if (files.Count == 0)
            {
                Messages.Message("RimPLC: no ladder files in " + Transfer.Folder, MessageTypeDefOf.RejectInput, false);
                return;
            }

            var opts = files.Take(30).Select(f => new FloatMenuOption(System.IO.Path.GetFileName(f), () =>
            {
                JsonObject doc;
                try { doc = Json.ParseObject(System.IO.File.ReadAllText(f)); }
                catch (Exception e)
                {
                    Messages.Message("RimPLC: " + System.IO.Path.GetFileName(f) + " is not a ladder: " + e.Message, MessageTypeDefOf.RejectInput, false);
                    return;
                }

                ImportPlan plan = Transfer.Plan(plc, doc, "player", false);
                if (plan.Error != null) Messages.Message("RimPLC: " + plan.Error, MessageTypeDefOf.RejectInput, false);
                else Find.WindowStack.Add(new Dialog_ImportDiff(plc, plan, System.IO.Path.GetFileName(f)));
            })).ToList();
            Find.WindowStack.Add(new FloatMenu(opts));
        }

        private void DrawRung(Rect row, RimPLCGameComponent plc, RungEval ev)
        {
            Rung rung = ev.Rung;
            if (!ev.Applicable) Widgets.DrawBoxSolid(row, NaRow);
            else if (ev.Off != null) Widgets.DrawBoxSolid(row, OffRow);
            else if (ev.Live) Widgets.DrawBoxSolid(row, LiveRow);
            if (selected == rung.Id) Widgets.DrawHighlight(row);
            Widgets.DrawHighlightIfMouseover(row);

            Text.Font = GameFont.Tiny;
            Text.Anchor = TextAnchor.MiddleLeft;
            Widgets.Label(new Rect(row.x + 2f, row.y, 46f, row.height), Json.Num(rung.Priority));
            string idText = rung.Id + (rung.Source != "book" ? " [" + rung.Source + "]" : string.Empty);
            var idRect = new Rect(row.x + 50f, row.y, 210f, row.height);
            Widgets.Label(idRect, idText);
            if (Widgets.ButtonInvisible(idRect)) selected = selected == rung.Id ? null : rung.Id;

            float x = row.x + 264f;
            float maxX = row.xMax - 130f;
            if (!ev.Applicable)
            {
                Widgets.Label(new Rect(x, row.y, maxX - x, row.height), "not applicable: requires " + string.Join(", ", rung.Requires.ToArray()));
            }
            else
            {
                foreach (var c in ev.Contacts)
                {
                    string label = c.Key;
                    float w = Mathf.Min(170f, Text.CalcSize(label).x + 10f);
                    if (x + w > maxX)
                    {
                        Widgets.Label(new Rect(x, row.y, 20f, row.height), "...");
                        break;
                    }

                    var box = new Rect(x, row.y + 3f, w, row.height - 6f);
                    Widgets.DrawBoxSolid(box, ColorOf(c.Value));
                    Text.Anchor = TextAnchor.MiddleCenter;
                    Widgets.Label(box, label);
                    Text.Anchor = TextAnchor.MiddleLeft;
                    object want = ev.When.Get(c.Key);
                    string tip = c.Key + " " + Json.Write(want) + "  -> " + c.Value;
                    if (ev.Matched != null && ev.Matched.TryGet(c.Key, out object m)) tip += "  (measured " + Json.Write(m) + ")";
                    TooltipHandler.TipRegion(box, tip);
                    x += w + 3f;
                }
            }

            string mode = plc.ModeOf(rung);
            if (Widgets.ButtonText(new Rect(row.xMax - 124f, row.y + 1f, 70f, row.height - 2f), mode))
            {
                plc.SetMode(rung.Id, mode == "auto" ? "advise" : "auto");
                plc.AddLog(Find.TickManager.TicksGame, rung.Id, "mode " + plc.ModeOf(rung), "player");
            }

            bool on = !plc.SwitchedOff.Contains(rung.Id);
            bool was = on;
            Widgets.Checkbox(row.xMax - 40f, row.y, ref on, 22f, rung.Disabled != null);
            if (on != was)
            {
                plc.EnableRung(rung.Id, on, true, out _);
                plc.AddLog(Find.TickManager.TicksGame, rung.Id, on ? "switched on" : "switched off", "player");
            }

            if (rung.Disabled != null) TooltipHandler.TipRegion(new Rect(row.xMax - 40f, row.y, 24f, row.height), "disabled in the book: " + rung.Disabled);
            Text.Font = GameFont.Small;
            Text.Anchor = TextAnchor.UpperLeft;
        }

        private static Color ColorOf(Contact c)
        {
            switch (c)
            {
                case Contact.True: return Green;
                case Contact.Unmeasured: return Amber;
                case Contact.Unresolved: return Red;
                default: return Dark;
            }
        }

        private static void DrawDetail(Rect rect, RungEval ev)
        {
            Widgets.DrawBoxSolid(rect, new Color(0f, 0f, 0f, 0.3f));
            Rung r = ev.Rung;
            var lines = new List<string>();
            lines.Add(r.Id + "  (priority " + Json.Num(r.Priority) + (r.Chain != null ? ", chain " + r.Chain : string.Empty) +
                      (r.Family != null ? ", " + r.Family : string.Empty) + ")" + (ev.Off != null ? "  OFF: " + ev.Off : string.Empty));
            if (r.Check != null) lines.Add("check: " + r.Check);
            if (r.Notice != null) lines.Add("notice: " + r.Notice);
            for (int i = 0; i < ev.Then.Count; i++) lines.Add((i + 1) + ". " + ev.Then[i]);
            foreach (string n in r.Never) lines.Add("NEVER: " + n);
            Text.Font = GameFont.Tiny;
            Widgets.Label(rect.ContractedBy(4f), string.Join("\n", lines.ToArray()));
            Text.Font = GameFont.Small;
        }

        // ------------------------------------------------------------------------------------------- tags

        private void DrawTags(Rect rect, RimPLCGameComponent plc, ScanResult r)
        {
            Ladder book = RimPLCMod.Book;
            var names = book.Variables.Select(kv => kv.Key).Concat(book.Constants.Select(kv => kv.Key)).ToList();
            var view = new Rect(0f, 0f, rect.width - 16f, (names.Count + 2) * RowH);
            Widgets.BeginScrollView(rect, ref scroll, view);
            float y = 0f;
            Widgets.Label(new Rect(0f, y, view.width, RowH), "Variables (setpoints: override inside min..max)   /   Constants (owner-only safety limits, read only here)");
            y += RowH;
            foreach (string name in names)
            {
                bool constant = book.Constants.Has(name);
                var row = new Rect(0f, y, view.width, RowH);
                Widgets.DrawHighlightIfMouseover(row);
                Text.Font = GameFont.Tiny;
                Text.Anchor = TextAnchor.MiddleLeft;
                Widgets.Label(new Rect(4f, y, 230f, RowH), name + (constant ? "  [const]" : string.Empty));
                Widgets.Label(new Rect(240f, y, 140f, RowH), Json.Write(r.Tags.Get(name)));
                JsonObject spec = book.Variables.GetObject(name);
                if (spec != null)
                {
                    Widgets.Label(new Rect(385f, y, 300f, RowH), (spec.GetString("rule") ?? string.Empty) +
                                                                  "  [" + Json.Write(spec.Get("min")) + ".." + Json.Write(spec.Get("max")) + "]");
                    string key = "tag:" + name;
                    if (!buffers.ContainsKey(key)) buffers[key] = plc.TagOverrides.TryGetValue(name, out double ov) ? Json.Num(ov) : string.Empty;
                    buffers[key] = Widgets.TextField(new Rect(690f, y + 1f, 90f, RowH - 2f), buffers[key]);
                    if (Widgets.ButtonText(new Rect(785f, y + 1f, 60f, RowH - 2f), "Set"))
                    {
                        if (plc.SetTag(name, buffers[key], false, out string note)) plc.AddLog(Find.TickManager.TicksGame, "-", "tag " + name + " = " + buffers[key] + note, "player");
                        else Messages.Message("RimPLC: " + note, MessageTypeDefOf.RejectInput, false);
                    }

                    if (plc.TagOverrides.ContainsKey(name) && Widgets.ButtonText(new Rect(850f, y + 1f, 60f, RowH - 2f), "Clear"))
                    {
                        plc.TagOverrides.Remove(name);
                        buffers[key] = string.Empty;
                    }
                }

                y += RowH;
            }

            Text.Font = GameFont.Small;
            Text.Anchor = TextAnchor.UpperLeft;
            Widgets.EndScrollView();
        }

        // ------------------------------------------------------------------------------------------- marks

        private void DrawMarks(Rect rect, RimPLCGameComponent plc)
        {
            Text.Font = GameFont.Tiny;
            Text.Anchor = TextAnchor.MiddleLeft;
            Widgets.Label(new Rect(rect.x, rect.y, 120f, RowH), "New mark:");
            newMarkName = Widgets.TextField(new Rect(rect.x + 125f, rect.y + 1f, 200f, RowH - 2f), newMarkName);
            newMarkValue = Widgets.TextField(new Rect(rect.x + 330f, rect.y + 1f, 90f, RowH - 2f), newMarkValue);
            if (Widgets.ButtonText(new Rect(rect.x + 425f, rect.y + 1f, 60f, RowH - 2f), "Set"))
            {
                if (plc.SetMark(newMarkName.Trim(), newMarkValue, out string err))
                {
                    plc.AddLog(Find.TickManager.TicksGame, "-", "mark " + newMarkName + " = " + newMarkValue, "player");
                    newMarkName = newMarkValue = string.Empty;
                }
                else
                {
                    Messages.Message("RimPLC: " + err, MessageTypeDefOf.RejectInput, false);
                }
            }

            var outRect = new Rect(rect.x, rect.y + RowH + 6f, rect.width, rect.height - RowH - 6f);
            List<KeyValuePair<string, object>> marks = plc.Marks.OrderBy(kv => kv.Key, StringComparer.Ordinal).ToList();
            var view = new Rect(0f, 0f, outRect.width - 16f, marks.Count * RowH);
            Widgets.BeginScrollView(outRect, ref scroll, view);
            float y = 0f;
            foreach (var kv in marks)
            {
                var row = new Rect(0f, y, view.width, RowH);
                Widgets.DrawHighlightIfMouseover(row);
                Widgets.Label(new Rect(4f, y, 300f, RowH), "mark_" + kv.Key);
                Widgets.Label(new Rect(310f, y, 120f, RowH), Json.Write(kv.Value));
                string key = "mark:" + kv.Key;
                if (!buffers.ContainsKey(key)) buffers[key] = Json.Write(kv.Value);
                buffers[key] = Widgets.TextField(new Rect(435f, y + 1f, 90f, RowH - 2f), buffers[key]);
                if (Widgets.ButtonText(new Rect(530f, y + 1f, 60f, RowH - 2f), "Set"))
                {
                    plc.SetMark(kv.Key, buffers[key], out _);
                    plc.AddLog(Find.TickManager.TicksGame, "-", "mark " + kv.Key + " = " + buffers[key], "player");
                }

                if (Widgets.ButtonText(new Rect(595f, y + 1f, 60f, RowH - 2f), "Clear"))
                {
                    plc.SetMark(kv.Key, null, out _);
                    buffers.Remove(key);
                    plc.AddLog(Find.TickManager.TicksGame, "-", "mark " + kv.Key + " cleared", "player");
                }

                y += RowH;
            }

            Widgets.EndScrollView();
            Text.Font = GameFont.Small;
            Text.Anchor = TextAnchor.UpperLeft;
        }

        // ------------------------------------------------------------------------------------------- sensors, log

        private void DrawSensors(Rect rect, ScanResult r)
        {
            List<KeyValuePair<string, object>> rows = r.State.Where(kv => kv.Key != "tags").OrderBy(kv => kv.Key, StringComparer.Ordinal).ToList();
            var view = new Rect(0f, 0f, rect.width - 16f, rows.Count * 20f);
            Widgets.BeginScrollView(rect, ref scroll, view);
            Text.Font = GameFont.Tiny;
            float y = 0f;
            JsonObject catalogue = RimPLCMod.Book.Sensors;
            foreach (var kv in rows)
            {
                if (y + 20f >= scroll.y && y <= scroll.y + rect.height)
                {
                    Widgets.Label(new Rect(4f, y, 260f, 20f), kv.Key);
                    string v = Json.Write(kv.Value);
                    Widgets.Label(new Rect(270f, y, view.width - 270f, 20f), v.Length > 160 ? v.Substring(0, 160) + "..." : v);
                    JsonObject desc = catalogue.GetObject(kv.Key);
                    if (desc != null) TooltipHandler.TipRegion(new Rect(4f, y, 260f, 20f), desc.GetString("source") ?? string.Empty);
                }

                y += 20f;
            }

            Text.Font = GameFont.Small;
            Widgets.EndScrollView();
        }

        private void DrawLog(Rect rect, RimPLCGameComponent plc)
        {
            var view = new Rect(0f, 0f, rect.width - 16f, plc.Journal.Count * 20f);
            Widgets.BeginScrollView(rect, ref scroll, view);
            Text.Font = GameFont.Tiny;
            for (int i = 0; i < plc.Journal.Count; i++)
            {
                Widgets.Label(new Rect(4f, i * 20f, view.width, 20f), plc.Journal[plc.Journal.Count - 1 - i]);
            }

            Text.Font = GameFont.Small;
            Widgets.EndScrollView();
        }
    }
}
