using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using Verse;

namespace RimPLC
{
    /// <summary>One line of an import diff: + added, ~ changed, = unchanged, ! refused, - note.</summary>
    public sealed class DiffLine
    {
        public char Kind;
        public string Text;
    }

    /// <summary>What an import would do, shown before anything changes (docs/RIMPLC_DESIGN.md 7: "Import shows a diff and the player confirms").</summary>
    public sealed class ImportPlan
    {
        public readonly List<DiffLine> Lines = new List<DiffLine>();
        public readonly List<Action> Actions = new List<Action>();
        public string Error;
        public int Changes;

        public void Line(char kind, string text)
        {
            Lines.Add(new DiffLine { Kind = kind, Text = text });
        }

        public object ToResult()
        {
            return Lines.Select(l => (object)(l.Kind + " " + l.Text)).ToList();
        }
    }

    /// <summary>
    /// Export and import of a ladder (docs/RIMPLC_DESIGN.md 7). The file is the ladder shape of
    /// docs/rimplc/schema/ladder.schema.json: version, preset {id: export}, gates = the player's and Unity's rungs
    /// (book rungs are not exported: the mod carries the book), tags = the book's tag table (the schema needs it), and
    /// rimplc_state = marks, tag overrides, switched-off ids and mode overrides. Files go to
    /// &lt;RimWorld config folder&gt;/RimPLC/exports/ and nowhere else.
    ///
    /// Import is a merge, never a wipe: every rung is checked with the rimplc-check rules (Validate) and the same
    /// upsert path as the API, rungs that equal the book or the current layer are reported unchanged, and nothing is
    /// applied until the plan is confirmed (the window) or dry_run is false (the API). Through the API the rungs become
    /// unity- rungs in advise mode, and switches / modes / constants need the owner flag.
    /// </summary>
    public static class Transfer
    {
        public static string Folder => Path.Combine(Path.Combine(GenFilePaths.ConfigFolderPath, "RimPLC"), "exports");

        public static JsonObject ExportDoc(RimPLCGameComponent plc)
        {
            Ladder book = RimPLCMod.Book;
            var tags = new JsonObject();
            tags.Set("constants", book.Constants);
            tags.Set("variables", book.Variables);
            var marks = plc.Marks.Copy();
            var overrides = new JsonObject();
            foreach (var kv in plc.TagOverrides.OrderBy(k => k.Key, StringComparer.Ordinal)) overrides.Set(kv.Key, kv.Value);
            var modes = new JsonObject();
            foreach (var kv in plc.ModeOverrides.OrderBy(k => k.Key, StringComparer.Ordinal)) modes.Set(kv.Key, kv.Value);
            var state = new JsonObject();
            state.Set("marks", marks);
            state.Set("tag_overrides", overrides);
            state.Set("switched_off", plc.SwitchedOff.OrderBy(x => x, StringComparer.Ordinal).Cast<object>().ToList());
            state.Set("modes", modes);
            var preset = new JsonObject();
            preset.Set("id", "export");
            preset.Set("source", "RimPLC " + book.PresetId);
            preset.Set("schema", "docs/rimplc/schema/ladder.schema.json");
            var doc = new JsonObject();
            doc.Set("version", (double)Math.Max(2, book.Version));
            doc.Set("preset", preset);
            doc.Set("gates", plc.MyRungs.Select(r => (object)r.ToJson()).ToList());
            doc.Set("tags", tags);
            doc.Set("rimplc_state", state);
            return doc;
        }

        /// <summary>Writes the export file; returns its path.</summary>
        public static string ExportFile(RimPLCGameComponent plc, string name = null)
        {
            Directory.CreateDirectory(Folder);
            string file = (string.IsNullOrEmpty(name) ? "ladder-" + (Find.TickManager?.TicksGame ?? 0).ToString(CultureInfo.InvariantCulture) : name);
            file = new string(file.Where(c => char.IsLetterOrDigit(c) || c == '-' || c == '_').ToArray());
            if (file.Length == 0) file = "ladder";
            string path = Path.Combine(Folder, file + ".json");
            File.WriteAllText(path, Json.Write(ExportDoc(plc), true) + "\n");
            return path;
        }

        public static List<string> ImportFiles()
        {
            var files = new List<string>();
            try
            {
                if (Directory.Exists(Folder)) files.AddRange(Directory.GetFiles(Folder, "*.json").OrderByDescending(File.GetLastWriteTimeUtc));
            }
            catch (Exception)
            {
                // an unreadable folder lists nothing
            }

            return files;
        }

        private static bool SameJson(object a, object b)
        {
            return Json.Write(a) == Json.Write(b);
        }

        /// <summary>The plan for importing doc. source: player (the window) or unity (the API). Nothing changes until plan.Actions run.</summary>
        public static ImportPlan Plan(RimPLCGameComponent plc, JsonObject doc, string source, bool owner)
        {
            var plan = new ImportPlan();
            Ladder book = RimPLCMod.Book;
            List<object> gates = doc?.GetList("gates");
            if (gates == null)
            {
                plan.Error = "not a ladder: no gates list";
                return plan;
            }

            var seen = new HashSet<string>();
            foreach (object g in gates)
            {
                var o = g as JsonObject;
                string id = o?.GetString("id") ?? "(no id)";
                if (o == null) { plan.Line('!', "a rung that is not an object"); continue; }
                if (!seen.Add(id)) { plan.Line('!', id + ": duplicate id in the file"); continue; }
                Rung bookRung = book.Rungs.FirstOrDefault(r => r.Id == id);
                string src = o.GetString("source") ?? "book";
                if (bookRung != null && src == "book" && SameJson(Strip(bookRung.ToJson()), Strip(o)))
                {
                    plan.Line('=', id + ": same as the book");
                    continue;
                }

                // dry run of the upsert on a scratch copy of the layer: the same id rules and checks as the API
                var trial = o.Copy();
                string as_ = source == "player" && src == "unity" ? "unity" : source;
                var probe = new RimPLCGameComponent.Probe(plc);
                if (!probe.Upsert(trial, as_, out string finalId, out string note))
                {
                    plan.Line('!', id + ": " + note);
                    continue;
                }

                Rung current = plc.MyRungs.FirstOrDefault(r => r.Id == finalId);
                JsonObject incoming = probe.Result.ToJson();
                if (current != null && SameJson(Strip(current.ToJson()), Strip(incoming)))
                {
                    plan.Line('=', finalId + ": unchanged");
                    continue;
                }

                string what = current == null
                    ? (bookRung != null && finalId == id ? "overrides the book rung" : "new " + as_ + " rung")
                    : "changes " + string.Join(", ", ChangedFields(current.ToJson(), incoming).ToArray());
                plan.Line(current == null ? '+' : '~', finalId + ": " + what + (note.Length > finalId.Length ? "  " + note.Substring(finalId.Length).Trim() : string.Empty));
                JsonObject apply = trial;
                plan.Actions.Add(() => plc.UpsertRung(apply, as_, out _));
                plan.Changes++;
            }

            JsonObject state = doc.GetObject("rimplc_state");
            if (state != null) PlanState(plc, state, owner || source == "player", plan);
            if (plan.Lines.Count == 0) plan.Line('-', "nothing to import");
            return plan;
        }

        private static void PlanState(RimPLCGameComponent plc, JsonObject state, bool trusted, ImportPlan plan)
        {
            foreach (var kv in state.GetObject("marks") ?? new JsonObject())
            {
                string name = kv.Key;
                object v = kv.Value;
                if (plc.Marks.TryGet(name, out object cur) && SameJson(cur, v)) continue;
                if (!new RimPLCGameComponent.Probe(plc).Mark(name, v, out string err)) { plan.Line('!', "mark " + name + ": " + err); continue; }
                plan.Line(plc.Marks.Has(name) ? '~' : '+', "mark " + name + " = " + Json.Write(v) + (plc.Marks.Has(name) ? " (was " + Json.Write(cur) + ")" : string.Empty));
                plan.Actions.Add(() => plc.SetMark(name, v, out _));
                plan.Changes++;
            }

            foreach (var kv in state.GetObject("tag_overrides") ?? new JsonObject())
            {
                string name = kv.Key;
                object v = kv.Value;
                if (plc.TagOverrides.TryGetValue(name, out double cur) && Engine.IsNumber(v) && Engine.ToDouble(v) == cur) continue;
                bool constant = RimPLCMod.Book.Constants.Has(name);
                if (constant && !trusted) { plan.Line('!', "tag " + name + ": a constant: a safety limit only the owner changes"); continue; }
                if (!constant && RimPLCMod.Book.Variables.GetObject(name) == null) { plan.Line('!', "tag " + name + ": not a variable on the ladder"); continue; }
                if (!Engine.IsNumber(v)) { plan.Line('!', "tag " + name + ": value must be a number"); continue; }
                plan.Line(plc.TagOverrides.ContainsKey(name) ? '~' : '+', "tag " + name + " = " + Json.Write(v));
                plan.Actions.Add(() => plc.SetTag(name, v, true, out _));
                plan.Changes++;
            }

            var off = Rung.Strings(state.GetList("switched_off"));
            foreach (string id in off.Where(i => !plc.SwitchedOff.Contains(i)))
            {
                bool isBook = RimPLCMod.Book.Rungs.Any(r => r.Id == id) && !plc.MyRungs.Any(r => r.Id == id);
                if (isBook && !trusted) { plan.Line('!', id + ": owner only: disabling a book rung"); continue; }
                plan.Line('~', id + ": switched off");
                string rid = id;
                plan.Actions.Add(() => plc.SwitchedOff.Add(rid));
                plan.Changes++;
            }

            foreach (var kv in state.GetObject("modes") ?? new JsonObject())
            {
                string id = kv.Key, mode = kv.Value as string;
                if (mode != "advise" && mode != "auto" && mode != "off") { plan.Line('!', id + ": mode " + Json.Write(kv.Value)); continue; }
                if (plc.ModeOverrides.TryGetValue(id, out string cur) && cur == mode) continue;
                if (mode == "auto" && !trusted) { plan.Line('!', id + ": owner only: turning a rung to auto"); continue; }
                plan.Line('~', id + ": mode " + mode);
                plan.Actions.Add(() => plc.SetMode(id, mode));
                plan.Changes++;
            }
        }

        private static JsonObject Strip(JsonObject o)
        {
            var c = o.Copy();
            c.RemoveKey("source");
            if (c.GetString("mode") == "advise") c.RemoveKey("mode");
            return c;
        }

        private static IEnumerable<string> ChangedFields(JsonObject a, JsonObject b)
        {
            var keys = a.Select(kv => kv.Key).Concat(b.Select(kv => kv.Key)).Distinct();
            foreach (string k in keys)
            {
                if (!SameJson(a.Get(k), b.Get(k))) yield return k;
            }
        }
    }
}
