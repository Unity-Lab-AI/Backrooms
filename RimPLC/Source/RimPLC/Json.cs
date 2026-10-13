using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace RimPLC
{
    /// <summary>
    /// A JSON object that keeps its key order. The ladder's meaning depends on order in two places (tag variables are
    /// computed in file order, and a rung's conditions are tested in file order), so a plain Dictionary is not enough.
    /// </summary>
    public sealed class JsonObject : List<KeyValuePair<string, object>>
    {
        public bool Has(string key)
        {
            return IndexOf(key) >= 0;
        }

        public int IndexOf(string key)
        {
            for (int i = 0; i < Count; i++)
            {
                if (this[i].Key == key) return i;
            }

            return -1;
        }

        public object Get(string key)
        {
            int i = IndexOf(key);
            return i >= 0 ? this[i].Value : null;
        }

        public bool TryGet(string key, out object value)
        {
            int i = IndexOf(key);
            value = i >= 0 ? this[i].Value : null;
            return i >= 0;
        }

        /// <summary>Replaces the value in place (order kept) or appends a new key at the end.</summary>
        public void Set(string key, object value)
        {
            int i = IndexOf(key);
            if (i >= 0) this[i] = new KeyValuePair<string, object>(key, value);
            else Add(new KeyValuePair<string, object>(key, value));
        }

        /// <summary>Python's dict.setdefault: only adds when the key is absent.</summary>
        public void SetDefault(string key, object value)
        {
            if (!Has(key)) Add(new KeyValuePair<string, object>(key, value));
        }

        public bool RemoveKey(string key)
        {
            int i = IndexOf(key);
            if (i < 0) return false;
            RemoveAt(i);
            return true;
        }

        public JsonObject Copy()
        {
            var o = new JsonObject();
            o.AddRange(this);
            return o;
        }

        public string GetString(string key)
        {
            return Get(key) as string;
        }

        public JsonObject GetObject(string key)
        {
            return Get(key) as JsonObject;
        }

        public List<object> GetList(string key)
        {
            return Get(key) as List<object>;
        }
    }

    /// <summary>
    /// Small strict JSON reader/writer. RimWorld's Core ships no JSON library and RimPLC takes no dependencies, so this
    /// is hand-written (docs/RIMPLC_DESIGN.md section 7). Numbers are doubles; objects keep key order; any syntax error
    /// throws FormatException with the offset, and callers refuse the whole input (never a partial apply).
    /// </summary>
    public static class Json
    {
        public static object Parse(string text)
        {
            if (text == null) throw new FormatException("json: null input");
            int i = 0;
            object v = ReadValue(text, ref i, 0);
            SkipWs(text, ref i);
            if (i != text.Length) throw new FormatException("json: trailing text at " + i);
            return v;
        }

        public static JsonObject ParseObject(string text)
        {
            var o = Parse(text) as JsonObject;
            if (o == null) throw new FormatException("json: expected an object");
            return o;
        }

        private static void SkipWs(string s, ref int i)
        {
            while (i < s.Length && (s[i] == ' ' || s[i] == '\t' || s[i] == '\n' || s[i] == '\r' || s[i] == '\uFEFF')) i++;
        }

        private static object ReadValue(string s, ref int i, int depth)
        {
            if (depth > 64) throw new FormatException("json: nested too deep at " + i);
            SkipWs(s, ref i);
            if (i >= s.Length) throw new FormatException("json: unexpected end");
            char c = s[i];
            if (c == '{') return ReadObject(s, ref i, depth);
            if (c == '[') return ReadArray(s, ref i, depth);
            if (c == '"') return ReadString(s, ref i);
            if (c == 't' && Lit(s, ref i, "true")) return true;
            if (c == 'f' && Lit(s, ref i, "false")) return false;
            if (c == 'n' && Lit(s, ref i, "null")) return null;
            if (c == '-' || (c >= '0' && c <= '9')) return ReadNumber(s, ref i);
            throw new FormatException("json: unexpected '" + c + "' at " + i);
        }

        private static bool Lit(string s, ref int i, string word)
        {
            if (string.CompareOrdinal(s, i, word, 0, word.Length) != 0) throw new FormatException("json: bad literal at " + i);
            i += word.Length;
            return true;
        }

        private static JsonObject ReadObject(string s, ref int i, int depth)
        {
            var o = new JsonObject();
            i++;
            SkipWs(s, ref i);
            if (i < s.Length && s[i] == '}') { i++; return o; }
            while (true)
            {
                SkipWs(s, ref i);
                if (i >= s.Length || s[i] != '"') throw new FormatException("json: expected a key at " + i);
                string key = ReadString(s, ref i);
                SkipWs(s, ref i);
                if (i >= s.Length || s[i] != ':') throw new FormatException("json: expected ':' at " + i);
                i++;
                o.Set(key, ReadValue(s, ref i, depth + 1));
                SkipWs(s, ref i);
                if (i >= s.Length) throw new FormatException("json: unexpected end in object");
                if (s[i] == ',') { i++; continue; }
                if (s[i] == '}') { i++; return o; }
                throw new FormatException("json: expected ',' or '}' at " + i);
            }
        }

        private static List<object> ReadArray(string s, ref int i, int depth)
        {
            var a = new List<object>();
            i++;
            SkipWs(s, ref i);
            if (i < s.Length && s[i] == ']') { i++; return a; }
            while (true)
            {
                a.Add(ReadValue(s, ref i, depth + 1));
                SkipWs(s, ref i);
                if (i >= s.Length) throw new FormatException("json: unexpected end in array");
                if (s[i] == ',') { i++; continue; }
                if (s[i] == ']') { i++; return a; }
                throw new FormatException("json: expected ',' or ']' at " + i);
            }
        }

        private static string ReadString(string s, ref int i)
        {
            var sb = new StringBuilder();
            i++;
            while (i < s.Length)
            {
                char c = s[i++];
                if (c == '"') return sb.ToString();
                if (c != '\\') { sb.Append(c); continue; }
                if (i >= s.Length) break;
                char e = s[i++];
                switch (e)
                {
                    case '"': sb.Append('"'); break;
                    case '\\': sb.Append('\\'); break;
                    case '/': sb.Append('/'); break;
                    case 'b': sb.Append('\b'); break;
                    case 'f': sb.Append('\f'); break;
                    case 'n': sb.Append('\n'); break;
                    case 'r': sb.Append('\r'); break;
                    case 't': sb.Append('\t'); break;
                    case 'u':
                        if (i + 4 > s.Length ||
                            !int.TryParse(s.Substring(i, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture, out int code))
                        {
                            throw new FormatException("json: bad \\u escape at " + i);
                        }

                        sb.Append((char)code);
                        i += 4;
                        break;
                    default: throw new FormatException("json: bad escape at " + i);
                }
            }

            throw new FormatException("json: unterminated string");
        }

        private static double ReadNumber(string s, ref int i)
        {
            int start = i;
            if (s[i] == '-') i++;
            while (i < s.Length && ((s[i] >= '0' && s[i] <= '9') || s[i] == '.' || s[i] == 'e' || s[i] == 'E' || s[i] == '+' || s[i] == '-')) i++;
            string t = s.Substring(start, i - start);
            if (!double.TryParse(t, NumberStyles.Float, CultureInfo.InvariantCulture, out double d))
            {
                throw new FormatException("json: bad number '" + t + "' at " + start);
            }

            return d;
        }

        // ------------------------------------------------------------------------------------------------ writing

        public static string Write(object value, bool pretty = false)
        {
            var sb = new StringBuilder();
            WriteValue(sb, value, pretty, 0);
            return sb.ToString();
        }

        public static string Num(double d)
        {
            if (double.IsNaN(d) || double.IsInfinity(d)) return "null";
            if (Math.Abs(d) < 1e15 && d == Math.Floor(d)) return ((long)d).ToString(CultureInfo.InvariantCulture);
            return d.ToString("R", CultureInfo.InvariantCulture);
        }

        private static void Indent(StringBuilder sb, bool pretty, int depth)
        {
            if (!pretty) return;
            sb.Append('\n');
            sb.Append(' ', depth);
        }

        private static void WriteValue(StringBuilder sb, object v, bool pretty, int depth)
        {
            switch (v)
            {
                case null: sb.Append("null"); return;
                case bool b: sb.Append(b ? "true" : "false"); return;
                case string str: WriteString(sb, str); return;
                case double d: sb.Append(Num(d)); return;
                case float f: sb.Append(Num(f)); return;
                case int n: sb.Append(n.ToString(CultureInfo.InvariantCulture)); return;
                case long l: sb.Append(l.ToString(CultureInfo.InvariantCulture)); return;
                case JsonObject o:
                    WritePairs(sb, o, pretty, depth);
                    return;
                case IDictionary<string, object> dict:
                    WritePairs(sb, dict, pretty, depth);
                    return;
                case IEnumerable seq:
                    sb.Append('[');
                    bool first = true;
                    foreach (object item in seq)
                    {
                        if (!first) sb.Append(',');
                        first = false;
                        Indent(sb, pretty, depth + 1);
                        WriteValue(sb, item, pretty, depth + 1);
                    }

                    if (!first) Indent(sb, pretty, depth);
                    sb.Append(']');
                    return;
                default:
                    WriteString(sb, Convert.ToString(v, CultureInfo.InvariantCulture));
                    return;
            }
        }

        private static void WritePairs(StringBuilder sb, IEnumerable<KeyValuePair<string, object>> pairs, bool pretty, int depth)
        {
            sb.Append('{');
            bool first = true;
            foreach (var kv in pairs)
            {
                if (!first) sb.Append(',');
                first = false;
                Indent(sb, pretty, depth + 1);
                WriteString(sb, kv.Key);
                sb.Append(pretty ? ": " : ":");
                WriteValue(sb, kv.Value, pretty, depth + 1);
            }

            if (!first) Indent(sb, pretty, depth);
            sb.Append('}');
        }

        private static void WriteString(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                        else sb.Append(c);
                        break;
                }
            }

            sb.Append('"');
        }
    }
}
