# -*- coding: utf-8 -*-
"""List every member carrying two consecutive <summary> blocks, with both halves and the member.

Two <summary> elements on one member is malformed XML documentation: tooling keeps one and
discards the other, so half of every pair is invisible to the reader who needs it and visible to
the reader who should not trust it. This found 29, and one of them documents a different field
than the one it sits on.
"""
import io
import os

SEP = chr(92)
NL = chr(10)


def pairs():
    found = []
    for root, _, names in os.walk("src"):
        parts = root.split(os.sep)
        if "obj" in parts or "bin" in parts:
            continue
        for name in sorted(names):
            if not name.endswith(".cs"):
                continue
            path = os.path.join(root, name)
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
                first = [x.strip()[3:].strip() for x in lines[start + 1:index]
                         if x.strip().startswith("///")]
                end = after
                while end < len(lines) and lines[end].strip().startswith("///"):
                    end += 1
                second = [x.strip()[3:].strip() for x in lines[after + 1:end]
                          if x.strip().startswith("///")]
                decl = lines[end].strip() if end < len(lines) else "?"
                found.append((path.replace(SEP, "/"), index + 1,
                              " ".join(first), " ".join(second), decl))
    return found


if __name__ == "__main__":
    all_pairs = pairs()
    print("TOTAL STACKED: %d" % len(all_pairs))
    for path, line, first, second, decl in all_pairs:
        print("")
        print("--- %s:%d" % (path, line))
        print("  MEMBER : %s" % decl[:95])
        print("  FIRST  : %s" % first[:170])
        print("  SECOND : %s" % second[:120])
