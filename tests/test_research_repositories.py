"""Tests for the patient repository."""


def test_all_patients(patient_repository):
    """Test repository to get all patients."""
    patients = patient_repository.all()
    assert len(patients) > 0


def test_get_patient(patient_repository, patient_id):
    """Test repository to get one patient by id."""
    patient = patient_repository.get(patient_id)
    assert patient is not None
    assert patient['meta']['uuid'] == patient_id


def test_create_patient(patient_repository):
    """Test repository to create a new patient."""
    patient_repository.create({'meta': {'uuid': 'new-patient'}})
    patient = patient_repository.get('new-patient')
    assert patient['meta']['uuid'] == 'new-patient'


def test_update_patient(patient_repository, patient_id):
    """Test repository to update one patient by id."""
    patient = patient_repository.get(patient_id)
    patient_age = patient['patient']['age']
    patient_new_age = patient_age + 10
    patient['patient']['age'] = patient_new_age

    patient_repository.update(patient_id, patient)
    updated_patient = patient_repository.get(patient_id)

    assert updated_patient['patient']['age'] == patient_new_age


def test_delete_patient(patient_repository, patient_id):
    """Test repository to delete one patient by id."""
    patient = patient_repository.get(patient_id)
    assert patient is not None
    patient_repository.delete(patient_id)
    assert patient_repository.get(patient_id) is None
