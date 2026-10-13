using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using Verse;

namespace RimPLC
{
    /// <summary>
    /// What a sensor reading means for the player: its label, group, tooltip, and whether the value is a problem. Read
    /// from the book's sensor catalogue (label, group, tip, warn, severity -- written by tools/annotate-sensors.py). Owner,
    /// 2026-10-13: "the other hundred and hundreds of sensores need to wewarn properly and be diplayed well organized and
    /// formated with in game tool tip explinations".
    /// </summary>
    public static class SensorView
    {
        public enum Level { None, Info, Warning, Critical }

        public sealed class Reading
        {
            public string Key;
            public object Value;
            public string Label;
            public string Group;
            public string Tip;
            public string Rule;
            public Level Severity;
            public bool Warning;
        }

        public static readonly string[] GroupOrder =
        {
            "Threats", "Health", "Crew", "Food", "Stores", "Power", "Rooms", "Defence", "Research", "Production",
            "Colony", "World", "Stream", "Game", "Alerts", "Events", "Item counts", "Research done", "Not measured",
        };

        public static List<Reading> All(Dictionary<string, object> state)
        {
            var list = new List<Reading>();
            JsonObject cat = RimPLCMod.Book.Sensors;
            foreach (var kv in state)
            {
                if (kv.Key == "tags") continue;
                list.Add(Describe(kv.Key, kv.Value, cat));
            }

            return list;
        }

        public static Reading Describe(string key, object value, JsonObject cat)
        {
            var r = new Reading { Key = key, Value = value, Severity = Level.Info };
            JsonObject spec = cat?.GetObject(key);
            if (spec != null)
            {
                r.Label = spec.GetString("label") ?? key;
                r.Group = spec.GetString("group") ?? "Colony";
                r.Tip = spec.GetString("tip") ?? spec.GetString("source") ?? string.Empty;
                r.Severity = Sev(spec.GetString("severity"));
                object warn = spec.Get("warn");
                if (warn != null)
                {
                    r.Rule = Json.Write(warn);
                    r.Warning = Trips(warn, value);
                }
            }
            else if (key.StartsWith("alert_", StringComparison.Ordinal))
            {
                r.Group = "Alerts";
                r.Label = Pretty(key.Substring(6));
                r.Tip = "A RimWorld alert is active (any mod's alerts included).";
                r.Severity = Level.Warning;
                r.Warning = value is bool b && b;
                r.Rule = "true";
            }
            else if (key.StartsWith("condition_", StringComparison.Ordinal))
            {
                r.Group = "Events";
                r.Label = Pretty(key.Substring(10));
                r.Tip = "A map or world condition is active (any mod's events included).";
                r.Severity = Level.Warning;
                r.Warning = value is bool b && b;
                r.Rule = "true";
            }
            else if (key.StartsWith("research_", StringComparison.Ordinal))
            {
                r.Group = "Research done";
                r.Label = Pretty(key.Substring(9));
                r.Tip = "Research project finished.";
            }
            else if (key.StartsWith("count_", StringComparison.Ordinal))
            {
                r.Group = "Item counts";
                r.Label = Pretty(key.Substring(6));
                r.Tip = "Things of this kind on the home map (asked for by a rung).";
            }
            else
            {
                r.Group = "Colony";
                r.Label = Pretty(key);
                r.Tip = "Measured by RimPLC.";
            }

            if (!r.Warning) r.Severity = r.Severity == Level.Critical || r.Severity == Level.Warning ? r.Severity : Level.Info;
            return r;
        }

        private static Level Sev(string s)
        {
            switch (s)
            {
                case "critical": return Level.Critical;
                case "warning": return Level.Warning;
                default: return Level.Info;
            }
        }

        /// <summary>true when the value is a problem: rule ">0", "<3", "==0", ">=x", "<=x", "!=x", or a boolean to equal.</summary>
        public static bool Trips(object rule, object value)
        {
            if (value == null) return false;
            if (rule is bool rb) return value is bool vb && vb == rb;
            if (!(rule is string s) || s.Length < 2) return false;
            string op = s.StartsWith(">=") || s.StartsWith("<=") || s.StartsWith("==") || s.StartsWith("!=") ? s.Substring(0, 2) : s.Substring(0, 1);
            if (!double.TryParse(s.Substring(op.Length), NumberStyles.Float, CultureInfo.InvariantCulture, out double want)) return false;
            double got;
            if (value is double d) got = d;
            else if (value is bool b) got = b ? 1 : 0;
            else if (!double.TryParse(Convert.ToString(value, CultureInfo.InvariantCulture), NumberStyles.Float, CultureInfo.InvariantCulture, out got)) return false;
            switch (op)
            {
                case ">": return got > want;
                case "<": return got < want;
                case ">=": return got >= want;
                case "<=": return got <= want;
                case "==": return Math.Abs(got - want) < 1e-9;
                case "!=": return Math.Abs(got - want) >= 1e-9;
                default: return false;
            }
        }

        public static string Format(object v)
        {
            switch (v)
            {
                case null: return "-";
                case bool b: return b ? "yes" : "no";
                case double d: return Math.Abs(d - Math.Round(d)) < 1e-9 ? ((long)Math.Round(d)).ToString(CultureInfo.InvariantCulture) : d.ToString("0.##", CultureInfo.InvariantCulture);
                case string s: return s;
                case System.Collections.IList l:
                    var items = l.Cast<object>().Select(x => Convert.ToString(x, CultureInfo.InvariantCulture)).Where(x => !string.IsNullOrEmpty(x)).ToList();
                    if (items.Count == 0) return "none";
                    string joined = string.Join(", ", items.Take(6).ToArray());
                    return items.Count > 6 ? joined + " (+" + (items.Count - 6) + ")" : joined;
                default: return Json.Write(v);
            }
        }

        public static string Pretty(string k)
        {
            string s = k.Replace("_", " ").Trim();
            return s.Length == 0 ? k : char.ToUpperInvariant(s[0]) + s.Substring(1);
        }

        public static string Tooltip(Reading r)
        {
            string t = r.Label + "\n\n" + r.Tip + "\n\nvalue: " + Format(r.Value);
            if (r.Rule != null) t += "\nwarns when: " + r.Rule + (r.Warning ? "  <-- NOW" : string.Empty);
            t += "\nkey: " + r.Key;
            return t;
        }
    }

    /// <summary>
    /// RimWorld's own alert column carries RimPLC's critical sensors (an unarmed colonist, bleeding, fire, no food...):
    /// the game warns, not just the RimPLC window. Discovered by the game like every Alert subclass.
    /// </summary>
    public sealed class Alert_RimPLC : Alert_Critical
    {
        private List<SensorView.Reading> Critical()
        {
            RimPLCGameComponent plc = RimPLCGameComponent.Get();
            ScanResult r = plc?.Last;
            if (r?.State == null) return new List<SensorView.Reading>();
            return SensorView.All(r.State).Where(x => x.Warning && x.Severity == SensorView.Level.Critical)
                             .OrderBy(x => x.Group, StringComparer.Ordinal).ToList();
        }

        public override string GetLabel()
        {
            List<SensorView.Reading> c = Critical();
            return c.Count == 1 ? "RimPLC: " + c[0].Label : "RimPLC: " + c.Count + " critical";
        }

        public override TaggedString GetExplanation()
        {
            return string.Join("\n\n", Critical().Select(x => x.Label + " = " + SensorView.Format(x.Value) + "\n" + x.Tip).ToArray());
        }

        public override AlertReport GetReport()
        {
            return Critical().Count > 0 ? AlertReport.Active : AlertReport.Inactive;
        }
    }
}
