from __future__ import annotations
from app.data_layer.repository import Repository
from app.services.provenance import ProvenanceResolver
from app.models.schemas import QcoDetail, QcoMatchType

class QcoLookup:
    def __init__(self, repository: Repository, provenance: ProvenanceResolver):
        self.repository = repository
        self.provenance = provenance

    def lookup(self, product: str) -> list[QcoDetail]:
        records = self.repository.get_qco_for_product(product)
        details = []
        for r in records:
            source_id = r.get("source_id")
            evidence_text = f"QCO applicable for {product}"
            evidence = self.provenance.resolve(source_id, evidence_text)
            
            details.append(QcoDetail(
                product=r.get("product"),
                qco_name=r.get("qco_name"),
                is_number=r.get("is_number"),
                enforcement_date=r.get("enforcement_date"),
                in_force=True, # simplified
                match_type=QcoMatchType.PRODUCT_MATCH,
                source_id=source_id,
                evidence=[evidence] if evidence.source_id else []
            ))
        return details
