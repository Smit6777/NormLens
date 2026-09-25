"""
Embedding generation service.

Wraps sentence-transformers behind a small interface so the rest of the
application depends on `generate_embedding` / `generate_embeddings`, not
on the sentence-transformers API directly -- swapping models or
providers later only touches this file.

Per <ml_architecture>, the model must be loaded once (in the FastAPI
lifespan, Phase 6) and never per-request: `EmbeddingService.__init__`
loads it eagerly, exactly once, unless a fake `encoder` is injected for
tests -- which lets unit tests run without ever downloading a model.

Vectors are L2-normalized by default so that inner product == cosine
similarity downstream (FAISS IndexFlatIP).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

import numpy as np

from app.core.logging import get_logger

if TYPE_CHECKING:  # pragma: no cover
    from app.models.schemas import ExtractedRequirement

logger = get_logger(__name__)


class Encoder(Protocol):
    """Structural type for anything that can turn texts into vectors.

    `sentence_transformers.SentenceTransformer` satisfies this
    structurally (it has a compatible `.encode()` method) without this
    module needing to import it.
    """

    def encode(self, texts: list[str], **kwargs: Any) -> Any: ...


def _load_sentence_transformer(model_name: str) -> Encoder:
    # Imported lazily so this module -- and anything that only needs
    # build_search_text() -- stays importable without sentence-transformers
    # installed.
    from sentence_transformers import SentenceTransformer

    logger.info("Loading embedding model", extra={"context": {"model": model_name}})
    return SentenceTransformer(model_name)


def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize rows of a 2-D array. Zero vectors are left as zeros."""
    vectors = np.asarray(vectors, dtype="float32")
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return vectors / norms


class EmbeddingService:
    """Generates dense vector embeddings for standards text and requirement text."""

    def __init__(
        self,
        model_name: str = "all-mpnet-base-v2",
        encoder: Encoder | None = None,
        normalize: bool = True,
    ):
        self.model_name = model_name
        self.normalize = normalize
        self._encoder: Encoder = encoder if encoder is not None else _load_sentence_transformer(model_name)
        self._dimension: int | None = None

    @property
    def dimension(self) -> int:
        """Embedding dimensionality, read from the model (never hardcoded)."""
        if self._dimension is None:
            self._dimension = int(self.generate_embeddings(["dimension probe"]).shape[1])
        return self._dimension

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """Embed a batch of texts. Returns an (n, dim) float32 array."""
        if not texts:
            return np.zeros((0, 0), dtype="float32")
        vectors = np.asarray(self._encoder.encode(list(texts)), dtype="float32")
        if vectors.ndim != 2:
            raise ValueError(f"Encoder returned shape {vectors.shape}; expected (n, dim).")
        if self._dimension is None:
            self._dimension = int(vectors.shape[1])
        return l2_normalize(vectors) if self.normalize else vectors

    def generate_embedding(self, text: str) -> np.ndarray:
        """Embed a single text. Returns a (dim,) float32 array."""
        return self.generate_embeddings([text])[0]


# Fields combined into the text that actually gets embedded. Deliberately
# excludes URLs, source ids, dates, confidence values, and compliance
# flags -- those remain structured metadata (<ml_architecture>).
_SEARCH_TEXT_FIELDS = ("is_number", "title", "keywords", "product", "sector", "scope_summary")


def build_search_text(record: dict[str, Any]) -> str:
    """Build the text representation of a standard record that gets embedded.

    Combines IS number, title, keywords, product, sector, and scope
    summary only.
    """
    parts: list[str] = []
    for field_name in _SEARCH_TEXT_FIELDS:
        value = record.get(field_name)
        if not value:
            continue
        if isinstance(value, (list, tuple)):
            parts.append(", ".join(str(v) for v in value))
        else:
            parts.append(str(value))
    return " | ".join(parts)


def build_requirement_search_text(requirement: "ExtractedRequirement") -> str:
    """Search representation of a requirement, mirroring `build_search_text`.

    Uses product, category and the ORIGINAL raw text. Parameters, clause
    references, page numbers and cited standards are deliberately left out.
    """
    parts = [requirement.product, requirement.category, requirement.raw_text]
    return " | ".join(p.strip() for p in parts if p and p.strip())
