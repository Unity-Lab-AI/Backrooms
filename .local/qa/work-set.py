"""Set work cells by clicking N times each, slowly: python .local/qa/work-set.py ROW_Y "x:n x:n ..." """
import subprocess, sys, time
y = sys.argv[1]
for spec in sys.argv[2].split():
    x, n = spec.split(":")
    for _ in range(int(n)):
        subprocess.run([sys.executable, ".local/qa/hands.py", x, y], capture_output=True); time.sleep(0.25)
print("done")
