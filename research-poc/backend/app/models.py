"""SQLAlchemy ORM models for patient data and related records."""

import uuid

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
)
from sqlalchemy.sql import func

from .database import Base


def gen_uuid():
    """Generate a UUID string for database IDs."""
    return str(uuid.uuid4())


class Patient(Base):
    """Patient record with basic demographics and status tracking."""

    __tablename__ = 'patients'
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=True)
    status = Column(String, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_visit_date = Column(DateTime(timezone=True), nullable=True)


class Demographics(Base):
    """Patient demographic information (age, gender, height, weight)."""

    __tablename__ = 'demographics'
    patient_id = Column(
        String(36),
        ForeignKey('patients.id', ondelete='CASCADE'),
        primary_key=True,
    )
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    weight = Column(Numeric(6, 2), nullable=True)
    height = Column(Numeric(6, 2), nullable=True)


class Lifestyle(Base):
    """Patient lifestyle factors (diet, sleep, exercise, mental)."""

    __tablename__ = 'lifestyle'
    patient_id = Column(
        String(36),
        ForeignKey('patients.id', ondelete='CASCADE'),
        primary_key=True,
    )
    diet = Column(String, nullable=True)
    sleep_hours = Column(Numeric(4, 2), nullable=True)
    exercise = Column(Text, nullable=True)
    mental_activities = Column(Text, nullable=True)


class ClinicalNote(Base):
    """Clinical notes for symptoms, mental health, or exams."""

    __tablename__ = 'clinical_notes'
    id = Column(String(36), primary_key=True, default=gen_uuid)
    patient_id = Column(
        String(36),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
    )
    note_type = Column(String, nullable=False)  # symptoms|mental|exams
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WearableFile(Base):
    """Wearable device file upload with metadata and content."""

    __tablename__ = 'wearable_files'
    id = Column(String(36), primary_key=True, default=gen_uuid)
    patient_id = Column(
        String(36),
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
    )
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    file_content = Column(LargeBinary, nullable=True)  # raw file bytes in DB
    storage_path = Column(String, nullable=True)  # optional disk path
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    parsed_rows = Column(Integer, nullable=True)
    parsed_summary = Column(JSON, nullable=True)


class WearableData(Base):
    """Parsed wearable data points (HR, steps, etc.) from files."""

    __tablename__ = 'wearable_data'
    id = Column(String(36), primary_key=True, default=gen_uuid)
    wearable_file_id = Column(
        String(36),
        ForeignKey('wearable_files.id', ondelete='CASCADE'),
        nullable=False,
    )
    recorded_at = Column(DateTime(timezone=True), nullable=True)
    metric = Column(String, nullable=True)  # e.g., "heart_rate", "steps"
    value = Column(Numeric, nullable=True)
    raw = Column(JSON, nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=True)
    metric = Column(String, nullable=False)
    value = Column(Numeric, nullable=True)
    raw = Column(JSON, nullable=True)
