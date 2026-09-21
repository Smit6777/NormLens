from __future__ import annotations
from app.models.schemas import Gap, GapType, FixSuggestion, SuggestionStatus, ConfidenceLevel

class AIFixer:
    def suggest(self, gaps: list[Gap], requirement_text_by_id: dict[str, str]) -> list[FixSuggestion]:
        suggestions = []
        for gap in gaps:
            orig_req = requirement_text_by_id.get(gap.requirement_id, "")
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
                    reason="Mandatory legal compliance.",
                    supporting_standard=std,
                    confidence=ConfidenceLevel.HIGH,
                    suggestion_status=SuggestionStatus.PROPOSED
                ))
        return suggestions
