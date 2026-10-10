"""Write the post-move docs/TODO.md to .local/qa/TODO.kept.md for inspection.

Writes nowhere near docs/. Lets the result be read before anything is committed
to the real ledger.
"""

import importlib.util
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "mover", os.path.join(HERE, "archive-finished-todo.py")
)
mover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mover)

lines = mover.read_lines(mover.TODO)
labels, whole, groups_moved, blocks, untouched = mover.plan(lines)
kept, moved = mover.assert_lossless(lines, labels)

out = os.path.join(HERE, "TODO.kept.md")
with io.open(out, "w", encoding="utf-8", newline="") as handle:
    handle.write("\n".join(kept))

print("wrote", out, len(kept), "lines")
