# -*- coding: utf-8 -*-
"""Look at the rendered mod list: is the table whole, and did the search and sort arrive."""
import io
import os
import re
import sys

PATH = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "probeout",
                    "mods-list.html")


def main():
    if not os.path.isfile(PATH):
        print("REFUSED: no rendered page at %s" % PATH)
        return 1
    html = io.open(PATH, encoding="utf-8", errors="replace").read()
    bodies = re.findall(r"<tbody>(.*?)</tbody>", html, re.S)
    print("tables with a tbody : %d" % len(bodies))
    for body in bodies:
        print("   rows             : %d" % len(re.findall(r"<tr>", body)))
    print("thead present       : %s" % ("<thead>" in html))
    print("search and sort     : %s" % ("Search this table" in html))
    print("rows are not escaped: %s" % ("&lt;tr" not in html))
    return 0


if __name__ == "__main__":
    sys.exit(main())
