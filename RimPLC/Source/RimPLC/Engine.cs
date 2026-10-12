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
        public JsonObject BaseWhen;      // after latch, before grace (what gates.explain reports)
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
        /// <summary>Timer / counter / one-shot memory after this scan (kept only when the scan commits).</summary>
        public Dictionary<string, Instr> Memory = new Dictionary<string, Instr>();
    }

    /// <summary>The memory of one timer, counter or one-shot (gates._instructions: prev, start, last, count).</summary>
    public sealed class Instr
    {
        public bool Prev;
        public int? Start;
        public int? Last;
        public int Count;

        public Instr Copy()
        {
            return new Instr { Prev = Prev, Start = Start, Last = Last, Count = Count };
        }

        /// <summary>Save form: "prev,start,last,count" (an empty field is no value).</summary>
        public string Pack()
        {
            Func<int?, string> f = v => v.HasValue ? v.Value.ToString(CultureInfo.InvariantCulture) : string.Empty;
            return (Prev ? "1" : "0") + "," + f(Start) + "," + f(Last) + "," + Count.ToString(CultureInfo.InvariantCulture);
        }

        public static Instr Unpack(string s)
        {
            string[] p = (s ?? string.Empty).Split(',');
            if (p.Length != 4) return null;
            Func<string, int?> f = v => int.TryParse(v, NumberStyles.Integer, CultureInfo.InvariantCulture, out int n) ? n : (int?)null;
            return new Instr { Prev = p[0] == "1", Start = f(p[1]), Last = f(p[2]), Count = f(p[3]) ?? 0 };
        }
    }

    /// <summary>One scan's instruction state: working memory, outputs by path, and the game tick.</summary>
    public sealed class ScanContext
    {
        public Dictionary<string, Instr> Memory = new Dictionary<string, Instr>();
        public Dictionary<string, Contact> Out = new Dictionary<string, Contact>();
        public int? Now;
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

        /// <summary>Nested instructions (an object as a condition value), same names and rules as gates.NESTED.</summary>
        public static readonly string[] Nested = { "any", "not", "ton", "tof", "ctu", "ons" };
        public static readonly string[] Stateful = { "ton", "tof", "ctu", "ons" };
        public const int TicksPerHour = 2500;

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

        /// <summary>
        /// One condition, the way gates._leaf tests it. unresolved (may be null) collects unresolved bounds. A value that
        /// is an object is a nested instruction (any / not / ton / tof / ctu / ons); ctx carries the outputs of this
        /// scan's instruction pass and path names the instruction (rung id / key ...). Without ctx a timer, counter or
        /// one-shot reads unmeasured.
        /// </summary>
        public static Contact Test(string key, object want, Dictionary<string, object> st, JsonObject tagvals, List<string> unresolved,
                                   ScanContext ctx = null, string path = null)
        {
            if (key == "letter_matches")
            {
                string sub = PyStr(want).ToLowerInvariant();
                var labels = st.TryGetValue("letter_labels", out object ll) ? ll as List<object> : null;
                bool any = labels != null && labels.Any(l => (l as string ?? string.Empty).ToLowerInvariant().Contains(sub));
                return any ? Contact.True : Contact.False;
            }

            if (want is JsonObject expr) return Expr(key, expr, st, tagvals, unresolved, ctx, path ?? key);

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
            return Contact.False;
        }

        /// <summary>gates._branch: an AND tested in order; the first condition that does not hold is the result.</summary>
        public static Contact Branch(object cond, Dictionary<string, object> st, JsonObject tagvals, List<string> unresolved,
                                     ScanContext ctx, string path)
        {
            var when = cond as JsonObject;
            if (when == null) return Contact.Unresolved;
            foreach (var kv in when)
            {
                Contact c = Test(kv.Key, kv.Value, st, tagvals, unresolved, ctx, path + "/" + kv.Key);
                if (c != Contact.True) return c;
            }

            return Contact.True;
        }

        /// <summary>The instruction an object condition holds, or null when it is not exactly one known instruction.</summary>
        public static string ExprOp(JsonObject e)
        {
            string found = null;
            foreach (string op in Nested)
            {
                if (!e.Has(op)) continue;
                if (found != null) return null;
                found = op;
            }

            return found;
        }

        private static Contact Expr(string key, JsonObject e, Dictionary<string, object> st, JsonObject tagvals, List<string> unresolved,
                                    ScanContext ctx, string path)
        {
            string op = ExprOp(e);
            if (op == null)
            {
                unresolved?.Add(key + " not one instruction of " + string.Join("/", Nested));
                return Contact.Unresolved;
            }

            if (op == "any")
            {
                var got = new List<Contact>();
                List<object> branches = e.GetList("any") ?? new List<object>();
                for (int i = 0; i < branches.Count; i++)
                {
                    got.Add(Branch(branches[i], st, tagvals, unresolved, ctx, path + "." + i.ToString(CultureInfo.InvariantCulture)));
                }

                if (got.Contains(Contact.True)) return Contact.True;
                if (got.Contains(Contact.Unresolved)) return Contact.Unresolved;
                if (got.Contains(Contact.Unmeasured)) return Contact.Unmeasured;
                return Contact.False;
            }

            if (op == "not")
            {
                Contact c = Branch(e.Get("not"), st, tagvals, unresolved, ctx, path + ".0");
                return c == Contact.True ? Contact.False : c == Contact.False ? Contact.True : c;
            }

            // timers, counter, one-shot: the output the instruction pass computed for this scan
            return ctx != null && ctx.Out.TryGetValue(path, out Contact o) ? o : Contact.Unmeasured;
        }

        /// <summary>Every plain (key, want) condition inside a when, nested instructions opened up, in order (gates.leaves).</summary>
        public static IEnumerable<KeyValuePair<string, object>> Leaves(JsonObject when)
        {
            if (when == null) yield break;
            foreach (var kv in when)
            {
                if (kv.Value is JsonObject e)
                {
                    string op = ExprOp(e);
                    if (op == null) continue;
                    var subs = new List<object>();
                    if (op == "any") subs.AddRange(e.GetList("any") ?? new List<object>());
                    else subs.Add(e.Get(op));
                    if (op == "ctu" && e.Get("reset") is JsonObject reset) subs.Add(reset);
                    foreach (object s in subs)
                    {
                        if (!(s is JsonObject sw)) continue;
                        foreach (var leaf in Leaves(sw)) yield return leaf;
                    }
                }
                else
                {
                    yield return kv;
                }
            }
        }

        private static int? Duration(JsonObject e)
        {
            if (IsNumber(e.Get("ticks"))) return (int)ToDouble(e.Get("ticks"));
            if (IsNumber(e.Get("hours"))) return (int)Math.Round(ToDouble(e.Get("hours")) * TicksPerHour, MidpointRounding.ToEven);
            return null;
        }

        /// <summary>
        /// gates._instructions: every timer / counter / one-shot in a rung moves once per scan, children first, whether
        /// or not an earlier condition of the rung already failed (a timer must see its input every scan).
        /// </summary>
        private static void Instructions(JsonObject when, Dictionary<string, object> st, JsonObject tagvals, ScanContext ctx, string path)
        {
            if (when == null) return;
            foreach (var kv in when)
            {
                if (!(kv.Value is JsonObject w)) continue;
                string p = path + "/" + kv.Key;
                string op = ExprOp(w);
                if (op == null) continue;
                if (op == "any")
                {
                    List<object> branches = w.GetList("any") ?? new List<object>();
                    for (int i = 0; i < branches.Count; i++)
                    {
                        Instructions(branches[i] as JsonObject, st, tagvals, ctx, p + "." + i.ToString(CultureInfo.InvariantCulture));
                    }
                }
                else
                {
                    Instructions(w.Get(op) as JsonObject, st, tagvals, ctx, p + ".0");
                }

                if (op == "ctu" && w.Get("reset") is JsonObject rs) Instructions(rs, st, tagvals, ctx, p + ".r");
                if (Array.IndexOf(Stateful, op) < 0) continue;

                Contact c = Branch(w.Get(op), st, tagvals, null, ctx, p + ".0");
                Instr m = ctx.Memory.TryGetValue(p, out Instr old) ? old.Copy() : new Instr();
                int? now = ctx.Now;
                int? dur = Duration(w);
                bool inp = c == Contact.True;
                bool measured = c == Contact.True || c == Contact.False;
                Contact output;
                switch (op)
                {
                    case "ons":
                        output = measured ? (inp && !m.Prev ? Contact.True : Contact.False) : c;
                        break;
                    case "ton":
                        if (!inp) m.Start = null;
                        else if (m.Start == null) m.Start = now;
                        if (now == null || dur == null) output = Contact.Unmeasured;
                        else if (inp && now.Value - m.Start.Value >= dur.Value) output = Contact.True;
                        else output = measured ? Contact.False : c;
                        break;
                    case "tof":
                        if (inp) m.Last = now;
                        bool held = m.Last != null && now != null && dur != null && now.Value - m.Last.Value < dur.Value;
                        if (now == null || dur == null) output = Contact.Unmeasured;
                        else if (inp || held) output = Contact.True;
                        else output = measured ? Contact.False : c;
                        break;
                    default: // ctu
                        Contact r = w.Get("reset") is JsonObject ? Branch(w.Get("reset"), st, tagvals, null, ctx, p + ".r") : Contact.False;
                        if (r == Contact.True) m.Count = 0;
                        else if (inp && !m.Prev) m.Count++;
                        object pre = w.Get("preset");
                        output = !IsNumber(pre) ? Contact.Unresolved : m.Count >= ToDouble(pre) ? Contact.True : Contact.False;
                        break;
                }

                m.Prev = inp;
                ctx.Memory[p] = m;
                ctx.Out[p] = output;
            }
        }

        /// <summary>gates._holds: an AND, tested in order, stopping at the first failure (as Python does).</summary>
        public static bool Holds(JsonObject when, Dictionary<string, object> st, JsonObject tagvals, List<string> unresolved,
                                 ScanContext ctx = null, string path = "")
        {
            foreach (var kv in when)
            {
                if (Test(kv.Key, kv.Value, st, tagvals, unresolved, ctx, path + "/" + kv.Key) != Contact.True) return false;
            }

            return true;
        }

        private static object ValueOf(string key, object want, Dictionary<string, object> st, JsonObject tagvals)
        {
            if (key == "letter_matches") return want;
            if (st.TryGetValue(key, out object v)) return v;
            if (tagvals.TryGet(key, out object t)) return t;
            return "unmeasured";
        }

        /// <summary>gates.explain: the measured value behind each condition (a nested instruction: those of the conditions inside it).</summary>
        public static JsonObject Explain(JsonObject when, Dictionary<string, object> st, JsonObject tagvals)
        {
            var o = new JsonObject();
            foreach (var kv in when)
            {
                if (kv.Value is JsonObject e)
                {
                    var inner = new JsonObject();
                    foreach (var leaf in Leaves(new JsonObject { new KeyValuePair<string, object>(kv.Key, e) }))
                    {
                        inner.Set(leaf.Key, ValueOf(leaf.Key, leaf.Value, st, tagvals));
                    }

                    o.Set(kv.Key, inner);
                }
                else
                {
                    o.Set(kv.Key, ValueOf(kv.Key, kv.Value, st, tagvals));
                }
            }

            return o;
        }

        /// <summary>gates.apply_fallbacks: a measured sensor that replaced a mark reads that mark while it is unmeasured.</summary>
        public static void ApplyFallbacks(Ladder book, Dictionary<string, object> st)
        {
            foreach (var kv in book.Sensors)
            {
                string fb = (kv.Value as JsonObject)?.GetString("fallback");
                if (fb == null || st.ContainsKey(kv.Key)) continue;
                st[kv.Key] = st.TryGetValue(fb, out object v) ? v : (object)false;
            }
        }

        private static int? Now(Dictionary<string, object> st)
        {
            if (st.TryGetValue("ticks", out object t) && IsNumber(t)) return (int)ToDouble(t);
            if (st.TryGetValue("day", out object d) && IsNumber(d)) return (int)Math.Round(ToDouble(d) * 60000, MidpointRounding.ToEven);
            return null;
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
                                      Func<string, bool> applicable, IDictionary<string, Instr> memory = null)
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
                var ev = new RungEval { Rung = r, When = when, BaseWhen = when, Then = then };
                ev.Applicable = r.Requires.Count == 0 || r.Requires.All(q => applicable == null || applicable(q));
                if (!string.IsNullOrEmpty(r.Disabled)) ev.Off = r.Disabled;
                else if (r.Mode == "off") ev.Off = "mode off";
                else if (switchedOff != null && switchedOff.Contains(r.Id)) ev.Off = "switched off in RimPLC";
                evals.Add(ev);
                foreach (var kv in Leaves(when))
                {
                    if (kv.Key.StartsWith("mark_", StringComparison.Ordinal) && kv.Value is bool && !st.ContainsKey(kv.Key))
                    {
                        st[kv.Key] = false;
                    }
                }
            }

            ApplyFallbacks(book, st);

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
            res.UnknownKeys = scanned.SelectMany(e => Leaves(e.Rung.When).Select(kv => kv.Key))
                .Where(k => k != "letter_matches" && !k.StartsWith("mark_", StringComparison.Ordinal) &&
                            !k.StartsWith("alert_", StringComparison.Ordinal) && !known.Contains(k) &&
                            !tagvals.Has(k) && !st.ContainsKey(k))
                .Distinct().OrderBy(k => k, StringComparer.Ordinal).ToList();

            // the instruction pass: timers, counters and one-shots move once, before any rung is tested
            var ctx = new ScanContext { Now = Now(st) };
            if (memory != null)
            {
                foreach (var kv in memory) ctx.Memory[kv.Key] = kv.Value.Copy();
            }

            foreach (RungEval ev in scanned) Instructions(ev.When, st, tagvals, ctx, ev.Rung.Id);
            foreach (var kv in ctx.Memory)
            {
                if (ctx.Out.ContainsKey(kv.Key)) res.Memory[kv.Key] = kv.Value;
            }

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
                if (scan) ev.Live = Holds(ev.When, st, tagvals, res.Unresolved, ctx, ev.Rung.Id);
                foreach (var kv in ev.When)
                {
                    ev.Contacts.Add(new KeyValuePair<string, Contact>(kv.Key, Test(kv.Key, kv.Value, st, tagvals, null, ctx, ev.Rung.Id + "/" + kv.Key)));
                }

                if (ev.Live)
                {
                    ev.Matched = Explain(ev.BaseWhen ?? ev.When, st, tagvals);
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
