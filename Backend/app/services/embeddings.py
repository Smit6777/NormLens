from __future__ import annotations
from typing import Any, Protocol
import numpy as np
from app.core.logging import get_logger
import os

logger = get_logger(__name__)

class Encoder(Protocol):
    def encode(self, texts: list[str], **kwargs: Any) -> Any: ...

class FastEmbedEncoder:
    def __init__(self, model_name: str):
        logger.info(f"Loading FastEmbed model: {model_name}...")
        from fastembed import TextEmbedding
        self.model = TextEmbedding(model_name=model_name)
    
    def encode(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        # embed returns a generator of numpy arrays
        return list(self.model.embed(texts))

def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    vectors = np.asarray(vectors, dtype="float32")
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return vectors / norms

class EmbeddingService:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        encoder: Encoder | None = None,
        normalize: bool = True,
    ):
        self.model_name = model_name
        self.normalize = normalize
        self._encoder: Encoder = encoder if encoder is not None else FastEmbedEncoder(model_name)
        self._dimension: int | None = 384

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = 384
        return self._dimension

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype="float32")
        raw = self._encoder.encode(list(texts))
        vectors = np.asarray(raw, dtype="float32")
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        elif vectors.ndim == 3:
            vectors = np.mean(vectors, axis=1)
        if vectors.ndim != 2:
            raise ValueError(f"Encoder returned shape {vectors.shape}; expected (n, dim).")
        if self._dimension is None:
            self._dimension = int(vectors.shape[1])
        return l2_normalize(vectors) if self.normalize else vectors

    def generate_embedding(self, text: str) -> np.ndarray:
        return self.generate_embeddings([text])[0]

_SEARCH_TEXT_FIELDS = ("is_number", "title", "keywords", "product", "sector", "scope_summary")

def build_search_text(record: dict[str, Any]) -> str:
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

def build_requirement_search_text(requirement) -> str:
    parts = [requirement.product, requirement.category, requirement.raw_text]
    return " | ".join(p.strip() for p in parts if p and p.strip())
