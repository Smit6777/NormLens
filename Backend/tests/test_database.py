"""Tests for database layer and models (Track 02)."""
import pytest
from datetime import datetime
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, TenderDocument, AnalysisRecord, AuditFeedback
from app.core.security import get_password_hash, verify_password


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup test records
    db = SessionLocal()
    try:
        db.query(AuditFeedback).delete()
        db.query(AnalysisRecord).delete()
        db.query(TenderDocument).delete()
        db.query(User).filter(User.username.like("test_%")).delete()
        db.commit()
    finally:
        db.close()


def test_password_hashing():
    pw = "SecretP@ssw0rd123"
    hashed = get_password_hash(pw)
    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_user_creation_and_query():
    db = SessionLocal()
    try:
        user = User(
            username="test_officer_1",
            email="test_officer_1@tender.gov.in",
            hashed_password=get_password_hash("password123"),
            full_name="Test Procurement Officer",
            department="Electrical",
            role="officer",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.is_active is True
        assert user.role == "officer"

        # Query user
        fetched = db.query(User).filter(User.username == "test_officer_1").first()
        assert fetched is not None
        assert fetched.email == "test_officer_1@tender.gov.in"
        assert fetched.to_dict()["department"] == "Electrical"
    finally:
        db.close()


def test_analysis_record_persistence():
    db = SessionLocal()
    try:
        record = AnalysisRecord(
            title="Analysis: 90W LED Street Lighting",
            query_text="Require 90W Outdoor LED Street Lighting with IP66 housing",
            category="Electrical & Lighting",
            standards_found_count=3,
            gaps_count=0,
            status="Completed",
            result_data='{"requirements": [], "recommendations": {"REQ-001": []}}',
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        assert record.id is not None
        assert record.standards_found_count == 3
        assert record.get_result() == {"requirements": [], "recommendations": {"REQ-001": []}}
        summary = record.to_summary_dict()
        assert summary["standards_found"] == 3
        assert summary["status"] == "Completed"
    finally:
        db.close()
