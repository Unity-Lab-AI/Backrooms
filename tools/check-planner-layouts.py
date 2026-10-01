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
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE = os.path.join(REPO, ".local", "harness", "PlannerProbe")
PROJECT = os.path.join(PROBE, "PlannerProbe.csproj")
BUILT = os.path.join(PROBE, "bin", "Release", "net472", "PlannerProbe.exe")
ASSEMBLY = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "bin", "Release", "net472",
                        "RimroomsAsyncIndustries.dll")

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
    print("OK: every depth produces a layout the validator accepts, back-to-back pairs exist, "
          "and every room can put its landmark beside a reserved route cross.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
