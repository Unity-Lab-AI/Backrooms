"""Click a work-tab row slowly: python .local/qa/work-row.py <rowY> <x:clicks> ..."""
import subprocess, sys, time
y = sys.argv[1]
for spec in sys.argv[2:]:
    x, n = spec.split(":")
    for _ in range(int(n)):
        subprocess.run([sys.executable, ".local/qa/hands.py", x, y], capture_output=True)
        time.sleep(0.45)
