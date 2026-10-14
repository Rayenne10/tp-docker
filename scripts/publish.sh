#!/usr/bin/env bash
# Le login est interactif ; aucun secret ne figure dans le depot.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${DOCKERHUB_USERNAME:?Definir DOCKERHUB_USERNAME avec votre compte reel}"
TAG="${IMAGE_TAG:-1.0}"
if [[ "$DOCKERHUB_USERNAME" == "CHANGE_ME" ]]; then
  echo 'Remplacer CHANGE_ME par votre compte Docker Hub.' >&2
  exit 1
fi
docker login -u "$DOCKERHUB_USERNAME"
docker build -t counter-app:1.0 .
docker tag counter-app:1.0 "$DOCKERHUB_USERNAME/counter-app:$TAG"
docker tag counter-app:1.0 "$DOCKERHUB_USERNAME/counter-app:latest"
docker push "$DOCKERHUB_USERNAME/counter-app:$TAG"
docker push "$DOCKERHUB_USERNAME/counter-app:latest"
printf 'Lien public (si le depot est public) : https://hub.docker.com/r/%s/counter-app\n' "$DOCKERHUB_USERNAME"
