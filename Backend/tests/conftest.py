"""Shared pytest fixtures for the test suite."""
import json
from pathlib import Path

import pytest


@pytest.fixture
def tmp_knowledge_base(tmp_path: Path) -> Path:
    """Write a small, clearly-fake knowledge base for repository tests.

    IS numbers here are obviously fictitious test fixtures (prefixed
    ``TEST-``) -- never real BIS standards -- so they can never be
    mistaken for genuine data if a test failure surfaces them in a log
    or report.
    """
    metadata = [
        {
            "is_number": "TEST-IS-0001",
            "title": "Test Standard One",
            "keywords": ["test", "fixture"],
            "product": "Test Widget",
            "sector": "Testing",
            "scope_summary": "A fictitious standard used only for unit tests.",
        }
    ]
    compliance = {
        "TEST-IS-0001": {
            "standard_status": "ACTIVE",
            "current_version": "TEST-IS-0001:2024",
            "amendments": [],
            "qco_applicable": False,
        }
    }
    qco_mapping = [
        {"product": "Test Widget", "qco_name": "Test QCO", "is_number": "TEST-IS-0001"}
    ]
    normative_graph = [
        {
            "from_is": "TEST-IS-0001",
            "to_is": "TEST-IS-0002",
            "relationship_type": "REFERENCES_TEST_METHOD",
            "source_id": "TEST-SRC-1",
        }
    ]
    sources = {
        "TEST-SRC-1": {"title": "Test Source", "url": "https://example.invalid/test"}
    }

    files = {
        "bis_metadata.json": metadata,
        "bis_compliance.json": compliance,
        "qco_mapping.json": qco_mapping,
        "normative_graph.json": normative_graph,
        "sources.json": sources,
    }
    for filename, content in files.items():
        (tmp_path / filename).write_text(json.dumps(content), encoding="utf-8")

    return tmp_path


# ---------------------------------------------------------------------------
# Phase 2 fixtures: fake encoder + tiny fictitious corpus (no model download)
# ---------------------------------------------------------------------------
import hashlib
import re

import numpy as np


class FakeEncoder:
    """Deterministic bag-of-words hashing encoder. Texts sharing words get similar vectors."""

    DIM = 64

    def encode(self, texts, **kwargs):
        out = np.zeros((len(texts), self.DIM), dtype="float32")
        for i, text in enumerate(texts):
            for word in re.findall(r"[a-z0-9]+", text.lower()):
                h = int(hashlib.md5(word.encode()).hexdigest(), 16)
                out[i, h % self.DIM] += 1.0
        return out


@pytest.fixture
def fake_encoder() -> FakeEncoder:
    return FakeEncoder()


@pytest.fixture
def embedding_service(fake_encoder):
    from app.services.embeddings import EmbeddingService

    return EmbeddingService(model_name="fake", encoder=fake_encoder)


@pytest.fixture
def search_kb(tmp_path: Path) -> Path:
    """Knowledge base with three fictitious standards (TEST- prefixed) for search tests."""
    metadata = [
        {"is_number": "TEST-IS-CEMENT", "title": "Portland cement specification",
         "keywords": ["cement", "portland", "binder"], "product": "Cement",
         "sector": "Building Materials", "scope_summary": "Covers manufacture and chemical requirements of portland cement.",
         "source_id": "TEST-SRC-1"},
        {"is_number": "TEST-IS-LAMP", "title": "LED lamp performance",
         "keywords": ["led", "lamp", "lighting"], "product": "LED Lamp",
         "sector": "Electrical", "scope_summary": "Performance requirements for LED lamps for general lighting.",
         "source_id": "TEST-SRC-2"},
        {"is_number": "TEST-IS-PIPE", "title": "Steel water pipe",
         "keywords": ["pipe", "steel", "water"], "product": "Pipe",
         "sector": "Plumbing", "scope_summary": "Steel pipes for water supply."},
    ]
    files = {"bis_metadata.json": metadata, "bis_compliance.json": {}, "qco_mapping.json": [],
             "normative_graph.json": [], "sources.json": {}}
    for name, content in files.items():
        (tmp_path / name).write_text(json.dumps(content), encoding="utf-8")
    return tmp_path


@pytest.fixture
def search_repo(search_kb: Path):
    from app.data_layer.repository import Repository

    return Repository(
        metadata_path=search_kb / "bis_metadata.json", compliance_path=search_kb / "bis_compliance.json",
        qco_mapping_path=search_kb / "qco_mapping.json", normative_graph_path=search_kb / "normative_graph.json",
        sources_path=search_kb / "sources.json",
    )


# ---------------------------------------------------------------------------
# Phase 3 fixtures: in-memory PDF builder (no PDF-writing dependency needed)
# ---------------------------------------------------------------------------
def build_pdf(pages: list[str]) -> bytes:
    """Build a minimal valid multi-page text PDF (Helvetica). Each string is one page; '\\n' = new line."""

    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    bodies: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    kids = []
    for i, text in enumerate(pages):
        page_id, content_id = 4 + 2 * i, 5 + 2 * i
        kids.append(f"{page_id} 0 R")
        ops = ["BT", "/F1 11 Tf", "50 750 Td", "16 TL"]
        for line in text.split("\n"):
            ops.append(f"({esc(line)}) Tj T*")
        ops.append("ET")
        stream = "\n".join(ops).encode("latin-1")
        bodies[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {content_id} 0 R "
            f"/Resources << /Font << /F1 3 0 R >> >> >>"
        ).encode()
        bodies[content_id] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
    bodies[2] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(pages)} >>".encode()

    out = bytearray(b"%PDF-1.4\n")
    offsets = {}
    for obj_id in sorted(bodies):
        offsets[obj_id] = len(out)
        out += f"{obj_id} 0 obj\n".encode() + bodies[obj_id] + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(bodies) + 1}\n".encode() + b"0000000000 65535 f \n"
    for obj_id in sorted(bodies):
        out += f"{offsets[obj_id]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(bodies) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    return bytes(out)


@pytest.fixture
def make_pdf():
    return build_pdf
