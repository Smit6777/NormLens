import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import Settings

@pytest.fixture(scope="module")
def api_settings(tmp_path_factory):
    d = tmp_path_factory.mktemp("kb")
    
    # Needs valid JSON lists for repository initialization
    for name in ["bis_metadata.json", "qco_mapping.json", "normative_graph.json"]:
        (d / name).write_text("[]", encoding="utf-8")
    for name in ["bis_compliance.json", "sources.json"]:
        (d / name).write_text("{}", encoding="utf-8")
        
    return Settings(
        data_dir=d,
        vector_index_dir=tmp_path_factory.mktemp("index"),
        api_key="test-key",
        admin_api_key="admin-key",
        rate_limit="100/hour"
    )

@pytest.fixture(scope="module")
def client(api_settings):
    from tests.conftest import FakeEncoder
    from app.core.config import get_settings
    app = create_app(settings=api_settings, encoder=FakeEncoder())
    app.dependency_overrides[get_settings] = lambda: api_settings
    with TestClient(app) as c:
        yield c

def test_health_exempt_from_auth(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "components" in response.json()

def test_rebuild_index_without_admin_key_fails(client):
    response = client.post("/api/v1/rebuild-index")
    assert response.status_code in [401, 403]

def test_rebuild_index_with_normal_key_fails(client):
    response = client.post("/api/v1/rebuild-index", headers={"X-API-Key": "test-key"})
    assert response.status_code == 403

def test_rebuild_index_with_admin_key_succeeds(client):
    response = client.post("/api/v1/rebuild-index", headers={"X-API-Key": "admin-key"})
    assert response.status_code == 200

def test_rate_limiter_exceeds(client, api_settings):
    # Temporarily override limit to something very small
    api_settings.rate_limit = "2/hour"
    
    # Two requests should succeed
    r1 = client.post("/api/v1/search", json={"query": "test", "top_k": 1})
    # Since search throws 422 if repository is empty and FAISS not ready, we use health? No, health is exempt.
    # Let's use a 422 return directly, rate limit is checked BEFORE 422 validation? Depends on routing.
    # Let's just use empty search request to trigger 422, rate limit is checked first if applied via dependencies.
    
    # 1st request
    client.post("/api/v1/search", json={"query": "test"})
    # 2nd request
    client.post("/api/v1/search", json={"query": "test"})
    
    # 3rd request should be 429
    r3 = client.post("/api/v1/search", json={"query": "test"})
    assert r3.status_code == 429
    assert r3.json()["detail"] == "Rate limit exceeded"
    
    # Reset limit
    api_settings.rate_limit = "100/hour"
