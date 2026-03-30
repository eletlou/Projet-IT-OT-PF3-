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

if "${COMPOSE_CMD[@]}" ps -a --services 2>/dev/null | grep -q "^web$"; then
    "${COMPOSE_CMD[@]}" start

    STATUS_MESSAGE="Application relancee sans recreer les conteneurs."
else
    "${COMPOSE_CMD[@]}" up --build -d
    STATUS_MESSAGE="Application demarree pour la premiere fois."
fi

echo
echo "${STATUS_MESSAGE}"
echo "Flask   : http://localhost:5005"
