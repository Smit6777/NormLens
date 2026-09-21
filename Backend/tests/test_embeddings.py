"""Tests for the embeddings service (Phase 2)."""
import numpy as np

from app.services.embeddings import EmbeddingService, build_search_text, l2_normalize


def test_batch_shape_dtype_and_normalization(embedding_service):
    vecs = embedding_service.generate_embeddings(["portland cement", "led lamp"])
    assert vecs.shape == (2, 64) and vecs.dtype == np.float32
    assert np.allclose(np.linalg.norm(vecs, axis=1), 1.0, atol=1e-5)


def test_single_embedding_is_1d(embedding_service):
    assert embedding_service.generate_embedding("cement").shape == (64,)


def test_empty_batch(embedding_service):
    assert embedding_service.generate_embeddings([]).shape == (0, 0)


def test_dimension_read_from_model(embedding_service):
    assert embedding_service.dimension == 64


def test_normalize_can_be_disabled(fake_encoder):
    svc = EmbeddingService(model_name="fake", encoder=fake_encoder, normalize=False)
    assert not np.allclose(np.linalg.norm(svc.generate_embedding("cement cement cement")), 1.0)


def test_l2_normalize_zero_vector_safe():
    assert np.all(l2_normalize(np.zeros((1, 4))) == 0)


def test_deterministic(embedding_service):
    a = embedding_service.generate_embedding("same text")
    b = embedding_service.generate_embedding("same text")
    assert np.array_equal(a, b)


def test_build_search_text_only_allowed_fields():
    text = build_search_text({
        "is_number": "X-1", "title": "T", "keywords": ["a", "b"], "product": "P", "sector": "S",
        "scope_summary": "scope", "source_id": "SRC-SECRET", "url": "http://x", "confidence": "HIGH",
    })
    assert text == "X-1 | T | a, b | P | S | scope"
    assert "SRC-SECRET" not in text and "http" not in text
