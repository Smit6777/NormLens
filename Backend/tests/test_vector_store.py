"""Tests for the FAISS vector store (Phase 2)."""
import numpy as np
import pytest

from app.core.exceptions import ModelNotReadyError
from app.services.vector_db import FaissVectorStore


def _store():
    s = FaissVectorStore(3)
    s.add(["a", "b", "c"], np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype="float32"))
    return s


def test_search_ranks_by_cosine():
    hits = _store().search(np.array([1, 0, 0], dtype="float32"), 3)
    assert [h.id for h in hits] == ["a", "c", "b"]
    assert hits[0].score == pytest.approx(1.0, abs=1e-5)
    assert hits[1].score == pytest.approx(0.7071, abs=1e-3)


def test_scale_invariance_cosine():
    hits = _store().search(np.array([50, 0, 0], dtype="float32"), 1)
    assert hits[0].id == "a" and hits[0].score == pytest.approx(1.0, abs=1e-5)


def test_top_k_larger_than_size():
    assert len(_store().search(np.array([1, 0, 0], dtype="float32"), 100)) == 3


def test_empty_store_returns_no_hits():
    assert FaissVectorStore(3).search(np.array([1, 0, 0], dtype="float32"), 5) == []


def test_dimension_mismatch_rejected():
    with pytest.raises(ValueError):
        _store().add(["z"], np.ones((1, 4), dtype="float32"))
    with pytest.raises(ValueError):
        _store().search(np.ones(4, dtype="float32"), 1)


def test_duplicate_ids_rejected():
    with pytest.raises(ValueError):
        _store().add(["a"], np.ones((1, 3), dtype="float32"))


def test_id_vector_count_mismatch_rejected():
    with pytest.raises(ValueError):
        FaissVectorStore(3).add(["a", "b"], np.ones((1, 3), dtype="float32"))


def test_invalid_top_k():
    with pytest.raises(ValueError):
        _store().search(np.ones(3, dtype="float32"), 0)


def test_save_and_load_roundtrip(tmp_path):
    _store().save(tmp_path)
    loaded = FaissVectorStore.load(tmp_path)
    assert loaded.size == 3 and loaded.dimension == 3
    assert loaded.search(np.array([0, 1, 0], dtype="float32"), 1)[0].id == "b"


def test_load_missing_index_raises(tmp_path):
    with pytest.raises(ModelNotReadyError):
        FaissVectorStore.load(tmp_path)


def test_metadata_returned_with_hits_and_persisted(tmp_path):
    s = FaissVectorStore(3)
    s.add(["a", "b"], np.array([[1, 0, 0], [0, 1, 0]], dtype="float32"), [{"title": "A"}, {"title": "B"}])
    assert s.search(np.array([1, 0, 0], dtype="float32"), 1)[0].metadata == {"title": "A"}
    s.save(tmp_path)
    assert FaissVectorStore.load(tmp_path).search(np.array([0, 1, 0], dtype="float32"), 1)[0].metadata == {"title": "B"}


def test_metadata_defaults_to_empty_and_length_checked():
    s = FaissVectorStore(3)
    s.add(["a"], np.ones((1, 3), dtype="float32"))
    assert s.search(np.ones(3, dtype="float32"), 1)[0].metadata == {}
    with pytest.raises(ValueError):
        s.add(["b"], np.ones((1, 3), dtype="float32"), [{}, {}])
