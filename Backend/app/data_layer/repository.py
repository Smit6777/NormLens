"""
Repository / data loader for the five knowledge-layer JSON files.

This module owns ALL access to the on-disk knowledge base. Nothing else
in the codebase should open these JSON files directly -- that keeps the
knowledge layer (JSON) cleanly separated from the reasoning layer
(Python services), per the project's architecture rules.

Deliberately has zero third-party dependencies (stdlib only) so it can be
unit-tested without installing FastAPI/Pydantic/etc.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.exceptions import DataLoadError, DataValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _load_json_file(path: Path) -> Any:
    if not path.exists():
        raise DataLoadError(
            f"Knowledge base file not found: {path}",
            details={"path": str(path)},
        )
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise DataLoadError(
            f"Knowledge base file is not valid JSON: {path} ({exc})",
            details={"path": str(path), "line": exc.lineno, "column": exc.colno},
        ) from exc
    except OSError as exc:
        raise DataLoadError(
            f"Could not read knowledge base file: {path} ({exc})",
            details={"path": str(path)},
        ) from exc


class Repository:
    """In-memory, indexed view over the five knowledge-layer JSON files.

    Expected on-disk shapes (see data/SCHEMA.md for full field docs):
      - bis_metadata.json:      list[dict]  each with a unique "is_number"
      - bis_compliance.json:    dict[is_number -> compliance dict]
      - qco_mapping.json:       list[dict]  each with a "product" key
      - normative_graph.json:   list[dict]  each with "from_is", "to_is",
                                 "relationship_type", and optionally "source_id"
      - sources.json:           dict[source_id -> source metadata dict]

    All lookup accessors return None / [] on a miss -- they never raise a
    "not found" error, and a miss must never be read by a caller as
    "does not exist" (project Rule 2). Reload is atomic: a failed reload
    never leaves the repository in a partially-updated state.
    """

    def __init__(
        self,
        metadata_path: Path,
        compliance_path: Path,
        qco_mapping_path: Path,
        normative_graph_path: Path,
        sources_path: Path,
    ) -> None:
        self._metadata_path = metadata_path
        self._compliance_path = compliance_path
        self._qco_mapping_path = qco_mapping_path
        self._normative_graph_path = normative_graph_path
        self._sources_path = sources_path

        self._metadata_by_is: dict[str, dict] = {}
        self._compliance_by_is: dict[str, dict] = {}
        self._qco_by_product: dict[str, list[dict]] = {}
        self._normative_by_is: dict[str, list[dict]] = {}
        self._sources_by_id: dict[str, dict] = {}

        self.reload()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def reload(self) -> None:
        """(Re)load all five JSON files from disk and rebuild in-memory indices."""
        metadata_raw = _load_json_file(self._metadata_path)
        compliance_raw = _load_json_file(self._compliance_path)
        qco_raw = _load_json_file(self._qco_mapping_path)
        normative_raw = _load_json_file(self._normative_graph_path)
        sources_raw = _load_json_file(self._sources_path)

        if not isinstance(metadata_raw, list):
            raise DataValidationError(
                "bis_metadata.json must contain a JSON array of standard records.",
                details={"path": str(self._metadata_path)},
            )
        if not isinstance(compliance_raw, dict):
            raise DataValidationError(
                "bis_compliance.json must contain a JSON object keyed by IS number.",
                details={"path": str(self._compliance_path)},
            )
        if not isinstance(qco_raw, list):
            raise DataValidationError(
                "qco_mapping.json must contain a JSON array of QCO mapping records.",
                details={"path": str(self._qco_mapping_path)},
            )
        if not isinstance(normative_raw, list):
            raise DataValidationError(
                "normative_graph.json must contain a JSON array of relationship records.",
                details={"path": str(self._normative_graph_path)},
            )
        if not isinstance(sources_raw, dict):
            raise DataValidationError(
                "sources.json must contain a JSON object keyed by source_id.",
                details={"path": str(self._sources_path)},
            )

        metadata_by_is: dict[str, dict] = {}
        for record in metadata_raw:
            is_number = record.get("is_number") if isinstance(record, dict) else None
            if not is_number:
                logger.warning("Skipping bis_metadata.json record with no is_number.")
                continue
            metadata_by_is[is_number] = record

        qco_by_product: dict[str, list[dict]] = {}
        for record in qco_raw:
            product = record.get("product") if isinstance(record, dict) else None
            if not product:
                logger.warning("Skipping qco_mapping.json record with no product.")
                continue
            qco_by_product.setdefault(product.strip().lower(), []).append(record)

        normative_by_is: dict[str, list[dict]] = {}
        for record in normative_raw:
            from_is = record.get("from_is") if isinstance(record, dict) else None
            if not from_is:
                logger.warning("Skipping normative_graph.json record with no from_is.")
                continue
            normative_by_is.setdefault(from_is, []).append(record)

        # Swap in atomically so a failed reload never leaves partial state.
        self._metadata_by_is = metadata_by_is
        self._compliance_by_is = dict(compliance_raw)
        self._qco_by_product = qco_by_product
        self._normative_by_is = normative_by_is
        self._sources_by_id = dict(sources_raw)

        logger.info(
            "Knowledge base loaded",
            extra={"context": {
                "standards": len(self._metadata_by_is),
                "compliance_records": len(self._compliance_by_is),
                "qco_products": len(self._qco_by_product),
                "normative_edges": sum(len(v) for v in self._normative_by_is.values()),
                "sources": len(self._sources_by_id),
            }},
        )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_all_standards(self) -> list[dict]:
        return list(self._metadata_by_is.values())

    def get_standard(self, is_number: str) -> dict | None:
        return self._metadata_by_is.get(is_number)

    def get_compliance(self, is_number: str) -> dict | None:
        return self._compliance_by_is.get(is_number)

    def get_qco_for_product(self, product: str) -> list[dict]:
        return self._qco_by_product.get(product.strip().lower(), [])

    def get_normative_relationships(self, is_number: str) -> list[dict]:
        return self._normative_by_is.get(is_number, [])

    def get_source(self, source_id: str) -> dict | None:
        return self._sources_by_id.get(source_id)
