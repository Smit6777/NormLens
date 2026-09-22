from __future__ import annotations
from app.data_layer.repository import Repository
from app.models.schemas import Evidence, ConfidenceLevel

class ProvenanceResolver:
    def __init__(self, repository: Repository):
        self.repository = repository

    def resolve(self, source_id: str | None, evidence_text: str) -> Evidence:
        if not source_id:
            return Evidence(
                evidence_text=evidence_text,
                verification_status=ConfidenceLevel.NOT_VERIFIED
            )
        source = self.repository.get_source(source_id)
        if not source:
            return Evidence(
                source_id=source_id,
                evidence_text=evidence_text,
                verification_status=ConfidenceLevel.NOT_VERIFIED
            )
        return Evidence(
            source_id=source_id,
            source_url=source.get("url"),
            document_title=source.get("title"),
            retrieved_on=source.get("retrieved_on"),
            evidence_text=evidence_text,
            verification_status=ConfidenceLevel.HIGH
        )
