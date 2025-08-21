#!/usr/bin/env bash
set -euo pipefail
URL_BASE="${URL_BASE:-http://localhost:8000}"

curl -fsS "$URL_BASE/health" >/dev/null
curl -fsS "$URL_BASE/api/docs" >/dev/null

echo "Smoke test OK"
