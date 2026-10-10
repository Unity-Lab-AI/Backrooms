# -*- coding: utf-8 -*-
"""Wrap every remaining window entry point in a clean IMGUI state.

The company setup page is fixed in its own file. These are the other five, and they share the
identical flaw: not one reset `GUI.color`, `Text.Font` or `Text.Anchor`, so each inherits whatever
the previously drawn mod left in Unity's global draw state. The setup page is the one the owner
hit first because it is the first of ours a player ever sees.

Every anchor asserted before anything is written, one write per file at the end.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GUARD_NOTE = (u"            // Known-good IMGUI state for this draw, restored on the way out.\n"
              u"            // Unity's draw state is process-wide and every mod's OnGUI shares\n"
              u"            // it; a mod that leaves GUI.color set paints every window after it.\n"
              u"            // See RimroomsWindowState -- this is the fix for the first bug a\n"
              u"            // real launch found.\n")

EDITS = {
    os.path.join("src", "RimroomsAsyncIndustries", "UI", "MainTabWindow_Operations.cs"): [
        (u"""        public override void DoWindowContents(Rect inRect)
        {
            using (Core.RimroomsDiagnostics.Measure("operations-draw")) { DrawOperations(inRect); }
        }""",
         u"""        public override void DoWindowContents(Rect inRect)
        {
""" + GUARD_NOTE + u"""            using (RimroomsWindowState.Clean())
            using (Core.RimroomsDiagnostics.Measure("operations-draw"))
            { DrawOperations(inRect); }
        }"""),
    ],
    os.path.join("src", "RimroomsAsyncIndustries", "UI", "ExpeditionRecordDialogs.cs"): [
        (u"""        public override void DoWindowContents(Rect inRect)
        {
            Rect content = new Rect(0, 0, inRect.width - 20f, contentHeight);""",
         u"""        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { DrawClosure(inRect); }
        }

        private void DrawClosure(Rect inRect)
        {
            Rect content = new Rect(0, 0, inRect.width - 20f, contentHeight);"""),
        (u"""        public override void DoWindowContents(Rect inRect)
        {
            var listing = new Listing_Standard(); listing.Begin(inRect);""",
         u"""        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { DrawDeclaration(inRect); }
        }

        private void DrawDeclaration(Rect inRect)
        {
            var listing = new Listing_Standard(); listing.Begin(inRect);"""),
    ],
    os.path.join("src", "RimroomsAsyncIndustries", "UI", "OperationsPersonnel.cs"): [
        (u"""        public override void DoWindowContents(Rect inRect)
        {
            inRect.yMax -= 40f;""",
         u"""        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { DrawDossier(inRect); }
        }

        private void DrawDossier(Rect inRect)
        {
            inRect.yMax -= 40f;"""),
        (u"""        public override void DoWindowContents(Rect inRect)
        {
            RimroomsPersonnelComponent personnel = Current.Game == null ? null : Current.Game.GetComponent<RimroomsPersonnelComponent>();""",
         u"""        public override void DoWindowContents(Rect inRect)
        {
            using (RimroomsWindowState.Clean()) { DrawConfirmation(inRect); }
        }

        private void DrawConfirmation(Rect inRect)
        {
            RimroomsPersonnelComponent personnel = Current.Game == null ? null : Current.Game.GetComponent<RimroomsPersonnelComponent>();"""),
    ],
}

problems = []
loaded = {}
for rel, edits in EDITS.items():
    path = os.path.join(REPO, rel)
    text = io.open(path, encoding="utf-8").read()
    loaded[rel] = text
    for old, _ in edits:
        if text.count(old) != 1:
            problems.append("%s: %d of %r" % (rel, text.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for rel, edits in EDITS.items():
    text = loaded[rel]
    for old, new in edits:
        text = text.replace(old, new, 1)
    io.open(os.path.join(REPO, rel), "w", encoding="utf-8", newline="").write(text)

print("%d window entry points guarded across %d files"
      % (sum(len(v) for v in EDITS.values()), len(EDITS)))
