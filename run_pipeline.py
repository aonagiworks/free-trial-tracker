#!/usr/bin/env python3
import subprocess, os, sys

REPO = "/home/ec2-user/free-trial-tracker"

def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True)

r = sh("python3 build_data.py")
if r.returncode != 0:
    print("BUILD FAIL: " + r.stdout + r.stderr)
    sys.exit(1)

sh("git add data.json index.html build_data.py run_pipeline.py")
staged = sh("git diff --cached --name-only").stdout.strip()
if not staged:
    sys.exit(0)  # silent, nothing changed

sh('git commit -m "auto: refresh free trial data"')
p = sh("git push origin gh-pages")
if p.returncode != 0:
    print("PUSH FAIL: " + p.stdout + p.stderr)
    sys.exit(1)
print("free-trial-tracker updated: " + r.stdout.strip())
