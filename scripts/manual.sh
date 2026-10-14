#!/usr/bin/env bash
# Partie B2. Depuis la racine du projet : bash scripts/manual.sh
set -euo pipefail
cd "$(dirname "$0")/.."
docker version
# Ne pas lancer en meme temps que Compose : memes noms de reseau et volume.
docker network inspect app-network >/dev/null 2>&1 || docker network create app-network
docker volume inspect redis-data >/dev/null 2>&1 || docker volume create redis-data
docker build -t counter-app:1.0 .
docker run -d --name db-service --network app-network \
  -v redis-data:/data redis:8-alpine \
  redis-server --appendonly yes --appendfsync always
for attempt in {1..30}; do
  if docker exec db-service redis-cli ping | grep -q PONG; then break; fi
  sleep 1
done
docker exec db-service redis-cli ping | grep -q PONG
docker run -d --name counter-web --network app-network \
  -p 80:5000 --read-only --tmpfs /tmp --cap-drop ALL \
  --security-opt no-new-privileges counter-app:1.0
printf '\nApplication : http://localhost\n'
printf 'Test manuel : suivre docs/GUIDE_FR.md (Partie 2).\n'
