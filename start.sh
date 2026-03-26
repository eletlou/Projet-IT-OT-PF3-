#!/usr/bin/env bash

set -e

if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
else
    echo "Docker Compose n'est pas disponible sur cette machine."
    exit 1
fi

"${COMPOSE_CMD[@]}" up --build -d

echo
echo "Application demarree."
echo "Flask   : http://localhost:5000"
echo "Adminer : http://localhost:8081"

