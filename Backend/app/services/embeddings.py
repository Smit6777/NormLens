"""
Embedding generation service.

Wraps sentence-transformers behind a small interface so the rest of the
application depends on `generate_embedding` / `generate_embeddings`, not
on the sentence-transformers API directly -- swapping models or
providers later only touches this file.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol
import time
import httpx
import os
import numpy as np

from app.core.logging import get_logger

if TYPE_CHECKING:  # pragma: no cover
    from app.models.schemas import ExtractedRequirement

logger = get_logger(__name__)


class Encoder(Protocol):
    def encode(self, texts: list[str], **kwargs: Any) -> Any: ...


class HFApiEncoder:
    """Uses Hugging Face Inference API instead of local heavy PyTorch."""
    def __init__(self, model_name: str):
        self.api_url = f"https://router.huggingface.co/hf-inference/pipeline/feature-extraction/sentence-transformers/{model_name}"
        self.headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"} if os.environ.get("HF_TOKEN") else {}

    def encode(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        logger.info(f"Sending {len(texts)} texts to HF Inference API...")
        for attempt in range(5):
            try:
                response = httpx.post(self.api_url, headers=self.headers, json={"inputs": texts}, timeout=45.0)
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 503 and "loading" in response.text.lower():
                    logger.info(f"HF model loading, waiting 15s... (Attempt {attempt+1}/5)")
                    time.sleep(15)
                    continue
                if response.status_code >= 400:
                    raise Exception(f"HF API returned {response.status_code}: {response.text}")
                response.raise_for_status()
            except Exception as e:
                logger.error(f"HF API Error: {e}")
                if attempt == 4:
                    raise
                time.sleep(5)
        raise Exception("HF API failed to respond.")


def _load_sentence_transformer(model_name: str) -> Encoder:
    logger.info("Loading HFApiEncoder (API-based) instead of local model", extra={"context": {"model": model_name}})
    return HFApiEncoder(model_name)


def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize rows of a 2-D array. Zero vectors are left as zeros."""
    vectors = np.asarray(vectors, dtype="float32")
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
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
        self._dimension: int | None = 768

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = 768
        return self._dimension

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype="float32")
        raw = self._encoder.encode(list(texts))
        vectors = np.asarray(raw, dtype="float32")
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        elif vectors.ndim == 3:
            vectors = np.mean(vectors, axis=1) # Mean pooling if HF returns token embeddings
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


def build_requirement_search_text(requirement: "ExtractedRequirement") -> str:
    parts = [requirement.product, requirement.category, requirement.raw_text]
    return " | ".join(p.strip() for p in parts if p and p.strip())
