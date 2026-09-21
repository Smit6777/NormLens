from __future__ import annotations
from dataclasses import dataclass
from app.data_layer.repository import Repository
from app.services.provenance import ProvenanceResolver
from app.services.qco import QcoLookup
from app.services.normative import NormativeGraphService
from app.models.schemas import ComplianceInfo, Recommendation, ConfidenceLevel, Evidence

@dataclass
class Assessment:
    compliance: ComplianceInfo
    evidence: list[Evidence]
    confidence: ConfidenceLevel
    verification_required: list[str]

class ComplianceEngine:
    def __init__(
        self,
        repository: Repository,
        provenance: ProvenanceResolver,
        qco_lookup: QcoLookup,
        normative: NormativeGraphService
    ):
        self.repository = repository
        self.provenance = provenance
        self.qco_lookup = qco_lookup
        self.normative = normative

    def assess(self, is_number: str) -> Assessment:
        comp_data = self.repository.get_compliance(is_number)
        norm_rels = self.normative.get_relationships(is_number)
        
        info = ComplianceInfo()
        evidence_list = []
        confidence = ConfidenceLevel.NOT_VERIFIED
        reqs = ["Verification required"]
        
        if comp_data:
            info.standard_status = comp_data.get("standard_status")
            info.current_version = comp_data.get("current_version")
            info.amendments = comp_data.get("amendments", [])
            info.superseded_by = comp_data.get("superseded_by")
            info.supersedes = comp_data.get("supersedes", [])
            info.qco_applicable = comp_data.get("qco_applicable")
            info.certification_required = comp_data.get("certification_required")
            info.testing_scheme = comp_data.get("testing_scheme")
            info.normative_relationships = norm_rels
            info.normative_references = [r.to_is for r in norm_rels]
            
            source_id = comp_data.get("source_id")
            if source_id:
                ev = self.provenance.resolve(source_id, f"Compliance data for {is_number}")
                evidence_list.append(ev)
                confidence = ConfidenceLevel.HIGH
                reqs = []
        else:
            info.missing_information.append("Compliance data not verified")
            
        std_data = self.repository.get_standard(is_number)
        if std_data and std_data.get("product"):
            info.qco_details = self.qco_lookup.lookup(std_data.get("product"))
            
        return Assessment(
            compliance=info,
            evidence=evidence_list,
            confidence=confidence,
            verification_required=reqs
        )

    def enrich(self, recommendation: Recommendation) -> Recommendation:
        assessment = self.assess(recommendation.is_number)
        recommendation.compliance = assessment.compliance
        recommendation.evidence.extend(assessment.evidence)
        recommendation.confidence = assessment.confidence
        recommendation.verification_required = assessment.verification_required
        return recommendation
