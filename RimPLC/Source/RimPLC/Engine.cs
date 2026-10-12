using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

namespace RimPLC
{
    /// <summary>The book: a ladder file in the frozen shape (docs/rimplc/schema/ladder.schema.json).</summary>
    public sealed class Ladder
    {
        public string PresetId = "LadderV2";
        public int Version;
        public JsonObject Sensors = new JsonObject();
        public List<Rung> Rungs = new List<Rung>();
        public JsonObject Constants = new JsonObject();
        public JsonObject Variables = new JsonObject();
        public JsonObject MarkDefaults = new JsonObject();
        public string LoadError;

        public static Ladder Load(string path)
        {
            var l = new Ladder();
            try
            {
                l.Read(Json.ParseObject(File.ReadAllText(path)));
            }
            catch (Exception e)
            {
                l.LoadError = Path.GetFileName(path) + ": " + e.Message;
            }

            return l;
        }

        public void Read(JsonObject o)
        {
            Version = o.Get("version") is double v ? (int)v : 0;
            PresetId = o.GetObject("preset")?.GetString("id") ?? PresetId;
            Sensors = o.GetObject("sensors") ?? new JsonObject();
            var gates = o.GetList("gates") ?? throw new FormatException("no gates");
            Rungs = gates.Select(g => Rung.From(g as JsonObject, "book")).ToList();
            JsonObject tags = o.GetObject("tags") ?? new JsonObject();
            Constants = tags.GetObject("constants") ?? new JsonObject();
            Variables = tags.GetObject("variables") ?? new JsonObject();
            MarkDefaults = o.GetObject("marks")?.GetObject("defaults") ?? new JsonObject();
        }
    }

    /// <summary>The colour of one contact in the ladder window.</summary>
    public enum Contact
    {
        True,
        False,
        Unmeasured,
        Unresolved,
    }

    public sealed class RungEval
    {
        public Rung Rung;
        public JsonObject When;          // after latch and grace
        public List<string> Then;        // after latch
        public bool Applicable = true;   // requires satisfied
        public string Off;               // reason it is not scanned (disabled, off, switched off), null when scanned
        public bool Live;                // every condition holds
        public List<KeyValuePair<string, Contact>> Contacts = new List<KeyValuePair<string, Contact>>();
        public JsonObject Matched;
    }

    public sealed class ScanResult
    {
        public int Tick;
        public double Ms;
        public bool PausedScan;
        public Dictionary<string, object> State = new Dictionary<string, object>();
        public JsonObject Tags = new JsonObject();
        public List<RungEval> Rungs = new List<RungEval>();      // every rung, priority order
        public List<RungEval> Hits = new List<RungEval>();       // live rungs, priority order
        public List<string> UnknownKeys = new List<string>();
        public List<string> Unresolved = new List<string>();
        public JsonObject DisabledRungs = new JsonObject();
        public List<string> NotApplicable = new List<string>();
    }

    /// <summary>
    /// The logic scan. A line-for-line port of .local/autopilot/gates.py (tags, _latched, _bound, _holds, explain,
    /// rungs, decide) so the in-game ladder and the Python ladder agree on every rung:
    ///   * a key that is not measured fails its condition (unmeasured is not false);
    ///   * an unresolved bound fails and is recorded in unresolved_conditions;
    ///   * hers (here: player and unity rungs) replace a book rung of the same id;
    ///   * latched rungs get their done-mark; grace holds rungs GRACE_FROM_PRIORITY..98 until day &gt; START_GRACE_DAYS;
    ///   * the live rung is the first hit plus always.
    /// RimPLC adds only: rungs whose requires is not active are not scanned, and the player's on/off switch and mode
    /// off count as disabled.
    /// </summary>
    public static class Engine
    {
        private static readonly string[] Ops = { ">=", "<=", "!=", ">", "<" };

        public static bool IsNumber(object v)
        {
            return v is double || v is int || v is float || v is long;
        }

        public static double ToDouble(object v)
        {
            return Convert.ToDouble(v, CultureInfo.InvariantCulture);
        }

        /// <summary>Python truthiness.</summary>
        public static bool Truthy(object v)
        {
            switch (v)
            {
                case null: return false;
                case bool b: return b;
                case string s: return s.Length > 0;
                case System.Collections.ICollection c: return c.Count > 0;
                default: return !IsNumber(v) || ToDouble(v) != 0;
            }
        }

        /// <summary>Python str() for the exact-text comparison. An integral number prints without ".0" (C# keeps no int/float split).</summary>
        public static string PyStr(object v)
        {
            switch (v)
            {
                case null: return "None";
                case bool b: return b ? "True" : "False";
                case string s: return s;
                default: return IsNumber(v) ? Json.Num(ToDouble(v)) : Convert.ToString(v, CultureInfo.InvariantCulture);
            }
        }

        // -------------------------------------------------------------------------------------------- tags

        /// <summary>gates.tags(): constants stay put, variables are recomputed from the colony's size, clamped, overridable.</summary>
        public static JsonObject Tags(Ladder book, Dictionary<string, object> st, IDictionary<string, double> overrides)
        {
            int n = Math.Max(1, st.TryGetValue("colonists", out object c) && IsNumber(c) ? (int)ToDouble(c) : 0);
            var computed = new Dictionary<string, double>
            {
                { "FOOD_MIN_DAYS", 2 + 0.4 * n },
                { "FOOD_COMFORT_DAYS", 2 * (2 + 0.4 * n) },
                { "MEAL_BILL_TARGET", 10 * n },
                { "WOOD_RESERVE", 60 * n },
                { "MEDICINE_RESERVE", 2 * n },
                { "BEDS_NEEDED", n + 1 },
                { "COOLERS_PER_ROOM", 1 },
                { "TURRET_TARGET", 2 + n / 3 },
                { "STOCK_CELLS", 30 + 15 * n },
                { "COMPONENT_RESERVE", 5 + n },
                { "STEEL_RESERVE", 150 * n },
                { "AID_CALL_FOES", 2 * n },
                { "MOUNT_TARGET", n },
                { "WEAPON_KEEP", n + 2 },
            };
            if (st.TryGetValue("home_cells", out object home) && IsNumber(home))
            {
                computed["EMBRASURE_TARGET"] = (int)(4 * Math.Sqrt(ToDouble(home)));
            }

            JsonObject output = book.Constants.Copy();
            if (overrides != null)
            {
                // a constant changes only through an owner-flagged set_tag (the API refuses it otherwise)
                foreach (var kv in book.Constants)
                {
                    if (overrides.TryGetValue(kv.Key, out double ov)) output.Set(kv.Key, ov);
                }
            }

            double? podSquad = null;
            foreach (var kv in book.Variables)
            {
                string name = kv.Key;
                var spec = kv.Value as JsonObject ?? new JsonObject();
                double v;
                bool overridden = overrides != null && overrides.ContainsKey(name);
                if (overridden) v = overrides[name];
                else if (computed.TryGetValue(name, out double cv)) v = cv;
                else v = spec.Get("value") is double sv ? sv : 0;
                if (name == "POD_FUEL" && !overridden && podSquad.HasValue) v = 150 * podSquad.Value;
                if (spec.Get("min") is double lo) v = Math.Max(lo, v);
                if (spec.Get("max") is double hi) v = Math.Min(hi, v);
                v = Math.Round(v, 2);
                output.Set(name, v);
                if (name == "POD_SQUAD") podSquad = v;
            }

            return output;
        }

        // -------------------------------------------------------------------------------------------- conditions

        /// <summary>gates._bound: a number, a {TAG}, or a measured state/tag name. Null when it cannot be resolved.</summary>
        public static double? Bound(string expr, Dictionary<string, object> st, JsonObject tagvals)
        {
            string e = expr.Trim();
            if (e.StartsWith("{") && e.EndsWith("}")) e = e.Substring(1, e.Length - 2).Trim();
            if (double.TryParse(e, NumberStyles.Float, CultureInfo.InvariantCulture, out double d)) return d;
            if (tagvals.TryGet(e, out object tv) && IsNumber(tv)) return ToDouble(tv);
            if (st.TryGetValue(e, out object sv) && IsNumber(sv)) return ToDouble(sv);
            return null;
        }

        /// <summary>One condition, the way gates._holds tests it. unresolved (may be null) collects unresolved bounds.</summary>
        public static Contact Test(string key, object want, Dictionary<string, object> st, JsonObject tagvals, List<string> unresolved)
        {
            if (key == "letter_matches")
            {
                string sub = PyStr(want).ToLowerInvariant();
                var labels = st.TryGetValue("letter_labels", out object ll) ? ll as List<object> : null;
                bool any = labels != null && labels.Any(l => (l as string ?? string.Empty).ToLowerInvariant().Contains(sub));
                return any ? Contact.True : Contact.False;
            }

            object got;
            if (st.TryGetValue(key, out object sg)) got = sg;
            else if (tagvals.TryGet(key, out object tg)) got = tg;
            else return Contact.Unmeasured;

            if (want is bool wb) return Truthy(got) == wb ? Contact.True : Contact.False;
            if (IsNumber(want))
            {
                if (got == null || got is bool || !IsNumber(got)) return Contact.False;
                return ToDouble(got) == ToDouble(want) ? Contact.True : Contact.False;
            }

            if (want is string ws && ws.Length > 0 && (ws[0] == '<' || ws[0] == '>' || ws[0] == '!'))
            {
                string op = Ops.FirstOrDefault(o => ws.StartsWith(o, StringComparison.Ordinal));
                double? reference = op == null ? null : Bound(ws.Substring(op.Length), st, tagvals);
                if (reference == null)
                {
                    unresolved?.Add(key + " " + ws);
                    return Contact.Unresolved;
                }

                if (got == null || got is bool || !IsNumber(got)) return Contact.False;
                double g = ToDouble(got), r = reference.Value;
                bool ok;
                switch (op)
                {
                    case ">": ok = g > r; break;
                    case "<": ok = g < r; break;
                    case ">=": ok = g >= r; break;
                    case "<=": ok = g <= r; break;
                    default: ok = g != r; break;
                }

                return ok ? Contact.True : Contact.False;
            }

            if (want is string text) return PyStr(got) == text ? Contact.True : Contact.False;
            return Contact.False;   // null or a nested object: reserved for the P2 operators, never fires in P1
        }

        /// <summary>gates._holds: an AND, tested in order, stopping at the first failure (as Python does).</summary>
        public static bool Holds(JsonObject when, Dictionary<string, object> st, JsonObject tagvals, List<string> unresolved)
        {
            foreach (var kv in when)
            {
                if (Test(kv.Key, kv.Value, st, tagvals, unresolved) != Contact.True) return false;
            }

            return true;
        }

        /// <summary>gates.explain: the measured value behind each condition.</summary>
        public static JsonObject Explain(JsonObject when, Dictionary<string, object> st, JsonObject tagvals)
        {
            var o = new JsonObject();
            foreach (var kv in when)
            {
                if (kv.Key == "letter_matches") o.Set(kv.Key, kv.Value);
                else if (st.TryGetValue(kv.Key, out object v)) o.Set(kv.Key, v);
                else if (tagvals.TryGet(kv.Key, out object t)) o.Set(kv.Key, t);
                else o.Set(kv.Key, "unmeasured");
            }

            return o;
        }

        // -------------------------------------------------------------------------------------------- the scan

        /// <summary>gates.rungs: book rungs plus mine; mine replace a book rung of the same id.</summary>
        public static List<Rung> Merge(Ladder book, IList<Rung> mine)
        {
            var ids = new HashSet<string>(mine.Select(r => r.Id));
            return book.Rungs.Where(r => !ids.Contains(r.Id)).Concat(mine).ToList();
        }

        /// <param name="sensors">the measured input image (absent keys are simply not in it)</param>
        /// <param name="marks">mark name -> bool or double</param>
        /// <param name="switchedOff">ids the player switched off in the window</param>
        /// <param name="applicable">requires test (DLC / mod active)</param>
        public static ScanResult Scan(Ladder book, IList<Rung> mine, Dictionary<string, object> sensors, JsonObject marks,
                                      IDictionary<string, double> tagOverrides, ICollection<string> switchedOff,
                                      Func<string, bool> applicable)
        {
            var res = new ScanResult();
            var st = new Dictionary<string, object>(sensors);
            // her own marks: numbers stay numbers, everything else is a boolean (gates.derive)
            foreach (var kv in marks)
            {
                st["mark_" + kv.Key] = IsNumber(kv.Value) ? (object)ToDouble(kv.Value) : Truthy(kv.Value);
            }

            foreach (string k in new[] { "pawns_set", "assign_set", "beds_set", "stove_set", "bill_set" })
            {
                if (!st.ContainsKey("mark_" + k)) st["mark_" + k] = false;
            }

            // gates.py read explore_done from a file the bridge client wrote; in game it is her (or the player's) mark
            if (!st.ContainsKey("explore_done")) st["explore_done"] = st.TryGetValue("mark_explore_done", out object ex) && Truthy(ex);

            Sensors.ChainInputs(st);

            JsonObject tagvals = Tags(book, st, tagOverrides);
            res.Tags = tagvals;

            List<Rung> all = Merge(book, mine);
            // marks: numeric defaults from the book; a boolean mark nobody has set yet reads false
            foreach (var kv in book.MarkDefaults)
            {
                if (!st.ContainsKey("mark_" + kv.Key)) st["mark_" + kv.Key] = kv.Value;
            }

            var evals = new List<RungEval>();
            foreach (Rung r in all)
            {
                r.Latched(out JsonObject when, out List<string> then);
                var ev = new RungEval { Rung = r, When = when, Then = then };
                ev.Applicable = r.Requires.Count == 0 || r.Requires.All(q => applicable == null || applicable(q));
                if (!string.IsNullOrEmpty(r.Disabled)) ev.Off = r.Disabled;
                else if (r.Mode == "off") ev.Off = "mode off";
                else if (switchedOff != null && switchedOff.Contains(r.Id)) ev.Off = "switched off in RimPLC";
                evals.Add(ev);
                foreach (var kv in when)
                {
                    if (kv.Key.StartsWith("mark_", StringComparison.Ordinal) && kv.Value is bool && !st.ContainsKey(kv.Key))
                    {
                        st[kv.Key] = false;
                    }
                }
            }

            double? gfrom = tagvals.Get("GRACE_FROM_PRIORITY") is object gf && IsNumber(gf) ? ToDouble(gf) : (double?)null;
            object graceV = tagvals.Get("START_GRACE_DAYS");
            bool hasGrace = graceV != null && IsNumber(graceV);

            foreach (RungEval ev in evals)
            {
                if (ev.Off != null) res.DisabledRungs.Set(ev.Rung.Id, ev.Off);
                if (!ev.Applicable) res.NotApplicable.Add(ev.Rung.Id);
            }

            var scanned = evals.Where(e => e.Off == null && e.Applicable).ToList();
            var known = new HashSet<string>(book.Sensors.Select(kv => kv.Key));
            res.UnknownKeys = scanned.SelectMany(e => e.Rung.When.Select(kv => kv.Key))
                .Where(k => k != "letter_matches" && !k.StartsWith("mark_", StringComparison.Ordinal) &&
                            !k.StartsWith("alert_", StringComparison.Ordinal) && !known.Contains(k) &&
                            !tagvals.Has(k) && !st.ContainsKey(k))
                .Distinct().OrderBy(k => k, StringComparer.Ordinal).ToList();

            foreach (RungEval ev in scanned)
            {
                if (gfrom.HasValue && hasGrace && ev.Rung.Id != "always" && gfrom.Value <= ev.Rung.Priority && ev.Rung.Priority < 99)
                {
                    ev.When = ev.When.Copy();
                    ev.When.SetDefault("day", ">" + PyStr(graceV));
                }
            }

            // stable sort by priority, as Python's sorted()
            var ordered = evals.Select((e, i) => new { e, i }).OrderBy(x => x.e.Rung.Priority).ThenBy(x => x.i).Select(x => x.e).ToList();
            foreach (RungEval ev in ordered)
            {
                bool scan = ev.Off == null && ev.Applicable;
                if (scan) ev.Live = Holds(ev.When, st, tagvals, res.Unresolved);
                foreach (var kv in ev.When)
                {
                    ev.Contacts.Add(new KeyValuePair<string, Contact>(kv.Key, Test(kv.Key, kv.Value, st, tagvals, null)));
                }

                if (ev.Live)
                {
                    ev.Matched = Explain(ev.When, st, tagvals);
                    res.Hits.Add(ev);
                }
            }

            st["tags"] = tagvals;
            res.Rungs = ordered;
            res.State = st;
            return res;
        }

        /// <summary>gates.decide(every=False): the first live rung plus always.</summary>
        public static List<RungEval> LiveRung(ScanResult r)
        {
            var o = r.Hits.Take(1).ToList();
            o.AddRange(r.Hits.Where(h => h.Rung.Id == "always").Take(1));
            return o;
        }
    }
}
