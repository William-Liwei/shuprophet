#!/bin/sh
set -eu

echo "=== 启动应用 ==="
workers="${WEB_CONCURRENCY:-1}"
port="${PORT:-8080}"

exec gunicorn -w "$workers" --threads 4 -b "0.0.0.0:$port" --timeout 300 --preload app:app --chdir backend
