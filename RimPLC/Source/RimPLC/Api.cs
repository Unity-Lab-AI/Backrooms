using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace RimPLC
{
    /// <summary>
    /// The AI API, one implementation behind both transports: the RimBridgeServer companion tools (RimPLC.BridgeTools,
    /// rimplc/*) and the command-file fallback (Inbox). Shapes are frozen in docs/rimplc/schema/tools.schema.json.
    /// read_ladder keeps the field names of today's ladder tool (live_rungs, tags, my_marks, my_rungs, unknown_keys),
    /// so the brain keeps calling ladder / ladder_set (owner decision 2). Must be called on the main thread.
    /// Every result is a plain dictionary / list / string / double / bool tree.
    /// </summary>
    public static class Api
    {
        /// <summary>
        /// The result tree with every ordered JsonObject turned into a Dictionary, for transports that serialize .NET
        /// objects themselves (the bridge); a List of pairs would otherwise come out as an array of {Key, Value}.
        /// </summary>
        public static object Plain(object v)
        {
            switch (v)
            {
                case null: return null;
                case string s: return s;
                case JsonObject o:
                    var d = new Dictionary<string, object>();
                    foreach (var kv in o) d[kv.Key] = Plain(kv.Value);
                    return d;
                case IDictionary<string, object> dict:
                    var e = new Dictionary<string, object>();
                    foreach (var kv in dict) e[kv.Key] = Plain(kv.Value);
                    return e;
                case System.Collections.IList list:
                    var l = new List<object>();
                    foreach (object x in list) l.Add(Plain(x));
                    return l;
                default: return v;
            }
        }

        public static Dictionary<string, object> Refused(string why)
        {
            return new Dictionary<string, object> { { "ok", false }, { "refused", why } };
        }

        private static Dictionary<string, object> Ok(string result, string note = null)
        {
            var d = new Dictionary<string, object> { { "ok", true }, { "result", result } };
            if (!string.IsNullOrEmpty(note)) d["note"] = note;
            return d;
        }

        private static RimPLCGameComponent Plc(out Dictionary<string, object> refusal)
        {
            refusal = null;
            RimPLCGameComponent c = RimPLCGameComponent.Get();
            if (c == null) refusal = Refused("no game loaded");
            else if (RimPLCMod.Book.LoadError != null) refusal = Refused("book preset did not load: " + RimPLCMod.Book.LoadError);
            return c;
        }

        /// <summary>rimplc/read_ladder. A fresh input + logic scan (no output), then the live rungs.</summary>
        public static Dictionary<string, object> ReadLadder(int top = 4, bool all = false)
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            ScanResult r = c.Scan(false);
            if (r == null) return Refused("scan failed (see the game log)");
            top = Math.Max(1, Math.Min(50, top));
            IEnumerable<RungEval> hits = all ? r.Hits : r.Hits.Take(top);
            var live = hits.Select(h =>
            {
                var o = new JsonObject
                {
                    new KeyValuePair<string, object>("id", h.Rung.Id),
                    new KeyValuePair<string, object>("priority", h.Rung.Priority),
                    new KeyValuePair<string, object>("matched", h.Matched),
                    new KeyValuePair<string, object>("then", h.Then.Cast<object>().ToList()),
                };
                if (h.Rung.Notice != null) o.Set("notice", h.Rung.Notice);
                if (h.Rung.Chain != null) o.Set("chain", h.Rung.Chain);
                if (h.Rung.Check != null) o.Set("check", h.Rung.Check);
                return (object)o;
            }).ToList();
            return new Dictionary<string, object>
            {
                { "ok", true },
                { "live_rungs", live },
                { "tags", r.Tags },
                { "my_marks", c.Marks },
                { "my_rungs", c.MyRungs.Select(x => (object)x.Id).ToList() },
                { "unknown_keys", r.UnknownKeys.Cast<object>().ToList() },
                { "live", Engine.LiveRung(r).Select(h => (object)h.Rung.Id).ToList() },
                { "unresolved_conditions", r.Unresolved.Distinct().Cast<object>().ToList() },
                { "disabled_rungs", r.DisabledRungs },
                { "not_applicable", r.NotApplicable.Cast<object>().ToList() },
                { "scan_tick", (double)r.Tick },
                { "scan_ms", Math.Round(r.Ms, 3) },
                { "paused", r.State.TryGetValue("paused", out object p) && Engine.Truthy(p) },
            };
        }

        /// <summary>rimplc/read_state: the sensor dict, absent keys omitted.</summary>
        public static Dictionary<string, object> ReadState(IList<string> keys = null)
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            ScanResult r = c.Scan(false);
            if (r == null) return Refused("scan failed (see the game log)");
            var st = new JsonObject();
            foreach (var kv in r.State.OrderBy(kv => kv.Key, StringComparer.Ordinal))
            {
                if (kv.Key == "tags") continue;
                if (keys != null && keys.Count > 0 && !keys.Contains(kv.Key)) continue;
                st.Add(kv);
            }

            return new Dictionary<string, object> { { "ok", true }, { "state", st }, { "scan_tick", (double)r.Tick } };
        }

        public static Dictionary<string, object> SetTag(string name, object value, bool owner = false)
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            if (!c.SetTag(name, value, owner, out string note)) return Refused(note);
            c.AddLog(Tick(), "-", "tag " + name + " = " + Json.Write(value) + note, "api");
            return Ok("ladder updated: tag " + name, note.Trim());
        }

        public static Dictionary<string, object> SetMark(string name, object value)
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            if (!c.SetMark(name, value, out string err)) return Refused(err);
            c.AddLog(Tick(), "-", "mark " + name + " = " + Json.Write(c.Marks.Get(name)), "api");
            return Ok("ladder updated: mark " + name);
        }

        /// <summary>rimplc/upsert_rung: the rung as a JSON object or its text. Forced to unity-*, advise.</summary>
        public static Dictionary<string, object> UpsertRung(object rung)
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            JsonObject o = rung as JsonObject;
            if (o == null)
            {
                // a JSON text, or an object the transport passed through (its ToString() is its JSON text)
                string text = rung as string ?? Convert.ToString(rung, CultureInfo.InvariantCulture);
                try { o = Json.ParseObject(text); }
                catch (FormatException e) { return Refused("rung is not a JSON object: " + e.Message); }
            }

            if (!c.UpsertRung(o, "unity", out string note)) return Refused(note);
            c.AddLog(Tick(), note.Split(' ')[0], "upserted", "api");
            return Ok("ladder updated: add_rung " + note);
        }

        public static Dictionary<string, object> RemoveRung(string id)
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            if (!c.RemoveRung(id, out string note)) return Refused(note);
            c.AddLog(Tick(), id, "removed", "api");
            return Ok("ladder updated: remove_rung " + id);
        }

        public static Dictionary<string, object> EnableRung(string id, bool enabled, bool owner = false)
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            if (!c.EnableRung(id, enabled, owner, out string note)) return Refused(note);
            c.AddLog(Tick(), id, enabled ? "switched on" : "switched off", "api");
            return Ok("ladder updated: " + id + (enabled ? " on" : " off"));
        }

        public static Dictionary<string, object> LettersSeen()
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            c.MarkLettersSeen();
            return Ok("letters marked seen: " + c.LettersSeen.Count);
        }

        /// <summary>rimplc/export: the player's and Unity's layer as a ladder file (Transfer.ExportDoc), written to the exports folder.</summary>
        public static Dictionary<string, object> Export(string name = null)
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            string path = Transfer.ExportFile(c, name);
            return new Dictionary<string, object> { { "ok", true }, { "result", "exported " + c.MyRungs.Count + " rungs" }, { "path", path }, { "ladder", Transfer.ExportDoc(c) } };
        }

        /// <summary>
        /// rimplc/import: a ladder (object or JSON text). dry_run (the default) returns the diff only; dry_run false applies
        /// it. Rungs become unity- rungs in advise mode; switches, auto modes and constants need the owner flag.
        /// </summary>
        public static Dictionary<string, object> Import(object ladder, bool dryRun = true, bool owner = false)
        {
            RimPLCGameComponent c = Plc(out var refusal);
            if (c == null) return refusal;
            JsonObject doc = ladder as JsonObject;
            if (doc == null)
            {
                try { doc = Json.ParseObject(ladder as string ?? Convert.ToString(ladder, CultureInfo.InvariantCulture)); }
                catch (FormatException e) { return Refused("ladder is not a JSON object: " + e.Message); }
            }

            ImportPlan plan = Transfer.Plan(c, doc, "unity", owner);
            if (plan.Error != null) return Refused(plan.Error);
            if (!dryRun)
            {
                foreach (Action act in plan.Actions) act();
                c.AddLog(Tick(), "-", "import: " + plan.Changes + " changes", "api");
            }

            return new Dictionary<string, object>
            {
                { "ok", true },
                { "result", (dryRun ? "import would make " : "imported: ") + plan.Changes + " changes" },
                { "diff", plan.ToResult() },
                { "applied", !dryRun },
            };
        }

        private static int Tick()
        {
            return Verse.Find.TickManager?.TicksGame ?? 0;
        }
    }
}
