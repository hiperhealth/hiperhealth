"""Repositories for reading and saving the web app data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar

from sqlmodel import Session

from ..app.db import ResearchPatientRecord

T = TypeVar('T')
# Patient type is an alias for now
# TODO: swap for Pydantic in future update
# once we have a better defined schema
# Patient = dict[str, Any]


class RepositoryInterface(ABC):
    """Repository interface."""

    @abstractmethod
    def all(self) -> list[T]:
        """Return all records."""
        pass

    @abstractmethod
    def get(self, id: str | int) -> T | None:
        """Return a single record."""
        pass

    @abstractmethod
    def create(self, data: T) -> T:
        """Create a new record."""
        pass

    @abstractmethod
    def update(self, id: str | int, data: T) -> bool:
        """Update a record."""
        pass

    @abstractmethod
    def delete(self, id: str | int) -> bool:
        """Delete a record."""
        pass


class PatientRepository(RepositoryInterface):
    """A repository for managing Patient data."""

    def get(self, patient_id: str, session: Session) -> Dict[str, Any] | None:
        """Retrieve a patient record by its ID."""
        record = session.get(ResearchPatientRecord, patient_id)
        return record.data if record else None

    def all(self, session: Session) -> List[Dict[str, Any]]:
        """Retrieve all patient records."""
        records = session.query(ResearchPatientRecord).all()
        return [record.data for record in records]

    def create(
        self, patient_record: Dict[str, Any], session: Session
    ) -> Dict[str, Any]:
        """Create a new patient record."""
        patient_id = patient_record.get('meta', {}).get('uuid')
        db_record = ResearchPatientRecord(id=patient_id, data=patient_record)
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
        return db_record.data

    def update(
        self, patient_id: str, patient_record: Dict[str, Any], session: Session
    ) -> Dict[str, Any]:
        """Update an existing patient record."""
        db_record = session.get(ResearchPatientRecord, patient_id)
        if db_record:
            db_record.data = patient_record
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
            return db_record.data
        return None

    def delete(self, patient_id: str, session: Session) -> None:
        """Delete a patient record."""
        record = session.get(ResearchPatientRecord, patient_id)
        if record:
            session.delete(record)
            session.commit()
