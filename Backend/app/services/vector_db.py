"""
Vector store abstraction and FAISS implementation.

The rest of the app depends on the `VectorStore` interface only, so FAISS
can later be replaced (e.g. pgvector) without touching the matcher.

The store maps FAISS row positions to string ids (IS numbers). It holds
no BIS facts itself -- only vectors and ids. Cosine similarity is
obtained via inner product over L2-normalized vectors; the store
normalizes defensively so callers cannot get this wrong.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from app.core.exceptions import DataLoadError, ModelNotReadyError
from app.core.logging import get_logger
from app.services.embeddings import l2_normalize

logger = get_logger(__name__)

INDEX_FILENAME = "standards.faiss"
IDS_FILENAME = "standards_ids.json"


@dataclass(frozen=True)
class SearchHit:
    id: str
    score: float  # cosine similarity in [-1, 1]
    # Lightweight denormalized display metadata stored alongside the vector.
    # NOT authoritative: facts must always be re-read from the Repository.
    metadata: dict = field(default_factory=dict)


class VectorStore(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int: ...

    @property
    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def add(self, ids: list[str], vectors: np.ndarray, metadata: list[dict] | None = None) -> None: ...

    @abstractmethod
    def search(self, query: np.ndarray, top_k: int) -> list[SearchHit]: ...

    @abstractmethod
    def save(self, directory: Path) -> None: ...


class FaissVectorStore(VectorStore):
    """Exact (flat) inner-product FAISS index. Ample for hundreds/thousands of standards."""

    def __init__(self, dimension: int) -> None:
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        import faiss

        self._dimension = dimension
        self._index = faiss.IndexFlatIP(dimension)
        self._ids: list[str] = []
        self._metadata: list[dict] = []

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def size(self) -> int:
        return len(self._ids)

    def add(self, ids: list[str], vectors: np.ndarray, metadata: list[dict] | None = None) -> None:
        vectors = np.asarray(vectors, dtype="float32")
        if len(ids) == 0:
            return
        if metadata is not None and len(metadata) != len(ids):
            raise ValueError(f"Got {len(ids)} ids but {len(metadata)} metadata records.")
        if vectors.ndim != 2 or vectors.shape[0] != len(ids):
            raise ValueError(f"Got {len(ids)} ids but vectors of shape {vectors.shape}.")
        if vectors.shape[1] != self._dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} != index dimension {self._dimension}.")
        if len(set(ids)) != len(ids) or set(ids) & set(self._ids):
            raise ValueError("Duplicate ids are not allowed in the vector store.")
        self._index.add(np.ascontiguousarray(l2_normalize(vectors)))
        self._ids.extend(ids)
        self._metadata.extend(dict(m) for m in metadata) if metadata is not None else self._metadata.extend({} for _ in ids)

    def search(self, query: np.ndarray, top_k: int) -> list[SearchHit]:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        if self.size == 0:
            return []
        q = np.asarray(query, dtype="float32").reshape(1, -1)
        if q.shape[1] != self._dimension:
            raise ValueError(f"Query dimension {q.shape[1]} != index dimension {self._dimension}.")
        scores, positions = self._index.search(np.ascontiguousarray(l2_normalize(q)), min(top_k, self.size))
        return [
            SearchHit(id=self._ids[pos], score=float(score), metadata=dict(self._metadata[pos]))
            for score, pos in zip(scores[0], positions[0])
            if pos >= 0
        ]

    def save(self, directory: Path) -> None:
        import faiss

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(directory / INDEX_FILENAME))
        (directory / IDS_FILENAME).write_text(
            json.dumps({"dimension": self._dimension, "ids": self._ids, "metadata": self._metadata}), encoding="utf-8"
        )
        logger.info("Vector index saved", extra={"context": {"dir": str(directory), "size": self.size}})

    @classmethod
    def load(cls, directory: Path) -> "FaissVectorStore":
        import faiss

        directory = Path(directory)
        index_path, ids_path = directory / INDEX_FILENAME, directory / IDS_FILENAME
        if not index_path.exists() or not ids_path.exists():
            raise ModelNotReadyError(
                "Vector index not found; build it first.", details={"dir": str(directory)}
            )
        try:
            meta = json.loads(ids_path.read_text(encoding="utf-8"))
            index = faiss.read_index(str(index_path))
        except (OSError, ValueError, RuntimeError) as exc:
            raise DataLoadError(f"Could not read vector index: {exc}", details={"dir": str(directory)}) from exc
        if index.ntotal != len(meta["ids"]) or index.d != meta["dimension"]:
            raise DataLoadError("Vector index and id map are inconsistent.", details={"dir": str(directory)})
        store = cls(meta["dimension"])
        store._index = index
        store._ids = list(meta["ids"])
        store._metadata = list(meta.get("metadata") or [{} for _ in store._ids])
        if len(store._metadata) != len(store._ids):
            raise DataLoadError("Vector index metadata and id map are inconsistent.", details={"dir": str(directory)})
        return store
