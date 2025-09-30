def test_items_empty_list(client):
    r = client.get("/api/items")
    assert r.status_code == 200
    body = r.get_json()
    assert body["items"] == []
    assert body["total"] == 0


def test_items_create_list_get_update_delete(client):
    # create
    r = client.post("/api/items", json={"name": "First"})
    assert r.status_code == 201
    item = r.get_json()
    item_id = item["id"]
    assert item["name"] == "First"

    # list (q filter works too)
    r = client.get("/api/items?q=fir")
    body = r.get_json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == item_id

    # get
    r = client.get(f"/api/items/{item_id}")
    assert r.status_code == 200
    assert r.get_json()["name"] == "First"

    # update (validation)
    bad = client.put(f"/api/items/{item_id}", json={"name": ""})
    assert bad.status_code == 422

    # update ok
    r = client.put(f"/api/items/{item_id}", json={"name": "Renamed"})
    assert r.status_code == 200
    assert r.get_json()["name"] == "Renamed"

    # delete
    r = client.delete(f"/api/items/{item_id}")
    assert r.status_code == 204

    # not found after delete
    r = client.get(f"/api/items/{item_id}")
    assert r.status_code == 404
    assert r.get_json()["error"] == "not_found"


def test_items_create_requires_name(client):
    r = client.post("/api/items", json={"name": ""})
    assert r.status_code == 422
    r = client.post("/api/items", json={})
    assert r.status_code == 422
