# Alpine : base compacte ; nos dependances ne requierent pas de compilateur.
# Tag de version mineure : reconstruire permet de recuperer ses correctifs.
FROM python:3.11-alpine
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_PORT=5000
ENV GUNICORN_CMD_ARGS="--workers=2 --threads=2 --access-logfile=- --error-logfile=-"
WORKDIR /app
# Le code change plus souvent que les dependances : conserver leur cache.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && addgroup -S appgroup && adduser -S -G appgroup -u 1000 appuser
# Le code reste possede par root et lisible, sans etre modifiable par appuser.
COPY app.py healthcheck.py .
# L'application ne tourne pas avec les droits root dans le conteneur.
USER appuser
# EXPOSE documente le port ; la publication est faite par -p ou Compose.
EXPOSE 5000
# Controle HTTP sans incrementer hits ; Redis doit aussi etre disponible.
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
 CMD python healthcheck.py
# sh est remplace par Gunicorn via exec pour recevoir SIGTERM.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${APP_PORT} app:app"]
