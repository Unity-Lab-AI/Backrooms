using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace RimPLC
{
    /// <summary>
    /// The stream is clean: a port of the clean-word filter the stream speech uses (.local/autopilot/guards.py
    /// clean_for_stream, whose SOFTEN and CLEAN_BLOCK rules come from .claude/tools/unity-voice.py, plus guards'
    /// EXTRA_BLOCK and TECH_BLOCK). Text from Unity's rungs (notices and message coils) shows in the game, and the game
    /// is on stream, so it passes here first: mild words are softened, and a line that still has a blocked word is not
    /// shown at all (Clean returns null). The owner-only secret words list is not part of the mod and is not ported.
    /// Keep the patterns in step with the Python originals.
    /// </summary>
    public static class CleanText
    {
        private const RegexOptions I = RegexOptions.IgnoreCase | RegexOptions.CultureInvariant;
        public const int MaxLength = 320;

        private static readonly KeyValuePair<Regex, string>[] Soften =
        {
            P(@"\bmother ?f+u+c+k\w*", "mother-hugger"), P(@"\bf+u+c+k+i+n+g?\b", "freaking"),
            P(@"\bf+u+c+k+e+d\b", "wrecked"), P(@"\bf+u+c+k+\w*", "frick"), P(@"\bgod ?damn\w*", "gosh-dang"),
            P(@"\bdamn\w*", "dang"), P(@"\bsh+i+t+t+y\b", "crummy"), P(@"\bbullsh+i+t\b", "nonsense"),
            P(@"\bsh+i+t+\w*", "stuff"), P(@"\bhell\b", "heck"), P(@"\bass+hole\w*", "jerk"), P(@"\bass\b", "butt"),
            P(@"\bbitch\w*", "witch"), P(@"\bpiss(ed)?\b", "ticked"), P(@"\bcrap\w*", "junk"),
            P(@"\bfriggin'?", "freaking"), P(@"\bwtf\b", "what the heck"), P(@"\btf\b", "the heck"),
            P(@"f+u+c+k+", "mess"), P(@"sh+i+t+", "stuff"),
        };

        private static readonly Regex CleanBlock = new Regex(
            @"(f+u+c+k|sh+i+t|c+u+n+t|n+i+g+g|\b(?:bitch\w*|damn\w*|hell|ass|asses|asshole\w*|crap\w*|piss\w*|" +
            @"dick\w*|cock\w*|pussy|tits?|boobs?|sex\w*|sexy|horny|cum\w*|whore\w*|slut\w*|bastard\w*|" +
            @"retard\w*|fag\w*|weed|joint|blunt|stoned|high af|bong|cocaine|meth|" +
            @"wtf|tf|stfu|af|losers?|idiots?|morons?)\b)", I);

        private static readonly Regex ExtraBlock = new Regex(
            @"(\bkill yourself\b|\bkys\b|\bshut up\b|\bstupid\b|\bdumb\b|\bugly\b|\btrash\b(?= (?:viewer|chat|person|people)))", I);

        private static readonly Regex TechBlock = new Regex(
            @"\b(bridge|server|servers|connection|connections|socket|port|api|script|scripts|" +
            @"python|ollama|model|tokens?|prompt|mod loader|load(?:ing)? the (?:backrooms )?mod|" +
            @"rimbridge|automation|autopilot|crash(?:ed|ing)?|bug(?:gy|s)?|error|exception|code)\b", I);

        private static KeyValuePair<Regex, string> P(string pattern, string replacement)
        {
            return new KeyValuePair<Regex, string>(new Regex(pattern, I), replacement);
        }

        /// <summary>The stream-safe form of text, or null when it cannot be made clean (then it is not shown).</summary>
        public static string Clean(string text)
        {
            if (text == null) return null;
            string t = text;
            t = Regex.Replace(t, @"\*[^*]{0,120}\*|\[[^\]]{0,200}\]|<[^>]{0,120}>", " ");                    // stage directions, tags
            t = Regex.Replace(t, @"https?://\S+|www\.\S+", " ");                                                // links are not shown
            t = Regex.Replace(t, @"(?:[A-Za-z]:)?(?:[\\/][\w.\-]+){2,}", " ");                                  // file paths
            t = Regex.Replace(t, @"\b[\w\-]+\.(?:py|cjs|js|cs|xml|json|md|dll|bat|cmd)\b", " ");                // filenames
            t = Regex.Replace(t, @"#\w+", " ");
            t = t.Replace('’', '\'').Replace('‘', '\'').Replace("“", string.Empty).Replace("”", string.Empty);
            t = Regex.Replace(t, @"\s*[–—]\s*", ", ");
            var sb = new StringBuilder(t.Length);
            foreach (char ch in t)
            {
                if (ch < 0x2190 && !char.IsSurrogate(ch)) sb.Append(ch);                                       // emoji, pictographs, arrows
            }

            t = sb.ToString();
            t = Regex.Replace(t, @"[_~`^|\\{}]+", " ");
            foreach (var kv in Soften) t = kv.Key.Replace(t, kv.Value);
            t = Regex.Replace(t, @"\s+", " ").Trim(' ', '-', ',');
            if (t.Length > MaxLength)
            {
                string cut = t.Substring(0, MaxLength);
                int sp = cut.LastIndexOf(' ');
                t = sp >= 0 ? cut.Substring(0, sp) : cut;
            }

            if (t.Length < 2 || CleanBlock.IsMatch(t) || ExtraBlock.IsMatch(t) || TechBlock.IsMatch(t)) return null;
            return t;
        }

        /// <summary>True when the text would be shown (Clean does not reject it).</summary>
        public static bool IsClean(string text)
        {
            return Clean(text) != null;
        }
    }
}
