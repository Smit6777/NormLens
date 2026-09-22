"""Tests for the knowledge-base repository (Phase 1)."""
import json
from pathlib import Path

import pytest

from app.core.exceptions import DataLoadError, DataValidationError
from app.data_layer.repository import Repository


def _build_repo(base: Path) -> Repository:
    return Repository(
        metadata_path=base / "bis_metadata.json",
        compliance_path=base / "bis_compliance.json",
        qco_mapping_path=base / "qco_mapping.json",
        normative_graph_path=base / "normative_graph.json",
        sources_path=base / "sources.json",
    )


def test_repository_loads_valid_knowledge_base(tmp_knowledge_base):
    repo = _build_repo(tmp_knowledge_base)

    standards = repo.get_all_standards()
    assert len(standards) == 1
    assert standards[0]["is_number"] == "TEST-IS-0001"


def test_get_standard_hit_and_miss(tmp_knowledge_base):
    repo = _build_repo(tmp_knowledge_base)

    assert repo.get_standard("TEST-IS-0001") is not None
    # A miss must return None, never raise -- "not found" != "does not exist".
    assert repo.get_standard("TEST-IS-9999-DOES-NOT-EXIST") is None


def test_get_compliance(tmp_knowledge_base):
    repo = _build_repo(tmp_knowledge_base)

    compliance = repo.get_compliance("TEST-IS-0001")
    assert compliance["standard_status"] == "ACTIVE"
    assert repo.get_compliance("UNKNOWN") is None


def test_get_qco_for_product_is_case_insensitive(tmp_knowledge_base):
    repo = _build_repo(tmp_knowledge_base)

    assert len(repo.get_qco_for_product("test widget")) == 1
    assert len(repo.get_qco_for_product("Test Widget")) == 1
    assert repo.get_qco_for_product("nonexistent product") == []


def test_get_normative_relationships(tmp_knowledge_base):
    repo = _build_repo(tmp_knowledge_base)

    rels = repo.get_normative_relationships("TEST-IS-0001")
    assert len(rels) == 1
    assert rels[0]["to_is"] == "TEST-IS-0002"
    assert repo.get_normative_relationships("UNKNOWN") == []


def test_get_source(tmp_knowledge_base):
    repo = _build_repo(tmp_knowledge_base)

    assert repo.get_source("TEST-SRC-1")["title"] == "Test Source"
    assert repo.get_source("UNKNOWN") is None


def test_missing_file_raises_data_load_error(tmp_path):
    with pytest.raises(DataLoadError):
        _build_repo(tmp_path)  # none of the five files exist in an empty tmp_path


def test_invalid_json_raises_data_load_error(tmp_path):
    (tmp_path / "bis_metadata.json").write_text("{not valid json", encoding="utf-8")
    (tmp_path / "bis_compliance.json").write_text("{}", encoding="utf-8")
    (tmp_path / "qco_mapping.json").write_text("[]", encoding="utf-8")
    (tmp_path / "normative_graph.json").write_text("[]", encoding="utf-8")
    (tmp_path / "sources.json").write_text("{}", encoding="utf-8")

    with pytest.raises(DataLoadError):
        _build_repo(tmp_path)


def test_wrong_top_level_type_raises_validation_error(tmp_path):
    # bis_metadata.json must be a JSON array, not an object.
    (tmp_path / "bis_metadata.json").write_text("{}", encoding="utf-8")
    (tmp_path / "bis_compliance.json").write_text("{}", encoding="utf-8")
    (tmp_path / "qco_mapping.json").write_text("[]", encoding="utf-8")
    (tmp_path / "normative_graph.json").write_text("[]", encoding="utf-8")
    (tmp_path / "sources.json").write_text("{}", encoding="utf-8")

    with pytest.raises(DataValidationError):
        _build_repo(tmp_path)


def test_record_missing_key_field_is_skipped_not_crashed(tmp_path):
    (tmp_path / "bis_metadata.json").write_text(
        json.dumps([{"title": "No is_number here"}, {"is_number": "TEST-IS-0002", "title": "Valid"}]),
        encoding="utf-8",
    )
    (tmp_path / "bis_compliance.json").write_text("{}", encoding="utf-8")
    (tmp_path / "qco_mapping.json").write_text("[]", encoding="utf-8")
    (tmp_path / "normative_graph.json").write_text("[]", encoding="utf-8")
    (tmp_path / "sources.json").write_text("{}", encoding="utf-8")

    repo = _build_repo(tmp_path)
    standards = repo.get_all_standards()
    assert len(standards) == 1
    assert standards[0]["is_number"] == "TEST-IS-0002"
