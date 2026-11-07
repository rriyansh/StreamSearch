#!/usr/bin/env bash
set -euo pipefail

status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ready || true)
if [[ "$status" == "200" ]]; then
  echo "OK"
  exit 0
fi
echo "UNHEALTHY (status=$status)"
exit 1
