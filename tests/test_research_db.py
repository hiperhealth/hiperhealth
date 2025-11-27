"""Tests for patient creation, retrieval, and listing."""

from hiperhealth.models.sqla.fhirx import Base

from tests.conftest import engine


def setup_function():
    """Create the database schema before each test."""
    Base.metadata.create_all(bind=engine)


def teardown_function():
    """Drop the database schema after each test."""
    Base.metadata.drop_all(bind=engine)


def test_create_and_get_patient(test_repo, patients_json):
    """Test creating and retrieving a patient."""
    # Arrange
    patient_data = patients_json[0]
    patient_uuid = patient_data['meta']['uuid']

    # Act
    test_repo.create_patient_and_consultation(patient_data)
    retrieved_patient = test_repo.get_patient_by_uuid(patient_uuid)

    # Assert
    assert retrieved_patient is not None
    assert retrieved_patient.uuid == patient_uuid
    assert retrieved_patient.age == 38


def test_list_patients(test_repo, patients_json):
    """Test listing all patients."""
    # Arrange
    for patient_data in patients_json:
        test_repo.create_patient_and_consultation(patient_data)

    # Act
    all_patients = test_repo.list_patients()

    # Assert
    assert len(all_patients) == len(patients_json)
