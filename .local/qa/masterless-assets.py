"""Which shipped asset entries have no master under assets/source/, and which do.

One-off read-only inspection written because `build-asset-page.py` prints the master count as a
total and `docs/NOW.md` published a different total still. A number copied between documents is
how both of them came to be wrong, so this asks the generator itself rather than either page.
"""
import importlib.util
import os
import sys

# `.local/qa/`, two levels down -- the exact depth mistake `archive-finished-todo.py` records
# having made when it moved, which a stale join resolves to somebody else's files.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

spec = importlib.util.spec_from_file_location(
    "build_asset_page", os.path.join(REPO, "tools", "build-asset-page.py"))
module = importlib.util.module_from_spec(spec)
sys.modules["build_asset_page"] = module
spec.loader.exec_module(module)

entries = module.build()

drawings = [e for e in entries if not e["sound"]]
sounds = [e for e in entries if e["sound"]]
print("entries        : %d  (%d drawings, %d cues)" % (len(entries), len(drawings), len(sounds)))
print("with a master  : %d" % len([e for e in entries if e["master"]]))
print("")
print("NO MASTER:")
for entry in sorted(entries, key=lambda e: e["stem"]):
    if not entry["master"]:
        print("  %-42s %s" % (entry["stem"], entry["relative"]))
