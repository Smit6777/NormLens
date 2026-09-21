"""
Index builder: knowledge-layer standards -> embeddings -> vector store.

Only text from `build_search_text` is embedded (public metadata; never
full BIS standard text). An empty knowledge base yields an empty index
rather than an error, so the app can start before data is curated; the
matcher then returns "insufficient evidence" for every query.
"""
from __future__ import annotations

from pathlib import Path

from app.core.logging import get_logger
from app.data_layer.repository import Repository
from app.services.embeddings import EmbeddingService, build_search_text
from app.services.vector_db import FaissVectorStore

logger = get_logger(__name__)


def build_index(
    repository: Repository,
    embedding_service: EmbeddingService,
    index_dir: Path | None = None,
) -> FaissVectorStore:
    """Build a FAISS store from every standard in the repository; persist it if `index_dir` is given."""
    standards = repository.get_all_standards()
    ids: list[str] = []
    texts: list[str] = []
    metadata: list[dict] = []
    for record in standards:
        text = build_search_text(record)
        if not text.strip():
            logger.warning("Skipping standard with empty search text", extra={"context": {"is_number": record.get("is_number")}})
            continue
        ids.append(record["is_number"])
        texts.append(text)
        metadata.append({k: record.get(k) for k in ("title", "product", "sector")})

    store = FaissVectorStore(embedding_service.dimension)
    if texts:
        store.add(ids, embedding_service.generate_embeddings(texts), metadata)
    else:
        logger.warning("Knowledge base has no indexable standards; index is empty.")

    if index_dir is not None:
        store.save(index_dir)
    logger.info("Index built", extra={"context": {"indexed": store.size, "model": embedding_service.model_name}})
    return store
