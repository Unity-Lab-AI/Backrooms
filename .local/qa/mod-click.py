"""Click a pixel N times holding a modifier: python .local/qa/mod-click.py ctrl|shift x y [n]
Unity's OWN mouse: the modifier is held for the game window only (hands.py --ctrl/--shift), never pressed
on the owner's keyboard."""
import subprocess, sys, time
mod = {"ctrl": "--ctrl", "shift": "--shift"}[sys.argv[1]]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 1
for _ in range(n):
    r = subprocess.run([sys.executable, ".local/qa/hands.py", mod, sys.argv[2], sys.argv[3]], capture_output=True, text=True)
    if r.returncode: sys.exit((r.stdout + r.stderr).strip())
    time.sleep(0.15)
print("clicked", n)
