"""
Matcher service: requirement text -> ranked candidate standards.

Anti-hallucination guarantees (project Rules 1, 2, 5):
  * Only IS numbers present in BOTH the vector index and the repository
    are ever returned; nothing is generated.
  * Hits below `min_score` are dropped. If none remain the result status
    is INSUFFICIENT_EVIDENCE -- never a guess.
  * `system_match_score` is an internal similarity score only. Compliance
    `confidence` is left NOT_VERIFIED here; Phase 4 owns it.
  * Evidence is the standard's public scope text, taken verbatim from the
    knowledge layer, with its source_id for traceability.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.core.logging import get_logger
from app.data_layer.repository import Repository
from app.models.schemas import ConfidenceLevel, Evidence, ExtractedRequirement, Recommendation
from app.services.embeddings import EmbeddingService, build_requirement_search_text
from app.services.reranker import RerankedCandidate, Reranker, ScoredCandidate
from app.services.vector_db import VectorStore

logger = get_logger(__name__)


class MatchStatus(str, Enum):
    OK = "OK"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass
class MatchResult:
    status: MatchStatus
    recommendations: list[Recommendation] = field(default_factory=list)
    message: str | None = None


class Matcher:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        repository: Repository,
        top_k: int = 10,
        min_score: float = 0.3,
        reranker: Reranker | None = None,
        retrieval_multiplier: int = 3,
        provenance: Any = None,
    ) -> None:
        self._embeddings = embedding_service
        self._store = vector_store
        self._repo = repository
        self._top_k = top_k
        self._min_score = min_score
        self._reranker = reranker
        self._retrieval_multiplier = max(1, retrieval_multiplier)

    def match(self, requirement_text: str, top_k: int | None = None) -> MatchResult:
        """Match free text (e.g. a search query)."""
        text = (requirement_text or "").strip()
        if not text:
            return MatchResult(MatchStatus.INSUFFICIENT_EVIDENCE, message="Empty requirement text.")
        return self._run(text, text, top_k)

    def match_requirement(self, requirement: ExtractedRequirement, top_k: int | None = None) -> MatchResult:
        """Match a structured requirement; its product/category also feed the reranker."""
        if not requirement.raw_text.strip():
            return MatchResult(MatchStatus.INSUFFICIENT_EVIDENCE, message="Empty requirement text.")
        return self._run(build_requirement_search_text(requirement), requirement, top_k)

    def _run(self, query_text: str, rerank_input: "ExtractedRequirement | str", top_k: int | None) -> MatchResult:
        k = top_k or self._top_k
        pool = k * self._retrieval_multiplier if self._reranker else k
        hits = self._store.search(self._embeddings.generate_embedding(query_text), pool)

        candidates: list[ScoredCandidate] = []
        for hit in hits:
            if hit.score < self._min_score:
                continue
            record = self._repo.get_standard(hit.id)
            if record is None:  # stale index entry: never surface it
                logger.warning("Index hit not in repository; dropped", extra={"context": {"id": hit.id}})
                continue
            candidates.append(ScoredCandidate(record=record, semantic_score=hit.score))

        if not candidates:
            return MatchResult(
                MatchStatus.INSUFFICIENT_EVIDENCE,
                message="No standard in the local knowledge base matched with sufficient similarity. Manual verification required.",
            )

        if self._reranker is not None:
            ranked = self._reranker.rerank(rerank_input, candidates)[:k]
        else:
            ranked = [
                RerankedCandidate(
                    record=c.record, final_score=c.semantic_score,
                    components={"semantic_similarity": max(0.0, min(1.0, c.semantic_score))},
                    reasons=["Semantic similarity between requirement text and the standard's public metadata/scope."],
                )
                for c in candidates[:k]
            ]
        return MatchResult(MatchStatus.OK, [self._to_recommendation(r) for r in ranked])

    @staticmethod
    def _to_recommendation(ranked: RerankedCandidate) -> Recommendation:
        record = ranked.record
        source_id = record.get("source_id")
        scope = record.get("scope_summary")
        evidence = (
            [Evidence(source_id=source_id, document_title=record.get("title"), evidence_text=scope)]
            if scope
            else []
        )
        return Recommendation(
            is_number=record["is_number"],
            title=record.get("title", ""),
            system_match_score=max(0.0, min(1.0, ranked.final_score)),
            match_reasons=list(ranked.reasons),
            score_components={k: round(v, 4) for k, v in ranked.components.items()},
            evidence=evidence,
            source_ids=[source_id] if source_id else [],
            confidence=ConfidenceLevel.NOT_VERIFIED,
            verification_required=["Compliance status, version and QCO not yet checked (Phase 4)."],
        )
