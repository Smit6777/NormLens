import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import Settings
import json

@pytest.fixture(scope="module")
def api_settings(tmp_path_factory):
    d = tmp_path_factory.mktemp("kb")
    
    # Initialize basic files
    for name in ["bis_metadata.json", "qco_mapping.json", "normative_graph.json"]:
        (d / name).write_text("[]", encoding="utf-8")
    for name in ["bis_compliance.json", "sources.json"]:
        (d / name).write_text("{}", encoding="utf-8")
        
    import os
    os.environ["ENABLE_LLM_EXTRACTOR"] = "true"
    os.environ["ENABLE_HINDI"] = "true"
    os.environ["ENABLE_CACHE"] = "true"
    
    # Must import and clear cache if it was already loaded
    from app.core.config import get_settings
    get_settings.cache_clear()
    
    return Settings(
        data_dir=d,
        vector_index_dir=tmp_path_factory.mktemp("index"),
    )

@pytest.fixture(scope="module")
def client(api_settings):
    from tests.conftest import FakeEncoder
    from app.core.config import get_settings
    app = create_app(settings=api_settings, encoder=FakeEncoder())
    app.dependency_overrides[get_settings] = lambda: api_settings
    with TestClient(app) as c:
        yield c

def test_multilingual_translation(api_settings):
    from app.services.multilingual import translate_to_english
    assert translate_to_english("सीमेंट") == "cement"
    assert translate_to_english("This is a test") == "This is a test"

def test_llm_extractor_integration(client, api_settings):
    response = client.post("/api/v1/analyze", data={"text": "This is a complex requirement"})
    assert response.status_code == 200
    data = response.json()
    req_ids = [r["requirement_id"] for r in data["requirements"]]
    assert "LLM-REQ-001" in req_ids

def test_cache_hits(client):
    from app.core.cache import cache_get
    
    # Issue search
    res1 = client.post("/api/v1/search", json={"query": "cement", "top_k": 5})
    assert res1.status_code == 200
    
    # Check cache
    cached = cache_get("search", query="cement", top_k=5)
    assert cached is not None
    assert cached["query"] == "cement"

def test_analytics_tracking(client):
    from app.services.analytics import get_usage
    
    # Start with 0
    count_before = get_usage("IS 269")
    
    # Force a tracking via direct call or recommend
    # We will just call the function for pure unit test approach since mock data might not trigger recommendation for IS 269
    from app.services.analytics import track_recommendation
    track_recommendation("IS 269")
    
    count_after = get_usage("IS 269")
    assert count_after == count_before + 1

def test_export_endpoint(client):
    # Pass arbitrary text to get a response
    response = client.post("/api/v1/analyze/export", data={"text": "cement requirements"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Requirement ID" in response.text
