def test_root_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.data.decode() == "Hello, World!"


def test_root_content_type(client):
    r = client.get("/")
    assert r.headers["Content-Type"] == "text/html; charset=utf-8"


def test_not_found(client):
    r = client.get("/no-such")
    assert r.status_code == 404
    assert r.get_json()["error"] == "not_found"
