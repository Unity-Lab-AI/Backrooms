"""Kept for old shortcuts only: the one engine is stream/admin.py, and this just runs it with the same arguments.
A second copy here drifted from it (different paths, missing model setup), so it is no longer a copy."""
import os, runpy, sys

ENGINE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "stream", "admin.py")
sys.argv[0] = ENGINE
runpy.run_path(ENGINE, run_name="__main__")
