using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;
using System.Text.RegularExpressions;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimPLC
{
    /// <summary>
    /// The PLC. Owns the per-game ladder state and runs the scan cycle (docs/RIMPLC_DESIGN.md 3.4):
    ///   1. input scan   sensors by cadence class (fast every scan, normal every 4th, slow every 16th)
    ///   2. logic scan   every enabled, applicable rung in priority order (Engine.Scan, the gates.py port)
    ///   3. output scan  on the rising edge of a rung: its notice as a game message (book and player rungs), and for
    ///                   rungs in auto mode the advise-only coils message / set_mark / set_tag. Nothing that changes
    ///                   the game world is executed in this version.
    ///   4. live rung    the first live rung plus always, exactly the gates.decide() contract.
    ///
    /// Owner decision 3, verbatim in the design: advise-only by default, "a auto updating checkl ist of controls and
    /// switchs and replays and contactors". The scan runs every ScanTicks game ticks (250 = one rare tick, settable
    /// 60-2500); while the game is paused it runs once a real second for the window with no output, so nothing acts
    /// while the player has paused. Saved in the save file through ExposeData; the book itself is not saved, only
    /// what the player and Unity changed on top of it.
    /// </summary>
    public sealed class RimPLCGameComponent : GameComponent
    {
        public const int DefaultScanTicks = 250;
        public const double BudgetMs = 3.0;     // measured live 2026-10-12: 1.31 ms per scan with ~300 mods; a scan runs every 250 ticks, so 3 ms is still ~0.01 ms per tick
        private const int LogKeep = 200;

        // ------------------------------------------------------------------ saved
        public int ScanTicks = DefaultScanTicks;
        public bool Notify = true;
        public string PresetId = "LadderV2";
        private Dictionary<string, string> marksSaved = new Dictionary<string, string>();
        private Dictionary<string, string> tagsSaved = new Dictionary<string, string>();
        private Dictionary<string, string> modesSaved = new Dictionary<string, string>();
        private List<string> rungsSaved = new List<string>();
        private List<string> switchedOffSaved = new List<string>();
        private List<string> edgesSaved = new List<string>();
        private List<int> lettersSeenSaved = new List<int>();
        private Dictionary<string, string> memorySaved = new Dictionary<string, string>();

        // ------------------------------------------------------------------ runtime
        public readonly JsonObject Marks = new JsonObject();
        public readonly Dictionary<string, double> TagOverrides = new Dictionary<string, double>();
        public readonly Dictionary<string, string> ModeOverrides = new Dictionary<string, string>();
        public readonly List<Rung> MyRungs = new List<Rung>();
        public readonly HashSet<string> SwitchedOff = new HashSet<string>();
        private HashSet<string> edges = new HashSet<string>();
        public readonly HashSet<int> LettersSeen = new HashSet<int>();
        public readonly List<string> Journal = new List<string>();
        /// <summary>Timer / counter / one-shot memory (moves only on tick scans, saved with the game).</summary>
        public Dictionary<string, Instr> Memory = new Dictionary<string, Instr>();
        /// <summary>Colonists whose setup was once complete (load ids); read by SensorsWorld for pawns_unconfigured.</summary>
        public HashSet<string> ConfiguredPawns = new HashSet<string>();
        private List<string> configuredSaved = new List<string>();
        /// <summary>Prisoners already seen with a stance of their own (load ids); read by SensorsWorld for prisoners_new.</summary>
        public HashSet<string> PrisonersSeen = new HashSet<string>();
        private List<string> prisonersSeenSaved = new List<string>();

        public ScanResult Last;
        public bool OverBudget;
        private int scanCount;
        private Dictionary<string, object> fast, normal, slow, demand;
        private bool skipSlowOnce;
        private float lastRealtimeScan = -10f;
        private float lastRealtimeInbox = -10f;
        private string lastError;

        public RimPLCGameComponent(Game game)
        {
        }

        public static RimPLCGameComponent Get()
        {
            return Current.Game?.GetComponent<RimPLCGameComponent>();
        }

        public static Ladder Book => RimPLCMod.Book;

        // ================================================================== cycle

        public override void GameComponentTick()
        {
            int every = Mathf.Clamp(ScanTicks, 60, 2500);
            if (Find.TickManager.TicksGame % every != 0) return;
            Scan(true);
        }

        public override void GameComponentUpdate()
        {
            if (Current.ProgramState != ProgramState.Playing) return;
            float now = Time.realtimeSinceStartup;
            if (now - lastRealtimeInbox >= 1f)
            {
                lastRealtimeInbox = now;
                Inbox.Process(this);
            }

            // paused: keep the window live once a real second, input + logic only
            if (Find.TickManager != null && Find.TickManager.Paused && now - lastRealtimeScan >= 1f)
            {
                lastRealtimeScan = now;
                Scan(false);
            }
        }

        /// <summary>One scan. output=false is the paused / on-demand scan: it never fires edges or coils.</summary>
        public ScanResult Scan(bool output)
        {
            Ladder book = Book;
            if (book.LoadError != null) return Last;
            var sw = Stopwatch.StartNew();
            try
            {
                Map home = Sensors.HomeMap();
                var f = new Dictionary<string, object>();
                Sensors.ReadFast(f, home, LettersSeen);
                fast = f;
                if (normal == null || scanCount % 4 == 0)
                {
                    var n = new Dictionary<string, object>();
                    Sensors.ReadNormal(n, home, f.TryGetValue("colonists", out object c) ? Engine.ToDouble(c) : 0);
                    SensorsBuild.Read(n, home);   // the rebuilt ladder's inputs (2026-10-13)
                    normal = n;
                }

                if (slow == null || (scanCount % 16 == 0 && !skipSlowOnce))
                {
                    var s = new Dictionary<string, object>();
                    Sensors.ReadSlow(s, home);
                    slow = s;
                }

                skipSlowOnce = false;
                scanCount++;

                // def-named keys the rungs ask for (count_<def>, alert_<class>), read every scan
                var dm = new Dictionary<string, object>();
                Sensors.ReadDemand(dm, home, DemandedKeys(), normal);
                demand = dm;

                ScanResult r = Engine.Scan(book, MyRungs, Merge(), Marks, TagOverrides, EffectiveOff(), RimPLCMod.Applicable, Memory);
                sw.Stop();
                r.Tick = Find.TickManager.TicksGame;
                r.Ms = sw.Elapsed.TotalMilliseconds;
                r.PausedScan = !output;
                // over budget: the logic finished; the slow sensors are skipped on the next due scan
                OverBudget = r.Ms > BudgetMs;
                if (OverBudget) skipSlowOnce = true;
                if (output)
                {
                    // timers, counters and one-shots move on tick scans only; a paused or on-demand scan only looks
                    Memory = r.Memory;
                    Outputs(r);
                }

                Last = r;
                lastError = null;
                return r;
            }
            catch (Exception e)
            {
                string msg = e.GetType().Name + ": " + e.Message;
                if (msg != lastError) Verse.Log.Warning("[RimPLC] scan failed: " + e);
                lastError = msg;
                return Last;
            }
        }

        /// <summary>The input image: slow, then normal, then fast on top; alert_* flags combine by OR (direct health reads and alert classes).</summary>
        /// <summary>Host inputs (remote I/O): readings only the stream PC has -- chat unanswered, seconds since she spoke,
        /// voice playing, owner at the controls. Pushed by the autopilot with rimplc/set_host every turn, merged first so a
        /// game reading of the same name wins, and dropped when older than HostMaxAgeSeconds (her player stopped).</summary>
        public Dictionary<string, object> Host = new Dictionary<string, object>();
        public DateTime HostAt = DateTime.MinValue;
        public const double HostMaxAgeSeconds = 120;

        private Dictionary<string, object> Merge()
        {
            var st = new Dictionary<string, object>();
            if ((DateTime.UtcNow - HostAt).TotalSeconds <= HostMaxAgeSeconds)
            {
                foreach (var kv in Host) st[kv.Key] = kv.Value;
            }

            foreach (var src in new[] { slow, normal, fast, demand })
            {
                if (src == null) continue;
                foreach (var kv in src)
                {
                    if (kv.Key.StartsWith("alert_", StringComparison.Ordinal) && st.TryGetValue(kv.Key, out object prev) &&
                        prev is bool pb && pb)
                    {
                        continue;
                    }

                    st[kv.Key] = kv.Value;
                }
            }

            return st;
        }

        private HashSet<string> DemandedKeys()
        {
            var keys = new HashSet<string>();
            foreach (Rung r in Engine.Merge(Book, MyRungs))
            {
                foreach (var kv in Engine.Leaves(r.When))
                {
                    if (kv.Key.StartsWith("count_", StringComparison.Ordinal) || kv.Key.StartsWith("alert_", StringComparison.Ordinal)) keys.Add(kv.Key);
                }
            }

            return keys;
        }

        public string ModeOf(Rung r)
        {
            return ModeOverrides.TryGetValue(r.Id, out string m) ? m : r.Mode;
        }

        private HashSet<string> EffectiveOff()
        {
            var off = new HashSet<string>(SwitchedOff);
            foreach (var kv in ModeOverrides)
            {
                if (kv.Value == "off") off.Add(kv.Key);
            }

            return off;
        }

        /// <summary>Rising edges only (OTE): a rung that stays true does nothing more; edge memory is saved, so a load does not re-fire.</summary>
        private void Outputs(ScanResult r)
        {
            var now = new HashSet<string>(r.Hits.Select(h => h.Rung.Id));
            foreach (RungEval h in r.Hits)
            {
                if (edges.Contains(h.Rung.Id)) continue;
                Rung rung = h.Rung;
                // the stream is clean: a notice from Unity's own rungs is shown only through the clean-word filter
                string notice = rung.Source == "unity" ? CleanText.Clean(rung.Notice) : rung.Notice;
                if (Notify && !string.IsNullOrEmpty(notice))
                {
                    Messages.Message("RimPLC: " + notice, MessageTypeDefOf.NeutralEvent, false);
                }
                else if (Notify && rung.Source == "unity" && !string.IsNullOrEmpty(rung.Notice))
                {
                    AddLog(r.Tick, rung.Id, "notice not shown: not clean for the stream", "scan");
                }

                AddLog(r.Tick, rung.Id, "rising edge" + (rung.Notice != null ? ": " + rung.Notice : string.Empty), "scan");
                if (ModeOf(rung) == "auto")
                {
                    foreach (JsonObject coil in rung.Coils) AddLog(r.Tick, rung.Id, RunCoil(coil, rung), "scan");
                }
            }

            edges = now;
        }

        /// <summary>The advise-only coils. Anything else is refused and logged (P3 adds the game actions).</summary>
        private string RunCoil(JsonObject coil, Rung rung)
        {
            string act = coil.GetString("do") ?? string.Empty;
            string type = coil.GetString("type") ?? "OTE";
            switch (act)
            {
                case "message":
                    string text = coil.GetString("text");
                    if (string.IsNullOrEmpty(text)) return "refused: message has no text";
                    if (rung.Source == "unity") text = CleanText.Clean(text);
                    if (text == null) return "refused: message is not clean for the stream";
                    Messages.Message("RimPLC: " + text, MessageTypeDefOf.NeutralEvent, false);
                    return "ok: message";
                case "set_mark":
                    object v = type == "OTL" ? (object)true : type == "OTU" ? (object)false : coil.Get("value");
                    return SetMark(coil.GetString("name"), v, out _) ? "ok: mark " + coil.GetString("name") : "refused: bad mark";
                case "set_tag":
                    return SetTag(coil.GetString("name"), coil.Get("value"), false, out string note) ? "ok: tag " + coil.GetString("name") + note : "refused: " + note;
                default:
                    return "refused: " + act + " is not an advise-only coil (game actions arrive in P3)";
            }
        }

        public void AddLog(int tick, string rung, string what, string who)
        {
            Journal.Add(tick.ToString(CultureInfo.InvariantCulture) + "  " + rung + "  " + what + "  (" + who + ")");
            if (Journal.Count > LogKeep) Journal.RemoveRange(0, Journal.Count - LogKeep);
        }

        // ================================================================== edits (UI, AI API, file inbox)

        private static readonly Regex MarkName = new Regex("^[a-z0-9_]{1,40}$");
        private static readonly Regex TagName = new Regex("^[A-Z0-9_]{1,40}$");

        /// <summary>ladder_set mark rules: numbers stay numbers ("3" -> 3); true/yes/done/on -> true; else false; null clears.</summary>
        public bool SetMark(string name, object value, out string error)
        {
            error = null;
            if (name == null || !MarkName.IsMatch(name)) { error = "mark name: lowercase_with_underscores, at most 40"; return false; }
            if (value == null) { Marks.RemoveKey(name); return true; }
            object v;
            if (value is bool b) v = b;
            else if (Engine.IsNumber(value)) v = Engine.ToDouble(value);
            else
            {
                string s = Convert.ToString(value, CultureInfo.InvariantCulture).Trim().ToLowerInvariant();
                if (Regex.IsMatch(s, "^-?\\d+$") || Regex.IsMatch(s, "^-?\\d+\\.\\d+$")) v = double.Parse(s, CultureInfo.InvariantCulture);
                else v = s == "true" || s == "yes" || s == "done" || s == "on";
            }

            Marks.Set(name, v);
            return true;
        }

        /// <summary>ladder_set tag rules: variables only (constants need the owner), a number, clamped when read.</summary>
        public bool SetTag(string name, object value, bool owner, out string note)
        {
            note = string.Empty;
            if (name == null || !TagName.IsMatch(name)) { note = "tag name: UPPER_CASE"; return false; }
            bool constant = Book.Constants.Has(name);
            var spec = Book.Variables.GetObject(name);
            if (constant && !owner) { note = name + " is a constant: a safety limit only the owner changes"; return false; }
            if (!constant && spec == null) { note = name + " is not a variable on the ladder"; return false; }
            if (value == null) { TagOverrides.Remove(name); note = " (override cleared)"; return true; }
            double d;
            if (Engine.IsNumber(value)) d = Engine.ToDouble(value);
            else if (!double.TryParse(Convert.ToString(value, CultureInfo.InvariantCulture), NumberStyles.Float, CultureInfo.InvariantCulture, out d))
            {
                note = "tag value must be a number";
                return false;
            }

            if (spec != null && ((spec.Get("min") is double lo && d < lo) || (spec.Get("max") is double hi && d > hi)))
            {
                note = " (clamped to " + Json.Write(spec.Get("min")) + ".." + Json.Write(spec.Get("max")) + " when read)";
            }

            TagOverrides[name] = d;
            return true;
        }

        /// <summary>
        /// t_ladder_set add_rung rules: id forced to the unity- prefix (player- for the editor), then capped at 8 lines of
        /// 300 characters, latch kept, mode forced to advise for unity rungs. A rung with a book rung's id replaces it:
        /// the editor keeps a book id for a player copy ("Edit" on a book rung); the AI API always prefixes. Then the
        /// rimplc-check rules (Validate.Rung). For the AI API a key with no sensor is a note, not a refusal, exactly
        /// as ladder_set says it; the editor (unknownIsError) refuses it, as the checker does.
        /// </summary>
        public bool UpsertRung(JsonObject o, string source, out string note, bool unknownIsError = false)
        {
            note = string.Empty;
            if (o == null || !(o.Get("id") is string rawId) || rawId.Length == 0 || !(o.Get("priority") is double) || !(o.Get("when") is JsonObject))
            {
                note = "rung needs id, priority (number), when (object), then (list)";
                return false;
            }

            string prefix = source + "-";
            bool keepBookId = source == "player" && Book.Rungs.Any(b => b.Id == rawId);
            string id = keepBookId ? rawId
                : rawId.StartsWith(prefix, StringComparison.Ordinal)
                    ? (rawId.Length > 46 ? rawId.Substring(0, 46) : rawId)
                    : prefix + Clip(Regex.Replace(rawId.ToLowerInvariant(), "[^a-z0-9-]", "-"), 40);
            id = Regex.Replace(id, "[^a-z0-9-]", "-");
            var copy = o.Copy();
            copy.Set("id", id);
            var then = Rung.Strings(o.GetList("then")).Take(8).Select(s => Clip(s, 300)).Cast<object>().ToList();
            copy.Set("then", then);
            if (copy.Has("latch")) copy.Set("latch", Engine.Truthy(copy.Get("latch")));
            copy.Set("source", source);
            if (source == "unity") copy.Set("mode", "advise");
            copy.RemoveKey("disabled");

            var live = Last == null ? null : new HashSet<string>(Last.State.Keys);
            List<string> errors = Validate.Rung(copy, Book, live, out List<string> _);
            const string noSensor = " has no sensor, tag or mark";
            if (!unknownIsError) errors.RemoveAll(e => e.EndsWith(noSensor, StringComparison.Ordinal));
            if (errors.Count > 0)
            {
                note = string.Join("; ", errors.Take(3).ToArray());
                return false;
            }

            Rung r;
            try { r = Rung.From(copy, source); }
            catch (FormatException e) { note = e.Message; return false; }

            var unknown = Engine.Leaves(r.When).Select(kv => kv.Key).Where(k => !Validate.KnownKey(k, Book, live) ||
                                                                               (k.StartsWith("count_", StringComparison.Ordinal) && (live == null || !live.Contains(k))))
                .Where(k => !k.StartsWith("mark_", StringComparison.Ordinal) && !k.StartsWith("alert_", StringComparison.Ordinal)).Distinct().ToList();
            if (unknown.Count > 0) note = " (keys with no sensor, the rung stays quiet until measured: " + string.Join(", ", unknown) + ")";
            MyRungs.RemoveAll(x => x.Id == r.Id);
            MyRungs.Add(r);
            note = r.Id + note;
            return true;
        }

        /// <summary>Remove a unity- or player- rung (the AI API), or any rung of the player's layer, including a player copy of a book rung (the window's Revert).</summary>
        public bool RemoveRung(string id, out string note, bool byPlayer = false)
        {
            note = id;
            bool layered = id != null && MyRungs.Any(x => x.Id == id);
            if (id == null || !(id.StartsWith("unity-", StringComparison.Ordinal) || id.StartsWith("player-", StringComparison.Ordinal) || (byPlayer && layered)))
            {
                note = "only unity- and player- rungs can be removed; book rungs can only be switched off";
                return false;
            }

            if (MyRungs.RemoveAll(x => x.Id == id) == 0) { note = "no rung " + id; return false; }
            return true;
        }

        /// <summary>Switch a rung on or off. Switching a book rung off through the AI API needs the owner flag; the player may always.</summary>
        public bool EnableRung(string id, bool enabled, bool ownerOrPlayer, out string note)
        {
            note = id;
            bool exists = Book.Rungs.Any(r => r.Id == id) || MyRungs.Any(r => r.Id == id);
            if (!exists) { note = "no rung " + id; return false; }
            bool isBook = !MyRungs.Any(r => r.Id == id);
            if (!enabled && isBook && !ownerOrPlayer) { note = "owner only: disabling a book rung"; return false; }
            if (enabled) SwitchedOff.Remove(id);
            else SwitchedOff.Add(id);
            return true;
        }

        /// <summary>A dry run of an edit on this component: the edit is made, read back and undone (import planning).</summary>
        public sealed class Probe
        {
            private readonly RimPLCGameComponent plc;
            public Rung Result;

            public Probe(RimPLCGameComponent plc)
            {
                this.plc = plc;
            }

            public bool Upsert(JsonObject o, string source, out string id, out string note)
            {
                var saved = plc.MyRungs.ToList();
                bool ok = plc.UpsertRung(o, source, out note);
                id = null;
                if (ok)
                {
                    id = note.Split(' ')[0];
                    string found = id;
                    Result = plc.MyRungs.FirstOrDefault(r => r.Id == found);
                }

                plc.MyRungs.Clear();
                plc.MyRungs.AddRange(saved);
                return ok && Result != null;
            }

            public bool Mark(string name, object value, out string error)
            {
                JsonObject had = plc.Marks.Copy();
                bool ok = plc.SetMark(name, value, out error);
                plc.Marks.Clear();
                plc.Marks.AddRange(had);
                return ok;
            }
        }

        public void SetMode(string id, string mode)
        {
            if (mode == "advise" || mode == "auto" || mode == "off") ModeOverrides[id] = mode;
        }

        public void MarkLettersSeen()
        {
            List<Letter> letters = Find.LetterStack?.LettersListForReading;
            if (letters == null) return;
            foreach (Letter l in letters) LettersSeen.Add(l.ID);
        }

        private static string Clip(string s, int n)
        {
            return s == null ? string.Empty : s.Length > n ? s.Substring(0, n) : s;
        }

        // ================================================================== save

        public override void ExposeData()
        {
            if (Scribe.mode == LoadSaveMode.Saving) Pack();
            Scribe_Values.Look(ref ScanTicks, "scanTicks", DefaultScanTicks);
            Scribe_Values.Look(ref Notify, "notify", true);
            Scribe_Values.Look(ref PresetId, "presetId", "LadderV2");
            Scribe_Collections.Look(ref marksSaved, "marks", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref tagsSaved, "tagOverrides", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref modesSaved, "modes", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref rungsSaved, "rungs", LookMode.Value);
            Scribe_Collections.Look(ref switchedOffSaved, "switchedOff", LookMode.Value);
            Scribe_Collections.Look(ref edgesSaved, "edges", LookMode.Value);
            Scribe_Collections.Look(ref lettersSeenSaved, "lettersSeen", LookMode.Value);
            Scribe_Collections.Look(ref memorySaved, "instructionMemory", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.Saving) configuredSaved = ConfiguredPawns.ToList();
            Scribe_Collections.Look(ref configuredSaved, "configuredPawns", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit) ConfiguredPawns = new HashSet<string>(configuredSaved ?? new List<string>());
            if (Scribe.mode == LoadSaveMode.Saving) prisonersSeenSaved = PrisonersSeen.ToList();
            Scribe_Collections.Look(ref prisonersSeenSaved, "prisonersSeen", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit) PrisonersSeen = new HashSet<string>(prisonersSeenSaved ?? new List<string>());
            if (Scribe.mode == LoadSaveMode.PostLoadInit) Unpack();
        }

        private void Pack()
        {
            marksSaved = new Dictionary<string, string>();
            foreach (var kv in Marks)
            {
                marksSaved[kv.Key] = kv.Value is bool b ? (b ? "b:1" : "b:0") : "n:" + Engine.ToDouble(kv.Value).ToString("R", CultureInfo.InvariantCulture);
            }

            tagsSaved = TagOverrides.ToDictionary(kv => kv.Key, kv => kv.Value.ToString("R", CultureInfo.InvariantCulture));
            modesSaved = new Dictionary<string, string>(ModeOverrides);
            rungsSaved = MyRungs.Select(r => Json.Write(r.ToJson())).ToList();
            switchedOffSaved = SwitchedOff.ToList();
            edgesSaved = edges.ToList();
            lettersSeenSaved = LettersSeen.ToList();
            memorySaved = Memory.ToDictionary(kv => kv.Key, kv => kv.Value.Pack());
        }

        private void Unpack()
        {
            Marks.Clear();
            foreach (var kv in marksSaved ?? new Dictionary<string, string>())
            {
                string v = kv.Value ?? string.Empty;
                if (v.StartsWith("b:", StringComparison.Ordinal)) Marks.Set(kv.Key, v == "b:1");
                else if (v.StartsWith("n:", StringComparison.Ordinal) &&
                         double.TryParse(v.Substring(2), NumberStyles.Float, CultureInfo.InvariantCulture, out double d)) Marks.Set(kv.Key, d);
            }

            TagOverrides.Clear();
            foreach (var kv in tagsSaved ?? new Dictionary<string, string>())
            {
                if (double.TryParse(kv.Value, NumberStyles.Float, CultureInfo.InvariantCulture, out double d)) TagOverrides[kv.Key] = d;
            }

            ModeOverrides.Clear();
            foreach (var kv in modesSaved ?? new Dictionary<string, string>()) ModeOverrides[kv.Key] = kv.Value;
            MyRungs.Clear();
            foreach (string s in rungsSaved ?? new List<string>())
            {
                try
                {
                    JsonObject o = Json.ParseObject(s);
                    MyRungs.Add(Rung.From(o, o.GetString("source") ?? "player"));
                }
                catch (FormatException e)
                {
                    Verse.Log.Warning("[RimPLC] a saved rung did not load and was dropped: " + e.Message);
                }
            }

            SwitchedOff.Clear();
            foreach (string s in switchedOffSaved ?? new List<string>()) SwitchedOff.Add(s);
            edges = new HashSet<string>(edgesSaved ?? new List<string>());
            LettersSeen.Clear();
            foreach (int i in lettersSeenSaved ?? new List<int>()) LettersSeen.Add(i);
            Memory = new Dictionary<string, Instr>();
            foreach (var kv in memorySaved ?? new Dictionary<string, string>())
            {
                Instr m = Instr.Unpack(kv.Value);
                if (m != null) Memory[kv.Key] = m;
            }
        }
    }
}
