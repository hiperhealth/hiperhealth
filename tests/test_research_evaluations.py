"""Tests for the research app evaluations."""

import uuid

from research.app.main import app, get_repository


def test_diagnosis_post_evaluation_form(client, patient_repository):
    """Test the diagnosis evaluation form."""
    # Override the app's dependency with the test repository
    app.dependency_overrides[get_repository] = lambda: patient_repository

    patient_id = str(uuid.uuid4())
    patient_record = {
        'patient': {},
        'meta': {'uuid': patient_id},
        'ai_diag': {
            'options': [
                'fake diagnosis option 1',
                'fake diagnosis option 2',
                'fake diagnosis option 3',
                'fake diagnosis option 4',
            ]
        },
    }
    patient_repository.create(patient_record)

    form_data = {
        'selected': ['fake diagnosis option 1', 'fake diagnosis option 4'],
        'fake diagnosis option 1--accuracy': '2',
        'fake diagnosis option 1--relevance': '4',
        'fake diagnosis option 1--usefulness': '6',
        'fake diagnosis option 1--coherence': '3',
        'fake diagnosis option 1--comments': 'This is a comment for option1.',
        'fake diagnosis option 2--accuracy': '2',
        'fake diagnosis option 2--relevance': '7',
        'fake diagnosis option 2--usefulness': '8',
        'fake diagnosis option 2--coherence': '9',
        'fake diagnosis option 2--comments': 'This is a comment for option2.',
        'fake diagnosis option 3--accuracy': '5',
        'fake diagnosis option 3--relevance': '7',
        'fake diagnosis option 3--usefulness': '3',
        'fake diagnosis option 3--coherence': '6',
        'fake diagnosis option 3--comments': 'This is a comment for option3.',
        'fake diagnosis option 4--accuracy': '8',
        'fake diagnosis option 4--relevance': '7',
        'fake diagnosis option 4--usefulness': '7',
        'fake diagnosis option 4--coherence': '8',
        'fake diagnosis option 4--comments': 'This is a comment for option4.',
    }

    # assert that there's no evaluation yet
    patient = patient_repository.get(patient_id)
    assert 'evaluations' not in patient

    # post form data
    response = client.post(
        f'/diagnosis?patient_id={patient_id}',
        data=form_data,
        follow_redirects=False,
    )
    assert response.status_code == 303

    # make form data was saved correctly
    patient = patient_repository.get(patient_id)
    for diagnosis in form_data['selected']:
        # check if selected dianosis was saved in evaluations
        assert diagnosis in patient['evaluations']['ai_diag']

        # check if saved data and form data match
        evaluations = patient['evaluations']['ai_diag'][diagnosis]['ratings']
        assert evaluations['accuracy'] == int(
            form_data[f'{diagnosis}--accuracy']
        )
        assert evaluations['relevance'] == int(
            form_data[f'{diagnosis}--relevance']
        )
        assert evaluations['usefulness'] == int(
            form_data[f'{diagnosis}--usefulness']
        )
        assert evaluations['coherence'] == int(
            form_data[f'{diagnosis}--coherence']
        )
        assert evaluations['comments'] == form_data[f'{diagnosis}--comments']

    # make sure not selected diagnoses are not in evaluations
    not_selected = set(patient['ai_diag']['options']) - set(
        form_data['selected']
    )
    for diagnosis in not_selected:
        assert diagnosis not in patient['evaluations']['ai_diag']

    # Clean up the override after the test
    app.dependency_overrides.clear()


def test_exams_post_evaluation_form(client, patient_repository):
    """Test the exams evaluation form."""
    # Override the app's dependency with the test repository
    app.dependency_overrides[get_repository] = lambda: patient_repository

    patient_id = str(uuid.uuid4())
    patient_record = {
        'patient': {},
        'meta': {'uuid': patient_id},
        'selected_diagnoses': [],
        'ai_exam': {
            'options': [
                'fake exam/test option 1',
                'fake exam/test option 2',
                'fake exam/test option 3',
                'fake exam/test option 4',
            ]
        },
    }
    patient_repository.create(patient_record)

    form_data = {
        'selected': ['fake exam/test option 1', 'fake exam/test option 4'],
        'fake exam/test option 1--accuracy': '2',
        'fake exam/test option 1--relevance': '4',
        'fake exam/test option 1--usefulness': '6',
        'fake exam/test option 1--coherence': '5',
        'fake exam/test option 1--safety': 'safe',
        'fake exam/test option 1--comments': 'This is a comment for option1.',
        'fake exam/test option 2--accuracy': '2',
        'fake exam/test option 2--relevance': '7',
        'fake exam/test option 2--usefulness': '8',
        'fake exam/test option 2--coherence': '10',
        'fake exam/test option 2--safety': 'needs_review',
        'fake exam/test option 2--comments': 'This is a comment for option2.',
        'fake exam/test option 3--accuracy': '5',
        'fake exam/test option 3--relevance': '6',
        'fake exam/test option 3--usefulness': '3',
        'fake exam/test option 3--coherence': '5',
        'fake exam/test option 3--safety': 'unsafe',
        'fake exam/test option 3--comments': 'This is a comment for option3.',
        'fake exam/test option 4--accuracy': '8',
        'fake exam/test option 4--relevance': '7',
        'fake exam/test option 4--usefulness': '7',
        'fake exam/test option 4--coherence': '9',
        'fake exam/test option 4--safety': 'safe',
        'fake exam/test option 4--comments': 'This is a comment for option4.',
    }

    # assert that there's no evaluation yet
    patient = patient_repository.get(patient_id)
    assert 'evaluations' not in patient

    # post form data
    response = client.post(
        f'/exams?patient_id={patient_id}',
        data=form_data,
        follow_redirects=False,
    )
    assert response.status_code == 303

    # make form data was saved correctly
    patient = patient_repository.get(patient_id)
    for exam in form_data['selected']:
        # check if selected dianosis was saved in evaluations
        assert exam in patient['evaluations']['ai_exam']

        # check if saved data and form data match
        evaluations = patient['evaluations']['ai_exam'][exam]['ratings']
        assert evaluations['accuracy'] == int(form_data[f'{exam}--accuracy'])
        assert evaluations['relevance'] == int(form_data[f'{exam}--relevance'])
        assert evaluations['usefulness'] == int(
            form_data[f'{exam}--usefulness']
        )
        assert evaluations['coherence'] == int(form_data[f'{exam}--coherence'])
        assert evaluations['safety'] == form_data[f'{exam}--safety']
        assert evaluations['comments'] == form_data[f'{exam}--comments']

    # make sure not selected diagnoses are not in evaluations
    not_selected = set(patient['ai_exam']['options']) - set(
        form_data['selected']
    )
    for exam in not_selected:
        assert exam not in patient['evaluations']['ai_exam']

    # Clean up the override after the test
    app.dependency_overrides.clear()
