"""Pydantic request/response schemas for API endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DemographicsBase(BaseModel):
    """Patient demographic information schema."""

    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None


class LifestyleBase(BaseModel):
    """Patient lifestyle information schema."""

    diet: Optional[str] = None
    sleep_hours: Optional[float] = None
    exercise: Optional[str] = None
    mental_activities: Optional[str] = None


class ClinicalNoteCreate(BaseModel):
    """Clinical note creation schema."""

    note_type: str
    content: str


class WearableFileOut(BaseModel):
    """Wearable file output schema."""

    id: str
    filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    parsed_rows: Optional[int] = None
    parsed_summary: Optional[Dict[str, Any]] = None

    class Config:
        """Enable ORM mode for SQLAlchemy compatibility."""

        from_attributes = True


class PatientCreate(BaseModel):
    """Patient creation schema."""

    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None


class PatientOut(BaseModel):
    """Patient output schema with all related data."""

    id: str
    name: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    demographics: Optional[DemographicsBase] = None
    lifestyle: Optional[LifestyleBase] = None
    notes: Optional[List[ClinicalNoteCreate]] = None
    wearable_files: Optional[List[WearableFileOut]] = None

    class Config:
        """Enable ORM mode for SQLAlchemy compatibility."""

        from_attributes = True
