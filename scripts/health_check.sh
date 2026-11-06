#!/usr/bin/env bash
set -euo pipefail

API_HOST="${API_HOST:-localhost}"
API_PORT="${API_PORT:-8000}"

echo "==> Health check: http://${API_HOST}:${API_PORT}/health"

if curl -sf "http://${API_HOST}:${API_PORT}/health" > /dev/null; then
  echo "API is healthy"
  exit 0
else
  echo "API health check failed" >&2
  exit 1
fi
