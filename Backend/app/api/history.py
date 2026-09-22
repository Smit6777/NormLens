"""History and Audit Records API router for Track 02 (NormLens)."""
from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.security import get_current_user_optional
from app.db.database import get_db
from app.db.models import AnalysisRecord, AuditFeedback, User
from app.models.auth_schemas import (
    FeedbackCreate,
    FeedbackResponse,
    HistoryDetail,
    HistoryItem,
)

router = APIRouter(prefix="/history", tags=["Analysis History"])


@router.get("", response_model=list[HistoryItem])
def list_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> list[HistoryItem]:
    """Retrieve historical tender analysis records from the persistent database."""
    query = db.query(AnalysisRecord)

    if category:
        query = query.filter(AnalysisRecord.category.ilike(f"%{category}%"))

    # If user is logged in, optionally show their records or all institutional records
    records = query.order_by(desc(AnalysisRecord.created_at)).offset(offset).limit(limit).all()

    return [
        HistoryItem(
            id=r.id,
            title=r.title,
            query=r.query_text,
            source_filename=r.source_filename,
            category=r.category,
            standards_found=r.standards_found_count,
            gaps_count=r.gaps_count,
            status=r.status,
            created_at=r.created_at.strftime("%d %b %Y, %I:%M %p") if r.created_at else None,
            timestamp=r.created_at.isoformat() if r.created_at else None,
        )
        for r in records
    ]


@router.get("/stats")
def get_history_stats(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get high-level analysis activity metrics for dashboard trust indicators."""
    total_analyses = db.query(AnalysisRecord).count()
    completed_analyses = db.query(AnalysisRecord).filter(AnalysisRecord.status == "Completed").count()
    total_feedbacks = db.query(AuditFeedback).count()
    verified_standards = db.query(AuditFeedback).filter(AuditFeedback.feedback_status == "verified").count()

    return {
        "total_tenders_analyzed": total_analyses,
        "completed_audits": completed_analyses,
        "officer_feedbacks_recorded": total_feedbacks,
        "verified_standards_count": verified_standards,
    }


@router.get("/{record_id}", response_model=HistoryDetail)
def get_history_detail(record_id: int, db: Session = Depends(get_db)) -> HistoryDetail:
    """Get full JSON evaluation results for a previous analysis."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record #{record_id} not found.",
        )

    return HistoryDetail(
        id=record.id,
        title=record.title,
        query=record.query_text,
        source_filename=record.source_filename,
        category=record.category,
        standards_found=record.standards_found_count,
        gaps_count=record.gaps_count,
        status=record.status,
        created_at=record.created_at.strftime("%d %b %Y, %I:%M %p") if record.created_at else None,
        timestamp=record.created_at.isoformat() if record.created_at else None,
        result_data=record.get_result(),
    )


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_record(record_id: int, db: Session = Depends(get_db)):
    """Delete a past analysis record from the database."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record #{record_id} not found.",
        )
    db.delete(record)
    db.commit()
    return None


@router.post("/{record_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_audit_feedback(
    record_id: int,
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> FeedbackResponse:
    """Submit procurement officer verification feedback on a recommended standard."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record #{record_id} not found.",
        )

    fb_entry = AuditFeedback(
        analysis_id=record.id,
        user_id=current_user.id if current_user else None,
        is_number=feedback.is_number,
        feedback_status=feedback.feedback_status,
        notes=feedback.notes,
    )
    db.add(fb_entry)
    db.commit()
    db.refresh(fb_entry)

    return FeedbackResponse(
        id=fb_entry.id,
        analysis_id=fb_entry.analysis_id,
        is_number=fb_entry.is_number,
        feedback_status=fb_entry.feedback_status,
        notes=fb_entry.notes,
        created_at=fb_entry.created_at.isoformat() if fb_entry.created_at else None,
    )
