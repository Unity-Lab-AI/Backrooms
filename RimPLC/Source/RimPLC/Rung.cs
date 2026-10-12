using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.RegularExpressions;

namespace RimPLC
{
    /// <summary>
    /// One rung, read from the frozen shape in docs/rimplc/schema/rung.schema.json. The original JSON object is kept
    /// (<see cref="Raw"/>) so a rung round-trips through save, export and the AI API with every field it came with.
    /// </summary>
    public sealed class Rung
    {
        public string Id;
        public double Priority;
        public JsonObject When = new JsonObject();
        public List<string> Then = new List<string>();
        public List<string> Never = new List<string>();
        public string Why;
        public string Family;
        public string Chain;
        public string Check;
        public string Notice;
        public string Disabled;
        public bool Latch;
        public string Mode = "advise";
        public string Source = "book";
        public List<string> Requires = new List<string>();
        public List<JsonObject> Coils = new List<JsonObject>();
        public JsonObject Raw;

        public static readonly Regex IdRule = new Regex("^[a-z0-9][a-z0-9-]{0,63}$");

        public static Rung From(JsonObject o, string defaultSource)
        {
            if (o == null) throw new FormatException("rung is not an object");
            var r = new Rung { Raw = o.Copy() };
            r.Id = o.GetString("id");
            if (string.IsNullOrEmpty(r.Id)) throw new FormatException("rung has no id");
            if (!(o.Get("priority") is double p)) throw new FormatException(r.Id + ": priority is not a number");
            r.Priority = p;
            var when = o.Get("when");
            if (when != null && !(when is JsonObject)) throw new FormatException(r.Id + ": when is not an object");
            r.When = ((JsonObject)when)?.Copy() ?? new JsonObject();
            r.Then = Strings(o.GetList("then"));
            r.Never = Strings(o.GetList("never"));
            r.Why = o.GetString("why");
            r.Family = o.GetString("family");
            r.Chain = o.GetString("chain");
            r.Check = o.GetString("check");
            r.Notice = o.GetString("notice");
            r.Disabled = o.GetString("disabled");
            r.Latch = o.Get("latch") is bool l && l;
            r.Mode = o.GetString("mode") ?? "advise";
            if (r.Mode != "advise" && r.Mode != "auto" && r.Mode != "off") r.Mode = "advise";
            r.Source = o.GetString("source") ?? defaultSource;
            r.Requires = Strings(o.GetList("requires"));
            r.Coils = (o.GetList("coils") ?? new List<object>()).OfType<JsonObject>().ToList();
            return r;
        }

        public static List<string> Strings(List<object> list)
        {
            return list == null ? new List<string>() : list.Select(x => x as string ?? Convert.ToString(x, CultureInfo.InvariantCulture)).ToList();
        }

        /// <summary>The rung as JSON, with the fields RimPLC may have changed written back over the original.</summary>
        public JsonObject ToJson()
        {
            JsonObject o = Raw?.Copy() ?? new JsonObject();
            o.Set("id", Id);
            o.Set("priority", Priority);
            o.Set("when", When);
            o.Set("then", Then.Cast<object>().ToList());
            o.Set("mode", Mode);
            o.Set("source", Source);
            if (Latch) o.Set("latch", true);
            return o;
        }

        /// <summary>gates.latch_name: lowercase, underscores, at most 35 characters, then _done.</summary>
        public static string LatchName(string id)
        {
            string s = Regex.Replace((id ?? string.Empty).ToLowerInvariant(), "[^a-z0-9]+", "_").Trim('_');
            if (s.Length > 35) s = s.Substring(0, 35);
            return s + "_done";
        }

        /// <summary>gates._latched: a latched rung gets mark_&lt;id&gt;_done false in when and the set step in then.</summary>
        public void Latched(out JsonObject when, out List<string> then)
        {
            when = When;
            then = Then;
            if (!Latch) return;
            string name = LatchName(Id);
            when = When.Copy();
            when.SetDefault("mark_" + name, false);
            string step = "ladder_set mark " + name + " true";
            then = new List<string>(Then);
            if (!then.Any(s => s.Contains(step))) then.Add(step);
        }
    }
}
