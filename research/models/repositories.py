"""Repositories for reading and saving the web app data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar

from sdx.models.sqlmodel.fhirx import Patient
from sqlmodel import Session, select

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
        patient = session.get(Patient, patient_id)
        return patient.model_dump() if patient else None

    def all(self, session: Session) -> List[Dict[str, Any]]:
        """Retrieve all patient records."""
        statement = select(Patient)
        results = session.exec(statement)
        patients = results.all()
        return [p.model_dump() for p in patients]

    def create(
        self, patient_record: Dict[str, Any], session: Session
    ) -> Dict[str, Any]:
        """Create a new patient record."""
        patient_data = patient_record.get('patient', {})
        patient_data['id'] = patient_record.get('meta', {}).get('uuid')

        db_patient = Patient.model_validate(patient_data)
        session.add(db_patient)
        session.commit()
        session.refresh(db_patient)
        return db_patient.model_dump()

    def update(
        self, patient_id: str, patient_record: Dict[str, Any], session: Session
    ) -> Dict[str, Any]:
        """Update an existing patient record."""
        db_patient = session.get(Patient, patient_id)
        if not db_patient:
            return None

        patient_data = patient_record.get('patient', {})
        for key, value in patient_data.items():
            setattr(db_patient, key, value)

        session.add(db_patient)
        session.commit()
        session.refresh(db_patient)
        return db_patient.model_dump()

    def delete(self, patient_id: str, session: Session) -> None:
        """Delete a patient record."""
        patient = session.get(Patient, patient_id)
        if patient:
            session.delete(patient)
            session.commit()
