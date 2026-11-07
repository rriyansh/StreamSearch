#!/usr/bin/env bash
set -euo pipefail

echo "==> Checking prerequisites"
command -v docker >/dev/null || { echo "docker is required"; exit 1; }
command -v docker compose >/dev/null 2>&1 || command -v docker-compose >/dev/null || { echo "docker compose is required"; exit 1; }

if [[ ! -f .env ]]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
fi

mkdir -p data/videos data/frames qdrant_storage

echo "==> Building images"
docker compose build

echo "==> Starting services"
docker compose up -d

echo "==> Waiting for API readiness"
for i in {1..60}; do
  if curl -sf http://localhost:8000/health/live >/dev/null; then
    echo "API is live"
    break
  fi
  sleep 2
done

echo "StreamSearch is up:"
echo "  API:  http://localhost:8000/docs"
echo "  UI:   http://localhost:8080"
