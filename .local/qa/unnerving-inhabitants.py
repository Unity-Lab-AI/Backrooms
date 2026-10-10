# -*- coding: utf-8 -*-
"""The unnerving register, applied to people: a readable tell, an ally, and animals.

## Owner direction, 2026-10-04, verbatim

*"remember lsd unnerving feeling with all things ie events random spanwns,
enemies, allies, nuetrals, even all the crazy things ive mentioned in the past
and anything u can find in the many many prep docs on the Backrooms Universe"*

## The mechanism was written down before any of this code existed

`docs/UNIVERSE_ADAPTATION.md`, on how the source's feeling is produced:
*"Ordinary industrial interiors become uncanny through exact changes ... a
shifted doorway, impossible adjacency, repeated hall, changed room dimensions, or
a feature that has moved since the last visit."*

**The uncanny is one exact change to something ordinary.** The generator already
applies that to space, which is why the floors read. Nothing applied it to
people, and the owner's four-word version of the complaint was *"zero weird
events or people"*.

## Three gaps, and the first one is the mechanism

1. **The tell was a one-time letter.** The letters are good -- the echo's reads
   *"{0} is standing in this space, wearing what they were wearing this morning.
   {0} is also at home right now"* -- but they fire once and then the pawn is
   just a pawn. A player who dismissed the letter, or who comes back next
   opening, has **no way to read what is wrong with it**. `THREAT_DESIGN_SHEETS.md`
   requires *"a visible or otherwise accessible warning"* and forbids colour or
   sound as the only cue; a letter that has scrolled away is neither. So every
   family now carries a `tellKey` that prints **on the pawn, forever**, and
   `ConfigErrors` refuses a family without one.
2. **No ally existed.** Owner: *"they should be nutral, allies, and enemy in all
   differnt kinds and relations and scenrios"*. Enemy shipped and neutral
   shipped. **Somebody down there who helps you is more unnerving than somebody
   who attacks**, because an attack is explicable -- and it is built from Core:
   an existing non-hostile faction and Core's own defend-the-area lord, so they
   really do fight the psychotics for you.
3. **No animals.** Owner: *"just npc pawns and wild animals and shit of the
   gasme"*. Animals reached the player only through the chaser, never as
   something found in a room.

## Why the identity comp is reused rather than a second one added

`CompRimroomsSurvivor` already sits on the human race def, is carried dormant by
**every pawn in the game**, is saved, and already prints an inspect line. A
second comp on the same def would double the per-pawn cost across thousands of
pawns to do the same job.

**The class name is now narrower than its job and that is recorded rather than
renamed.** Renaming would mean touching the patch that attaches it and buys no
behaviour; the doc comment says what it actually is.
"""
import io
import sys

NL = chr(10)

DEF = "src/RimroomsAsyncIndustries/Threats/RimroomsInhabitantDef.cs"
COMP = "src/RimroomsAsyncIndustries/Threats/CompRimroomsSurvivor.cs"
SERVICE = "src/RimroomsAsyncIndustries/Threats/InhabitantService.cs"

EDITS = [
    # ====================================================== the def: two kinds, a tell, a relation
    (DEF,
     "        /// <summary>" + NL
     + "        /// Somebody wearing the name and clothes of a colonist who is **alive right now**.",

     "        /// <summary>" + NL
     + "        /// Somebody who helps, and should not be able to." + NL
     + "        ///" + NL
     + "        /// **Owner direction, 2026-10-04, verbatim:** *\"they should be nutral, allies,"
     + NL
     + "        /// and enemy in all differnt kinds and relations and scenrios\"*, under the"
     + NL
     + "        /// standing *\"remember lsd unnerving feeling with all things\"*." + NL
     + "        ///" + NL
     + "        /// **An ally is the most unnerving of the three relations, not the friendliest.**"
     + NL
     + "        /// A thing that attacks you is explicable. Somebody who has been down here long"
     + NL
     + "        /// enough to be part of it, who takes your side against what else is in the"
     + NL
     + "        /// space, and who **will not leave with you**, is not. They are generated into an"
     + NL
     + "        /// existing non-hostile faction and given Core's own defend-the-area lord, so the"
     + NL
     + "        /// help is real: they fight the psychotic families for you with ordinary AI."
     + NL
     + "        /// </summary>" + NL
     + "        Helper = 6," + NL
     + NL
     + "        /// <summary>" + NL
     + "        /// An animal that is simply in here." + NL
     + "        ///" + NL
     + "        /// **Owner direction, 2026-10-04, verbatim:** *\"things that chase you are just"
     + NL
     + "        /// npc pawns and wild animals and shit of the gasme\"*. Animals reached the"
     + NL
     + "        /// player only as a chaser until now, never as something found standing in a"
     + NL
     + "        /// room. Unfactioned, like any wild animal anywhere -- the unnerving part is not"
     + NL
     + "        /// that it is dangerous but that it is **in here**, and something had to bring it."
     + NL
     + "        /// </summary>" + NL
     + "        Fauna = 7," + NL
     + NL
     + "        /// <summary>" + NL
     + "        /// Somebody wearing the name and clothes of a colonist who is **alive right now**."),

    (DEF,
     "        /// <summary>Keyed string announcing the find, or empty for no letter.</summary>" + NL
     + "        public string letterLabelKey;" + NL
     + "        public string letterTextKey;",

     "        /// <summary>Keyed string announcing the find, or empty for no letter.</summary>" + NL
     + "        public string letterLabelKey;" + NL
     + "        public string letterTextKey;" + NL
     + NL
     + "        /// <summary>" + NL
     + "        /// **The one exact thing that is wrong about this encounter, readable on the"
     + NL
     + "        /// pawn itself, forever.**" + NL
     + "        ///" + NL
     + "        /// Owner direction, 2026-10-04: *\"remember lsd unnerving feeling with all things"
     + NL
     + "        /// ie events random spanwns, enemies, allies, nuetrals\"*. The mechanism comes"
     + NL
     + "        /// from `docs/UNIVERSE_ADAPTATION.md`, which already said how the source's"
     + NL
     + "        /// feeling is produced: *\"Ordinary industrial interiors become uncanny through"
     + NL
     + "        /// exact changes\"*. The generator applies that to space; **nothing applied it to"
     + NL
     + "        /// people**, and the owner's version of the complaint was *\"zero weird events or"
     + NL
     + "        /// people\"*." + NL
     + "        ///" + NL
     + "        /// **A letter is not a tell.** The letters this package writes are good, but they"
     + NL
     + "        /// fire once and scroll away, and then the pawn is just a pawn -- a player who"
     + NL
     + "        /// comes back next opening has nothing to read. `THREAT_DESIGN_SHEETS.md` requires"
     + NL
     + "        /// *\"a visible or otherwise accessible warning\"* and forbids colour or sound as"
     + NL
     + "        /// the only cue. This is that warning, on the thing, in text."
     + NL
     + "        /// </summary>" + NL
     + "        public string tellKey;" + NL
     + NL
     + "        /// <summary>" + NL
     + "        /// Whether this family takes the branch's side against what else is in the space."
     + NL
     + "        ///" + NL
     + "        /// Only ever true for <see cref=\"InhabitantKind.Helper\"/>, and checked rather"
     + NL
     + "        /// than assumed for the same reason `hostile` is: a family whose relation does not"
     + NL
     + "        /// match what it reads as breaks the warning-first rule in the other direction."
     + NL
     + "        /// </summary>" + NL
     + "        public bool friendly;"),

    # the config errors enforce the tell and the new relation
    (DEF,
     "            if (hostile && kind != InhabitantKind.Psychotic)",

     "            // **A FAMILY WITHOUT A TELL IS THE DEFECT THIS FIELD EXISTS FOR.** Owner,"
     + NL
     + "            // 2026-10-04: the unnerving feeling applies to *\"all things\"*, and a family"
     + NL
     + "            // whose uncanny detail exists only in a letter that has scrolled away has no"
     + NL
     + "            // readable warning at all. Enforced at load so a new family cannot ship without"
     + NL
     + "            // one -- which is how the seven that existed before this got away with it."
     + NL
     + "            if (string.IsNullOrEmpty(tellKey))" + NL
     + "            {" + NL
     + "                yield return \"RimroomsInhabitantDef \" + defName +" + NL
     + "                    \" has no tellKey, so nothing on the pawn says what is wrong with it.\";"
     + NL
     + "            }" + NL
     + "            if (friendly && kind != InhabitantKind.Helper)" + NL
     + "            {" + NL
     + "                yield return \"RimroomsInhabitantDef \" + defName +" + NL
     + "                    \" is friendly but is not a Helper family, which breaks the "
     + "warning-first rule.\";" + NL
     + "            }" + NL
     + "            if (friendly && hostile)" + NL
     + "            {" + NL
     + "                yield return \"RimroomsInhabitantDef \" + defName +" + NL
     + "                    \" is both friendly and hostile.\";" + NL
     + "            }" + NL
     + "            if (hostile && kind != InhabitantKind.Psychotic)"),

    # ====================================================== the comp carries the family and its tell
    (COMP,
     "    /// ## Dormant unless marked",

     "    /// ## It also carries WHAT a coordinate produced this person as, and the tell that"
     + NL
     + "    /// goes with it" + NL
     + "    ///" + NL
     + "    /// **Owner direction, 2026-10-04, verbatim:** *\"remember lsd unnerving feeling with"
     + NL
     + "    /// all things ie events random spanwns, enemies, allies, nuetrals\"*. Every inhabitant"
     + NL
     + "    /// family now has one exact wrong detail, and this is where a player reads it --"
     + NL
     + "    /// **on the pawn, for as long as the pawn exists.** The letters fire once and scroll"
     + NL
     + "    /// away; `THREAT_DESIGN_SHEETS.md` wants *\"a visible or otherwise accessible"
     + NL
     + "    /// warning\"* and forbids colour or sound as the only cue."
     + NL
     + "    ///" + NL
     + "    /// **THE CLASS NAME IS NOW NARROWER THAN THE JOB, and that is recorded rather than"
     + NL
     + "    /// renamed.** This comp already sits on the human race def, is carried dormant by"
     + NL
     + "    /// every pawn in the game, is saved and already prints an inspect line -- a second"
     + NL
     + "    /// comp on the same def would double the per-pawn cost across thousands of pawns to do"
     + NL
     + "    /// the same job. Renaming would mean touching the patch that attaches it and buys no"
     + NL
     + "    /// behaviour at all." + NL
     + "    ///" + NL
     + "    /// ## Dormant unless marked"),

    (COMP,
     "        /// <summary>Saved. True once they have accepted passage, so the offer is not repeated.</summary>"
     + NL
     + "        private bool joined;",

     "        /// <summary>Saved. True once they have accepted passage, so the offer is not repeated.</summary>"
     + NL
     + "        private bool joined;" + NL
     + NL
     + "        /// <summary>" + NL
     + "        /// Saved. The `RimroomsInhabitantDef` a coordinate produced this person as, or"
     + NL
     + "        /// empty for everybody else in the game." + NL
     + "        ///" + NL
     + "        /// Stored as a defName rather than a resolved def because this is saved on a pawn"
     + NL
     + "        /// that can outlive a content change: a family removed from the package must leave"
     + NL
     + "        /// the pawn standing and silent, not throw on load." + NL
     + "        /// </summary>" + NL
     + "        private string inhabitantFamily;"),

    (COMP,
     '            Scribe_Values.Look(ref joined, "rr_survivorJoined", false);',
     '            Scribe_Values.Look(ref joined, "rr_survivorJoined", false);' + NL
     + '            Scribe_Values.Look(ref inhabitantFamily, "rr_inhabitantFamily");'),

    (COMP,
     "        public override string CompInspectStringExtra()" + NL
     + "        {" + NL
     + '            return IsSurvivor ? "RR_Survivor_Inspect".Translate().ToString() : null;' + NL
     + "        }",

     "        /// <summary>Marks what a coordinate produced this person as.</summary>" + NL
     + "        public void MarkInhabitant(string familyDefName)" + NL
     + "        {" + NL
     + "            if (!string.IsNullOrEmpty(familyDefName)) { inhabitantFamily = familyDefName; }"
     + NL
     + "        }" + NL
     + NL
     + "        /// <summary>The one exact wrong detail about this person, or null.</summary>" + NL
     + "        public string InhabitantTell" + NL
     + "        {" + NL
     + "            get" + NL
     + "            {" + NL
     + "                if (string.IsNullOrEmpty(inhabitantFamily)) { return null; }" + NL
     + "                RimroomsInhabitantDef family =" + NL
     + "                    DefDatabase<RimroomsInhabitantDef>.GetNamedSilentFail(inhabitantFamily);"
     + NL
     + "                if (family == null || string.IsNullOrEmpty(family.tellKey)) { return null; }"
     + NL
     + "                return family.tellKey.Translate().ToString();" + NL
     + "            }" + NL
     + "        }" + NL
     + NL
     + "        public override string CompInspectStringExtra()" + NL
     + "        {" + NL
     + "            // **THE TELL COMES FIRST and it outlives the letter.** A player who dismissed"
     + NL
     + "            // the announcement, or who is back a dozen openings later, reads here why this"
     + NL
     + "            // person is wrong. The passage offer is state; the tell is what the thing IS."
     + NL
     + "            var lines = new List<string>();" + NL
     + "            string tell = InhabitantTell;" + NL
     + "            if (!string.IsNullOrEmpty(tell)) { lines.Add(tell); }" + NL
     + '            if (IsSurvivor) { lines.Add("RR_Survivor_Inspect".Translate().ToString()); }' + NL
     + "            return lines.Count == 0 ? null : string.Join(\"" + chr(92) + "n\", lines.ToArray());"
     + NL
     + "        }"),

    # ====================================================== the service: mark, ally faction, fauna
    (SERVICE,
     "            if (family.kind == InhabitantKind.Survivor)",

     "            // **EVERY INHABITANT CARRIES ITS FAMILY, so every one of them can be read.**"
     + NL
     + "            // Marked before the spawn so the tell is on the pawn the instant it exists and"
     + NL
     + "            // there is no frame in which it is an unexplained stranger."
     + NL
     + "            pawn.TryGetComp<CompRimroomsSurvivor>()?.MarkInhabitant(family.defName);"
     + NL
     + "            if (family.kind == InhabitantKind.Survivor)"),

    (SERVICE,
     "            if (family.hostile && faction != null)" + NL
     + "            {" + NL
     + "                LordMaker.MakeNewLord(faction, HostileLordJob(band, cell, faction), map, new List<Pawn> { pawn });"
     + NL
     + "            }",

     "            if (family.hostile && faction != null)" + NL
     + "            {" + NL
     + "                LordMaker.MakeNewLord(faction, HostileLordJob(band, cell, faction), map, new List<Pawn> { pawn });"
     + NL
     + "            }" + NL
     + "            else if (family.friendly && faction != null)" + NL
     + "            {" + NL
     + "                // **THE HELP IS REAL, and it is Core's.** `LordJob_DefendPoint` makes them"
     + NL
     + "                // hold the room they are found in and fight whatever comes at it with"
     + NL
     + "                // ordinary AI -- which in a coordinate means the psychotic families. No"
     + NL
     + "                // bespoke assistance behaviour, and nothing here lets them near a gate:"
     + NL
     + "                // `PortalTraversalPolicy` is still the single chokepoint and an inhabitant"
     + NL
     + "                // still never decides anything about one."
     + NL
     + "                LordMaker.MakeNewLord(faction, new LordJob_DefendPoint(cell), map,"
     + NL
     + "                    new List<Pawn> { pawn });" + NL
     + "            }"),

    (SERVICE,
     "        private static Faction FactionFor(RimroomsInhabitantDef family)" + NL
     + "        {" + NL
     + "            if (!family.hostile) { return null; }",

     "        private static Faction FactionFor(RimroomsInhabitantDef family)" + NL
     + "        {" + NL
     + "            // **AN ALLY NEEDS A FACTION THAT IS NOT HOSTILE, and an existing one.** Owner,"
     + NL
     + "            // 2026-10-04: *\"they should be nutral, allies, and enemy\"*. A new faction"
     + NL
     + "            // would be exactly the *\"new type of np0c\"* the same message forbids, so this"
     + NL
     + "            // takes the first loaded faction that is neither the player's nor hostile to"
     + NL
     + "            // them, and falls back to unfactioned -- which makes a helper merely neutral"
     + NL
     + "            // rather than turning them into a threat."
     + NL
     + "            if (family.friendly)" + NL
     + "            {" + NL
     + "                return Find.FactionManager == null ? null" + NL
     + "                    : Find.FactionManager.AllFactionsListForReading" + NL
     + "                        .FirstOrDefault(candidate => candidate != null && !candidate.IsPlayer"
     + NL
     + "                            && !candidate.HostileTo(Faction.OfPlayer)" + NL
     + "                            && candidate.def != null && candidate.def.humanlikeFaction);"
     + NL
     + "            }" + NL
     + "            if (!family.hostile) { return null; }"),
]

problems = 0
touched = {}

for path, old, new in EDITS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d) in %s: %r"
              % (text.count(old), path.split("/")[-1], old.strip().split(NL)[0][:72]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-28s patched %s" % (path.split("/")[-1], old.strip().split(NL)[0][:50]))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
