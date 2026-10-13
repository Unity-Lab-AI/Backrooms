using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.RegularExpressions;

namespace RimPLC
{
    /// <summary>
    /// The import rules of tools/rimplc-check.py (docs/RIMPLC_DESIGN.md section 7) for one rung, so the in-game editor,
    /// import and the AI API refuse exactly what the checker refuses:
    ///   * id ^[a-z0-9][a-z0-9-]{0,63}$, priority a number, when an object, then a list of strings;
    ///   * a player / unity rung's id starts with its source and carries at most 8 then lines of at most 300 characters;
    ///   * every plain when key is a sensor, a tag, mark_*, alert_*, count_*, research_* or letter_matches
    ///     (a disabled rung may name an unmeasured key: a note, not an error);
    ///   * every {TAG} bound names a tag, and a string starting with &lt; &gt; ! has an operator;
    ///   * a nested instruction is exactly one of any / not / ton / tof / ctu / ons with its own fields;
    ///   * requires entries are a DLC name or mod:&lt;packageId&gt;; coils name a known action and type;
    ///   * a unity rung's notice passes the clean-word filter (it shows in the game, and the game is on stream).
    /// </summary>
    public static class Validate
    {
        public static readonly Regex IdRule = new Regex("^[a-z0-9][a-z0-9-]{0,63}$");
        public static readonly Regex KeyRule = new Regex("^([a-z][a-z0-9_]*|[A-Z][A-Z0-9_]*)$");
        private static readonly Regex RequiresRule = new Regex("^(Royalty|Ideology|Biotech|Anomaly|Odyssey|mod:[A-Za-z0-9_.-]+)$");
        private static readonly Regex TagRef = new Regex(@"\{([^}]*)\}");
        private static readonly string[] KnownPrefixes = { "mark_", "alert_", "count_", "research_" };

        public static readonly string[] CoilActions =
        {
            "message", "set_mark", "set_tag", "letter", "set_work_priority", "add_bill", "set_bill_count", "set_zone_plant",
            "set_zone_sowing", "set_area", "set_schedule", "set_medical_care", "set_hostility_response", "draft", "undraft",
            "designate", "forbid", "unforbid", "set_research", "pause", "set_speed",
        };

        private static readonly string[] CoilTypes = { "OTE", "OTL", "OTU", "pulse" };
        private static readonly string[] Chains = { "combat", "medical", "repairs", "defense", "supply" };

        /// <summary>Errors (refuse) and notes (show, allow) for one rung object.</summary>
        /// <param name="liveKeys">keys measured right now (optional): a key the game measures is known even if the catalogue does not list it</param>
        public static List<string> Rung(JsonObject o, Ladder book, ICollection<string> liveKeys, out List<string> notes)
        {
            var errs = new List<string>();
            notes = new List<string>();
            if (o == null) { errs.Add("rung is not an object"); return errs; }
            string id = o.Get("id") as string;
            string label = id ?? "(no id)";
            if (id == null || !IdRule.IsMatch(id)) errs.Add(label + ": id must match ^[a-z0-9][a-z0-9-]{0,63}$");
            if (!(o.Get("priority") is double)) errs.Add(label + ": priority is not a number");
            if (!(o.Get("when") is JsonObject when)) { errs.Add(label + ": when is not an object"); when = null; }
            object then = o.Get("then");
            if (!(then is List<object> tl) || tl.Any(x => !(x is string))) errs.Add(label + ": then is not a list of text lines");
            string source = o.GetString("source") ?? "book";
            if (source != "book" && source != "player" && source != "unity") errs.Add(label + ": source is book, player or unity");
            bool disabled = o.Get("disabled") is string;
            if (source != "book")
            {
                List<string> lines = Rung_Strings(then);
                if (lines.Count > 8 || lines.Any(s => s.Length > 300)) errs.Add(label + ": then over 8 lines / 300 characters");
                bool overrideOfBook = source == "player" && book != null && book.Rungs.Any(r => r.Id == id);
                if (id != null && !id.StartsWith(source + "-", StringComparison.Ordinal) && !overrideOfBook)
                {
                    errs.Add(label + ": a " + source + " rung id starts with " + source + "-");
                }
            }

            string mode = o.Get("mode") as string;
            if (o.Has("mode") && mode != "advise" && mode != "auto" && mode != "off") errs.Add(label + ": mode is advise, auto or off");
            string chain = o.Get("chain") as string;
            if (o.Has("chain") && Array.IndexOf(Chains, chain) < 0) errs.Add(label + ": chain is one of " + string.Join(", ", Chains));
            foreach (object q in o.GetList("requires") ?? new List<object>())
            {
                if (!(q is string qs) || !RequiresRule.IsMatch(qs)) errs.Add(label + ": requires entry " + Json.Write(q) + " is not a DLC or mod:<packageId>");
            }

            foreach (object c in o.GetList("coils") ?? new List<object>())
            {
                var coil = c as JsonObject;
                if (coil == null || Array.IndexOf(CoilActions, coil.GetString("do")) < 0) errs.Add(label + ": coil " + Json.Write(c) + " has no known do");
                else if (coil.Has("type") && Array.IndexOf(CoilTypes, coil.GetString("type")) < 0) errs.Add(label + ": coil type is OTE, OTL, OTU or pulse");
            }

            string notice = o.Get("notice") as string;
            if (notice != null && !CleanText.IsClean(notice))
            {
                if (source == "unity") errs.Add("notice is not clean for the stream: reword it");
                else notes.Add(label + ": notice is not clean for the stream and will not be shown");
            }

            if (when != null) When(label, when, book, liveKeys, disabled, errs, notes, 0);
            return errs;
        }

        private static List<string> Rung_Strings(object then)
        {
            return then is List<object> l ? l.Select(x => x as string ?? Convert.ToString(x, CultureInfo.InvariantCulture)).ToList() : new List<string>();
        }

        public static bool KnownKey(string k, Ladder book, ICollection<string> liveKeys)
        {
            if (k == "letter_matches") return true;
            if (KnownPrefixes.Any(p => k.StartsWith(p, StringComparison.Ordinal))) return true;
            if (book != null && (book.Sensors.Has(k) || book.Constants.Has(k) || book.Variables.Has(k))) return true;
            return liveKeys != null && liveKeys.Contains(k);
        }

        private static bool KnownTag(string t, Ladder book)
        {
            return book != null && (book.Constants.Has(t) || book.Variables.Has(t));
        }

        private static void When(string rid, JsonObject when, Ladder book, ICollection<string> liveKeys, bool disabled,
                                 List<string> errs, List<string> notes, int depth)
        {
            if (depth > 8) { errs.Add(rid + ": instructions nested too deep"); return; }
            foreach (var kv in when)
            {
                string k = kv.Key;
                if (!KeyRule.IsMatch(k)) errs.Add(rid + ": when key " + k + " is not lower_case or UPPER_CASE");
                object w = kv.Value;
                if (w is JsonObject e)
                {
                    Instruction(rid, k, e, book, liveKeys, disabled, errs, notes, depth);
                    continue;
                }

                if (!(w is bool || w is double || w is string)) errs.Add(rid + ": " + k + " wants a bool, number or text");
                if (!KnownKey(k, book, liveKeys))
                {
                    (disabled ? notes : errs).Add(rid + ": when key " + k + " has no sensor, tag or mark");
                }

                if (w is string ws)
                {
                    foreach (Match m in TagRef.Matches(ws))
                    {
                        if (!KnownTag(m.Groups[1].Value.Trim(), book)) errs.Add(rid + ": " + k + " names unknown tag {" + m.Groups[1].Value + "}");
                    }

                    if (ws.Length > 0 && (ws[0] == '<' || ws[0] == '>' || ws[0] == '!') &&
                        !new[] { ">=", "<=", "!=", ">", "<" }.Any(op => ws.StartsWith(op, StringComparison.Ordinal)))
                    {
                        errs.Add(rid + ": " + k + " has no operator in " + Json.Write(ws));
                    }
                }
            }
        }

        private static void Instruction(string rid, string k, JsonObject e, Ladder book, ICollection<string> liveKeys, bool disabled,
                                        List<string> errs, List<string> notes, int depth)
        {
            string op = Engine.ExprOp(e);
            if (op == null)
            {
                errs.Add(rid + ": " + k + " is not exactly one of " + string.Join("/", Engine.Nested));
                return;
            }

            var allowed = new HashSet<string> { op };
            if (op == "ton" || op == "tof") { allowed.Add("ticks"); allowed.Add("hours"); }
            if (op == "ctu") { allowed.Add("preset"); allowed.Add("reset"); }
            foreach (var kv in e)
            {
                if (!allowed.Contains(kv.Key)) errs.Add(rid + ": " + k + " (" + op + ") has an unknown field " + kv.Key);
            }

            if (op == "any")
            {
                List<object> branches = e.GetList("any");
                if (branches == null || branches.Count == 0) errs.Add(rid + ": " + k + " any needs a list of at least one condition object");
                foreach (object b in branches ?? new List<object>())
                {
                    if (b is JsonObject bw) When(rid, bw, book, liveKeys, disabled, errs, notes, depth + 1);
                    else errs.Add(rid + ": " + k + " any branch is not an object");
                }

                return;
            }

            if (e.Get(op) is JsonObject inner) When(rid, inner, book, liveKeys, disabled, errs, notes, depth + 1);
            else errs.Add(rid + ": " + k + " " + op + " needs a condition object");
            if (op == "ton" || op == "tof")
            {
                bool ticks = e.Get("ticks") is double t && t >= 1 && t == Math.Floor(t);
                bool hours = e.Get("hours") is double h && h > 0;
                if (ticks == hours) errs.Add(rid + ": " + k + " " + op + " needs ticks (a whole number, 1 or more) or hours (more than 0), not both");
            }

            if (op == "ctu")
            {
                if (!(e.Get("preset") is double p && p >= 1 && p == Math.Floor(p))) errs.Add(rid + ": " + k + " ctu needs preset (a whole number, 1 or more)");
                if (e.Has("reset"))
                {
                    if (e.Get("reset") is JsonObject rw) When(rid, rw, book, liveKeys, disabled, errs, notes, depth + 1);
                    else errs.Add(rid + ": " + k + " ctu reset is not a condition object");
                }
            }
        }
    }
}
