# -*- coding: utf-8 -*-
"""The last suite: `write_verified(path, original, "restore")` takes a third argument."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-rest.py")

OLD = u'''    write_verified(path, original.replace(old, new, 1), "plant into")
    code = subprocess.call([sys.executable, ".local/register/proof-areas-and-debrief.py"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    write_verified(path, original, "restore")
'''

NEW = u'''    write_verified(path, original.replace(old, new, 1), "plant into")
    try:
        code = subprocess.call([sys.executable, ".local/register/proof-areas-and-debrief.py"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what makes a destructive
        # instrument safe, and it was the one line not protected: a leaked devnull handle raised
        # OSError mid-run twice and left planted source on disk both times.
        write_verified(path, original, "restore")
'''

text = io.open(SUITE, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("plant-rest.py guarded")
