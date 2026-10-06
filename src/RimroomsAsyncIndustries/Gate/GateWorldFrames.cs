using RimroomsAsyncIndustries.Core;
using UnityEngine;
using Verse;

namespace RimroomsAsyncIndustries.Gate
{
    /// <summary>
    /// Optional artwork on a native gate's complete door run. No new door, collision, power,
    /// connection or traversal state is introduced by this renderer.
    ///
    /// **A NATURAL GATE NEVER GETS THIS FRAME, AND THAT IS A DECISION RATHER THAN AN OVERSIGHT.**
    /// This draw hangs off <c>CompRimroomsGate</c> and keys on <c>IsDesignated</c>, so it reaches
    /// the gate a branch builds and nothing else. A permanent natural gate is the *other*
    /// component, <c>CompRimroomsEmergence</c>, and it stays a plain door with its blue glow.
    ///
    /// The asymmetry was reported as a gap and the owner overruled it, 2026-10-06, verbatim:
    ///
    ///     "remmebr natural gates dont look like the machine in the real univiverse of backrooms
    ///      they are mainly just normal doors and walls that u can majicly walk through but lets
    ///      keep natural doors just normal doors in game so there is distinction for it and long
    ///      time in the future if mod ever pics up in popularity we can add stuff like that"
    ///
    /// **So the difference in appearance IS the information.** A framed opening was built; an
    /// unframed one was found. Putting a machine frame on something nobody manufactured would read
    /// as manufactured, and the player would lose the only tell that separates the two kinds at a
    /// glance -- which is exactly backwards from the source material, where a natural way through
    /// is an ordinary door or stretch of wall.
    ///
    /// **Do not "fix" this by adding a PostDraw to the emergence component.** If the decision is
    /// ever reversed, the draw is extracted so both components call one derivation; two copies of
    /// the footprint and orientation rules would drift the first time either changes.
    /// </summary>
    public sealed partial class CompRimroomsGate
    {
        public override void PostDraw()
        {
            base.PostDraw();
            if (RimroomsMod.Settings == null || !RimroomsMod.Settings.GateFramesEnabled ||
                parent == null || !parent.Spawned || parent.Destroyed || parent.Map == null ||
                parent.Map.Disposed || parent.Map != Find.CurrentMap || !IsDesignated)
            { return; }

            // IsDesignated excludes run extensions, so only the run's host draws this frame.
            CellRect rect = GateOccupiedRect;
            if (rect.Area <= 0 || !LegalGateFootprint(new IntVec2(rect.Width, rect.Height)))
            { return; }
            foreach (IntVec3 cell in rect)
            {
                // A visible host must not reveal an extension still covered by fog.
                if (!cell.InBounds(parent.Map) || cell.Fogged(parent.Map)) { return; }
            }

            // DoorPreDraw mutates a single-cell door's live Rotation. The designation's saved
            // orientation is authoritative here, just as it is for the gate's entry cells.
            if (nativeBoundRotation < 0 || nativeBoundRotation > 3) { return; }
            Rot4 orientation = new Rot4(nativeBoundRotation);
            int shortSide = rect.Width <= rect.Height ? rect.Width : rect.Height;
            int longSide = rect.Width <= rect.Height ? rect.Height : rect.Width;
            int expectedWidth = orientation.IsHorizontal ? shortSide : longSide;
            int expectedDepth = orientation.IsHorizontal ? longSide : shortSide;
            // A run bound along the depth instead of the opening's width has no matching authored
            // frame. Keep the native door rather than stretch horizontal art into a tall run.
            if (rect.Width != expectedWidth || rect.Height != expectedDepth) { return; }

            bool flip;
            Material material = RimroomsGateWorldFrames.MaterialFor(shortSide, longSide,
                orientation, out flip);
            if (material == null) { return; }

            Vector3 center = new Vector3((rect.minX + rect.maxX + 1) * 0.5f,
                AltitudeLayer.Blueprint.AltitudeFor() + Altitudes.AltInc,
                (rect.minZ + rect.maxZ + 1) * 0.5f);
            // SupportedDoor's top graphic is already at Blueprint altitude. The frame sits one
            // small increment above it, below overhead flecks and fog. Its transparent center
            // leaves the native leaves, tint, opening animation and pawns visible underneath.
            // Each cardinal PNG is already oriented. Resize the plane to the world footprint and
            // use identity rotation; rotating it again would rotate the authored view twice.
            Mesh mesh = MeshPool.GridPlane(new Vector2(rect.Width, rect.Height), flip);
            Graphics.DrawMesh(mesh, center, Quaternion.identity, material, 0);

            // The energy, drawn over the frame rather than instead of it. One increment higher
            // again, so it sits on the frame and still below overhead flecks and fog.
            Material overlay = OverlayFrameNow();
            if (overlay == null) { return; }
            Vector3 overlayCenter = center;
            overlayCenter.y += Altitudes.AltInc;
            Graphics.DrawMesh(MeshPool.GridPlane(new Vector2(rect.Width, rect.Height)),
                overlayCenter, Quaternion.identity, overlay, 0);
        }

        /// <summary>
        /// Which overlay frame belongs on this gate right now, or null for none.
        ///
        /// **THE BURST IS TRANSIENT ON PURPOSE AND IS NOT SAVED.** `activationBurstTick` is a plain
        /// field with no `Scribe` call, so a save reloaded mid-cycle shows no burst. That is the
        /// correct behaviour rather than a shortcut: a one-off flash replaying every time somebody
        /// loads a game would announce an event that is not happening.
        ///
        /// **REDUCED MOTION STOPS THE ANIMATION AND KEEPS THE FRAME**, and the first version of this
        /// honoured neither. `GateFramesEnabled` was read at `PostDraw` and `PortalReducedMotion` was
        /// read nowhere, so a player who had asked for no moving effects got three new animated
        /// sequences the moment this shipped. The static frame is not motion and stays: it says a
        /// gate was built, which is information. The charge, activation and live cycles are motion
        /// and stop here, at the one place all three are resolved.
        /// </summary>
        private Material OverlayFrameNow()
        {
            if (Current.Game == null || Find.TickManager == null) { return null; }
            if (RimroomsMod.Settings == null || RimroomsMod.Settings.PortalReducedMotion)
            { return null; }
            int now = Find.TickManager.TicksGame;
            if (activationBurstTick >= 0)
            {
                int elapsed = now - activationBurstTick;
                if (elapsed >= 0 && elapsed < RimroomsGateWorldFrames.ActivationTicks)
                { return RimroomsGateWorldFrames.ActivationFrame(elapsed); }
                // Past its last frame, and cleared so the subtraction cannot drift on a long save.
                activationBurstTick = -1;
            }
            if (IsSpinningUp) { return RimroomsGateWorldFrames.ChargeFrame(now); }
            return IsOpening ? RimroomsGateWorldFrames.OpenFrame(now) : null;
        }

        /// <summary>Start the one-off activation burst. Called when the ramp reaches full.</summary>
        internal void BeginActivationBurst()
        {
            if (Current.Game != null && Find.TickManager != null)
            { activationBurstTick = Find.TickManager.TicksGame; }
        }

        private int activationBurstTick = -1;
    }

    /// <summary>
    /// Four bounded material caches. A missing or malformed cardinal set disables only that
    /// decoration; ContentFinder is silent and never hands a missing texture to MaterialPool.
    /// </summary>
    internal static class RimroomsGateWorldFrames
    {
        private sealed class FrameSet
        {
            internal readonly int ShortSide;
            internal readonly int LongSide;
            private readonly string stem;
            private bool resolved;
            private Material[] materials;

            internal FrameSet(int shortSide, int longSide, string textureStem)
            {
                ShortSide = shortSide;
                LongSide = longSide;
                stem = textureStem;
            }

            internal Material MaterialAt(Rot4 orientation)
            {
                if (!resolved) { Resolve(); }
                if (materials == null) { return null; }
                // Graphic_Multi uses this same fallback: west reads east with mirrored UVs.
                return materials[orientation == Rot4.West ? 1 : orientation.AsInt];
            }

            private void Resolve()
            {
                resolved = true;
                Texture2D north = ContentFinder<Texture2D>.Get(stem + "_north", false);
                Texture2D east = ContentFinder<Texture2D>.Get(stem + "_east", false);
                Texture2D south = ContentFinder<Texture2D>.Get(stem + "_south", false);
                if (!MatchesAspect(north, LongSide, ShortSide) ||
                    !MatchesAspect(east, ShortSide, LongSide) ||
                    !MatchesAspect(south, LongSide, ShortSide) || ShaderDatabase.Cutout == null)
                { return; }

                Material northMaterial = MaterialPool.MatFrom(north, ShaderDatabase.Cutout, Color.white);
                Material eastMaterial = MaterialPool.MatFrom(east, ShaderDatabase.Cutout, Color.white);
                Material southMaterial = MaterialPool.MatFrom(south, ShaderDatabase.Cutout, Color.white);
                if (northMaterial == null || eastMaterial == null || southMaterial == null ||
                    northMaterial == BaseContent.BadMat || eastMaterial == BaseContent.BadMat ||
                    southMaterial == BaseContent.BadMat)
                { return; }
                materials = new[] { northMaterial, eastMaterial, southMaterial };
            }
        }

        /// <summary>
        /// A numbered overlay sequence drawn on top of the frame: the charge cycle, the activation
        /// burst and the live cycle.
        ///
        /// **ONE SQUARE SHEET PER SEQUENCE, NOT ONE PER FOOTPRINT.** Four footprints times three
        /// facings times eight frames is ninety-six files for a single animation, and every future
        /// footprint multiplies it. These are stretched across whatever run they are drawn over,
        /// which is honest for the content: the frames are edge filaments around a clear aperture,
        /// so a wider run reads as a wider field rather than as a distorted object.
        ///
        /// Resolved once and cached like the frames. A sequence with any frame missing disables
        /// **that sequence only** -- a half-loaded animation that skips a frame looks like a fault
        /// in the game rather than a fault in the package.
        /// </summary>
        private sealed class Sequence
        {
            private readonly string stem;
            private readonly int count;
            private bool resolved;
            private Material[] frames;

            internal Sequence(string textureStem, int frameCount)
            {
                stem = textureStem;
                count = frameCount;
            }

            internal int Count { get { return count; } }

            internal Material At(int index)
            {
                if (!resolved) { Resolve(); }
                if (frames == null || count <= 0) { return null; }
                int wrapped = index % count;
                if (wrapped < 0) { wrapped += count; }
                return frames[wrapped];
            }

            private void Resolve()
            {
                resolved = true;
                if (ShaderDatabase.Transparent == null) { return; }
                var loaded = new Material[count];
                for (int index = 0; index < count; index++)
                {
                    // Two digits, matching the delivered names: _01 through _08.
                    Texture2D texture = ContentFinder<Texture2D>.Get(
                        stem + (index + 1).ToString("00"), false);
                    if (texture == null) { return; }
                    Material material = MaterialPool.MatFrom(texture, ShaderDatabase.Transparent,
                        Color.white);
                    if (material == null || material == BaseContent.BadMat) { return; }
                    loaded[index] = material;
                }
                frames = loaded;
            }
        }

        private static readonly Sequence ChargeSequence =
            new Sequence("Things/Building/Rimrooms/Gates/RR_GateCharge_", 8);
        private static readonly Sequence ActivationSequence =
            new Sequence("Things/Building/Rimrooms/Gates/RR_GateActivation_", 6);
        private static readonly Sequence OpenSequence =
            new Sequence("Things/Building/Rimrooms/Gates/RR_GateOpen_", 8);

        /// <summary>Six ticks a frame: ten frames a second at normal speed.</summary>
        internal const int TicksPerOverlayFrame = 6;

        /// <summary>
        /// The live cycle runs slower than the charge cycle, on purpose.
        ///
        /// A ramp is work in progress and should look busy; an open connection is a steady state and
        /// should look settled. Running both at the same rate made a finished gate look like it was
        /// still straining. Ten ticks a frame is six frames a second against the charge cycle's ten.
        /// </summary>
        internal const int TicksPerOpenFrame = 10;

        internal static int ActivationTicks { get { return ActivationSequence.Count * TicksPerOverlayFrame; } }

        internal static Material ChargeFrame(int tick)
        { return UnityData.IsInMainThread ? ChargeSequence.At(tick / TicksPerOverlayFrame) : null; }

        internal static Material OpenFrame(int tick)
        { return UnityData.IsInMainThread ? OpenSequence.At(tick / TicksPerOpenFrame) : null; }

        /// <summary>The burst, which plays once. Past its last frame it answers null, not frame one.</summary>
        internal static Material ActivationFrame(int elapsedTicks)
        {
            if (!UnityData.IsInMainThread || elapsedTicks < 0) { return null; }
            int index = elapsedTicks / TicksPerOverlayFrame;
            return index >= ActivationSequence.Count ? null : ActivationSequence.At(index);
        }

        private static readonly FrameSet[] Sets =
        {
            new FrameSet(1, 1, "Things/Building/Rimrooms/Gates/RR_GateFrame_1x1"),
            new FrameSet(1, 2, "Things/Building/Rimrooms/Gates/RR_GateFrame_1x2"),
            new FrameSet(1, 3, "Things/Building/Rimrooms/Gates/RR_GateFrame_1x3"),
            new FrameSet(2, 3, "Things/Building/Rimrooms/Gates/RR_GateFrame_2x3"),
        };

        internal static Material MaterialFor(int shortSide, int longSide, Rot4 orientation,
            out bool flip)
        {
            flip = orientation == Rot4.West;
            if (!UnityData.IsInMainThread || orientation.AsInt < 0 || orientation.AsInt > 3)
            { return null; }
            for (int index = 0; index < Sets.Length; index++)
            {
                FrameSet set = Sets[index];
                if (set.ShortSide == shortSide && set.LongSide == longSide)
                { return set.MaterialAt(orientation); }
            }
            return null;
        }

        private static bool MatchesAspect(Texture2D texture, int widthCells, int depthCells)
        {
            return texture != null && texture.width > 0 && texture.height > 0 &&
                texture.width * depthCells == texture.height * widthCells;
        }
    }
}
