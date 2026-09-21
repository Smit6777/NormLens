"""
Pydantic V2 schemas used by the API and service layer.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NOT_VERIFIED = "NOT_VERIFIED"

class SuggestionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"

class GapSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class GapType(str, Enum):
    CITED_STANDARD_NOT_IN_KB = "CITED_STANDARD_NOT_IN_KB"
    CITED_STANDARD_WITHDRAWN = "CITED_STANDARD_WITHDRAWN"
    CITED_STANDARD_SUPERSEDED = "CITED_STANDARD_SUPERSEDED"
    CITED_STANDARD_OUTDATED = "CITED_STANDARD_OUTDATED"
    CITED_REVISION_UNSPECIFIED = "CITED_REVISION_UNSPECIFIED"
    CITED_REVISION_MISMATCH = "CITED_REVISION_MISMATCH"
    MISSING_NORMATIVE_REFERENCE = "MISSING_NORMATIVE_REFERENCE"
    MISSING_QCO_REFERENCE = "MISSING_QCO_REFERENCE"
    MISSING_STANDARD = "MISSING_STANDARD"
    INSUFFICIENT_SPECIFICATION = "INSUFFICIENT_SPECIFICATION"

class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str | None = None
    source_url: str | None = None
    document_title: str | None = None
    page_number: int | None = None
    evidence_text: str
    retrieved_on: str | None = None
    verification_status: ConfidenceLevel = ConfidenceLevel.NOT_VERIFIED

class QcoMatchType(str, Enum):
    EXACT = "EXACT"
    BASE_NUMBER_ONLY = "BASE_NUMBER_ONLY"
    DIFFERENT_REVISION = "DIFFERENT_REVISION"
    PRODUCT_MATCH = "PRODUCT_MATCH"

class QcoDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product: str
    qco_name: str | None = None
    is_number: str | None = None
    enforcement_date: str | None = None
    in_force: bool | None = Field(default=None)
    match_type: QcoMatchType
    source_id: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)

class NormativeRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")
    from_is: str
    to_is: str
    relationship_type: str
    depth: int = 1
    to_title: str | None = None
    to_in_knowledge_base: bool = False
    source_id: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)

class ExtractedRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requirement_id: str
    raw_text: str
    product: str | None = None
    category: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    mandatory: bool | None = None
    source_page: int | None = None

class ComplianceInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    standard_status: str | None = None
    current_version: str | None = None
    amendments: list[str] = Field(default_factory=list)
    superseded_by: str | None = None
    supersedes: list[str] = Field(default_factory=list)
    qco_applicable: bool | None = None
    certification_required: bool | None = None
    testing_scheme: str | None = None
    normative_references: list[str] = Field(default_factory=list)
    qco_details: list[QcoDetail] = Field(default_factory=list)
    normative_relationships: list[NormativeRelationship] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)

class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_number: str
    title: str
    system_match_score: float = Field(ge=0.0, le=1.0)
    match_reasons: list[str] = Field(default_factory=list)
    score_components: dict[str, float] = Field(default_factory=dict)
    compliance: ComplianceInfo = Field(default_factory=ComplianceInfo)
    evidence: list[Evidence] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.NOT_VERIFIED
    verification_required: list[str] = Field(default_factory=list)

class Gap(BaseModel):
    model_config = ConfigDict(extra="forbid")
    gap_id: str
    gap_type: GapType
    severity: GapSeverity
    requirement_id: str
    message: str
    related_standards: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.NOT_VERIFIED
    verification_required: list[str] = Field(default_factory=list)

class FixSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    original_requirement: str
    issue: str
    suggested_revision: str
    reason: str
    supporting_standard: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.NOT_VERIFIED
    suggestion_status: SuggestionStatus = SuggestionStatus.MANUAL_REVIEW_REQUIRED

class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    app_name: str
    app_env: str
    components: dict[str, str] = Field(default_factory=dict)

class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1)
    top_k: int = Field(default=10, ge=1, le=100)

class SearchResponse(BaseModel):
    query: str
    results: list[Recommendation] = Field(default_factory=list)

class ExtractResponse(BaseModel):
    requirements: list[ExtractedRequirement] = Field(default_factory=list)
    source_filename: str | None = None
    page_count: int | None = None

class RecommendRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requirement: ExtractedRequirement

class RecommendResponse(BaseModel):
    requirement_id: str
    status: str
    message: str | None = None
    results: list[Recommendation] = Field(default_factory=list)

class AuditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requirements: list[ExtractedRequirement]
    recommendations: dict[str, list[Recommendation]] = Field(default_factory=dict)
    document_title: str | None = None

class AuditResponse(BaseModel):
    gaps: list[Gap] = Field(default_factory=list)

class FixRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    gaps: list[Gap]
    requirement_text_by_id: dict[str, str] = Field(default_factory=dict)

class FixResponse(BaseModel):
    fix_suggestions: list[FixSuggestion] = Field(default_factory=list)

class StandardResponse(BaseModel):
    is_number: str
    found_in_metadata: bool
    title: str | None = None
    compliance: ComplianceInfo = Field(default_factory=ComplianceInfo)
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.NOT_VERIFIED
    verification_required: list[str] = Field(default_factory=list)

class RebuildIndexResponse(BaseModel):
    status: str = "ok"
    standards_indexed: int
    embedding_model: str

class AnalyzeResponse(BaseModel):
    requirements: list[ExtractedRequirement] = Field(default_factory=list)
    recommendations: dict[str, list[Recommendation]] = Field(default_factory=dict)
    fix_suggestions: list[FixSuggestion] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
