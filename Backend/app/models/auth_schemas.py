"""Pydantic schemas for Authentication and History (Track 02)."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    department: Optional[str] = "Procurement & Tenders"
    role: Optional[str] = "officer"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class HistoryItem(BaseModel):
    id: int
    title: str
    query: str
    source_filename: Optional[str] = None
    category: str
    standards_found: int
    gaps_count: int
    status: str
    created_at: Optional[str] = None
    timestamp: Optional[str] = None


class HistoryDetail(HistoryItem):
    result_data: dict[str, Any]


class FeedbackCreate(BaseModel):
    is_number: str
    feedback_status: str = Field(..., description="'verified', 'rejected', or 'modified'")
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    analysis_id: int
    is_number: str
    feedback_status: str
    notes: Optional[str] = None
    created_at: Optional[str] = None
