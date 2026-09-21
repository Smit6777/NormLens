"""SQLAlchemy database models for Track 02 (NormLens)."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """User account model for procurement officers and administrators."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    department = Column(String(100), default="Procurement & Tenders")
    role = Column(String(20), default="officer")  # "officer", "evaluator", "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    analyses = relationship("AnalysisRecord", back_populates="user", cascade="all, delete-orphan")
    tenders = relationship("TenderDocument", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "department": self.department,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TenderDocument(Base):
    """Uploaded tender document registry."""
    __tablename__ = "tender_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    page_count = Column(Integer, default=1)
    status = Column(String(50), default="processed")  # "uploaded", "processing", "processed", "failed"
    extracted_text_preview = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tenders")
    analyses = relationship("AnalysisRecord", back_populates="tender", cascade="all, delete-orphan")


class AnalysisRecord(Base):
    """Persistent audit record of an AI analysis run."""
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tender_id = Column(Integer, ForeignKey("tender_documents.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    query_text = Column(Text, nullable=False)
    source_filename = Column(String(255), nullable=True)
    category = Column(String(100), default="General Procurement")
    standards_found_count = Column(Integer, default=0)
    gaps_count = Column(Integer, default=0)
    status = Column(String(50), default="Completed")
    result_data = Column(Text, nullable=False)  # JSON-serialized AnalyzeResponse
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="analyses")
    tender = relationship("TenderDocument", back_populates="analyses")
    feedbacks = relationship("AuditFeedback", back_populates="analysis", cascade="all, delete-orphan")

    def get_result(self) -> dict[str, Any]:
        """Safely parse the stored JSON result data."""
        try:
            return json.loads(self.result_data)
        except Exception:
            return {}

    def to_summary_dict(self) -> dict[str, Any]:
        """Format for the Analysis History table on the frontend."""
        return {
            "id": self.id,
            "title": self.title,
            "query": self.query_text,
            "source_filename": self.source_filename,
            "category": self.category,
            "standards_found": self.standards_found_count,
            "gaps_count": self.gaps_count,
            "status": self.status,
            "created_at": self.created_at.strftime("%d %b %Y, %I:%M %p") if self.created_at else None,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
        }


class AuditFeedback(Base):
    """Procurement officer verification feedback on standard recommendations."""
    __tablename__ = "audit_feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analysis_records.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_number = Column(String(100), nullable=False)
    feedback_status = Column(String(50), nullable=False)  # "verified", "rejected", "modified"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    analysis = relationship("AnalysisRecord", back_populates="feedbacks")
