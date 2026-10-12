using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;

namespace RimPLC.BridgeTools
{
    /// <summary>
    /// rimplc/* tools for RimBridgeServer (installed README, "Third-Party Extension Tools"). Each call hops to the
    /// main thread with IRimBridgeContext.MainThread.InvokeAsync (the member was read from RimBridgeServer.Sdk 2.1.1 by
    /// reflection) and runs the shared RimPLC.Api, the same code the file inbox runs. Shapes:
    /// docs/rimplc/schema/tools.schema.json. RimPLC core never references the SDK; without RimBridgeServer this
    /// assembly is simply never loaded.
    /// </summary>
    public sealed class RimPLCBridgeTools
    {
        private static Task<Dictionary<string, object>> Main(IRimBridgeContext ctx, Func<Dictionary<string, object>> f, CancellationToken ct)
        {
            if (ctx?.MainThread == null) return Task.FromResult(Api.Refused("no main-thread access from the bridge"));
            Func<Dictionary<string, object>> plain = () => (Dictionary<string, object>)Api.Plain(f());
            if (ctx.MainThread.IsMainThread) return Task.FromResult(plain());
            return ctx.MainThread.InvokeAsync(plain, ct);
        }

        [Tool("rimplc/read_ladder",
            Description = "The live ladder: the first live rungs with the measured values that made them fire, plus tags, marks and unity rungs. Same field names as the ladder tool.",
            ResultDescription = "ok, live_rungs[{id, priority, matched, then}], tags, my_marks, my_rungs, unknown_keys, live, unresolved_conditions, disabled_rungs, not_applicable, scan_tick")]
        public Task<Dictionary<string, object>> ReadLadder(
            IRimBridgeContext ctx,
            CancellationToken ct,
            [ToolParameter(Description = "How many live rungs (default 4)")] int top = 4,
            [ToolParameter(Description = "Every live rung instead of the first top")] bool all = false)
        {
            return Main(ctx, () => Api.ReadLadder(top, all), ct);
        }

        [Tool("rimplc/read_state", Description = "The sensor values RimPLC measured (absent keys are unmeasured, never zero-filled).")]
        public Task<Dictionary<string, object>> ReadState(
            IRimBridgeContext ctx,
            CancellationToken ct,
            [ToolParameter(Description = "Optional comma-separated key filter")] string keys = null)
        {
            var list = string.IsNullOrWhiteSpace(keys) ? null : new List<string>(keys.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries));
            if (list != null) for (int i = 0; i < list.Count; i++) list[i] = list[i].Trim();
            return Main(ctx, () => Api.ReadState(list), ct);
        }

        [Tool("rimplc/set_tag", Description = "Override a tag variable (UPPER_CASE). Constants are owner only. Clamped to min..max when read.")]
        public Task<Dictionary<string, object>> SetTag(
            IRimBridgeContext ctx,
            CancellationToken ct,
            [ToolParameter(Description = "Tag name", Required = true)] string name,
            [ToolParameter(Description = "Number, or empty to clear the override", Required = true)] string value,
            [ToolParameter(Description = "Owner flag: set only by the owner's CLI side, never from chat")] bool owner = false)
        {
            object v = string.IsNullOrWhiteSpace(value) ? null : value;
            return Main(ctx, () => Api.SetTag(name, v, owner), ct);
        }

        [Tool("rimplc/set_mark", Description = "Record a mark (lower_case): true/false or a number. Numbers stay numbers. Empty clears it.")]
        public Task<Dictionary<string, object>> SetMark(
            IRimBridgeContext ctx,
            CancellationToken ct,
            [ToolParameter(Description = "Mark name", Required = true)] string name,
            [ToolParameter(Description = "true, false or a number; empty clears", Required = true)] string value)
        {
            object v = string.IsNullOrWhiteSpace(value) ? null : value;
            return Main(ctx, () => Api.SetMark(name, v), ct);
        }

        [Tool("rimplc/upsert_rung", Description = "Add or replace one of Unity's rungs (forced to the unity- prefix and advise mode; then capped at 8 lines of 300 characters).")]
        public Task<Dictionary<string, object>> UpsertRung(
            IRimBridgeContext ctx,
            CancellationToken ct,
            [ToolParameter(Description = "The rung as JSON text (id, priority, when, then, optional latch/why/never/notice)", Required = true)] string rung)
        {
            return Main(ctx, () => Api.UpsertRung(rung), ct);
        }

        [Tool("rimplc/remove_rung", Description = "Remove a unity- or player- rung. Book rungs can only be switched off.")]
        public Task<Dictionary<string, object>> RemoveRung(
            IRimBridgeContext ctx,
            CancellationToken ct,
            [ToolParameter(Description = "Rung id", Required = true)] string id)
        {
            return Main(ctx, () => Api.RemoveRung(id), ct);
        }

        [Tool("rimplc/letters_seen", Description = "Mark every letter in the stack as seen (the letters count drops to 0).")]
        public Task<Dictionary<string, object>> LettersSeen(IRimBridgeContext ctx, CancellationToken ct)
        {
            return Main(ctx, () => Api.LettersSeen(), ct);
        }

        [Tool("rimplc/export", Description = "Write the player's and Unity's rungs, marks, tag overrides, switches and modes as a ladder file in the RimPLC exports folder; returns the path and the ladder.")]
        public Task<Dictionary<string, object>> Export(
            IRimBridgeContext ctx,
            CancellationToken ct,
            [ToolParameter(Description = "Optional file name (letters, digits, - and _)")] string name = null)
        {
            return Main(ctx, () => Api.Export(name), ct);
        }

        [Tool("rimplc/import", Description = "Import a ladder (JSON text). dry_run true (default) returns the diff only. Rungs become unity- rungs in advise mode; switches, auto modes and constants need the owner flag.")]
        public Task<Dictionary<string, object>> Import(
            IRimBridgeContext ctx,
            CancellationToken ct,
            [ToolParameter(Description = "The ladder as JSON text", Required = true)] string json,
            [ToolParameter(Description = "true = only show the diff")] bool dry_run = true,
            [ToolParameter(Description = "Owner flag: set only by the owner's CLI side, never from chat")] bool owner = false)
        {
            return Main(ctx, () => Api.Import(json, dry_run, owner), ct);
        }

        [Tool("rimplc/enable_rung", Description = "Switch a rung on or off. Switching a book rung off needs the owner flag.")]
        public Task<Dictionary<string, object>> EnableRung(
            IRimBridgeContext ctx,
            CancellationToken ct,
            [ToolParameter(Description = "Rung id", Required = true)] string id,
            [ToolParameter(Description = "true = on", Required = true)] bool enabled,
            [ToolParameter(Description = "Owner flag: set only by the owner's CLI side, never from chat")] bool owner = false)
        {
            return Main(ctx, () => Api.EnableRung(id, enabled, owner), ct);
        }
    }
}
