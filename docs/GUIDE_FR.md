# Guide complet - TP1 Docker et pipeline Jenkins

## 0. Environnement

Windows : installer Docker Desktop avec le backend WSL 2, demarrer Docker et
utiliser les conteneurs Linux. Linux : Docker Engine et plugin Compose v2.
Git Bash/WSL est necessaire pour les scripts .sh ; les commandes Docker et le
script Python fonctionnent aussi dans PowerShell. Extraire le dossier fourni.

```sh
cd TP_Docker_ABID_RAYENNE
docker version
docker compose version
docker login
```

Le dossier respecte le format TP_Docker_NOM_PRENOM. Le fichier `.env` fourni ne
contient aucun mot de passe. Il definit HOST_PORT=80, APP_PORT=5000 et
REDIS_PORT=6379. Si 80 est occupe, changer HOST_PORT en 8080 (URL correspondante).

## 1. Dockerfile et isolation

```sh
docker build -t counter-app:1.0 .
docker images counter-app:1.0
docker run --rm --entrypoint id counter-app:1.0
```

Python 3.11 Alpine fournit une base compacte pour les dependances Python
utilisees. La taille exacte depend du build et de l'architecture : la mesurer,
ne pas inventer un nombre. `pip --no-cache-dir` n'embarque pas le cache pip.
Copier requirements.txt avant app.py permet de reutiliser la couche des
paquets quand seul le code change. Aucun compilateur n'est ajoute.
`.dockerignore` exclut les tests, les preuves et l'environnement virtuel.
Le code reste possede par root mais Gunicorn tourne avec appuser (UID 1000).
Cela limite les privileges dans le conteneur ; ce n'est pas une garantie absolue
contre une faille du noyau. Gunicorn remplace le serveur de developpement Flask.

RUN execute une commande pendant docker build et enregistre ses modifications
au systeme de fichiers dans une couche. CMD definit la commande par defaut au
lancement du conteneur. CMD n'execute rien pendant le build et peut etre remplace
par la commande de docker run. EXPOSE documente le port, sans le publier.

## 2. Reseau et volume - deploiement manuel

Ne pas lancer simultanement le deploiement manuel et Compose : ils utilisent
les memes noms app-network, redis-data et db-service.

```sh
docker network create app-network
docker volume create redis-data
docker run -d --name db-service --network app-network -v redis-data:/data redis:8-alpine redis-server --appendonly yes --appendfsync always
docker exec db-service redis-cli ping
docker run -d --name counter-web --network app-network -p 80:5000 --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges counter-app:1.0
docker network inspect app-network
```

Ouvrir http://localhost et actualiser quelques fois. Redis n'est pas expose a
l'hote. Le DNS du bridge resout db-service. INCR est atomique, donc les replicas
partagent un compteur coherent. Le volume stocke les fichiers Redis a /data.
Un volume seul ne suffit pas : Redis doit ecrire les changements sur disque.
AOF avec appendfsync always favorise la durabilite au prix de performances
inferieures a everysec ; utile pour ce TP qui impose docker rm -f.

Test : fermer le navigateur pendant la comparaison, puis executer :

```sh
docker exec db-service redis-cli GET hits
docker rm -f db-service
docker run -d --name db-service --network app-network -v redis-data:/data redis:8-alpine redis-server --appendonly yes --appendfsync always
# Attendre PONG avant de comparer.
docker exec db-service redis-cli ping
docker exec db-service redis-cli GET hits
```

Les deux valeurs GET hits doivent etre identiques ; la visite suivante ajoute
1. Ne pas supprimer redis-data pendant ce test. Si la base est inaccessible,
l'application retourne 503 et la sonde /health aussi.

Passage au deploiement Compose (conserver le volume) :

```sh
docker rm -f counter-web db-service
docker network rm app-network
```

## 3. Compose et scaling

```sh
docker compose config
docker compose up -d --build --scale web=3
docker compose ps
docker network inspect app-network
```

Le fichier final contient db, web et lb. Trois replicas web n'ont ni
container_name fixe ni publication de port hote. Redis est unique. Nginx
publie le seul port HOST_PORT vers 8080 et distribue les requetes entre les
adresses DNS de web. La configuration utilise zone, resolver et resolve,
disponible dans Nginx open source depuis 1.27.3 ; la base choisie est 1.28.
Le filtre envsubst APP_PORT preserve $host et les autres variables Nginx.
Les ports variables de l'application, Redis et l'hote viennent de .env.
Le port 8080 est le port interne fixe du proxy, distinct du port hote variable.
Le DNS Docker et les valeurs techniques d'une sonde ne sont pas des ports hote.

Pourquoi `${HOST_PORT}:5000` sur chaque web echoue-t-il ? Un meme couple
adresse/port hote et protocole ne peut pas etre publie par trois conteneurs en
meme temps. Des ports hote differents sont possibles mais donnent plusieurs
URL. Le load balancer offre un point d'entree unique et repartit le trafic.
Le simple fait d'ecrire --scale n'ajoute pas un load balancer a Compose.

```sh
# Linux / Git Bash : verifier plusieurs identifiants
for i in $(seq 1 12); do curl -s -D - http://localhost/ -o /dev/null; done
# PowerShell : curl.exe -i http://localhost/
python scripts/verify_docker.py
```

Le script envoie 60 visites, exige 3 identifiants, verifie les UID non-root,
supprime et recree Redis et compare hits avant/apres. Les sondes ne comptent
pas comme visites. Les enregistrements textuels ne remplacent pas les captures
exigees par l'enseignante. Aucun test Docker n'a ete execute ici.

Debug :

```sh
docker compose logs -f
docker compose exec web sh
docker compose exec db sh
docker inspect db-service
docker compose exec lb nginx -t
```

## 4. Publication Docker Hub

Creer un depot PUBLIC nomme counter-app dans ton compte Docker Hub. Le compte
GitHub n'indique pas le nom du compte Docker Hub : ne pas les confondre.
Definir DOCKERHUB_USERNAME dans .env est utile pour les notes mais Compose
n'exporte pas ce fichier vers le shell. Pour les commandes, remplacer
VOTRE_COMPTE par ton vrai identifiant :

```sh
docker login -u VOTRE_COMPTE
docker tag counter-app:1.0 VOTRE_COMPTE/counter-app:1.0
docker tag counter-app:1.0 VOTRE_COMPTE/counter-app:latest
docker push VOTRE_COMPTE/counter-app:1.0
docker push VOTRE_COMPTE/counter-app:latest
```

Sous Bash, variante :

```sh
export DOCKERHUB_USERNAME=VOTRE_COMPTE
bash scripts/publish.sh
```

Lien a inscrire apres verification : https://hub.docker.com/r/VOTRE_COMPTE/counter-app
Ce lien est un modele ; aucune image n'a ete publiee ici.

### Nettoyage

Arret avec conservation des donnees : `docker compose down`.
Une seule commande pour supprimer les ressources Compose du TP, y compris le
compteur persistant et les images des services (si non utilisees ailleurs) :

```sh
docker compose down --rmi all --volumes --remove-orphans
```

Cette commande supprime les conteneurs actifs du projet, son reseau et ses
volumes nommes. Pour le deploiement manuel, retirer les deux conteneurs et le
reseau comme ci-dessus, puis le volume et counter-app:1.0.
Le deep clean global souvent cite est `docker system prune -a --volumes`.
Il ne supprime pas les conteneurs en cours d'execution ; --volumes cible les
volumes anonymes inutilises, pas redis-data nomme. Il touche egalement d'autres
projets inutilises. Il ne remplace donc pas la commande Compose du TP.

## C. Pipeline Jenkins automatique

### Prerequis agent

Agent Linux dedie (Python 3 avec module venv, Git, Docker CLI et daemon Docker
accessibles). Tester `docker version` en tant qu'utilisateur de l'agent Jenkins.
L'acces au daemon donne des privileges importants : utiliser un agent CI dedie.
Un Jenkins dans Docker sans Docker CLI/daemon accessible ne peut pas builder
une image simplement parce qu'un Jenkinsfile est present.

Plugins : Pipeline, Git, GitHub, Credentials Binding, JUnit et Timestamper.
Le pipeline utilise le Docker CLI et n'a pas besoin du plugin Docker Pipeline.

### Depot et job

1. Creer ou utiliser un depot GitHub pour CE projet et y ajouter les fichiers.
   Ne jamais committer un token. Ne pas inclure .venv ou les captures privees.
2. Jenkins > New Item > Pipeline > Pipeline script from SCM > Git.
3. Renseigner l'URL du depot et ses credentials si prive.
4. Branch Specifier : `*/main`. Script Path : `Jenkinsfile`.
5. Activer "GitHub hook trigger for GITScm polling" (le Jenkinsfile declare aussi
   githubPush). Executer un premier build manuel pour initialiser le job.
6. Dans le depot GitHub > Settings > Webhooks > Add webhook : URL HTTPS
   `https://VOTRE_JENKINS/github-webhook/`, Content type application/json,
   evenement "Just the push event". Jenkins doit etre joignable par GitHub.
   Configurer la verification du secret selon le plugin et l'installation.
7. Jenkins > Credentials : ajouter "Username with password", ID exact
   `dockerhub-credentials`, Username = compte Docker Hub,
   Password = token Docker Hub avec droits de lecture/ecriture.
8. Creer le depot Hub public counter-app. Faire un commit sur main et verifier
   la livraison du webhook, les etapes Jenkins et les tags Hub.

Si le Jenkins est local et inaccessible depuis GitHub, un endpoint HTTPS
joignable est necessaire. `pollSCM('H/5 * * * *')` est un secours periodique,
mais ne constitue pas le declenchement webhook immediat demande.

Pipeline : checkout -> installation/build Python -> tests/JUnit -> build Docker
-> login/push. Une erreur de test bloque les etapes suivantes. La publication
est limitee a main. Les images ont les tags BUILD_NUMBER-GIT_COMMIT et latest.
Un DOCKER_CONFIG temporaire isole le token et est nettoye meme en cas d'echec.
Le nettoyage final supprime seulement les tags CI locaux et le workspace.
Il ne supprime pas les images distantes ni les ressources d'execution du TP.

Preuves CI a joindre : capture du pipeline vert, livraison webhook reussie,
resultats JUnit et tags sur le depot public. Elles restent a produire localement.

## Rapport et preuves

Capturer et placer ces fichiers dans evidence/ :

- docker-images.png : `docker images counter-app:1.0`, taille visible.
- network-inspect.png : `docker network inspect app-network`, conteneurs visibles.
- browser.png : page Visit-Counter avec valeur et identifiant visibles.
- jenkins.png (recommande) : pipeline vert.
- dockerhub-url.txt : une ligne avec le vrai lien public verifie.

Regenerer le rapport :

```sh
python -m pip install reportlab
python docs/build_report.py
```

Le script insere les captures si elles existent et le lien reel. Sinon, il
signale les elements manquants. Le rapport initial ne doit pas etre remis comme
preuve d'une execution Docker. Le PDF fourni a l'entree est un exemple deja
redige par un autre groupe ; ses captures et son lien Hub ne sont pas reutilises.

## References officielles

- https://docs.docker.com/reference/dockerfile/
- https://docs.docker.com/reference/compose-file/services/
- https://docs.docker.com/compose/how-tos/networking/
- https://docs.docker.com/reference/cli/docker/compose/down/
- https://docs.docker.com/reference/cli/docker/system/prune/
- https://redis.io/docs/latest/management/persistence/
- https://nginx.org/en/docs/http/ngx_http_upstream_module.html
- https://www.jenkins.io/doc/book/pipeline/
- https://www.jenkins.io/doc/pipeline/steps/credentials-binding/
