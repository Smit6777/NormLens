"""Tests for the reranker and its integration into the matcher (Phase 3)."""
import pytest

from app.models.schemas import ExtractedRequirement
from app.services.index_builder import build_index
from app.services.matcher import Matcher, MatchStatus
from app.services.reranker import RerankWeights, Reranker, ScoredCandidate

CEMENT = {"is_number": "TEST-IS-CEMENT", "title": "Portland cement specification",
          "keywords": ["cement", "portland"], "product": "Cement", "sector": "Building Materials",
          "scope_summary": "Covers manufacture and chemical requirements of portland cement."}
LAMP = {"is_number": "TEST-IS-LAMP", "title": "LED lamp performance", "keywords": ["led", "lamp"],
        "product": "LED Lamp", "sector": "Electrical", "scope_summary": "Performance of LED lamps."}
BARE = {"is_number": "TEST-IS-BARE"}  # no title/keywords/product/sector/scope


def _req(text, product=None, category=None):
    return ExtractedRequirement(requirement_id="REQ-001", raw_text=text, product=product, category=category)


def test_lexical_evidence_can_overturn_a_slightly_higher_semantic_score():
    ranked = Reranker().rerank(
        "Portland cement for foundations",
        [ScoredCandidate(LAMP, 0.60), ScoredCandidate(CEMENT, 0.55)],
    )
    assert [r.record["is_number"] for r in ranked] == ["TEST-IS-CEMENT", "TEST-IS-LAMP"]


def test_components_are_explainable_and_bounded():
    top = Reranker().rerank("Portland cement for foundations", [ScoredCandidate(CEMENT, 0.7)])[0]
    assert {"semantic_similarity", "keyword_overlap", "product_match", "scope_relevance"} <= set(top.components)
    assert all(0.0 <= v <= 1.0 for v in top.components.values()) and 0.0 <= top.final_score <= 1.0
    assert any("Cement" in r for r in top.reasons) and any("portland" in r for r in top.reasons)


def test_unknown_is_not_a_mismatch_component_skipped_not_zeroed():
    # Requirement names no product and no sector -> those components are not evaluated.
    r = Reranker().rerank("something about pipes", [ScoredCandidate(CEMENT, 0.5)])[0]
    assert "product_match" in r.not_evaluated and "sector_match" in r.not_evaluated
    assert "product_match" not in r.components


def test_missing_standard_fields_do_not_penalize():
    r = Reranker().rerank("anything at all", [ScoredCandidate(BARE, 0.5)])[0]
    assert set(r.components) == {"semantic_similarity"} and r.final_score == pytest.approx(0.5)
    assert set(r.not_evaluated) == {"keyword_overlap", "product_match", "sector_match", "scope_relevance"}


def test_declared_product_mismatch_is_scored_zero_and_explained():
    r = Reranker().rerank(_req("light source", product="LED Lamp", category="Electrical"), [ScoredCandidate(CEMENT, 0.5)])[0]
    assert r.components["product_match"] == 0.0 and r.components["sector_match"] == 0.0
    assert any("differs" in reason for reason in r.reasons)


def test_declared_product_match_scores_one():
    r = Reranker().rerank(_req("light source", product="led lamp"), [ScoredCandidate(LAMP, 0.5)])[0]
    assert r.components["product_match"] == 1.0


def test_structured_requirement_and_string_inputs_both_work():
    cand = [ScoredCandidate(CEMENT, 0.6)]
    assert Reranker().rerank("portland cement", cand)[0].final_score == pytest.approx(
        Reranker().rerank(_req("portland cement"), cand)[0].final_score)


def test_out_of_range_semantic_score_is_clamped():
    assert Reranker().rerank("x y z", [ScoredCandidate(BARE, -0.4)])[0].final_score == 0.0
    assert Reranker().rerank("x y z", [ScoredCandidate(BARE, 1.7)])[0].final_score == 1.0


def test_tie_break_is_deterministic():
    a, b = {"is_number": "TEST-B"}, {"is_number": "TEST-A"}
    ranked = Reranker().rerank("q", [ScoredCandidate(a, 0.5), ScoredCandidate(b, 0.5)])
    assert [r.record["is_number"] for r in ranked] == ["TEST-A", "TEST-B"]


def test_empty_candidates():
    assert Reranker().rerank("anything", []) == []


def test_custom_weights_change_ranking_and_are_validated():
    semantic_only = Reranker(RerankWeights(1.0, 0.0, 0.0, 0.0, 0.0))
    ranked = semantic_only.rerank("Portland cement", [ScoredCandidate(LAMP, 0.6), ScoredCandidate(CEMENT, 0.55)])
    assert ranked[0].record["is_number"] == "TEST-IS-LAMP"
    with pytest.raises(ValueError):
        RerankWeights(semantic_similarity=0.0)
    with pytest.raises(ValueError):
        RerankWeights(keyword_overlap=-0.1)


# ---- matcher integration ------------------------------------------------

def _matcher(repo, svc, **kw):
    return Matcher(svc, build_index(repo, svc), repo, min_score=0.1, **kw)


def test_matcher_with_reranker_exposes_components(search_repo, embedding_service):
    result = _matcher(search_repo, embedding_service, reranker=Reranker()).match("portland cement binder")
    top = result.recommendations[0]
    assert result.status == MatchStatus.OK and top.is_number == "TEST-IS-CEMENT"
    assert "semantic_similarity" in top.score_components and top.match_reasons
    assert top.confidence.value == "NOT_VERIFIED"


def test_matcher_without_reranker_still_reports_semantic_component(search_repo, embedding_service):
    top = _matcher(search_repo, embedding_service).match("portland cement").recommendations[0]
    assert set(top.score_components) == {"semantic_similarity"}


def test_match_requirement_uses_structured_fields(search_repo, embedding_service):
    req = _req("Supply of building material as per specification", product="Cement", category="Building Materials")
    top = _matcher(search_repo, embedding_service, reranker=Reranker()).match_requirement(req).recommendations[0]
    assert top.score_components["product_match"] == 1.0 and top.is_number == "TEST-IS-CEMENT"


def test_match_requirement_blank_text_insufficient(search_repo, embedding_service):
    assert _matcher(search_repo, embedding_service, reranker=Reranker()).match_requirement(_req("  ")).status == MatchStatus.INSUFFICIENT_EVIDENCE


def test_reranker_never_returns_standards_outside_the_knowledge_base(search_repo, embedding_service):
    r = _matcher(search_repo, embedding_service, reranker=Reranker()).match("cement lamp pipe")
    known = {s["is_number"] for s in search_repo.get_all_standards()}
    assert {x.is_number for x in r.recommendations} <= known
