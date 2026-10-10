# -*- coding: utf-8 -*-
"""For each stacked pair, print the orphaned first block and the next few member declarations.

The repair is almost never a deletion. These are doc comments that were separated from the member
they describe when something was inserted between them, so the fix is to reunite the two -- and
that needs to see which of the nearby members the orphan is actually about.
"""
import io
import os
import re
import sys

SEP = chr(92)
NL = chr(10)
DECL = re.compile(r"^\s*(?:\[.*\]\s*)?(?:public|private|internal|protected|static|sealed|const|"
                  r"override|virtual|readonly|partial|class|struct|enum|void|bool|int|float|"
                  r"string|long|double|List|Dictionary|IEnumerable|IntVec3|Thing|Pawn|Map)")


def run(only=None):
    for root, _, names in os.walk("src"):
        parts = root.split(os.sep)
        if "obj" in parts or "bin" in parts:
            continue
        for name in sorted(names):
            if not name.endswith(".cs"):
                continue
            path = os.path.join(root, name).replace(SEP, "/")
            if only and only not in path:
                continue
            lines = io.open(path, encoding="utf-8-sig").read().split(NL)
            for index, line in enumerate(lines):
                if line.strip() != "/// </summary>":
                    continue
                after = index + 1
                while after < len(lines) and lines[after].strip() == "":
                    after += 1
                if after >= len(lines) or lines[after].strip() != "/// <summary>":
                    continue
                start = index
                while start > 0 and lines[start].strip().startswith("///"):
                    start -= 1
                first = [x for x in lines[start + 1:index + 1]]
                end = after
                while end < len(lines) and lines[end].strip().startswith("///"):
                    end += 1
                decls = []
                scan = end
                while scan < len(lines) and len(decls) < 4:
                    if DECL.match(lines[scan]) and "///" not in lines[scan]:
                        decls.append((scan + 1, lines[scan].strip()[:100]))
                    scan += 1
                print("")
                print("=== %s  orphan at lines %d-%d" % (path, start + 2, index + 1))
                for f in first:
                    print("   |%s" % f.strip()[:150])
                print("   NEXT MEMBERS:")
                for ln, d in decls:
                    print("     %5d  %s" % (ln, d))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
