def test_echo_ok(client):
    r = client.post("/api/echo", json={"a": 1})
    assert r.status_code == 200
    body = r.get_json()
    assert body["received"] == {"a": 1}
    assert body["count"] > 0


def test_echo_requires_json(client):
    r = client.post("/api/echo", data="not json", headers={"Content-Type": "text/plain"})
    assert r.status_code == 400
    assert r.get_json()["error"] == "bad_request"


def test_time_ok(client):
    r = client.get("/api/time")
    assert r.status_code == 200
    assert "now" in r.get_json()
