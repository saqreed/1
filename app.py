from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from flask import Flask, jsonify, request, abort, g


# ---------- Config ----------
class Config:
    APP_NAME = "Hello-API"
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    TESTING = False


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------- In-memory "DB" ----------
    ITEMS: Dict[str, Dict[str, Any]] = {}

    # ---------- Hooks & logging ----------
    @app.before_request
    def _start_timer():
        g._ts = datetime.now(timezone.utc)

    @app.after_request
    def _add_common_headers(resp):
        resp.headers.setdefault("X-App-Name", app.config["APP_NAME"])
        resp.headers.setdefault("Access-Control-Allow-Origin", "*")
        resp.headers.setdefault("Cache-Control", "no-store")
        return resp

    @app.teardown_request
    def _log_request(exc):
        try:
            dt = (datetime.now(timezone.utc) - g._ts).total_seconds()
            app.logger.info("%s %s -> %.3fs", request.method, request.path, dt)
        except Exception:
            pass

    # ---------- Error handlers ----------
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error="bad_request", message=str(e)), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="not_found", message="resource not found"), 404

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify(error="validation_error", message=str(e)), 422

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(error="server_error", message="unexpected error"), 500

    # ---------- Helpers ----------
    def require_json() -> Dict[str, Any]:
        if not request.is_json:
            abort(400, description="Expected application/json")
        data = request.get_json(silent=True)
        if data is None:
            abort(400, description="Malformed JSON")
        return data

    # ---------- Routes ----------
    @app.get("/")
    def hello():
        return "Hello, World!"

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            app=app.config["APP_NAME"],
            now_utc=datetime.now(timezone.utc).isoformat(),
        )

    @app.post("/api/echo")
    def echo():
        payload = require_json()
        return jsonify(received=payload, count=len(str(payload)))

    @app.get("/api/time")
    def api_time():
        return jsonify(now=datetime.now(timezone.utc).isoformat())

    # ----- CRUD: /api/items -----
    @app.get("/api/items")
    def list_items():
        q = request.args.get("q", "").lower()
        values = list(ITEMS.values())
        if q:
            values = [it for it in values if q in it["name"].lower()]
        return jsonify(items=values, total=len(values))

    @app.post("/api/items")
    def create_item():
        data = require_json()
        name = str(data.get("name", "")).strip()
        if not name:
            abort(422, description="Field 'name' is required and must be non-empty.")
        item_id = uuid.uuid4().hex[:8]
        item = {"id": item_id, "name": name, "created_at": datetime.now(timezone.utc).isoformat()}
        ITEMS[item_id] = item
        return jsonify(item), 201

    @app.get("/api/items/<item_id>")
    def get_item(item_id: str):
        item = ITEMS.get(item_id)
        if not item:
            abort(404)
        return jsonify(item)

    @app.put("/api/items/<item_id>")
    def update_item(item_id: str):
        item = ITEMS.get(item_id)
        if not item:
            abort(404)
        data = require_json()
        name = str(data.get("name", "")).strip()
        if not name:
            abort(422, description="Field 'name' is required and must be non-empty.")
        item = {**item, "name": name, "updated_at": datetime.now(timezone.utc).isoformat()}
        ITEMS[item_id] = item
        return jsonify(item)

    @app.delete("/api/items/<item_id>")
    def delete_item(item_id: str):
        if item_id not in ITEMS:
            abort(404)
        del ITEMS[item_id]
        return "", 204

    @app.options("/api/<path:_>")
    def _cors_preflight(_):
        resp = jsonify(ok=True)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return resp

    return app

app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
