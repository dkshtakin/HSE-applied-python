from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


def test_basic():
    response = client.get('/')
    assert response.json() == {'status': 'App healthy'}


def test_google():
    response = client.post(
        '/links/shorten',
        json={
            'url': 'https://www.google.com/',
            'alias': 'google',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'short_code': 'google'}

    response = client.get(
        '/links/google',
        follow_redirects=False,
    )
    assert response.status_code == 307
    assert response.headers['location'] == 'https://www.google.com/'

    response = client.get(
        '/links/search?original_url=https://www.google.com/',
    )
    assert response.status_code == 200
    assert response.json() == ['google']

    response = client.get(
        '/links/google/stats',
    )
    assert response.status_code == 200
    assert response.json()['url'] == 'https://www.google.com/'
    assert response.json()['access_count'] == 1


    response = client.put(
        '/links/google',
        json={
            'url': 'https://www.yandex.com/'
        },
    )
    assert response.status_code == 200
    assert response.json() == 'OK'

    response = client.get(
        '/links/google/stats',
    )
    assert response.status_code == 200
    assert response.json()['url'] == 'https://www.yandex.com/'
    assert response.json()['access_count'] == 1

    response = client.delete(
        '/links/google',
    )
    assert response.status_code == 200
    assert response.json() == 'OK'


def test_invalid():
    response = client.get(
        '/links/yandex/stats?original_url=https://www.google.com/',
    )
    assert response.status_code == 404
    assert response.json() == {'detail': "short code 'yandex' does not refer to any url"}


def test_format():
    response = client.post(
        '/links/shorten',
        json={
            'url': 'https://www.google.com/',
            'alias': 'google',
            'expires_at': '1212-12-12 12:12'
        },
    )
    assert response.status_code == 200
