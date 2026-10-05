# -*- coding: utf-8 -*-
"""Run the room planner for real, at every depth, and require a layout the validator accepts.

Why this checker exists
-----------------------
**Every other check in this repository reads source text, and the defect that cost the owner the
tenth launch was invisible to all of them.**

`DestinationService.ValidateRooms` refuses a room wider than `MaxRoomSpan`, and that property
recomputed the span of a room filling a single slot -- 34 cells at depth 1. The planner's grand
hall spans two slots and is 80. So every candidate layout was refused, `TrySelect` returned false,
and `SoloGroupOpening` stopped at step 2: no coordinate, so the door was never marked and no edge
was ever registered.

The owner's report was *"this run through the door is not blue and i dont see the backrooms is
there and cant portal to it"*. The log was clean. Thirteen checkers, forty-five proofs and five
hundred and fifty planted faults all passed, because **two numbers in two files disagreed and no
amount of reading either file can see that.** It is the same shape as the light count that stopped
every coordinate generating for thirty-nine checkpoints.

The planner is pure -- no map, no world, no defs, no global random -- so the question is
answerable here. This builds the probe against the compiled assembly and runs it over two hundred
seeds at every depth band, demanding:

  * every depth produces a layout `ValidateRooms` accepts,
  * back-to-back pairs actually exist, and
  * **every room can stand its landmark beside its own clear route cross.**

The second one matters as much as the first. A plant that moved a pushed room one cell back made
it overlap its host, the revert guard put it back, and the feature was **switched off with every
proof still passing.** Absence is the thing this checker is for.

The third was added at 0.12.71-dev, after `RR_Generation_UnreachableRequiredCell` stopped the
owner's solo/group start -- *"i ended up in the world map with no connection to the back rooms"*.
A clue landmark needs a standable, reachable cell orthogonally beside it; nothing reserved one;
`DressRoom` places fixtures until one will not fit, so the last cells it takes are exactly the
no-margin cells flush against the landmark. `RoomContentBuilder.RouteTrunk` now offers the
landmark a cell of the reserved cross instead, **and falls back to the old behaviour when a room
has none** -- so the number that matters is how often the guarantee is available rather than how
often the fallback saves it. It was zero rooms short across all seven bands when measured, which
is why anything above zero fails here. The `fellback` column exists for the same reason: it once
read `refused 0/200` while the net was catching every seed.

It never skips
--------------
A check that passes when it could not run is worse than no check. A missing `dotnet`, a missing
RimWorld install or a missing assembly is a failure here, not a skip.
"""
import io
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE = os.path.join(REPO, ".local", "harness", "PlannerProbe")
PROJECT = os.path.join(PROBE, "PlannerProbe.csproj")
BUILT = os.path.join(PROBE, "bin", "Release", "net472", "PlannerProbe.exe")
ASSEMBLY = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "bin", "Release", "net472",
                        "RimroomsAsyncIndustries.dll")
MOD_PROJECT = os.path.join(REPO, "src", "RimroomsAsyncIndustries",
                           "RimroomsAsyncIndustries.csproj")

DEFAULT_GAME = r"C:\Program Files (x86)\Steam\steamapps\common\Rimworld"


def fail(message):
    print("FAILED: %s" % message)
    raise SystemExit(1)


def game_path():
    path = os.environ.get("RIMWORLD_PATH") or DEFAULT_GAME
    if not os.path.isfile(os.path.join(path, "RimWorldWin64_Data", "Managed",
                                       "Assembly-CSharp.dll")):
        fail("the installed RimWorld managed assembly is not at %r. Set RIMWORLD_PATH." % path)
    return path


def run(argv, where):
    process = subprocess.Popen(argv, cwd=where, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    output = process.communicate()[0].decode("utf-8", "replace")
    return process.returncode, output


def main():
    if not os.path.isfile(PROJECT):
        fail("the probe project is missing: %s" % PROJECT)
    if not os.path.isfile(ASSEMBLY):
        fail("the mod assembly is not built. Run tools/build.ps1 first.")

    environment = dict(os.environ)
    environment["DOTNET_CLI_HOME"] = os.path.join(REPO, ".local", "dotnet")
    environment["NUGET_PACKAGES"] = os.path.join(REPO, ".local", "nuget")
    environment["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    os.environ.update(environment)

    # **THE MOD IS REBUILT FIRST, AND WITHOUT THIS THE PROBE MEASURES A STALE ASSEMBLY.**
    #
    # `PlannerProbe.csproj` binds the mod with a `HintPath` to
    # `src/.../bin/Release/net472/RimroomsAsyncIndustries.dll` rather than a `ProjectReference`,
    # so building the probe does **not** build the planner it is about to interrogate. It loads
    # whatever DLL happens to be sitting there.
    #
    # Found by planting a real regression -- the grand-room count cut back to one -- and watching
    # this check report the old numbers and pass. **A layout verdict about code that is no longer
    # the source is worse than no verdict**, because the whole purpose of this probe is to answer
    # at the desk what would otherwise need a launch.
    code, output = run(["dotnet", "build", MOD_PROJECT, "-c", "Release",
                        "-p:RimWorldPath=%s" % game_path(), "--verbosity", "quiet"], REPO)
    if code != 0:
        print(output)
        fail("the mod assembly did not build, so the probe would have measured a stale one.")

    code, output = run(["dotnet", "build", PROJECT, "-c", "Release",
                        "-p:RimWorldPath=%s" % game_path(), "--verbosity", "quiet"], REPO)
    if code != 0:
        print(output)
        fail("the probe did not compile against the built assembly.")
    if not os.path.isfile(BUILT):
        fail("the probe compiled but produced no executable.")

    code, output = run([BUILT], os.path.dirname(BUILT))
    print(output.rstrip())
    if code != 0:
        fail("the planner did not produce an acceptable layout at every depth.")
    if "PROBE HELD" not in output:
        fail("the probe exited zero without holding, which means it did not run its claims.")

    # **"GRAND ROOMS" IS PLURAL, AND A COUNT NOBODY ASSERTS IS A FEATURE NOBODY HAS.** Owner,
    # 2026-10-03: *"starts locations of main grand rooms can be anywhere on the map and lead
    # anywhere in multiple differetn varied ways"*. The probe reports `grand <average>/<target>`
    # per depth; this is what makes the number mean something.
    #
    # Asserted as a floor against the target rather than as equality. The walk only *asks* for a
    # grand room -- it still needs a free slot to extend into and the resulting two-slot room
    # still has to pass the same link checks as any other, so a seed is entitled to come up short.
    # Demanding exactness would be a rule that fails on a legal layout. A floor of the target
    # minus a quarter of a room still catches the thing worth catching: the feature silently
    # stopping.
    grand = re.findall(r"maze\s+depth\s+(\d+).*?grand\s+([0-9.]+)/(\d+)\s+ways\s+(-?\d+)", output)
    if not grand:
        fail("the probe printed no grand-room count, so the plural claim is unmeasured. "
             "A check that cannot see the feature is worse than no check.")
    for depth, average, target, ways in grand:
        if float(average) < int(target) - 0.25:
            fail("depth %s averaged %s grand rooms against a target of %s. The level is supposed "
                 "to contain several large spaces, not one arrival hall and a maze."
                 % (depth, average, target))
    # **AND A GRAND ROOM HAS TO LEAD SOMEWHERE, more than one way.** Owner: *"lead anywhere
    # in multiple differetn varied ways"*. The probe reports the WORST grand room across every
    # seed, not the average, because an average hides the one that is a dead end -- and a grand
    # space with a single door is a cul-de-sac wearing a hall's clothes.
    for depth, _, _, ways in grand:
        if int(ways) < 2:
            fail("depth %s has a grand room with %s way(s) out. A grand space is supposed to lead "
                 "anywhere in several varied ways, not be a dead end." % (depth, ways))

    shallow = [(d, a) for d, a, _, _ in grand if int(d) <= 1]
    for depth, average in shallow:
        if float(average) < 2.0:
            fail("depth %s averaged %s grand rooms. \"Grand rooms\" is plural and the shallow "
                 "band is the one that is supposed to read as a few huge spaces."
                 % (depth, average))

    print("OK: every depth produces a layout the validator accepts, back-to-back pairs exist, "
          "every room can put its landmark beside a reserved route cross, and every depth meets "
          "its grand-room count (%s)."
          % ", ".join("d%s %s/%s ways>=%s" % (d, a, t, w) for d, a, t, w in grand))
    return 0


if __name__ == "__main__":
    sys.exit(main())
