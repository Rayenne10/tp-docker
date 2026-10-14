# TP1 DevOps - Visit-Counter

Rayenne Abid - INSAT RT5 - Encadrante : Saloua BEN YAHIA

Application Flask/Gunicorn, Redis persistant, 3 replicas web derriere Nginx,
Dockerfile non-root, tests unitaires et pipeline Jenkins vers Docker Hub.
Projet prepare a partir du ZIP fourni ; rapport PDF fourni en complement.

## Demarrage rapide (Docker Desktop + Compose v2)

Dans PowerShell, WSL, Linux ou macOS, ouvrir un terminal dans ce dossier :

```sh
docker version
docker compose version
cp .env.example .env
# Changer HOST_PORT=8080 dans .env si le port 80 est occupe.
docker compose config
docker compose up -d --build --scale web=3
```

Ouvrir http://localhost (ou http://localhost:8080 si HOST_PORT=8080).
Chaque actualisation incremente le compteur partage et affiche le conteneur.
Les sondes /health ne modifient pas le compteur.

## Verification

```sh
python -m venv .venv
# Windows PowerShell : .venv\Scripts\Activate.ps1
# Linux / macOS / WSL : source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest
python scripts/verify_docker.py
```

Le dernier script supprime puis recree uniquement Redis du TP pour tester la
persistance. Fermer le navigateur pendant ce test pour eviter des visites
concurrentes. Il exige exactement 3 replicas et enregistre les preuves textuelles
dans evidence/. Les commandes Docker n'ont pas pu etre executees dans
l'environnement de preparation, ou Docker est absent. 14 tests unitaires passes.

## Livrables et suite

- `docs/GUIDE_FR.md` : toutes les commandes des parties 0 a 4 et Jenkins.
- `docs/PART_A_DOCKER_TUTORIAL_EN.md` : support anglais et exercices corriges.
- `Dockerfile`, `docker-compose.yml`, `.env`, `nginx/` : conteneurisation.
- `Jenkinsfile`, `tests/` : CI/CD et tests.
- `scripts/` : deploiement manuel, publication et validation Docker.
- `docs/build_report.py` : regenerer le PDF avec tes captures et ton lien Hub.
- `evidence/README.md` : preuves a produire avant remise.

La partie A notee doit etre realisee selon les consignes du tutoriel enseignant.
Son lien Drive n'etait pas accessible ici ; le support anglais fourni est un
complement original, pas la preuve d'une validation du tutoriel note.

A completer sur ta machine : execution Docker, captures demandees, creation du
depot Docker Hub public et push, configuration Jenkins et webhook, puis
regeneration du rapport avec les preuves reelles. Aucun compte, lien public,
resultat de build Docker ou capture d'un autre groupe n'est presente comme tien.
