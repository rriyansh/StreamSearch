#!/usr/bin/env bash
set -euo pipefail

echo "==> Setting up StreamSearch environment"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "==> Setup complete"
