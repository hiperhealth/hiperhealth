"""CRUD operations for patient records and related data."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models


def create_patient(db: Session, *, name: Optional[str] = None):
    """Create a new patient record."""
    obj = models.Patient(name=name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_patient(db: Session, patient_id: str):
    """Retrieve a patient by ID."""
    stmt = select(models.Patient).where(models.Patient.id == patient_id)
    return db.execute(stmt).scalars().unique().one_or_none()


def list_patients(db: Session, skip: int = 0, limit: int = 50):
    """List all patients with optional pagination."""
    stmt = select(models.Patient).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def get_dashboard_stats(db: Session, recent_limit: int = 5):
    """Compute dashboard statistics: totals, active, and monthly counts."""
    # total patients
    total = db.execute(
        select(func.count()).select_from(models.Patient)
    ).scalar_one()
    # active records
    active = db.execute(
        select(func.count())
        .select_from(models.Patient)
        .where(models.Patient.status == 'active')
    ).scalar_one()
    # patients created this month
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = db.execute(
        select(func.count())
        .select_from(models.Patient)
        .where(models.Patient.created_at >= month_start)
    ).scalar_one()
    # recent patients
    recent_stmt = (
        select(models.Patient)
        .order_by(models.Patient.created_at.desc())
        .limit(recent_limit)
    )
    recent = db.execute(recent_stmt).scalars().all()
    return {
        'total_patients': int(total),
        'active_records': int(active),
        'this_month': int(this_month),
        'recent_patients': recent,
    }


def upsert_demographics(db: Session, patient_id: str, data: dict):
    """Create or update patient demographics."""
    existing = db.get(models.Demographics, patient_id)
    if existing:
        for k, v in data.items():
            setattr(existing, k, v)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        obj = models.Demographics(patient_id=patient_id, **data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj


def upsert_lifestyle(db: Session, patient_id: str, data: dict):
    """Create or update patient lifestyle information."""
    existing = db.get(models.Lifestyle, patient_id)
    if existing:
        for k, v in data.items():
            setattr(existing, k, v)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        obj = models.Lifestyle(patient_id=patient_id, **data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj


def add_clinical_note(
    db: Session, patient_id: str, note_type: str, content: str
):
    """Add a clinical note for a patient."""
    obj = models.ClinicalNote(
        patient_id=patient_id, note_type=note_type, content=content
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_wearable_metadata(
    db: Session,
    patient_id: str,
    filename: str,
    content_type: str,
    size: int,
    file_content: Optional[bytes] = None,
    storage_path: Optional[str] = None,
    parsed_rows: Optional[int] = None,
    parsed_summary: Optional[dict] = None,
):
    """Create a wearable file record with metadata and content."""
    obj = models.WearableFile(
        patient_id=patient_id,
        filename=filename,
        content_type=content_type,
        size_bytes=size,
        file_content=file_content,
        storage_path=storage_path,
        parsed_rows=parsed_rows,
        parsed_summary=parsed_summary,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_wearables_for_patient(db: Session, patient_id: str):
    """List all wearable files for a patient."""
    stmt = select(models.WearableFile).where(
        models.WearableFile.patient_id == patient_id
    )
    return db.execute(stmt).scalars().all()


def delete_patient(db: Session, patient_id: str):
    """Delete a patient and all related records.

    Removes clinical notes, wearable data/files, demographics,
    lifestyle records, and the patient record itself.
    """
    # remove child records first to be safe across DB engines
    # clinical notes
    db.execute(
        models.ClinicalNote.__table__.delete().where(
            models.ClinicalNote.patient_id == patient_id
        )
    )
    # wearable data and files
    db.execute(
        models.WearableData.__table__.delete().where(
            models.WearableData.wearable_file_id.in_(
                select(models.WearableFile.id)
                .where(models.WearableFile.patient_id == patient_id)
                .scalar_subquery()
            )
        )
    )
    db.execute(
        models.WearableFile.__table__.delete().where(
            models.WearableFile.patient_id == patient_id
        )
    )
    # demographics and lifestyle
    db.execute(
        models.Demographics.__table__.delete().where(
            models.Demographics.patient_id == patient_id
        )
    )
    db.execute(
        models.Lifestyle.__table__.delete().where(
            models.Lifestyle.patient_id == patient_id
        )
    )
    # finally delete patient
    db.execute(
        models.Patient.__table__.delete().where(
            models.Patient.id == patient_id
        )
    )
    db.commit()
