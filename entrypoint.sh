#!/bin/sh
set -eu

case "${1:-web}" in
  web)
    exec gunicorn --workers "${WEB_CONCURRENCY:-2}" --threads 2 \
      --bind "0.0.0.0:${PORT:-8080}" --timeout 120 \
      --access-logfile - --error-logfile - 'studio_app:create_app()'
    ;;
  worker)
    exec python -m studio.worker
    ;;
  *)
    exec "$@"
    ;;
esac
