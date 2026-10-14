"""Sonde du conteneur, sans dependance externe et sans nouvelle visite."""
import os
import urllib.request

if __name__ == '__main__':
    port = os.getenv('APP_PORT', '5000')
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=2) as response:
        if response.status != 200:
            raise SystemExit(1)
