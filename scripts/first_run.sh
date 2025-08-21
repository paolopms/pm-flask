#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

export COMPOSE_FILE=docker-compose.yml

docker compose up -d db
sleep 3
docker compose run --rm web flask db upgrade
docker compose run --rm web flask seed
docker compose up -d web

echo "Aplicación desplegada. Revisa /health y /api/docs"
