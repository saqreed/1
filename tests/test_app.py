import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client

def test_root_ok(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.data.decode() == "Hello, World!"

def test_root_content_type(client):
    r = client.get("/")
    assert r.headers["Content-Type"] == "text/html; charset=utf-8"

def test_not_found(client):
    r = client.get("/not-found")
    assert r.status_code == 404