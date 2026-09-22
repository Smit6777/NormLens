import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import create_app
from app.core.config import get_settings
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, AnalysisRecord


@pytest.fixture(scope="module")
def app():
    settings = get_settings()
    application = create_app(settings=settings)
    Base.metadata.create_all(bind=engine)
    yield application
    # Teardown test users
    db = SessionLocal()
    try:
        db.query(User).filter(User.username.like("test_%")).delete()
        db.commit()
    finally:
        db.close()


@pytest.mark.asyncio
async def test_auth_registration_and_login(app):
    uid = uuid.uuid4().hex[:6]
    username = f"test_officer_{uid}"
    email = f"test_officer_{uid}@example.com"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register new officer
        reg_payload = {
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "full_name": "Test Officer",
            "department": "Civil Infrastructure",
            "role": "officer"
        }
        res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["user"]["username"] == username
        token = data["access_token"]

        # Duplicate registration should fail
        res_dup = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_dup.status_code == 400

        # Login with correct credentials
        login_res = await client.post("/api/v1/auth/login", json={
            "username": username,
            "password": "SecurePassword123!"
        })
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

        # Login with invalid password
        bad_login = await client.post("/api/v1/auth/login", json={
            "username": username,
            "password": "WrongPassword"
        })
        assert bad_login.status_code == 401

        # Check /auth/me with Bearer token
        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["username"] == username



@pytest.mark.asyncio
async def test_demo_login(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/auth/demo-login")
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["username"] == "rutvi_officer"


@pytest.mark.asyncio
async def test_history_endpoints(app):
    # Insert a dummy record directly to DB
    db = SessionLocal()
    record = AnalysisRecord(
        title="Analysis: Ordinary Portland Cement",
        query_text="Supply of Ordinary Portland Cement conforming to IS 269",
        category="Construction Materials",
        standards_found_count=2,
        gaps_count=0,
        status="Completed",
        result_data='{"requirements": [], "recommendations": {}}'
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    rec_id = record.id
    db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # List history
        res = await client.get("/api/v1/history")
        assert res.status_code == 200
        items = res.json()
        assert len(items) >= 1
        assert any(item["id"] == rec_id for item in items)

        # Get history stats
        stats_res = await client.get("/api/v1/history/stats")
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_tenders_analyzed"] >= 1

        # Get detail
        detail_res = await client.get(f"/api/v1/history/{rec_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["title"] == "Analysis: Ordinary Portland Cement"

        # Submit feedback
        fb_res = await client.post(f"/api/v1/history/{rec_id}/feedback", json={
            "is_number": "IS 269:2015",
            "feedback_status": "verified",
            "notes": "Standard actively checked against BIS portal"
        })
        assert fb_res.status_code == 201

        # Delete history record
        del_res = await client.delete(f"/api/v1/history/{rec_id}")
        assert del_res.status_code == 204
