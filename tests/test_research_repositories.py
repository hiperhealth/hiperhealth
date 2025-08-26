"""Tests for the patient repository."""

from __future__ import annotations

import pytest

from sqlmodel import Session, create_engine

from research.models.repositories import PatientRepository

# Use an in-memory SQLite database for test isolation and speed.
engine = create_engine('sqlite:///:memory:')


@pytest.fixture(name='repo')
def repo_fixture() -> PatientRepository:
    """Provide a PatientRepository instance."""
    return PatientRepository()


def test_create_patient(repo: PatientRepository, session: Session):
    """Test the create method of the repository."""
    patient_uuid = 'test-uuid-1'
    new_patient_record = {
        'patient': {'gender': 'male'},
        'meta': {'uuid': patient_uuid},
    }

    created_patient = repo.create(new_patient_record, session=session)
    assert created_patient is not None
    assert created_patient['id'] == patient_uuid
    assert created_patient['gender'] == 'male'


def test_get_patient(repo: PatientRepository, session: Session):
    """Test the get method of the repository."""
    patient_uuid = 'test-uuid-2'
    repo.create(
        {'patient': {'gender': 'female'}, 'meta': {'uuid': patient_uuid}},
        session=session,
    )

    retrieved_patient = repo.get(patient_uuid, session=session)
    assert retrieved_patient is not None
    assert retrieved_patient['id'] == patient_uuid


def test_all(repo: PatientRepository, session: Session):
    """Test the all method of the repository."""
    repo.create(
        {'patient': {'gender': 'male'}, 'meta': {'uuid': 'test-uuid-3'}},
        session=session,
    )
    repo.create(
        {'patient': {'gender': 'female'}, 'meta': {'uuid': 'test-uuid-4'}},
        session=session,
    )

    all_patients = repo.all(session=session)
    assert len(all_patients) == 2
    assert 'test-uuid-1' in [p['meta']['uuid'] for p in all_patients]
    assert 'test-uuid-2' in [p['meta']['uuid'] for p in all_patients]


def test_update_patient(repo: PatientRepository, session: Session):
    """Test the update method of the repository."""
    patient_uuid = 'test-uuid-5'
    repo.create(
        {'patient': {'gender': 'other'}, 'meta': {'uuid': patient_uuid}},
        session=session,
    )

    update_data = {'patient': {'gender': 'male'}}
    repo.update(patient_uuid, update_data, session=session)

    retrieved_patient = repo.get(patient_uuid, session=session)
    assert retrieved_patient['gender'] == 'male'


def test_delete_patient(repo: PatientRepository, session: Session):
    """Test the delete method of the repository."""
    patient_uuid = 'test-uuid-6'
    repo.create(
        {'patient': {'gender': 'female'}, 'meta': {'uuid': patient_uuid}},
        session=session,
    )

    repo.delete(patient_uuid, session=session)

    assert repo.get(patient_uuid, session=session) is None
