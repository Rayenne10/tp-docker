# Statut des preuves

REALISE ICI : 14 tests unitaires Flask/fakeredis, resultat dans unit-tests.xml.
Ces tests n'utilisent aucun daemon Docker et ne prouvent pas la persistance disque.

A REALISER SUR LA MACHINE DOCKER :
1. docker-images.png : taille reelle de counter-app:1.0.
2. network-inspect.png : reseau app-network et conteneurs connectes.
3. browser.png : page reelle de l'application conteneurisee.
4. python scripts/verify_docker.py : 3 replicas, UID non-root et persistance.
5. dockerhub-url.txt : lien d'une image publique vraiment poussee.
6. jenkins.png : execution CI reussie apres un commit sur main.

Ne pas reprendre les captures, valeurs, auteurs ou URL du rapport d'un autre
groupe. docs/build_report.py affiche explicitement les preuves absentes.
