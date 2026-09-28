import importlib
import sys
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_bridge_auth_and_cors(monkeypatch):
    origin = "https://agreeable-bay-0a770bc0f.2.azurestaticapps.net"
    token = "a" * 32
    inner = FastAPI()

    @inner.get("/api/v1/health/live")
    def health():
        return {"status": "ok"}

    monkeypatch.setenv("LOCAL_BRIDGE_TOKEN", token)
    monkeypatch.setenv("FRONTEND_ORIGIN", origin)
    monkeypatch.setitem(sys.modules, "app.main", SimpleNamespace(app=inner))
    sys.modules.pop("app.local_bridge", None)
    try:
        bridge = importlib.import_module("app.local_bridge")
        client = TestClient(bridge.app)
        assert client.get("/api/v1/health/live").status_code == 401
        assert client.get("/api/v1/health/live", headers={"Authorization": "Bearer wrong"}).status_code == 401
        response = client.get("/api/v1/health/live", headers={"Authorization": f"Bearer {token}", "Origin": origin})
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
        preflight = client.options("/api/v1/health/live", headers={"Origin": origin, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization,content-type"})
        assert preflight.status_code == 200
        assert client.options("/api/v1/health/live", headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"}).status_code == 400
    finally:
        sys.modules.pop("app.local_bridge", None)
