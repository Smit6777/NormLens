"""
API tests supplied by the user from Claude's Phase 6 work.

NOTE:
This file depends on the rest of the original repository, including
tests/conftest.py and all app services. This handoff package contains
only the code explicitly supplied in the conversation, so Antigravity
must merge this with the original Claude repository rather than treating
this ZIP as a complete runnable project.
"""
import pytest
from app.core.config import Settings

@pytest.fixture(scope="module")
def api_settings(tmp_path_factory, compliance_kb_module):
    return Settings(
        data_dir=compliance_kb_module,
        vector_index_dir=tmp_path_factory.mktemp("index"),
        min_match_score=0.0,
        top_k_candidates=5,
    )

@pytest.fixture(scope="module")
def compliance_kb_module(tmp_path_factory):
    import json as _json
    d = tmp_path_factory.mktemp("kb")

    def std(is_number, title, **kw):
        return {"is_number": is_number, "title": title,
                "product": kw.pop("product", None), **kw}

    metadata = [
        std("TEST-IS-100:2020", "Widget specification",
            product="Test Widget", source_id="TEST-SRC-1",
            scope_summary="Fictitious widget scope.", keywords=["widget"]),
        std("TEST-IS-300:2015", "Withdrawn thing"),
    ]
    compliance = {
        "TEST-IS-100:2020": {
            "standard_status": "ACTIVE",
            "current_version": "TEST-IS-100:2020",
            "amendments": [],
            "qco_applicable": True,
            "certification_required": True,
            "testing_scheme": "Scheme-X",
            "normative_references": [],
            "source_id": "TEST-SRC-1",
        },
        "TEST-IS-300:2015": {
            "standard_status": "WITHDRAWN",
            "superseded_by": "TEST-IS-301:2022",
            "current_version": "TEST-IS-300:2015",
            "source_id": "TEST-SRC-1",
            "amendments": [],
        },
    }
    qco = [{
        "product": "Test Widget",
        "qco_name": "Test Widget QCO",
        "is_number": "TEST-IS-100:2020",
        "enforcement_date": "2020-01-01",
        "source_id": "TEST-SRC-Q",
    }]
    sources = {
        "TEST-SRC-1": {
            "title": "Test Source One",
            "url": "https://example.invalid/1"
        },
        "TEST-SRC-Q": {
            "title": "Test QCO Source",
            "url": "https://example.invalid/q"
        },
    }

    for name, content in {
        "bis_metadata.json": metadata,
        "bis_compliance.json": compliance,
        "qco_mapping.json": qco,
        "normative_graph.json": [],
        "sources.json": sources,
    }.items():
        (d / name).write_text(_json.dumps(content), encoding="utf-8")
    return d

@pytest.fixture(scope="module")
def app(api_settings):
    from tests.conftest import FakeEncoder
    from app.main import create_app
    return create_app(settings=api_settings, encoder=FakeEncoder())

@pytest.fixture(scope="module")
def client(app):
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

class TestRootAndHealth:
    def test_root_ok(self, client):
        resp = client.get("/api/v1/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_health_reports_app_name(self, client, api_settings):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["app_name"] == api_settings.app_name

class TestValidation:
    def test_search_rejects_empty_query(self, client):
        assert client.post("/api/v1/search", json={"query": ""}).status_code == 422

    def test_search_rejects_unknown_fields(self, client):
        assert client.post(
            "/api/v1/search",
            json={"query": "widget", "bogus_field": 1},
        ).status_code == 422

    def test_search_rejects_out_of_range_top_k(self, client):
        assert client.post(
            "/api/v1/search", json={"query": "widget", "top_k": 0}
        ).status_code == 422

    def test_extract_with_neither_file_nor_text_is_422(self, client):
        resp = client.post("/api/v1/extract")
        assert resp.status_code == 422
        assert resp.json()["error"] == "DocumentExtractionError"

    def test_analyze_with_neither_file_nor_text_is_422(self, client):
        assert client.post("/api/v1/analyze").status_code == 422

    def test_recommend_requires_requirement_body(self, client):
        assert client.post("/api/v1/recommend", json={}).status_code == 422

    def test_extract_rejects_unsupported_extension(self, client):
        resp = client.post(
            "/api/v1/extract",
            files={"file": ("tender.exe", b"not a real file",
                             "application/octet-stream")},
        )
        assert resp.status_code == 415

class TestStandardsLookup:
    def test_known_standard_returns_200_with_metadata(self, client):
        resp = client.get("/api/v1/standards/TEST-IS-100:2020")
        assert resp.status_code == 200
        body = resp.json()
        assert body["found_in_metadata"] is True
        assert body["title"] == "Widget specification"
        assert body["compliance"]["standard_status"] == "ACTIVE"

    def test_unknown_standard_is_200_not_verified_never_404(self, client):
        resp = client.get("/api/v1/standards/TEST-IS-NOPE-9999")
        assert resp.status_code == 200
        body = resp.json()
        assert body["found_in_metadata"] is False
        assert body["confidence"] == "NOT_VERIFIED"

    def test_withdrawn_standard_reports_withdrawn_status(self, client):
        resp = client.get("/api/v1/standards/TEST-IS-300:2015")
        assert resp.status_code == 200
        assert resp.json()["compliance"]["standard_status"] == "WITHDRAWN"

class TestAnalyzeEndToEnd:
    TENDER_TEXT = (
        "Supply of Test Widget units, quantity 50, for laboratory use, "
        "to be delivered within 30 days of purchase order."
    )

    def test_analyze_from_raw_text_returns_well_formed_response(self, client):
        resp = client.post("/api/v1/analyze", data={"text": self.TENDER_TEXT})
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["requirements"]) >= 1
        assert any(r["product"] == "Test Widget"
                   for r in body["requirements"])
