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
        internal static bool Attach(ThingWithComps door)
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
                gate.Initialize(donorProps);
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
