import sys, os, runpy, traceback

# Force UTF-8 everywhere
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
os.environ["TERM"] = "dumb"

# Open logs in append mode with UTF-8
sys.stdout = open("stdout.log", "a", encoding="utf-8", buffering=1)
sys.stderr = open("stderr.log", "a", encoding="utf-8", buffering=1)

# Forward arguments
sys.argv = ["winremote"] + sys.argv[1:]

try:
    runpy.run_module("winremote", run_name="__main__")
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    raise
