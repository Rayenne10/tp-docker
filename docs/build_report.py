"""Genere un rapport honnete : aucune preuve Docker n'est fabriquee.
Ajouter les PNG et dockerhub-url.txt dans evidence/, puis relancer ce script.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import json
import xml.etree.ElementTree as ET
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                              Preformatted, Table, TableStyle, Image, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Compte_rendu_TP1_Rayenne_Abid.pdf'
FONT_DIR = ROOT / 'docs/fonts'
pdfmetrics.registerFont(TTFont('DejaVu', str(FONT_DIR/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', str(FONT_DIR/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuMono', str(FONT_DIR/'DejaVuSansMono.ttf')))
pdfmetrics.registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVu-Bold', italic='DejaVu', boldItalic='DejaVu-Bold')
W, H = A4
INK = colors.HexColor('#19324b')
TEAL = colors.HexColor('#16766e')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCustom', fontName='DejaVu-Bold', fontSize=31,
                          leading=35, textColor=INK, spaceAfter=16))
styles.add(ParagraphStyle(name='HCustom', fontName='DejaVu-Bold', fontSize=19,
                          leading=24, textColor=INK, spaceAfter=15))
styles.add(ParagraphStyle(name='SubCustom', fontName='DejaVu-Bold', fontSize=12,
                          leading=16, textColor=TEAL, spaceBefore=14, spaceAfter=7))
styles.add(ParagraphStyle(name='TextCustom', fontName='DejaVu', fontSize=10,
                          leading=15, textColor=INK, spaceAfter=10))
styles.add(ParagraphStyle(name='CodeCustom', fontName='DejaVuMono', fontSize=7.6,
                          leading=10, textColor=INK, backColor=colors.HexColor('#eef3f7'),
                          borderPadding=9, spaceAfter=12))
styles.add(ParagraphStyle(name='SmallCustom', fontName='DejaVu', fontSize=8,
                          leading=12, textColor=INK, spaceAfter=6))
story=[]

def p(text,style='TextCustom'):
    story.append(Paragraph(text,styles[style]))
def h(text): p(text,'HCustom')
def sub(text): p(text,'SubCustom')
def code(text):
    # Couper les longues commandes aux limites de mots pour eviter tout debordement.
    import textwrap
    lines=[]
    for line in text.strip('\n').splitlines():
        if len(line) > 101:
            parts=textwrap.wrap(line,width=98,break_long_words=False,break_on_hyphens=False)
            lines.extend(parts)
        else: lines.append(line)
    story.append(Preformatted('\n'.join(lines),styles['CodeCustom']))
def page(): story.append(PageBreak())
def table(rows,widths):
    content=[[Paragraph(escape(str(cell)),styles['SmallCustom']) for cell in row] for row in rows]
    t=Table(content,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcebe9')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#cbd6df')),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(t)

def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#cbd6df'))
    canvas.line(48,42,W-48,42)
    canvas.setFont('DejaVu',8)
    canvas.setFillColor(INK)
    canvas.drawString(48,29,'INSAT | RT5 | TP1 DevOps | Rayenne Abid')
    canvas.drawRightString(W-48,29,f'{doc.page}')

p('LABORATOIRE DEVOPS / 2026-2027','SubCustom')
story.append(Spacer(1,28))
p('Compréhension de<br/>l’écosystème Docker','TitleCustom')
p('Conteneurisation et orchestration<br/>de microservices','HCustom')
story.append(Spacer(1,16))
p('Application <b>Visit-Counter</b> : Flask, Redis, Nginx et Jenkins.')
p('<b>Réalisé par :</b> Rayenne Abid<br/><b>Classe :</b> RT5 - INSAT<br/>'
  '<b>Encadrante :</b> Saloua BEN YAHIA<br/><b>Date de préparation :</b> 14 octobre 2026')
sub('État du livrable')
p('Le code, les tests, la configuration Docker et le pipeline sont préparés. '
  'Les tests unitaires ont été exécutés. Docker et Jenkins étant absents de '
  'l’environnement de préparation, les preuves de conteneurisation et de '
  'publication restent à produire sur la machine de l’étudiant.')
table([['Livrable','État'],['Application et 14 tests unitaires','Vérifiés en Python 3.12'],
       ['Dockerfile, Compose, pipeline Jenkins','Préparés ; exécution Docker/CI à réaliser'],
       ['Captures et lien public Docker Hub','À compléter après une exécution réelle'],
       ['Partie A notée','Support anglais fourni ; tutoriel enseignant à réaliser']], [220,279])
p('Le PDF joint à l’énoncé est un exemple déjà rédigé par un autre groupe. '
  'Ses auteurs, captures et URL Docker Hub ne sont pas utilisés comme preuves de ce travail.','SmallCustom')
page()

h('01 / Architecture et application')
p('Le navigateur contacte un point d’entrée Nginx. Le proxy répartit les visites '
  'sur trois instances du service web, qui utilisent toutes le même Redis. '
  'La clé <b>hits</b> est incrémentée par INCR, opération atomique côté Redis.')
table([['Composant','Rôle'],['Nginx / lb','Un port hôte ; répartition entre les adresses DNS web'],
       ['Flask + Gunicorn / web x 3','INCR hits ; page en français et identifiant du conteneur'],
       ['Redis / db-service','Stockage du compteur ; AOF dans /data'],
       ['app-network','Bridge nommé ; résolution DNS entre services'],
       ['redis-data','Volume nommé indépendant du cycle de vie des conteneurs']], [155,344])
sub('Routes et comportement')
p('<b>GET /</b> ajoute une visite et affiche : « Bonjour ! Cette page a été vue X fois. '
  'Je suis le conteneur [ID] ». Le hostname fournit l’identifiant ; l’en-tête '
  'X-Container-ID permet aussi de tester la répartition. Cache-Control: no-store '
  'évite de réutiliser une réponse mise en cache.')
p('<b>GET /health</b> effectue un PING Redis sans incrémenter le compteur. '
  'Une erreur Redis produit un HTTP 503, sans exposer les détails internes. '
  'Les délais de connexion et de lecture Redis sont limités à deux secondes.')
sub('Partie A / English Docker tutorial')
p('The supplied English study guide covers images and containers, lifecycle, '
  'Dockerfiles, networking, persistence, Compose, registries and CI/CD. '
  'It includes ten self-check questions with answers.')
p('The teacher’s Drive tutorial was not accessible during preparation. The guide '
  'is original supporting material and does not certify completion of the graded '
  'tutorial or answer questions whose content was unavailable.')
sub('Choix de conception')
p('Gunicorn sert l’application ; le serveur de développement Flask reste réservé '
  'à un lancement local. Redis et les replicas web ne publient aucun port hôte '
  'dans Compose. Seul le proxy est accessible depuis le navigateur. Ce TP '
  'conserve un Redis et un proxy uniques : il ne fournit pas une haute disponibilité complète.')
page()

h('02 / Dockerfile commenté')
code((ROOT/'Dockerfile').read_text())
sub('Justification')
p('Python 3.11 Alpine est une base compacte adaptée aux dépendances retenues. '
  'Aucun compilateur n’est installé. La taille doit être mesurée par docker images '
  'après le build ; aucune taille supposée n’est présentée comme résultat.')
p('requirements.txt est copié avant le code pour conserver le cache des paquets. '
  'pip --no-cache-dir évite son cache de téléchargement. USER appuser réduit les '
  'privilèges ; le code reste possédé par root. Le mode lecture seule, tmpfs /tmp '
  'et cap_drop sont appliqués par Compose.')
code('docker build -t counter-app:1.0 .\ndocker images counter-app:1.0\ndocker run --rm --entrypoint id counter-app:1.0')
page()

h('03 / Réseau, volume et robustesse')
p('Le déploiement manuel permet d’observer séparément le réseau bridge, '
  'la résolution de noms et le stockage persistant. Les commandes suivantes '
  's’exécutent avant le déploiement Compose, pour éviter les conflits de noms.')
code('''docker network create app-network
docker volume create redis-data
docker run -d --name db-service --network app-network \\
  -v redis-data:/data redis:8-alpine \\
  redis-server --appendonly yes --appendfsync always
docker exec db-service redis-cli ping
docker run -d --name counter-web --network app-network \\
  -p 80:5000 counter-app:1.0
docker network inspect app-network''')
sub('Pourquoi AOF ?')
p('Redis garde le compteur en mémoire. Le volume seul ne sauvegarde pas chaque '
  'incrément. AOF journalise les écritures dans /data. appendfsync always demande '
  'une synchronisation à chaque écriture avant confirmation, au prix d’un débit '
  'inférieur. Ce choix favorise le test de suppression forcée exigé par le TP.')
sub('Protocole du test de persistance')
p('Fermer le navigateur pendant la comparaison. Lire hits, supprimer uniquement '
  'db-service, puis recréer Redis avec le même volume et les mêmes options. '
  'Attendre PONG ; hits doit être identique. Une visite suivante doit ajouter 1.')
code('''docker exec db-service redis-cli GET hits
docker rm -f db-service
docker run -d --name db-service --network app-network \\
  -v redis-data:/data redis:8-alpine \\
  redis-server --appendonly yes --appendfsync always
docker exec db-service redis-cli ping
docker exec db-service redis-cli GET hits''')
p('Un volume persistant ne constitue pas une sauvegarde. Ne pas supprimer '
  'redis-data pendant ce test. Le script scripts/verify_docker.py reproduit la '
  'comparaison pour le déploiement Compose et enregistre les valeurs observées.')
sub('Transition vers Compose')
code('docker rm -f counter-web db-service\ndocker network rm app-network')
p('Le volume est conservé. Compose pourra le réutiliser ; son nom explicite '
  'reste redis-data. Les réseaux et volumes aux noms fixes limitent ce TP à '
  'une seule installation simultanée sur un même moteur Docker.','SmallCustom')
page()

h('04 / Docker Compose final')
compose=(ROOT/'docker-compose.yml').read_text()
first,rest=compose.split('\n  lb:',1)
code(first)
p('Les paramètres obligatoires proviennent du fichier .env fourni. Redis est '
  'unique et healthy avant le démarrage web. Les replicas n’ont ni container_name '
  'fixe ni port hôte publié. Ils peuvent donc être multipliés.','SmallCustom')
page()
h('05 / Proxy et mise à l’échelle')
code('  lb:'+rest)
code((ROOT/'.env').read_text())
code('docker compose config\ndocker compose up -d --build --scale web=3\ndocker compose ps')
sub('Le conflit de port et sa solution')
p('Publier le même couple adresse/port hôte pour chaque replica entraîne un '
  'conflit de bind. Chaque conteneur peut écouter sur son port interne 5000, '
  'mais les trois ne peuvent pas réserver le port 80 de l’hôte. Le proxy '
  'réserve ce port une seule fois et répartit les requêtes.')
p('Nginx 1.28 utilise un upstream partagé, le resolver Docker et resolve pour '
  'actualiser les adresses de web. Le filtre envsubst APP_PORT préserve les '
  'variables Nginx. Le fichier nginx/default.conf.template est livré dans le ZIP.')
page()

h('06 / Pipeline Jenkins et publication')
p('Un job Pipeline from SCM suit la branche <b>*/main</b> et lit le Jenkinsfile '
  'du dépôt. Le trigger githubPush est associé au webhook GitHub : '
  'https://VOTRE_JENKINS/github-webhook/. Un premier build initialise le job.')
table([['Étape','Action et condition'],['Checkout','Récupérer la révision de main'],
       ['Build application','Créer un venv, installer les dépendances, compiler app.py'],
       ['Unit tests','Exécuter pytest ; publier le rapport JUnit'],
       ['Build image','docker build --pull ; seulement sur main'],
       ['Publish Docker Hub','Login via token ; push tag build-commit et latest']], [155,344])
sub('Configuration requise')
p('L’agent Linux doit fournir Git, Python avec venv, Docker CLI et un accès au '
  'daemon. Plugins : Pipeline, Git, GitHub, Credentials Binding, JUnit et '
  'Timestamper. Le job est limité à main. Jenkins doit être joignable depuis '
  'GitHub pour recevoir les événements push.')
p('Créer un credential Username with password, ID <b>dockerhub-credentials</b> : '
  'username = compte Docker Hub ; password = token autorisant le push. '
  'Créer un dépôt public counter-app dans ce compte. Le token reste dans '
  'withCredentials, sans interpolation Groovy ; DOCKER_CONFIG temporaire '
  'est supprimé même si le push échoue.')
sub('Publication manuelle équivalente')
code('''docker login -u VOTRE_COMPTE
docker tag counter-app:1.0 VOTRE_COMPTE/counter-app:1.0
docker push VOTRE_COMPTE/counter-app:1.0''')
hub=ROOT/'evidence/dockerhub-url.txt'
url=hub.read_text().strip() if hub.exists() else ''
if url.startswith('https://hub.docker.com/r/') and 'VOTRE_COMPTE' not in url and 'CHANGE_ME' not in url:
    p('<b>Lien renseigné par l’étudiant :</b> '+escape(url))
else:
    p('<b>Lien Docker Hub à compléter :</b> aucune publication effectuée ici. '
      'Le modèle est https://hub.docker.com/r/VOTRE_COMPTE/counter-app.')
p('Le Jenkinsfile intégral et les instructions du webhook figurent dans le '
  'projet. La présence d’un pipeline ne prouve pas son exécution : ajouter '
  'la capture Jenkins et vérifier le push après un commit sur main.')
page()

h('07 / Vérifications et preuves')
xml=ROOT/'evidence/unit-tests.xml'
summary='Rapport JUnit non présent.'
if xml.exists():
    tree=ET.parse(xml).getroot()
    suites=([tree] if tree.tag=='testsuite' else tree.findall('testsuite'))
    total=sum(int(s.get('tests','0')) for s in suites)
    failed=sum(int(s.get('failures','0'))+int(s.get('errors','0')) for s in suites)
    summary=f'{total} tests exécutés ; {failed} échec/erreur. Rapport : evidence/unit-tests.xml.'
p('<b>Résultat réel :</b> '+escape(summary))
p('Les tests couvrent les incréments successifs, le compteur partagé par deux '
  'instances applicatives, le hostname, la sonde sans visite, les erreurs de '
  'connexion et de timeout, une valeur Redis invalide, le rendu échappé et la '
  'configuration par variables d’environnement. Redis est simulé par fakeredis.')
p('La compilation Python, la syntaxe des scripts Bash et la structure YAML '
  'ont également été contrôlées. Les tests unitaires ne prouvent ni le build '
  'd’image, ni la distribution Nginx réelle, ni la persistance sur disque.')
integration=ROOT/'evidence/integration.json'
if integration.exists():
    p('<b>Compte rendu du script Docker fourni :</b>')
    code(integration.read_text())
else:
    p('<b>Intégration Docker :</b> non exécutée ici, Docker étant absent. '
      'Lancer python scripts/verify_docker.py après le démarrage des trois replicas.')
sub('Captures obligatoires')
for filename,label in [('docker-images.png','Taille de counter-app:1.0'),
                       ('network-inspect.png','app-network et conteneurs connectés'),
                       ('browser.png','Page réelle dans le navigateur')]:
    if not (ROOT/'evidence'/filename).exists():
        p('<b>'+escape(filename)+'</b> : à ajouter - '+label+'.')
p('Après exécution, placer les trois captures PNG dans evidence/, ajouter '
  'dockerhub-url.txt puis relancer python docs/build_report.py. Le rapport '
  'insère alors les images. Il ne substitue aucun exemple aux captures réelles.')
sub('Commande de collecte')
code('python scripts/verify_docker.py')
p('Le script exige trois identifiants, vérifie les UID non-root, compare le '
  'compteur après suppression forcée puis vérifie la visite suivante. Il '
  'collecte aussi docker images, network inspect et compose ps en texte.')
page()

h('08 / Réflexion, nettoyage et sources')
sub('RUN et CMD')
p('<b>RUN</b> s’exécute pendant docker build et modifie le système de fichiers '
  'de l’image. Exemple : installer requirements.txt. <b>CMD</b> définit la '
  'commande par défaut au démarrage, ici Gunicorn. Elle peut être remplacée '
  'par une commande fournie à docker run et ne s’exécute pas au build.')
sub('Nettoyage en une commande')
code('docker compose down --rmi all --volumes --remove-orphans')
p('Cette commande retire les conteneurs du projet, le réseau, les volumes '
  'déclarés et les images des services si elles ne sont pas utilisées ailleurs. '
  'Le compteur est supprimé avec redis-data. Pour conserver les données, '
  'utiliser simplement docker compose down.')
p('docker system prune -a --volumes nettoie les ressources globalement '
  'inutilisées ; il laisse les conteneurs actifs et ne supprime pas tous les '
  'volumes nommés. Ce n’est donc pas un remplacement du nettoyage Compose.')
sub('Éléments à finaliser avant remise')
p('Réaliser le tutoriel A noté ; exécuter le build et les tests Docker ; ajouter '
  'les trois captures obligatoires ; pousser une image publique dans le compte '
  'personnel ; vérifier le webhook et le pipeline Jenkins ; régénérer ce rapport. '
  'Le dossier fourni couvre le code et les procédures des parties B et C.')
sub('Documentation officielle utilisée')
for text,url in [
 ('Dockerfile','https://docs.docker.com/reference/dockerfile/'),
 ('Services Compose','https://docs.docker.com/reference/compose-file/services/'),
 ('Réseaux Compose','https://docs.docker.com/compose/how-tos/networking/'),
 ('Nettoyage Docker','https://docs.docker.com/reference/cli/docker/system/prune/'),
 ('Persistance Redis','https://redis.io/docs/latest/management/persistence/'),
 ('Upstream Nginx','https://nginx.org/en/docs/http/ngx_http_upstream_module.html'),
 ('Pipeline Jenkins','https://www.jenkins.io/doc/book/pipeline/'),
 ('Credentials Binding','https://www.jenkins.io/doc/pipeline/steps/credentials-binding/')]:
    p(escape(text)+' :<br/>'+escape(url),'SmallCustom')

for filename,label in [('docker-images.png','Taille réelle de l’image'),
                       ('network-inspect.png','Réseau et conteneurs'),
                       ('browser.png','Application dans le navigateur'),
                       ('jenkins.png','Exécution Jenkins')]:
    src=ROOT/'evidence'/filename
    if src.exists():
        page(); h('Annexe / '+label)
        im=Image(str(src))
        factor=min(499/im.imageWidth,640/im.imageHeight)
        im.drawWidth=im.imageWidth*factor; im.drawHeight=im.imageHeight*factor
        story.append(im)
        p(escape(filename),'SmallCustom')

SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=48,leftMargin=48,
                  topMargin=48,bottomMargin=60,title='TP1 Docker - Visit-Counter',
                  author='Rayenne Abid').build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
