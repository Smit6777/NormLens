from __future__ import annotations
from app.models.schemas import Gap, GapType, FixSuggestion, SuggestionStatus, ConfidenceLevel

class AIFixer:
    def suggest(self, gaps: list[Gap], requirements_by_id: dict) -> list[FixSuggestion]:
        suggestions = []
        for gap in gaps:
            req_obj = requirements_by_id.get(gap.requirement_id)
            orig_req = req_obj.raw_text if hasattr(req_obj, 'raw_text') else req_obj or ""
            product = getattr(req_obj, 'product', None) or "unknown product"
            category = getattr(req_obj, 'category', None) or "unknown category"

            if gap.gap_type == GapType.CITED_STANDARD_SUPERSEDED:
                new_std = gap.related_standards[1] if len(gap.related_standards) > 1 else "Unknown"
                suggestions.append(FixSuggestion(
                    original_requirement=orig_req,
                    issue=gap.message,
                    suggested_revision=f"Update reference to {new_std}.",
                    reason="Compliance with the active standard version.",
                    supporting_standard=new_std,
                    confidence=ConfidenceLevel.HIGH,
                    suggestion_status=SuggestionStatus.PROPOSED
                ))
            elif gap.gap_type == GapType.MISSING_QCO_REFERENCE:
                std = gap.related_standards[0] if gap.related_standards else "Unknown"
                suggestions.append(FixSuggestion(
                    original_requirement=orig_req,
                    issue=gap.message,
                    suggested_revision=f"Ensure explicit mention of mandatory BIS certification as per QCO for {std}.",
                    reason="Local QCO mapping indicates a certification requirement for this mapped product-standard combination. Verify the current notification, effective date, exceptions, and procurement applicability before publication.",
                    supporting_standard=std,
                    confidence=ConfidenceLevel.HIGH,
                    suggestion_status=SuggestionStatus.PROPOSED
                ))
            elif gap.gap_type == GapType.VAGUE_REQUIREMENT:
                # DOMAIN-AWARE SUGGESTION
                if "electrical" in category.lower() or "lighting" in category.lower():
                    suggested = f"Please provide explicit technical parameters for {product or 'the equipment'} (e.g., rated voltage, current, frequency, protection class, testing/certification requirements)."
                elif "medical" in category.lower() or "laboratory" in category.lower():
                    suggested = f"Please provide explicit technical parameters for {product or 'the equipment'} (e.g., device type, intended use, measurable performance, safety, and testing/regulatory requirements)."
                elif "construction" in category.lower() or "cement" in category.lower() or "steel" in category.lower():
                    suggested = f"Please provide explicit technical parameters for {product or 'the material'} (e.g., technical grade, material properties, dimensions, testing methods, and relevant BIS standard)."
                elif "railway" in category.lower():
                    suggested = f"Please provide explicit technical parameters for {product or 'the material'} (e.g., application, operating conditions, fire/safety/performance requirements, and test method)."
                else:
                    suggested = f"Please provide explicit technical parameters, material grade, capacity, and specific testing/certification requirements for {product or 'the item'}."

                suggestions.append(FixSuggestion(
                    original_requirement=orig_req,
                    issue=gap.message,
                    suggested_revision=suggested,
                    reason="Requirement lacks technical precision.",
                    supporting_standard=None,
                    confidence=ConfidenceLevel.LOW,
                    suggestion_status=SuggestionStatus.PROPOSED
                ))
            elif gap.gap_type == GapType.MISSING_STANDARD:
                suggestions.append(FixSuggestion(
                    original_requirement=orig_req,
                    issue=gap.message,
                    suggested_revision=f"Please provide explicit technical parameters, material grade, capacity, applicable Indian Standard reference, and specific testing/certification requirements for {product or 'the item'}.",
                    reason="No relevant BIS standard was identified. Additional technical detail may enable identification.",
                    supporting_standard=None,
                    confidence=ConfidenceLevel.LOW,
                    suggestion_status=SuggestionStatus.PROPOSED
                ))
        return suggestions
