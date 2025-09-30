def test_echo_bad_content_type(client):
    r = client.post("/api/echo", data="not json", headers={"Content-Type": "text/plain"})
    assert r.status_code == 400
    body = r.get_json()
    assert body["error"] == "bad_request"
    assert "Expected application/json" in body["message"]

def test_echo_malformed_json(client):
    # Заголовок JSON есть, но тело поломано
    r = client.post("/api/echo", data="{ not-json", headers={"Content-Type": "application/json"})
    assert r.status_code == 400
    body = r.get_json()
    assert body["error"] == "bad_request"
    assert "Malformed JSON" in body["message"]

def test_delete_not_found(client):
    r = client.delete("/api/items/nope")
    assert r.status_code == 404
    assert r.get_json()["error"] == "not_found"

def test_update_not_found(client):
    r = client.put("/api/items/nope", json={"name": "X"})
    assert r.status_code == 404
