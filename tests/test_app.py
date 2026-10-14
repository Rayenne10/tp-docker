import fakeredis
import pytest
import redis
from app import create_app

@pytest.fixture
def setup():
    cache = fakeredis.FakeStrictRedis(decode_responses=True)
    app = create_app(cache)
    app.config.update(TESTING=True, CONTAINER_ID='container-test')
    return app.test_client(), cache

def test_counter_increments(setup):
    client, cache = setup
    assert client.get('/').status_code == 200
    assert cache.get('hits') == '1'
    response = client.get('/')
    assert '<strong>2</strong>' in response.get_data(as_text=True)
    assert cache.get('hits') == '2'

def test_container_id_visible(setup):
    response = setup[0].get('/')
    assert 'container-test' in response.get_data(as_text=True)
    assert response.headers['X-Container-ID'] == 'container-test'

def test_health_does_not_count_visit(setup):
    client, cache = setup
    for _ in range(3):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.data == b'ok'
    assert cache.get('hits') is None

def test_counter_uses_existing_value(setup):
    client, cache = setup
    cache.set('hits', 41)
    assert '<strong>42</strong>' in client.get('/').get_data(as_text=True)

def test_replicas_share_counter():
    server = fakeredis.FakeServer()
    first = create_app(fakeredis.FakeStrictRedis(server=server, decode_responses=True))
    second = create_app(fakeredis.FakeStrictRedis(server=server, decode_responses=True))
    a, b = first.test_client(), second.test_client()
    assert '<strong>1</strong>' in a.get('/').get_data(as_text=True)
    assert '<strong>2</strong>' in b.get('/').get_data(as_text=True)
    assert '<strong>3</strong>' in a.get('/').get_data(as_text=True)

@pytest.mark.parametrize('error', [redis.ConnectionError, redis.TimeoutError])
@pytest.mark.parametrize('path', ['/', '/health'])
def test_redis_failure_returns_503(error, path):
    class Broken:
        def incr(self, key):
            raise error('secret-internal-details')
        def ping(self):
            raise error('secret-internal-details')
    app = create_app(Broken())
    with app.test_client() as client:
        response = client.get(path)
        assert response.status_code == 503
        assert b'secret-internal-details' not in response.data

def test_counter_invalid_type_returns_503(setup):
    client, cache = setup
    cache.set('hits', 'invalid')
    assert client.get('/').status_code == 503

def test_html_escapes_hostname(setup):
    client, _ = setup
    client.application.config['CONTAINER_ID'] = '<script>alert(1)</script>'
    html = client.get('/').get_data(as_text=True)
    assert '<script>' not in html
    assert '&lt;script&gt;' in html

def test_no_cache(setup):
    assert setup[0].get('/').headers['Cache-Control'] == 'no-store'

def test_unknown_route_does_not_count(setup):
    client, cache = setup
    assert client.get('/missing').status_code == 404
    assert cache.get('hits') is None

def test_config_from_environment(monkeypatch):
    monkeypatch.setenv('REDIS_HOST', 'db-example')
    monkeypatch.setenv('REDIS_PORT', '6380')
    app = create_app()
    options = app.extensions['redis'].connection_pool.connection_kwargs
    assert options['host'] == 'db-example'
    assert options['port'] == 6380
    assert options['socket_timeout'] == 2
