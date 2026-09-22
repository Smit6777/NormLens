from __future__ import annotations
from app.data_layer.repository import Repository
from app.services.compliance import ComplianceEngine
from app.services.qco import QcoLookup
from app.models.schemas import ExtractedRequirement, Recommendation, Gap, GapType, GapSeverity, ConfidenceLevel

class GapAnalyzer:
    def __init__(self, repository: Repository, compliance_engine: ComplianceEngine, qco_lookup: QcoLookup):
        self.repository = repository
        self.compliance_engine = compliance_engine
        self.qco_lookup = qco_lookup

    def analyze(self, requirements: list[ExtractedRequirement], recommendations: dict[str, list[Recommendation]], document_title: str | None) -> list[Gap]:
        gaps = []
        for req in requirements:
            cited = req.parameters.get("cited_standards", [])
            for c in cited:
                comp = self.repository.get_compliance(c)
                if comp and comp.get("superseded_by"):
                    gaps.append(Gap(
                        gap_id=f"GAP-{req.requirement_id}-{c}",
                        gap_type=GapType.CITED_STANDARD_SUPERSEDED,
                        severity=GapSeverity.HIGH,
                        requirement_id=req.requirement_id,
                        message=f"Cited standard {c} is superseded by {comp.get('superseded_by')}",
                        related_standards=[c, comp.get("superseded_by")]
                    ))
                elif not comp:
                    gaps.append(Gap(
                        gap_id=f"GAP-{req.requirement_id}-{c}",
                        gap_type=GapType.CITED_STANDARD_NOT_IN_KB,
                        severity=GapSeverity.LOW,
                        requirement_id=req.requirement_id,
                        message=f"Cited standard {c} not verified in knowledge base.",
                        related_standards=[c]
                    ))
            
            vague = not req.parameters.get("grade") and not req.parameters.get("measurements") and not cited
            
            recs = recommendations.get(req.requirement_id, [])
            if vague and recs:
                # Downgrade confidence
                for r in recs:
                    r.confidence = ConfidenceLevel.LOW
                # Generate vague gap instead of specific QCO gap
                gaps.append(Gap(
                    gap_id=f"GAP-{req.requirement_id}-VAGUE",
                    gap_type=GapType.VAGUE_REQUIREMENT,
                    severity=GapSeverity.MEDIUM,
                    requirement_id=req.requirement_id,
                    message="Tender requirement lacks specific technical details (e.g., grade, type, standard)."
                ))
                continue
            if not recs:
                gaps.append(Gap(
                    gap_id=f"GAP-{req.requirement_id}-MISSING",
                    gap_type=GapType.MISSING_STANDARD,
                    severity=GapSeverity.MEDIUM,
                    requirement_id=req.requirement_id,
                    message="No relevant BIS standard identified for requirement."
                ))
            else:
                best = recs[0]
                if best.compliance.qco_applicable:
                    gaps.append(Gap(
                        gap_id=f"GAP-{req.requirement_id}-QCO",
                        gap_type=GapType.MISSING_QCO_REFERENCE,
                        severity=GapSeverity.HIGH,
                        requirement_id=req.requirement_id,
                        message=f"Standard {best.is_number} requires QCO certification.",
                        related_standards=[best.is_number]
                    ))
        # Deduplicate
        unique_gaps = []
        seen = set()
        for gap in gaps:
            std = gap.related_standards[0] if gap.related_standards else "none"
            identity = (gap.gap_type.value, std, gap.message.lower().strip())
            if identity not in seen:
                seen.add(identity)
                unique_gaps.append(gap)
        return unique_gaps
