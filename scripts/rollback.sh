#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Variables
IMAGE="${IMAGE:-ghcr.io/org/repo:previous}"
URL_BASE="${URL_BASE:-http://localhost:8000}"

# Stop web, start previous image
export COMPOSE_FILE=docker-compose.yml

docker compose down web || true
# Override image if needed with compose override (not included). Here we pull and rely on :latest pointing to previous.
docker pull "$IMAGE" || true

docker compose up -d db
sleep 2
docker compose up -d web

bash scripts/smoke_test.sh || { echo "Smoke test falló tras rollback"; exit 1; }

echo "Rollback OK"
