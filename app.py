"""Compteur de visites : INCR atomique dans Redis, rendu Flask."""
import os
import socket
import redis
from flask import Flask, render_template_string

PAGE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Visit-Counter | TP Docker</title>
<style>
body{margin:0;background:#eef3f8;font-family:system-ui,sans-serif;color:#172d45;
min-height:100vh;display:grid;place-items:center}
main{background:white;max-width:650px;margin:24px;padding:40px;
border-radius:18px;box-shadow:0 16px 50px #172d4518}
small{color:#3273a8;letter-spacing:2px}h1{font-size:36px}
strong{font-size:44px;color:#16766e}code{background:#edf4f7;padding:5px 10px;
border-radius:6px}a{display:inline-block;margin-top:24px;color:#16766e}
</style></head><body><main><small>INSAT / LABORATOIRE DEVOPS</small>
<h1>Bonjour !</h1><p>Cette page a été vue <strong>{{ hits }}</strong> fois.</p>
<p>Je suis le conteneur <code>{{ container_id }}</code>.</p>
<a href="/">Nouvelle visite</a></main></body></html>"""


def create_app(cache=None):
    app = Flask(__name__)
    app.config['CONTAINER_ID'] = os.getenv('HOSTNAME', socket.gethostname())
    if cache is None:
        cache = redis.Redis(
            host=os.getenv('REDIS_HOST', 'db-service'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    app.extensions['redis'] = cache

    @app.get('/')
    def index():
        try:
            hits = cache.incr('hits')
        except redis.exceptions.RedisError:
            app.logger.warning('Redis indisponible')
            return 'Service temporairement indisponible : Redis est inaccessible.', 503
        response = app.make_response(render_template_string(
            PAGE, hits=hits, container_id=app.config['CONTAINER_ID']))
        response.headers['X-Container-ID'] = app.config['CONTAINER_ID']
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/health')
    def health():
        try:
            cache.ping()
        except redis.exceptions.RedisError:
            return 'redis unreachable', 503
        return 'ok', 200

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('APP_PORT', '5000')))
