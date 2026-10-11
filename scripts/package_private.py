"""Build an owner-only deployment archive with explicit file allowlists.

Never upload the resulting .private-release/ directory to the public repository.
Existing datasets, secrets, model credentials and working files are excluded.
"""

import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    required = ["backend/studio_app.py", "backend/requirements-studio.txt", "frontend/dist/index.html",
                "Dockerfile", "compose.yaml", "entrypoint.sh", ".env.example", ".dockerignore"]
    for name in required:
        if not (ROOT / name).is_file():
            raise SystemExit(f"Missing {name}. Restore the private backend and build the frontend first.")
    destination = ROOT / ".private-release"
    destination.mkdir(exist_ok=True)
    archive = destination / "shuprophet-private-mvp.tar.gz"
    paths = [ROOT / name for name in required if name != "frontend/dist/index.html"]
    paths += sorted((ROOT / "backend/studio").glob("*.py"))
    paths += sorted(path for path in (ROOT / "frontend/dist").rglob("*") if path.is_file())
    paths += [ROOT / "README.md", ROOT / "scripts/start_local.py", ROOT / "docs/DEPLOYMENT.md", ROOT / "docs/API.md", ROOT / "BACKEND_NOTICE.md"]
    manifest = {"private": True, "files": {str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}}
    metadata = destination / "release-manifest.json"
    metadata.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    with tarfile.open(archive, "w:gz") as bundle:
        for path in paths:
            bundle.add(path, arcname=path.relative_to(ROOT).as_posix(), recursive=False)
        bundle.add(metadata, arcname="release-manifest.json")
    print(f"Private release: {archive}")
    print(f"SHA256: {hashlib.sha256(archive.read_bytes()).hexdigest()}")
    print("Keep this archive private. On a Docker server: extract, then docker compose up --build -d")


if __name__ == "__main__":
    main()
