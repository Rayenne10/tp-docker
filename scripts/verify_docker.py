"""Integration reelle, apres docker compose up -d --build --scale web=3.
Supprime volontairement db-service ; conserve le volume redis-data.
A executer sur le TP uniquement, jamais sur une base de production.
"""
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

def run(*args):
    return subprocess.check_output(args, text=True).strip()

def redis_value():
    value = run('docker', 'compose', 'exec', '-T', 'db', 'sh', '-c',
                'redis-cli -p "$REDIS_PORT" --raw GET hits')
    return int(value or 0)

def main():
    settings = dict(line.split('=', 1) for line in (ROOT / '.env').read_text().splitlines()
                    if line.strip() and not line.startswith('#'))
    port = os.getenv('HOST_PORT', settings.get('HOST_PORT', '80'))
    url = f'http://127.0.0.1:{port}'
    def ready():
        for _ in range(60):
            try:
                with urllib.request.urlopen(url + '/health', timeout=3) as response:
                    if response.status == 200:
                        return
            except (urllib.error.URLError, TimeoutError):
                pass
            time.sleep(1)
        raise RuntimeError('Application non disponible apres 60 essais')
    ready()
    ids = set()
    for _ in range(60):
        with urllib.request.urlopen(url, timeout=5) as response:
            assert response.status == 200
            ids.add(response.headers['X-Container-ID'])
    assert len(ids) == 3, f'3 conteneurs attendus, obtenus : {ids}'
    web_ids = run('docker', 'compose', 'ps', '-q', 'web').splitlines()
    assert len(web_ids) == 3
    for cid in web_ids:
        assert run('docker', 'exec', cid, 'id', '-u') != '0'
    before = redis_value()
    run('docker', 'rm', '-f', 'db-service')
    run('docker', 'compose', 'up', '-d', 'db')
    ready()
    after = redis_value()
    assert after == before, (before, after)
    with urllib.request.urlopen(url, timeout=5) as response:
        assert response.status == 200
    assert redis_value() == before + 1
    evidence = ROOT / 'evidence'
    evidence.mkdir(exist_ok=True)
    (evidence / 'docker-images.txt').write_text(run('docker', 'images'))
    (evidence / 'network-inspect.json').write_text(run('docker', 'network', 'inspect', 'app-network'))
    (evidence / 'compose-ps.txt').write_text(run('docker', 'compose', 'ps'))
    results = {'status': 'PASS', 'replicas': sorted(ids), 'non_root': True,
               'hits_before_removal': before, 'hits_after_recreation': after,
               'hits_after_new_visit': before + 1}
    (evidence / 'integration.json').write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
