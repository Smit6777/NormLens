from __future__ import annotations
from app.data_layer.repository import Repository
from app.services.provenance import ProvenanceResolver
from app.models.schemas import NormativeRelationship

class NormativeGraphService:
    def __init__(self, repository: Repository, provenance: ProvenanceResolver):
        self.repository = repository
        self.provenance = provenance

    def get_relationships(self, is_number: str) -> list[NormativeRelationship]:
        records = self.repository.get_normative_relationships(is_number)
        rels = []
        for r in records:
            to_is = r.get("to_is")
            source_id = r.get("source_id")
            evidence = self.provenance.resolve(source_id, f"{is_number} references {to_is}")
            to_std = self.repository.get_standard(to_is)
            
            rels.append(NormativeRelationship(
                from_is=r.get("from_is"),
                to_is=to_is,
                relationship_type=r.get("relationship_type"),
                depth=1,
                to_title=to_std.get("title") if to_std else None,
                to_in_knowledge_base=to_std is not None,
                source_id=source_id,
                evidence=[evidence] if evidence.source_id else []
            ))
        return rels
