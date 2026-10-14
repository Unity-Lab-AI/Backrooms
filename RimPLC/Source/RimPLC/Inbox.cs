using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Verse;

namespace RimPLC
{
    /// <summary>
    /// The command-file fallback for when no RimBridgeServer is loaded (docs/RIMPLC_DESIGN.md 8.3), the same pattern
    /// as the Rimrooms automation inbox (which stays, owner decision 4):
    ///
    ///   commands  &lt;RimWorld config folder&gt;/RimPLC/inbox.jsonl    one JSON object per line, written by the client
    ///   results   &lt;RimWorld config folder&gt;/RimPLC/outbox.jsonl   {"id":..,"cmd":..,"result":{..}} per line
    ///
    /// cmd is a tool name without the rimplc/ prefix (read_ladder, read_state, set_tag, set_mark, upsert_rung,
    /// remove_rung, enable_rung, letters_seen, export, import) and the other fields are that tool's args (tools.schema.json). The
    /// inbox is claimed by an atomic rename, at most MAX_COMMANDS_PER_PASS lines run per pass and the rest stay
    /// queued. Runs once a real second from GameComponentUpdate, so it works while the game is paused.
    /// </summary>
    public static class Inbox
    {
        private static string Folder => Path.Combine(GenFilePaths.ConfigFolderPath, "RimPLC");
        private static string InboxPath => Path.Combine(Folder, "inbox.jsonl");
        private static string OutboxPath => Path.Combine(Folder, "outbox.jsonl");
        private static string ClaimPath => Path.Combine(Folder, "inbox.claimed.jsonl");
        private static string PendingPath => Path.Combine(Folder, "inbox.pending.jsonl");

        private static bool folderMade;

        public static void Process(RimPLCGameComponent plc)
        {
            // The folder is the "RimPLC is loaded" signal a command-file client waits for before writing, so the mod
            // makes it; otherwise neither side ever starts (found on the first live run, 2026-10-12).
            if (!folderMade)
            {
                try { Directory.CreateDirectory(Folder); } catch (IOException) { } catch (System.UnauthorizedAccessException) { }
                folderMade = true;
            }
            if (!File.Exists(InboxPath) && !File.Exists(PendingPath) && !File.Exists(ClaimPath)) return;
            int cap = RimPLCMod.Book.Constants.Get("MAX_COMMANDS_PER_PASS") is double d && d >= 1 ? (int)d : 32;
            List<string> lines;
            try
            {
                if (File.Exists(InboxPath) && !File.Exists(ClaimPath)) File.Move(InboxPath, ClaimPath);
                if (File.Exists(ClaimPath))
                {
                    if (File.Exists(PendingPath))
                    {
                        File.AppendAllLines(PendingPath, File.ReadAllLines(ClaimPath));
                        File.Delete(ClaimPath);
                    }
                    else
                    {
                        File.Move(ClaimPath, PendingPath);
                    }
                }

                lines = File.ReadAllLines(PendingPath).Where(l => !string.IsNullOrWhiteSpace(l)).ToList();
                if (lines.Count > cap) File.WriteAllLines(PendingPath, lines.Skip(cap));
                else File.Delete(PendingPath);
            }
            catch (Exception e)
            {
                // a file still open by the writer is tried again next pass
                Log.Warning("[RimPLC] could not read the command file: " + e.Message);
                return;
            }

            var results = new List<string>();
            foreach (string line in lines.Take(cap))
            {
                var row = new JsonObject();
                try
                {
                    JsonObject cmd = Json.ParseObject(line);
                    if (cmd.Get("id") != null) row.Set("id", Engine.PyStr(cmd.Get("id")));
                    row.Set("cmd", cmd.GetString("cmd") ?? string.Empty);
                    row.Set("result", Execute(cmd));
                }
                catch (Exception e)
                {
                    row.Set("result", Api.Refused("error: " + e.Message));
                }

                results.Add(Json.Write(row));
            }

            try
            {
                Directory.CreateDirectory(Folder);
                File.AppendAllLines(OutboxPath, results);
            }
            catch (Exception e)
            {
                Log.Warning("[RimPLC] could not write the result file: " + e.Message);
            }
        }

        private static Dictionary<string, object> Execute(JsonObject a)
        {
            string cmd = a.GetString("cmd");
            bool owner = a.Get("owner") is bool ob && ob;
            switch (cmd)
            {
                case "read_ladder":
                    return Api.ReadLadder(a.Get("top") is double t ? (int)t : 4, a.Get("all") is bool all && all);
                case "read_state":
                    return Api.ReadState(Rung.Strings(a.GetList("keys")));
                case "set_tag":
                    return Api.SetTag(a.GetString("name"), a.Get("value"), owner);
                case "set_mark":
                    return Api.SetMark(a.GetString("name"), a.Get("value"));
                case "set_host":
                    return Api.SetHost(a.Get("values"));
                case "upsert_rung":
                    return Api.UpsertRung(a.Get("rung"));
                case "remove_rung":
                    return Api.RemoveRung(a.GetString("id"));
                case "enable_rung":
                    return Api.EnableRung(a.GetString("id"), !(a.Get("enabled") is bool e) || e, owner);
                case "letters_seen":
                    return Api.LettersSeen();
                case "export":
                    return Api.Export(a.GetString("name"));
                case "import":
                    return Api.Import(a.Get("json") ?? a.Get("ladder"), !(a.Get("dry_run") is bool d0) || d0, owner);
                default:
                    return Api.Refused("unknown cmd " + (cmd ?? "(none)"));
            }
        }
    }
}
