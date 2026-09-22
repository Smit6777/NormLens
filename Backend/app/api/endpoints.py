"""
API endpoints (api_contract): GET /, GET /health, POST /extract, POST /search,
POST /recommend, POST /audit, POST /fix, POST /analyze, GET /standards/{is_number},
POST /rebuild-index.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_services
from app.core.exceptions import DocumentExtractionError
from app.main import AppState, refresh_state
from app.models.schemas import (
    AnalyzeResponse, AuditRequest, AuditResponse, ExtractResponse,
    FixRequest, FixResponse, HealthResponse, RecommendRequest,
    RecommendResponse, RebuildIndexResponse, SearchRequest,
    SearchResponse, StandardResponse,
)
from app.services.extractor import ExtractedDocument, extract_document, extract_text_pages
from app.services.matcher import MatchStatus
from app.core.rate_limiter import rate_limit_dependency
from app.core.security import get_admin_api_key
from app.core.cache import cache_get, cache_set, clear_cache
from app.services.analytics import track_recommendation, get_usage
from app.services.multilingual import translate_to_english
from app.services.export import generate_csv_report
from fastapi.responses import PlainTextResponse
import httpx
from fastapi import BackgroundTasks
import json
from app.db.database import get_db
from app.db.models import AnalysisRecord, TenderDocument, User
from app.core.security import get_current_user_optional
from app.core.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)

router = APIRouter(dependencies=[Depends(rate_limit_dependency)])

@router.get("/")
async def root() -> dict[str, Any]:
    return {
        "name": "AI-Driven BIS Standard Recommendation & Compliance Auditor",
        "status": "ok",
        "notice": "Decision-support only. Verify every output against the current BIS portal before official use.",
    }

@router.get("/health", response_model=HealthResponse)
async def health(services: AppState = Depends(get_services)) -> HealthResponse:
    components = {
        "repository": "ok" if len(services.repository.get_all_standards()) > 0 else "empty",
        "vector_store": "ok" if services.vector_store.size > 0 else "empty",
        "embedding_model": services.embedding_service.model_name
    }
    return HealthResponse(
        app_name=services.settings.app_name, 
        app_env=services.settings.app_env,
        components=components
    )

async def _extract_document(
    services: AppState, file: UploadFile | None, text: str | None
) -> ExtractedDocument:
    if file is not None:
        content = await file.read()
        return await run_in_threadpool(
            extract_document, file.filename or "upload", content,
            services.settings.allowed_upload_extensions_list,
            services.settings.max_upload_size_bytes,
        )
    if text is not None and text.strip():
        pages = await run_in_threadpool(extract_text_pages, text)
        return ExtractedDocument(filename=None, pages=pages)
    raise DocumentExtractionError("Provide either a file upload ('file') or raw text ('text').")

@router.post("/extract", response_model=ExtractResponse)
async def extract(
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    services: AppState = Depends(get_services),
) -> ExtractResponse:
    doc = await _extract_document(services, file, text)
    requirements = await run_in_threadpool(services.requirement_extractor.extract, doc.pages)
    return ExtractResponse(
        requirements=requirements,
        source_filename=doc.filename,
        page_count=doc.page_count,
    )

@router.post("/search", response_model=SearchResponse)
async def search(body: SearchRequest, services: AppState = Depends(get_services)) -> SearchResponse:
    query = translate_to_english(body.query)
    
    cached = cache_get("search", query=query, top_k=body.top_k)
    if cached:
        return SearchResponse(**cached)
        
    result = await run_in_threadpool(services.matcher.match, query, body.top_k)
    enriched = [services.compliance_engine.enrich(r) for r in result.recommendations]
    
    resp = SearchResponse(query=query, results=enriched)
    cache_set("search", resp.model_dump(), query=query, top_k=body.top_k)
    return resp

@router.post("/recommend", response_model=RecommendResponse)
async def recommend(body: RecommendRequest, services: AppState = Depends(get_services)) -> RecommendResponse:
    # Also support Hindi translations in requirement text if enabled
    req = body.requirement
    req.raw_text = translate_to_english(req.raw_text)
    
    result = await run_in_threadpool(services.matcher.match_requirement, req)
    enriched = [services.compliance_engine.enrich(r) for r in result.recommendations]
    
    for r in enriched:
        track_recommendation(r.is_number)
        
    return RecommendResponse(
        requirement_id=body.requirement.requirement_id,
        status=result.status.value,
        message=result.message,
        results=enriched,
    )

@router.post("/audit", response_model=AuditResponse)
async def audit(body: AuditRequest, services: AppState = Depends(get_services)) -> AuditResponse:
    gaps = services.gap_analyzer.analyze(
        body.requirements, body.recommendations, body.document_title
    )
    return AuditResponse(gaps=gaps)

@router.post("/fix", response_model=FixResponse)
async def fix(body: FixRequest, services: AppState = Depends(get_services)) -> FixResponse:
    suggestions = services.fixer.suggest(body.gaps, body.requirement_text_by_id)
    return FixResponse(fix_suggestions=suggestions)

async def send_webhook(url: str, data: dict):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=data, timeout=10.0)
    except Exception as e:
        pass # Silently fail for webhooks in MVP

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    callback_url: str | None = Form(None),
    services: AppState = Depends(get_services),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
) -> AnalyzeResponse:
    doc = await _extract_document(services, file, text)
    
    # Try LLM extraction if enabled, else fallback to rule-based
    from app.services.llm_extractor import LLMRequirementExtractor
    llm = LLMRequirementExtractor()
    requirements = await run_in_threadpool(llm.extract, doc.pages)
    
    if not requirements:
        requirements = await run_in_threadpool(
            services.requirement_extractor.extract, doc.pages
        )

    recommendations: dict[str, list] = {}
    for req in requirements:
        req.raw_text = translate_to_english(req.raw_text)
        result = await run_in_threadpool(
            services.matcher.match_requirement, req
        )
        if result.status == MatchStatus.OK:
            enriched = [
                services.compliance_engine.enrich(r)
                for r in result.recommendations
            ]
            recommendations[req.requirement_id] = enriched
            for r in enriched:
                track_recommendation(r.is_number)

    gaps = await run_in_threadpool(
        services.gap_analyzer.analyze,
        requirements,
        recommendations,
        doc.filename,
    )
    fix_suggestions = services.fixer.suggest(
        gaps, {r.requirement_id: r.raw_text for r in requirements}
    )

    resp = AnalyzeResponse(
        requirements=requirements,
        recommendations=recommendations,
        fix_suggestions=fix_suggestions,
        gaps=gaps,
    )
    
    # Track 02: Persist analysis and tender upload to database
    try:
        query_summary = doc.filename or (text[:100] if text else "Tender Requirement")
        first_category = "General Procurement"
        if requirements and requirements[0].product:
            first_category = requirements[0].product
            
        standards_count = sum(len(recs) for recs in recommendations.values())
        
        tender_doc_id = None
        if file is not None and doc.filename:
            tender_doc = TenderDocument(
                user_id=current_user.id if current_user else None,
                filename=doc.filename,
                file_size_bytes=doc.total_characters,
                page_count=doc.page_count,
                status="processed",
                extracted_text_preview=requirements[0].raw_text[:300] if requirements else None,
            )
            db.add(tender_doc)
            db.flush()
            tender_doc_id = tender_doc.id

        record = AnalysisRecord(
            user_id=current_user.id if current_user else None,
            tender_id=tender_doc_id,
            title=f"Analysis: {query_summary}",
            query_text=text or (f"Tender Document: {doc.filename}" if doc.filename else "Procurement Specification"),
            source_filename=doc.filename,
            category=first_category,
            standards_found_count=standards_count,
            gaps_count=len(gaps),
            status="Completed",
            result_data=json.dumps(resp.model_dump(mode="json")),
        )
        db.add(record)
        db.commit()
    except Exception as exc:
        logger.warning(f"Could not persist analysis record to database: {exc}")

    if callback_url:
        background_tasks.add_task(send_webhook, callback_url, resp.model_dump(mode="json"))
        
    return resp

@router.get("/standards/{is_number}", response_model=StandardResponse)
async def get_standard(
    is_number: str, services: AppState = Depends(get_services)
) -> StandardResponse:
    record = services.repository.get_standard(is_number)
    assessment = await run_in_threadpool(
        services.compliance_engine.assess, is_number
    )
    return StandardResponse(
        is_number=is_number,
        found_in_metadata=record is not None,
        title=(record or {}).get("title"),
        compliance=assessment.compliance,
        evidence=assessment.evidence,
        confidence=assessment.confidence,
        verification_required=assessment.verification_required,
    )

@router.get("/standards/{is_number}/usage")
async def get_standard_usage(is_number: str):
    """Get historical trend analysis for a standard."""
    count = get_usage(is_number)
    return {
        "is_number": is_number,
        "recommendation_count": count,
        "trend_message": f"This standard was recommended {count} times this month."
    }

@router.post("/analyze/export")
async def export_analysis(
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    services: AppState = Depends(get_services),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Export analysis report as CSV."""
    from fastapi import BackgroundTasks
    resp = await analyze(BackgroundTasks(), file=file, text=text, callback_url=None, services=services, db=db, current_user=current_user)
    
    csv_content = generate_csv_report(resp)
    
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="analysis_report.csv"'}
    )


@router.post("/rebuild-index", response_model=RebuildIndexResponse)
async def rebuild_index(
    services: AppState = Depends(get_services),
    api_key: str = Depends(get_admin_api_key)
) -> RebuildIndexResponse:
    new_state = await run_in_threadpool(refresh_state, services)
    services.__dict__.update(new_state.__dict__)
    clear_cache()
    return RebuildIndexResponse(
        status="ok",
        standards_indexed=services.vector_store.size,
        embedding_model=services.embedding_service.model_name,
    )

@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics(services: AppState = Depends(get_services)):
    """Prometheus formatted metrics."""
    metrics = []
    metrics.append("# HELP bis_standards_total Total number of standards in knowledge base")
    metrics.append("# TYPE bis_standards_total gauge")
    count = len(services.repository.get_all_standards())
    metrics.append(f"bis_standards_total {count}")
    
    metrics.append("# HELP bis_vector_index_size Total number of vectors in index")
    metrics.append("# TYPE bis_vector_index_size gauge")
    metrics.append(f"bis_vector_index_size {services.vector_store.size}")
    
    return "\n".join(metrics) + "\n"
