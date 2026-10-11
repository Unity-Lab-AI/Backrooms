"""Shift+left-click a pixel (eyes.py frame): python .local/qa/shift-click.py x y
Unity's OWN mouse: shift is held for the game window only, never pressed on the owner's keyboard."""
import subprocess, sys
r = subprocess.run([sys.executable, ".local/qa/hands.py", "--shift", sys.argv[1], sys.argv[2]], capture_output=True, text=True)
if r.returncode: sys.exit((r.stdout + r.stderr).strip())
print("shift-clicked")
