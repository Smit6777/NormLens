"""
Reranker: re-orders retrieved candidates using explainable components.

Components (each in [0, 1]):
  semantic_similarity  -- the retrieval cosine score (always evaluable)
  keyword_overlap      -- overlap of requirement terms with the standard's keywords + title
  product_match        -- standard's product vs. the requirement
  sector_match         -- standard's sector vs. the requirement
  scope_relevance      -- overlap of requirement terms with the standard's public scope summary

"Unknown is not a mismatch" (project Rule 2): a component is only scored
when there is evidence either way. Absence of data -- the standard has no
product field, or the requirement never mentions/declares one -- makes the
component NOT EVALUATED: it is left out of the score and the remaining
weights are renormalized, so missing data never silently penalizes a
candidate. Every returned result lists the components used and those skipped.

The final score is an INTERNAL ranking score only. It is not an official
BIS score and not evidence of compliance (Rule 5).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from app.core.logging import get_logger
from app.models.schemas import ExtractedRequirement

logger = get_logger(__name__)

_STOPWORDS = frozenset(
    "a an and are as at be by for from in is it of on or shall should that the this to with must will "
    "may per any all its their than then these those such other into over under using used use "
    "supply provide provided required conform conforming standard specification specified".split()
)


@dataclass(frozen=True)
class RerankWeights:
    semantic_similarity: float = 0.60
    keyword_overlap: float = 0.20
    product_match: float = 0.10
    sector_match: float = 0.05
    scope_relevance: float = 0.05

    def __post_init__(self) -> None:
        values = self.as_dict().values()
        if any(v < 0 for v in values):
            raise ValueError("Rerank weights must be non-negative.")
        if self.semantic_similarity <= 0:
            raise ValueError("semantic_similarity weight must be > 0 (it is the only always-evaluable component).")

    def as_dict(self) -> dict[str, float]:
        return {
            "semantic_similarity": self.semantic_similarity,
            "keyword_overlap": self.keyword_overlap,
            "product_match": self.product_match,
            "sector_match": self.sector_match,
            "scope_relevance": self.scope_relevance,
        }


@dataclass(frozen=True)
class ScoredCandidate:
    """A retrieved candidate: the knowledge-base record plus its retrieval (cosine) score."""

    record: dict[str, Any]
    semantic_score: float


@dataclass
class RerankedCandidate:
    record: dict[str, Any]
    final_score: float
    components: dict[str, float]
    not_evaluated: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def _stem(token: str) -> str:
    return token[:-1] if len(token) > 3 and token.endswith("s") and not token.endswith("ss") else token


def _tokens(text: str) -> set[str]:
    return {_stem(t) for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOPWORDS}


def _contains_phrase(text: str, phrase: str) -> bool:
    return bool(re.search(r"(?<!\w)" + re.escape(phrase.strip().lower()) + r"(?!\w)", text.lower()))


def _overlap(a: set[str], b: set[str]) -> tuple[float, list[str]]:
    """Overlap coefficient |a∩b| / min(|a|,|b|), plus the shared terms."""
    if not a or not b:
        return 0.0, []
    shared = sorted(a & b)
    return len(shared) / min(len(a), len(b)), shared


class Reranker:
    def __init__(self, weights: RerankWeights | None = None) -> None:
        self._weights = weights or RerankWeights()

    def rerank(
        self, requirement: ExtractedRequirement | str, candidates: Iterable[ScoredCandidate]
    ) -> list[RerankedCandidate]:
        """Score and sort candidates (best first; ties broken by semantic score, then IS number)."""
        if isinstance(requirement, str):
            text, req_product, req_category = requirement, None, None
        else:
            text, req_product, req_category = requirement.raw_text, requirement.product, requirement.category
        req_tokens = _tokens(text)

        results = [self._score(c, text, req_tokens, req_product, req_category) for c in candidates]
        results.sort(key=lambda r: (-r.final_score, -r.components["semantic_similarity"], r.record.get("is_number", "")))
        return results

    # ------------------------------------------------------------------

    def _score(
        self, cand: ScoredCandidate, text: str, req_tokens: set[str],
        req_product: str | None, req_category: str | None,
    ) -> RerankedCandidate:
        rec = cand.record
        components: dict[str, float] = {}
        reasons: list[str] = []
        skipped: list[str] = []

        sem = max(0.0, min(1.0, cand.semantic_score))
        components["semantic_similarity"] = sem
        reasons.append(f"Semantic similarity {sem:.2f} between the requirement and the standard's public metadata.")

        # keyword overlap: keywords + title
        kw_terms = _tokens(" ".join(str(k) for k in rec.get("keywords") or []) + " " + (rec.get("title") or ""))
        if kw_terms:
            score, shared = _overlap(req_tokens, kw_terms)
            components["keyword_overlap"] = score
            if shared:
                reasons.append("Shared keyword/title terms: " + ", ".join(shared[:6]) + ".")
        else:
            skipped.append("keyword_overlap")

        # product
        product = (rec.get("product") or "").strip()
        if not product:
            skipped.append("product_match")
        elif req_product:
            same = req_product.strip().casefold() == product.casefold()
            components["product_match"] = 1.0 if same else 0.0
            reasons.append(
                f"Requirement product '{req_product}' matches the standard's product."
                if same else f"Requirement product '{req_product}' differs from the standard's product '{product}'."
            )
        elif _contains_phrase(text, product):
            components["product_match"] = 1.0
            reasons.append(f"The standard's product '{product}' is mentioned in the requirement.")
        else:
            skipped.append("product_match")

        # sector
        sector = (rec.get("sector") or "").strip()
        if not sector:
            skipped.append("sector_match")
        elif req_category:
            same = req_category.strip().casefold() == sector.casefold()
            components["sector_match"] = 1.0 if same else 0.0
            reasons.append(
                f"Requirement category '{req_category}' matches the standard's sector."
                if same else f"Requirement category '{req_category}' differs from the standard's sector '{sector}'."
            )
        elif _contains_phrase(text, sector):
            components["sector_match"] = 1.0
            reasons.append(f"The standard's sector '{sector}' is mentioned in the requirement.")
        else:
            skipped.append("sector_match")

        # scope relevance
        scope_terms = _tokens(rec.get("scope_summary") or "")
        if scope_terms:
            score, shared = _overlap(req_tokens, scope_terms)
            components["scope_relevance"] = score
            if shared:
                reasons.append("Shared scope-summary terms: " + ", ".join(shared[:6]) + ".")
        else:
            skipped.append("scope_relevance")

        weights = self._weights.as_dict()
        total = sum(weights[name] for name in components)
        final = sum(weights[name] * value for name, value in components.items()) / total
        return RerankedCandidate(
            record=rec, final_score=max(0.0, min(1.0, final)), components=components,
            not_evaluated=skipped, reasons=reasons,
        )
