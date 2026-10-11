"""Linux server deployment: configure once, retain secrets across releases.

Requires Python 3.9+, Docker Engine and Compose v2. No third-party Python modules.
Secrets live outside the release directory and never enter the Docker build.
"""

import argparse
import getpass
import os
from pathlib import Path
import secrets
import subprocess
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "shuprophet-studio"


def atomic_write(path, value, mode):
    temporary = path.with_name(path.name + ".new")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(value)
        temporary.chmod(mode)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def configure(directory):
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    path = directory / "server.env"
    existing = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                name, value = line.split("=", 1)
                existing[name] = value.strip("'")
    print("Configure once. Press Enter to keep existing values; keys are never echoed.")
    key_path = directory / "llm_api_key"
    key = getpass.getpass("Model API key (Enter keeps existing, or disables chat on first setup): ").strip()
    if any(char in key for char in "\r\n\0"):
        raise ValueError("API key must be a single line.")
    base = existing.get("OPENAI_API_BASE", "https://api.moonshot.cn/v1")
    base = input(f"Model API base [{base}]: ").strip() or base
    parsed = urlparse(base)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Use a base URL without credentials, query strings or fragments.")
    model = existing.get("OPENAI_MODEL", "kimi-k2.6")
    model = input(f"Model name [{model}]: ").strip() or model
    token = existing.get("STUDIO_ACCESS_TOKEN") or secrets.token_urlsafe(32)
    values = {"APP_PORT": existing.get("APP_PORT", "8080"), "BIND_HOST": existing.get("BIND_HOST", "127.0.0.1"),
              "WEB_CONCURRENCY": existing.get("WEB_CONCURRENCY", "2"), "STUDIO_ACCESS_TOKEN": token,
              "OPENAI_API_BASE": base, "OPENAI_MODEL": model}
    if any(any(char in value for char in "\r\n\0'") for value in values.values()):
        raise ValueError("Configuration contains an unsupported character.")
    # Compose file-backed secrets preserve host modes. The parent directory is
    # private (0700); only this file is mounted, readable by container UID 10001.
    if key or not key_path.exists():
        atomic_write(key_path, key, 0o444)
    atomic_write(path, "".join(f"{name}='{value}'\n" for name, value in values.items()), 0o600)
    print(f"Saved server configuration in {directory}. No credentials were printed.")
    print("Read STUDIO_ACCESS_TOKEN from server.env privately and enter it in the site's connection settings.")


def deployment_command(directory):
    return ["docker", "compose", "--project-name", PROJECT, "--project-directory", str(ROOT),
            "--env-file", str(directory / "server.env"), "-f", str(ROOT / "compose.yaml"),
            "-f", str(ROOT / "compose.secrets.yaml")]


def deployment_environment(directory):
    environment = os.environ.copy()
    # Explicit server config wins over a stale key or setting in the caller's shell.
    for name in ("OPENAI_API_KEY", "OPENAI_API_BASE", "OPENAI_MODEL", "STUDIO_ACCESS_TOKEN",
                 "APP_PORT", "BIND_HOST", "WEB_CONCURRENCY", "COMPOSE_FILE", "COMPOSE_PROJECT_NAME"):
        environment.pop(name, None)
    environment["SHU_SECRET_DIR"] = str(directory)
    environment["COMPOSE_DISABLE_ENV_FILE"] = "1"
    return environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, default=Path.home() / ".config/shuprophet")
    parser.add_argument("--configure", action="store_true", help="Update saved configuration before deploying")
    parser.add_argument("--status", action="store_true", help="Show container status without deploying")
    args = parser.parse_args()
    if os.name != "posix":
        raise SystemExit("Run this on a Linux Docker server. For local preview, use scripts/start_local.py.")
    directory = args.config_dir.expanduser().resolve()
    if directory == ROOT or ROOT in directory.parents:
        raise SystemExit("Keep the configuration directory outside the release directory.")
    for relative in ("backend/studio_app.py", "frontend/dist/index.html", "compose.secrets.yaml"):
        if not (ROOT / relative).is_file():
            raise SystemExit("Use the complete private release (backend and built frontend required).")
    subprocess.run(["docker", "compose", "version"], check=True, stdout=subprocess.DEVNULL)
    ready = all((directory / name).is_file() for name in ("server.env", "llm_api_key"))
    if args.configure or not ready:
        if args.status or not sys.stdin.isatty():
            raise SystemExit("Initialize once in an interactive terminal: python3 scripts/deploy.py --configure")
        configure(directory)
    directory.chmod(0o700)
    (directory / "server.env").chmod(0o600)
    (directory / "llm_api_key").chmod(0o444)
    command = deployment_command(directory)
    environment = deployment_environment(directory)
    if not args.status:
        options = ["up", "--build", "-d", "--wait", "--wait-timeout", "180"]
        # Replaced secret files have new inodes: remount them after key rotation.
        if args.configure:
            options.append("--force-recreate")
        subprocess.run(command + options, check=True, env=environment)
    subprocess.run(command + ["ps"], check=True, env=environment)
    print("Model credentials stay on this server; deployments retain the named data volume.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError):
        raise SystemExit("Deployment failed. Check Docker availability and server configuration; credentials were not printed.") from None
