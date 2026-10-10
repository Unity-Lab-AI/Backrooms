# -*- coding: utf-8 -*-
"""How many numeric caps in the source carry no stated reason?

Owner, verbatim: *"so dont limit yourself"* -- where a bound exists it has to be a bound the
geometry imposes and is **stated**, not one chosen for convenience. `MaximumUndirectedEdgesPerRoom`
is the worked example: it was 2 *"because a slot has four neighbours"*, and when bent corridors
made eight neighbours reachable the constant was the thing refusing them.

A cap with no stated reason is the one nobody can tell from a convenience. This counts them before
deciding whether a rule is affordable.
"""
import io
import os
import re

NL = chr(10)
SRC = os.path.join("src", "RimroomsAsyncIndustries")
CAP = re.compile(
    r"^\s*(?:internal|public|private|protected)\s+(?:static\s+)?(?:readonly\s+)?const\s+"
    r"(?:int|float|long|double)\s+((?:Max|Min|Maximum|Minimum|Cap|Limit)\w*|\w*(?:Cap|Limit|Budget|Ceiling|Floor|Rarity))"
    r"\s*=")


def main():
    stated = 0
    bare = []
    for root, _, names in os.walk(SRC):
        parts = root.split(os.sep)
        if "obj" in parts or "bin" in parts:
            continue
        for name in sorted(names):
            if not name.endswith(".cs"):
                continue
            path = os.path.join(root, name)
            lines = io.open(path, encoding="utf-8-sig").read().split(NL)
            for index, line in enumerate(lines):
                if not CAP.match(line):
                    continue
                above = index - 1
                while above >= 0 and lines[above].strip() == "":
                    above -= 1
                documented = above >= 0 and (
                    lines[above].strip().endswith("</summary>")
                    or lines[above].strip().startswith("///")
                    or lines[above].strip().startswith("//"))
                if documented:
                    stated += 1
                else:
                    bare.append("%s:%d  %s" % (
                        path.replace(os.sep, "/"), index + 1, line.strip()[:84]))

    print("numeric caps found      : %d" % (stated + len(bare)))
    print("with a stated reason    : %d" % stated)
    print("with NO stated reason   : %d" % len(bare))
    print("")
    for entry in bare:
        print("  " + entry)


if __name__ == "__main__":
    main()
