"""Find holes in wall runs: cells flanked by wall-ish cells on a line that are not walls themselves.

    python .local/qa/find-gaps.py x0 z0 x1 z1

Wall-ish = a built wall/door/fence, or a blueprint or frame of one. A gap is a non-wall-ish cell
whose two neighbours along x, or along z, are both wall-ish, or a run of up to three such cells
closed at both ends. Prints each gap cell, what is on it, and the run it belongs to.
"""
import json, subprocess, sys

BR = ".local/qa/bridge.py"
WALLISH = ("Wall", "Door", "Autodoor", "Fence", "Embrasure", "GlassWall", "Gate")


def call(tool, args):
    out = subprocess.run([sys.executable, BR, "call", tool, json.dumps(args)],
                         capture_output=True, text=True).stdout
    return json.loads(out[out.find("{"):]) if "{" in out else {}


def is_wallish(cell):
    names = list(cell.get("solidThingDefs") or []) + list(cell.get("blueprintBuildDefs") or []) + \
        list(cell.get("frameBuildDefs") or [])
    for t in cell.get("things") or []:
        names.append(t.get("defName") or "")
    return any(any(k in n for k in WALLISH) for n in names)


def main():
    x0, z0, x1, z1 = map(int, sys.argv[1:5])
    grid, rock = {}, {}
    for cz in range(z0, z1 + 1, 6):
        for cx in range(x0, x1 + 1, 6):
            r = call("rimworld/get_cells_info", {"x": cx, "z": cz, "width": min(6, x1 - cx + 1),
                                                   "height": min(6, z1 - cz + 1)})
            for c in r.get("cells") or []:
                grid[(c["x"], c["z"])] = is_wallish(c)
                rock[(c["x"], c["z"])] = (not c.get("walkable")) and not grid[(c["x"], c["z"])]
    solid = lambda p: grid.get(p, False) or rock.get(p, False)
    gaps = {}
    for (x, z), w in grid.items():
        if w or rock.get((x, z)):
            continue
        for dx, dz in ((1, 0), (0, 1)):
            for span in (1, 2, 3):
                # does a run of `span` open cells starting at or before this one close at both ends?
                for start in range(span):
                    cells = [(x + (i - start) * dx, z + (i - start) * dz) for i in range(span)]
                    if any(solid(c) for c in cells):
                        continue
                    a = (cells[0][0] - dx, cells[0][1] - dz)
                    b = (cells[-1][0] + dx, cells[-1][1] + dz)
                    if grid.get(a) and grid.get(b):
                        # and the wall continues beyond both ends, so it is a run, not a corner
                        a2 = (a[0] - dx, a[1] - dz)
                        b2 = (b[0] + dx, b[1] + dz)
                        if solid(a2) and solid(b2):
                            gaps[(x, z)] = "x" if dx else "z"
    for p in sorted(gaps, key=lambda q: (q[1], q[0])):
        print(p, gaps[p])
    print("gaps:", len(gaps))


if __name__ == "__main__":
    main()
