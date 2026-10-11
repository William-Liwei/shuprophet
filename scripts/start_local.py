"""One command local Studio setup/start. Requires the private backend delivery."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description="Start ShuProphet Data Studio locally")
    parser.add_argument("--skip-setup", action="store_true", help="Use the current Python environment and existing frontend build")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    requirements = ROOT / "backend" / "requirements-studio.txt"
    if not requirements.exists():
        parser.error("Private engine delivery missing. Restore the owner-provided backend/ directory first.")
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")
    python = sys.executable
    if not args.skip_setup:
        venv = ROOT / ".venv-studio"
        interpreter = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if not interpreter.exists():
            subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        python = str(interpreter)
        subprocess.run([python, "-m", "pip", "install", "-r", str(requirements)], check=True)
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        if not npm:
            parser.error("Node.js 22+ and npm are required")
        subprocess.run([npm, "ci"], cwd=ROOT / "frontend", check=True)
        subprocess.run([npm, "run", "build"], cwd=ROOT / "frontend", check=True)
    if not (ROOT / "frontend/dist/index.html").exists() and not (ROOT / "dist/index.html").exists():
        parser.error("Frontend build missing. Run without --skip-setup.")
    print(f"ShuProphet Data Studio: http://127.0.0.1:{args.port}", flush=True)
    environment = {**os.environ, "PORT": str(args.port)}
    try:
        subprocess.run([python, "studio_app.py"], cwd=ROOT / "backend", env=environment, check=True)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
