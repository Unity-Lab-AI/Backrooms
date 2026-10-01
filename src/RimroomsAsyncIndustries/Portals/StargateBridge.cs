using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimroomsAsyncIndustries.Portals
{
    /// <summary>
    /// The Stargate mod's own gate, put on an ordinary Core door, driven by us.
    ///
    /// ## Owner direction, and it was given more than once before it was heard
    ///
    /// *"we use the fucjkign stargate MOD but use a normal door im not telling u again"*,
    /// *"and connect them together to the backrooms and the map"*, *"we just use our own dialing
    /// converstion in the background"*, and *"we still use the stargate mod as normal but we also
    /// use it for our backrroms purposes"*.
    ///
    /// Four sentences, four requirements, and they are all honoured literally:
    ///
    /// 1. **their mod does the travelling** — we add no portal of our own beside it;
    /// 2. **the gate is an ordinary Core `Door`** — no new ThingDef, nothing to build;
    /// 3. **both ends are connected** — the colony door and a door inside the coordinate;
    /// 4. **we dial, not the player** — our network already knows which door leads where, so the
    ///    address conversion happens here and the player never touches a DHD for the Backrooms.
    ///
    /// And the fifth, which constrains all of it: **their mod keeps working exactly as it does
    /// today.** Nothing of theirs is edited, patched, replaced or wrapped. Their gates, their
    /// DHD, their addresses, their quests are untouched, and this only ever adds a component to
    /// a door **this company designated**.
    ///
    /// ## Why the component is attached here rather than in XML
    ///
    /// A `comps` patch is per **def**, so patching `CompStargate` onto Core's `Door` would make
    /// every door in every colony a stargate. Their `InitGate` allows one gate per map and
    /// **hibernates the rest with a message**, so a nine-door shop would announce eight
    /// hibernating gates on the first tick. Attaching per **instance** is what matches the
    /// designation this mod already has, and `ThingWithComps.AllComps` is a public list.
    ///
    /// ## Why there is no hard dependency, and no Harmony, and no reflection write
    ///
    /// The build stays Core-only, so a collaborator without this mod installed still compiles
    /// the package — the owner asked for exactly that: *"i need someone else to work on this in
    /// parrellel through git hub"*.
    ///
    /// Everything reached here is **public**, and most of it is Core rather than theirs:
    ///
    /// * `GenTypes.GetTypeInAnyAssembly` is Core's own name lookup, the same one def loading uses;
    /// * `ThingComp.parent`, `ThingComp.props`, `Initialize` and `PostSpawnSetup` are public on
    ///   Core's own base class, so the component is attached without touching their type at all;
    /// * **their `CompProperties` is borrowed from their own gate def rather than constructed**,
    ///   so no field of theirs is ever assigned and their textures, vortex pattern and settings
    ///   are whatever they shipped — if they retune their gate, ours retunes with it;
    /// * only `OpenStargateDelayed` and `CloseStargate` are invoked, both public methods.
    ///
    /// No Harmony, no detour, no `SetValue`, no `BindingFlags.NonPublic`. Install this mod
    /// without theirs and every path here answers "not available" and the Backrooms behave as
    /// they did before.
    /// </summary>
    internal static class StargateBridge
    {
        private const string CompTypeName = "StargatesMod.CompStargate";
        private const string PropsTypeName = "StargatesMod.CompProperties_Stargate";
        private const string DialModeTypeName = "StargatesMod.DialMode";

        /// <summary>
        /// The gate def whose component settings ours borrows.
        ///
        /// **Borrowed, never built.** Constructing their `CompProperties` would mean assigning
        /// their fields, and the texture paths, draw size and vortex pattern would then be our
        /// copy of their numbers — stale the moment they retune. Taking the instance off their
        /// own def means a gate on a door is configured exactly as a gate on their stargate is.
        /// </summary>
        private const string DonorDefName = "StargateMod_Stargate";

        private static bool resolved;
        private static Type compType;
        private static Type dialModeType;
        private static MethodInfo openMethod;
        private static MethodInfo closeMethod;
        private static FieldInfo activeField;
        private static FieldInfo hibernatingField;
        private static FieldInfo receivingField;
        private static CompProperties donorProps;

        /// <summary>
        /// Whether the Stargate mod is installed and everything this needs from it was found.
        ///
        /// Resolved once. A missing type, a renamed method or a retired def all leave this false
        /// rather than throwing, because the one thing this must never do is break a colony that
        /// does not have the mod — or one that has a version of it this was not written against.
        /// </summary>
        internal static bool Available
        {
            get
            {
                Resolve();
                return compType != null && donorProps != null && openMethod != null;
            }
        }

        private static void Resolve()
        {
            if (resolved) { return; }
            resolved = true;
            compType = GenTypes.GetTypeInAnyAssembly(CompTypeName);
            Type propsType = GenTypes.GetTypeInAnyAssembly(PropsTypeName);
            dialModeType = GenTypes.GetTypeInAnyAssembly(DialModeTypeName);
            if (compType == null || propsType == null) { return; }

            ThingDef donor = DefDatabase<ThingDef>.GetNamedSilentFail(DonorDefName);
            if (donor != null && donor.comps != null)
            {
                for (int index = 0; index < donor.comps.Count; index++)
                {
                    CompProperties candidate = donor.comps[index];
                    if (candidate != null && propsType.IsInstanceOfType(candidate))
                    { donorProps = candidate; break; }
                }
            }

            // Public members only. A private lookup is banned outright and would also be a lie
            // about how stable this is: a public method is part of what they publish.
            openMethod = compType.GetMethod("OpenStargateDelayed");
            closeMethod = compType.GetMethod("CloseStargate");
            activeField = compType.GetField("StargateIsActive");
            hibernatingField = compType.GetField("IsHibernating");
            receivingField = compType.GetField("IsReceivingGate");
        }

        /// <summary>Their component on this door, or null.</summary>
        internal static ThingComp On(ThingWithComps thing)
        {
            Resolve();
            if (compType == null || thing == null) { return null; }
            List<ThingComp> all = thing.AllComps;
            if (all == null) { return null; }
            for (int index = 0; index < all.Count; index++)
            {
                if (compType.IsInstanceOfType(all[index])) { return all[index]; }
            }
            return null;
        }

        /// <summary>
        /// Make this door one of their gates, if it is not already.
        ///
        /// Idempotent, and silent when the mod is absent. The transporter is attached beside it
        /// because that is what their gate uses to be **loaded**: with it, colonists haul the
        /// chosen materials to the door on their own and carry them through, which is the owner's
        /// *"how the fuck are they suppose to auto pick up materials on one side and use them on
        /// the other"*. Without it a gate accepts pawns and nothing else.
        /// </summary>
        /// <param name="naturalGate">
        /// True for a way out that was always there, false for a machine a player dialled.
        /// **A natural gate gets no unstable vortex** -- see <see cref="SizedProps"/>.
        /// </param>
        internal static bool Attach(ThingWithComps door, bool naturalGate)
        {
            if (!Available || door == null) { return false; }
            if (On(door) != null) { return true; }
            try
            {
                AttachTransporter(door);

                ThingComp gate = (ThingComp)Activator.CreateInstance(compType);
                gate.parent = door;
                door.AllComps.Add(gate);
                // Core's own two-step: props first, then the spawn hook that registers the
                // address. `false` because this door is not being restored from a save -- it is
                // becoming a gate now, which is exactly what their InitGate expects.
                gate.Initialize(SizedProps(door.def, naturalGate));
                if (door.Spawned) { gate.PostSpawnSetup(false); }
                return true;
            }
            catch (Exception problem)
            {
                Log.Warning("[Rimrooms][Stargate] Could not make " + door.LabelShortCap
                            + " a gate; the Backrooms route still works without it: " + problem);
                return false;
            }
        }

        /// <summary>
        /// Their visual effects, sized to the door they are on.
        ///
        /// Owner: *"lets use the fx and visual stuff if we can and make them appropriate sizes to
        /// the sizes of possible doors natural and maching gate types"*.
        ///
        /// **Their event horizon and their iris, at a door's scale rather than a stargate's.**
        /// The ratio is taken from their own defs rather than invented — measured across all
        /// three of their gates, the puddle is about 1.6 to 1.77 times the gate's width and
        /// square:
        ///
        ///     StargateMod_Stargate          size (5,1)   puddle 8.7   = 1.74x
        ///     StargateMod_OrlinStargate     size (3,1)   puddle 5.3   = 1.77x
        ///     StargateMod_AdvancedStargate  size (5,1)   puddle 7.9   = 1.58x
        ///
        /// So a 1x1 door gets a 1.6-cell shimmer that fills its opening, and a three-wide door
        /// gets one three times that. **Every footprint a gate may use is covered** — Core's 1x1
        /// `Door`, the 2x1 `OrnateDoor` and Anomaly's `SecurityDoor`, and the wider doors another
        /// mod ships — because the number is read off `def.size` rather than listed.
        ///
        /// **The vortex is the part that had to shrink.** Theirs is thirteen cells, three wide and
        /// four deep, which is a ring standing in the open; on a shop's back wall that is a
        /// demolition charge. A door's unstable vortex is **its own opening, one cell deep,
        /// across its own width** — still fatal to stand in, which is the Stargate rule, and still
        /// a doorway rather than a crater.
        ///
        /// An iris needs something to close over, so it is offered only on a door wide enough to
        /// have an opening worth covering — their own makeshift gate sets `canHaveIris` false for
        /// the same reason.
        ///
        /// ## And not one field of theirs is assigned
        ///
        /// The properties are built by handing **Core's own XML-to-object loader** the same shape
        /// of node a def file would contain. `DirectXmlToObject.ObjectFromXml` reads the
        /// `Class="..."` attribute and populates the fields exactly as def loading does, so the
        /// values arrive through the game's own machinery and this file still contains no
        /// `SetValue` and no `BindingFlags`. The texture paths are **read** from their own gate's
        /// properties, so retextured gates retexture these too.
        /// </summary>
        private static readonly Dictionary<string, CompProperties> sizedProps =
            new Dictionary<string, CompProperties>();

        /// <summary>
        /// **A NATURAL GATE HAS NO UNSTABLE VORTEX, AND THAT IS NOT A SAFETY TWEAK — IT IS WHAT A
        /// NATURAL GATE IS.**
        ///
        /// Owner, verbatim: *"the gate is a natural one and shouuld always be open.... i
        /// understand the machine gate opening and closing and will kill anyone standing near in
        /// front on start up. but the natural portals are open always right?"*
        ///
        /// **Yes, and that distinction catches a defect that would otherwise have shipped.** Their
        /// vortex fires inside `OpenStargate`, once per open, and their wormhole closes itself:
        /// `IsReceivingGate &amp;&amp; _ticksSinceBufferUnloaded > 2500 &amp;&amp;
        /// !GateIsLoadingTransporter &amp;&amp; _sendBuffer.Empty()` calls `CloseStargate(true)`.
        /// A natural gate held permanently open is therefore **re-dialled every time their
        /// timeout closes it** — so with a vortex it would detonate its own doorway roughly every
        /// forty seconds, for ever.
        ///
        /// An empty pattern is also the honest fiction. **A natural gate never opens.** It was
        /// always there; nothing spins up, so nothing is vaporised. The kawoosh belongs to the
        /// machine gate, where a player chose to dial and the thing visibly starts — exactly as
        /// the owner described it.
        ///
        /// The event horizon stays on both, because that is what an open way through looks like.
        /// </summary>
        private static CompProperties SizedProps(ThingDef door, bool naturalGate)
        {
            string key = door.defName + (naturalGate ? "|natural" : "|machine");
            CompProperties cached;
            if (sizedProps.TryGetValue(key, out cached)) { return cached; }

            CompProperties built = null;
            try { built = BuildSizedProps(door, naturalGate); }
            catch (Exception problem)
            {
                Log.Warning("[Rimrooms][Stargate] Could not size the gate effects for "
                            + door.defName + "; using theirs unchanged: " + problem);
            }
            // Theirs unchanged is a worse look, never a broken gate. Falling back keeps a route
            // working when the only thing that failed was how it is drawn.
            cached = built ?? donorProps;
            sizedProps[key] = cached;
            return cached;
        }

        private static CompProperties BuildSizedProps(ThingDef door, bool naturalGate)
        {
            int width = Math.Max(1, Math.Max(door.size.x, door.size.z));
            float puddle = width * 1.6f;

            var pattern = new System.Text.StringBuilder();
            int half = width / 2;
            // EMPTY FOR A NATURAL GATE. It is always open, so it never opens, so there is nothing
            // for an unstable vortex to be unstable about -- and our own permanent re-dial would
            // otherwise fire one on a loop. A machine gate keeps it: a player dialled that.
            for (int offset = -half; naturalGate ? false : offset <= width - 1 - half; offset++)
            {
                // One cell in front, across the door's own width. `VortexCells` rotates these by
                // the door's rotation, so this is the threshold whichever way the door faces.
                pattern.Append("<li>(").Append(offset).Append(",0,1)</li>");
            }

            var xml = new System.Text.StringBuilder();
            xml.Append("<li Class=\"").Append(PropsTypeName).Append("\">");
            xml.Append("<canHaveIris>").Append(width >= 2 ? "true" : "false").Append("</canHaveIris>");
            xml.Append("<explodeOnUse>false</explodeOnUse>");
            AppendTexture(xml, "puddleTexture");
            AppendTexture(xml, "irisTexture");
            xml.Append("<puddleDrawSize>(")
               .Append(puddle.ToString("0.##", System.Globalization.CultureInfo.InvariantCulture))
               .Append(",")
               .Append(puddle.ToString("0.##", System.Globalization.CultureInfo.InvariantCulture))
               .Append(")</puddleDrawSize>");
            xml.Append("<vortexPattern>").Append(pattern).Append("</vortexPattern>");
            xml.Append("</li>");

            var document = new System.Xml.XmlDocument();
            document.LoadXml(xml.ToString());
            // Core's own loader, the same call def loading makes. No field of theirs is assigned
            // by this package; the game populates its own type from its own XML.
            return DirectXmlToObject.ObjectFromXml<CompProperties>(document.DocumentElement, false);
        }

        /// <summary>
        /// Copy a texture path off their own gate's properties, so a retextured gate retextures
        /// these. A public field read; nothing is written and nothing private is touched.
        /// </summary>
        private static void AppendTexture(System.Text.StringBuilder xml, string fieldName)
        {
            if (donorProps == null) { return; }
            FieldInfo field = donorProps.GetType().GetField(fieldName);
            if (field == null) { return; }
            string path = field.GetValue(donorProps) as string;
            if (string.IsNullOrEmpty(path)) { return; }
            xml.Append("<").Append(fieldName).Append(">")
               .Append(path).Append("</").Append(fieldName).Append(">");
        }

        /// <summary>
        /// Core's transporter, with the same settings their own gate def declares.
        ///
        /// `CompProperties_Transporter` is Core's, so this one really is constructed rather than
        /// borrowed — no other mod's fields are assigned. The numbers match their
        /// `StargateMod_StargateBase`: one group per gate, and a capacity that does not pretend a
        /// wormhole has a weight limit.
        /// </summary>
        private static void AttachTransporter(ThingWithComps door)
        {
            if (door.TryGetComp<CompTransporter>() != null) { return; }
            var props = new CompProperties_Transporter();
            props.max1PerGroup = true;
            props.massCapacity = 999999f;
            var transporter = new CompTransporter();
            transporter.parent = door;
            door.AllComps.Add(transporter);
            transporter.Initialize(props);
            if (door.Spawned) { transporter.PostSpawnSetup(false); }
        }

        /// <summary>
        /// **Our dialling conversion, in the background.** Owner: *"we just use our own dialing
        /// converstion in the background"*.
        ///
        /// Their address space is a `PlanetTile` for an ordinary map and a map index for a pocket
        /// map, and their `InitGate` registers whichever applies when a gate spawns. This company
        /// already knows which door leads to which coordinate, so the conversion is just reading
        /// the destination map's own address and handing it over — no DHD, no player input, and
        /// no address list for the Backrooms to appear in by accident.
        /// </summary>
        internal static bool Dial(ThingWithComps door, Map destination, int delay)
        {
            if (!Available || door == null || destination == null) { return false; }
            ThingComp gate = On(door);
            if (gate == null || openMethod == null || dialModeType == null) { return false; }
            if (IsHibernating(door)) { return false; }
            try
            {
                PlanetTile address = destination.IsPocketMap
                    ? new PlanetTile(destination.Index) : destination.Tile;
                object mode = Enum.Parse(dialModeType,
                    destination.IsPocketMap ? "PocketMap" : "Map");
                openMethod.Invoke(gate, new object[] { address, delay, mode });
                return true;
            }
            catch (Exception problem)
            {
                Log.Warning("[Rimrooms][Stargate] Dialling " + door.LabelShortCap
                            + " failed; the Backrooms route is unaffected: " + problem);
                return false;
            }
        }

        /// <summary>Shut a wormhole this company opened. Never touches a gate it did not dial.</summary>
        internal static bool Close(ThingWithComps door, bool closeFarSide)
        {
            if (!Available || door == null) { return false; }
            ThingComp gate = On(door);
            if (gate == null || closeMethod == null) { return false; }
            try
            {
                closeMethod.Invoke(gate, new object[] { closeFarSide });
                return true;
            }
            catch (Exception problem)
            {
                Log.Warning("[Rimrooms][Stargate] Closing " + door.LabelShortCap
                            + " failed: " + problem);
                return false;
            }
        }

        /// <summary>Whether a wormhole is open on this door right now.</summary>
        internal static bool IsOpen(ThingWithComps door)
        {
            return ReadFlag(door, activeField);
        }

        /// <summary>
        /// Whether their mod has put this gate to sleep.
        ///
        /// **Read rather than fought.** Their rule is one live gate per map; a coordinate that
        /// already holds one of their stargates makes ours hibernate, and that is their mod
        /// working correctly. The route still exists either way — this only decides whether the
        /// wormhole can be dialled, never whether the place can be reached.
        /// </summary>
        internal static bool IsHibernating(ThingWithComps door)
        {
            return ReadFlag(door, hibernatingField);
        }

        /// <summary>Whether this end is the receiving side, which cannot be entered.</summary>
        internal static bool IsReceiving(ThingWithComps door)
        {
            return ReadFlag(door, receivingField);
        }

        private static bool ReadFlag(ThingWithComps door, FieldInfo field)
        {
            if (!Available || door == null || field == null) { return false; }
            ThingComp gate = On(door);
            if (gate == null) { return false; }
            try
            {
                object value = field.GetValue(gate);
                return value is bool && (bool)value;
            }
            catch (Exception)
            {
                return false;
            }
        }
    }
}
