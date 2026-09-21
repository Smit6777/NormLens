"""Tests for the index builder and matcher (Phase 2)."""
import json

from app.services.index_builder import build_index
from app.services.matcher import Matcher, MatchStatus
from app.services.vector_db import FaissVectorStore


def _matcher(repo, svc, **kw):
    return Matcher(svc, build_index(repo, svc), repo, **kw)


def test_index_builder_indexes_all_and_persists(search_repo, embedding_service, tmp_path):
    store = build_index(search_repo, embedding_service, tmp_path / "idx")
    assert store.size == 3 and store.dimension == 64
    assert FaissVectorStore.load(tmp_path / "idx").size == 3


def test_index_builder_empty_kb(tmp_knowledge_base, embedding_service):
    from app.data_layer.repository import Repository

    (tmp_knowledge_base / "bis_metadata.json").write_text("[]")
    repo = Repository(*(tmp_knowledge_base / n for n in (
        "bis_metadata.json", "bis_compliance.json", "qco_mapping.json", "normative_graph.json", "sources.json")))
    store = build_index(repo, embedding_service)
    assert store.size == 0
    assert Matcher(embedding_service, store, repo).match("cement").status == MatchStatus.INSUFFICIENT_EVIDENCE


def test_match_finds_correct_standard(search_repo, embedding_service):
    result = _matcher(search_repo, embedding_service, min_score=0.2).match("portland cement for building")
    assert result.status == MatchStatus.OK
    top = result.recommendations[0]
    assert top.is_number == "TEST-IS-CEMENT"
    assert 0.0 <= top.system_match_score <= 1.0


def test_recommendation_has_evidence_and_no_compliance_confidence(search_repo, embedding_service):
    top = _matcher(search_repo, embedding_service, min_score=0.2).match("LED lamp lighting").recommendations[0]
    assert top.is_number == "TEST-IS-LAMP"
    assert top.evidence[0].evidence_text.startswith("Performance requirements")
    assert top.source_ids == ["TEST-SRC-2"]
    assert top.confidence.value == "NOT_VERIFIED" and top.verification_required


def test_low_similarity_yields_insufficient_evidence(search_repo, embedding_service):
    r = _matcher(search_repo, embedding_service, min_score=0.5).match("quantum banana telescope")
    assert r.status == MatchStatus.INSUFFICIENT_EVIDENCE and r.recommendations == [] and r.message


def test_empty_query_insufficient(search_repo, embedding_service):
    assert _matcher(search_repo, embedding_service).match("   ").status == MatchStatus.INSUFFICIENT_EVIDENCE


def test_only_indexed_repository_standards_returned(search_repo, embedding_service):
    r = _matcher(search_repo, embedding_service, min_score=0.0).match("cement lamp pipe")
    known = {s["is_number"] for s in search_repo.get_all_standards()}
    assert {x.is_number for x in r.recommendations} <= known


def test_stale_index_entry_is_dropped(search_repo, embedding_service, search_kb):
    store = build_index(search_repo, embedding_service)
    meta = json.loads((search_kb / "bis_metadata.json").read_text())
    (search_kb / "bis_metadata.json").write_text(json.dumps([m for m in meta if m["is_number"] != "TEST-IS-CEMENT"]))
    search_repo.reload()
    r = Matcher(embedding_service, store, search_repo, min_score=0.0).match("portland cement")
    assert "TEST-IS-CEMENT" not in {x.is_number for x in r.recommendations}


def test_top_k_respected(search_repo, embedding_service):
    r = _matcher(search_repo, embedding_service, min_score=-1.0).match("cement lamp pipe steel", top_k=2)
    assert len(r.recommendations) <= 2
