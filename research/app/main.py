"""
FastAPI application exposing a multi-step consultation wizard for physicians.

The workflow reproduces *exactly* the CLI steps:

1. Demographics
2. Lifestyle
3. Symptoms
4. Mental health
5. Previous tests
6. AI differential diagnosis → physician selects
7. AI exam suggestions → physician selects
8. Persist record & show confirmation

This refactored version ensures data is persisted at each step using a
repository pattern, preventing data loss on server restart. State is
derived from the patient data itself.
"""

from __future__ import annotations

import uuid

from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sdx.agents.diagnostics import core as diag  # OpenAI helpers
from sdx.agents.extraction.wearable import (
    WearableDataExtractorError,
    WearableDataFileExtractor,
)
from sdx.privacy.deidenitfier import (
    Deidentifier,
    deidentify_patient_record,
)

from research.models.repositories import PatientRepository

APP_DIR = Path(__file__).parent
PATIENTS_JSON_PATH = APP_DIR / 'data' / 'patients' / 'patients.json'

TEMPLATES = Environment(
    loader=FileSystemLoader(APP_DIR / 'templates'),
    autoescape=select_autoescape(),
)


@lru_cache(maxsize=None)
def get_deidentifier() -> Deidentifier:
    """Initialize and return a singleton instance of the Deidentifier."""
    return Deidentifier()


# Helper function to get a repository instance
def get_repository() -> PatientRepository:
    """Get an instance of the PatientRepository."""
    print(PATIENTS_JSON_PATH)
    return PatientRepository(data_path=PATIENTS_JSON_PATH)


_STATIC = StaticFiles(directory=APP_DIR / 'static')

app = FastAPI(title='TeleHealthCareAI — Physician Portal')
app.mount('/static', _STATIC, name='static')


def _render(template: str, **context: Any) -> HTMLResponse:
    """Render a Jinja template located in *templates/*."""
    tpl = TEMPLATES.get_template(template)
    return HTMLResponse(tpl.render(**context))


def _get_next_step(patient: Dict[str, Any]) -> str:
    """Determine the next step in the consultation by checking missing data.

    This is the core of the "Data Derivation" approach.
    """
    patient_data = patient.get('patient', {})
    if 'age' not in patient_data:
        return 'demographics'
    if 'diet' not in patient_data:
        return 'lifestyle'
    if 'symptoms' not in patient_data:
        return 'symptoms'
    if 'mental_health' not in patient_data:
        return 'mental'
    if 'previous_tests' not in patient_data:
        return 'tests'
    if 'wearable_data' not in patient_data:
        return 'wearable'
    if 'selected_diagnoses' not in patient:
        return 'diagnosis'
    if 'selected_exams' not in patient:
        return 'exams'
    return 'complete'


@app.get('/', response_class=HTMLResponse)
def dashboard(
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Dashboard page view with all recorded patients."""
    patients = repo.all()
    # Augment patient data with completion status for the template
    patients_with_status = []
    for p in patients:
        next_step = _get_next_step(p)
        is_complete = next_step == 'complete'
        patients_with_status.append({'record': p, 'is_complete': is_complete})

    context = {
        'title': 'Dashboard',
        'patients_with_status': patients_with_status,
    }
    return _render('dashboard.html', **context)


@app.get('/start', response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    """Show language selector."""
    return _render('language.html', request=request)


@app.post('/start', response_class=RedirectResponse, status_code=303)
def start_new_consultation(
    lang: str = Form(...),
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Create a new, empty patient record and redirect to the first step."""
    patient_id = str(uuid.uuid4())
    new_patient_record = {
        'patient': {},
        'meta': {'uuid': patient_id, 'lang': lang},
    }

    # The patient_id is already inside the record, so we don't pass it here.
    repo.create(new_patient_record)

    # Redirect to the central gatekeeper to start the flow
    return RedirectResponse(url=f'/consultation/{patient_id}', status_code=303)


@app.get('/consultation/{patient_id}', response_class=RedirectResponse)
def consultation_gatekeeper(
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Central redirector. Fetch patient, determine next step, and redirect."""
    patient = repo.get(patient_id)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail='Patient record not found.',
        )

    next_step = _get_next_step(patient)
    if next_step == 'complete':
        # If the consultation is done, go to the patient detail view
        return RedirectResponse(url=f'/patient/{patient_id}', status_code=303)

    # Redirect to the next required step in the wizard
    return RedirectResponse(
        url=f'/{next_step}?patient_id={patient_id}',
        status_code=303,
    )


@app.get('/select-language', response_class=HTMLResponse)
def select_language(request: Request) -> HTMLResponse:
    """Display language selection form."""
    return _render('language.html', request=request)


@app.get('/demographics', response_class=HTMLResponse)
def demographics(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Render demographics form."""
    patient = repo.get(patient_id)
    return _render(
        'demographics.html',
        request=request,
        patient_id=patient_id,
        lang=patient['meta'].get('lang', 'en'),
        patient_data=patient.get('patient', {}),
    )


@app.post('/demographics')
def demographics_post(
    patient_id: str,
    age: int = Form(...),
    gender: str = Form(...),
    weight_kg: float = Form(...),
    height_cm: float = Form(...),
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Handle demographics POST."""
    patient = repo.get(patient_id)
    patient['patient'].update(
        age=age,
        gender=gender,
        weight_kg=weight_kg,
        height_cm=height_cm,
    )
    repo.update(patient_id, patient)
    return RedirectResponse(url=f'/consultation/{patient_id}', status_code=303)


@app.get('/lifestyle', response_class=HTMLResponse)
def lifestyle(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle lifestyle GET request."""
    patient = repo.get(patient_id)
    return _render(
        'lifestyle.html',
        request=request,
        patient_id=patient_id,
        lang=patient['meta'].get('lang', 'en'),
        patient_data=patient.get('patient', {}),
    )


@app.post('/lifestyle')
def lifestyle_post(
    patient_id: str,
    diet: str = Form(...),
    sleep_hours: float = Form(...),
    physical_activity: str = Form(...),
    mental_exercises: str = Form(...),
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Handle lifestyle POST request."""
    patient = repo.get(patient_id)
    patient['patient'].update(
        diet=diet,
        sleep_hours=sleep_hours,
        physical_activity=physical_activity,
        mental_exercises=mental_exercises,
    )
    repo.update(patient_id, patient)
    return RedirectResponse(url=f'/consultation/{patient_id}', status_code=303)


@app.get('/symptoms', response_class=HTMLResponse)
def symptoms(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle symptoms GET request."""
    patient = repo.get(patient_id)
    return _render(
        'symptoms.html',
        request=request,
        patient_id=patient_id,
        lang=patient['meta'].get('lang', 'en'),
        patient_data=patient.get('patient', {}),
    )


@app.post('/symptoms')
def symptoms_post(
    patient_id: str,
    symptoms: str = Form(...),
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Handle symptoms POST request."""
    patient = repo.get(patient_id)
    patient['patient']['symptoms'] = symptoms
    repo.update(patient_id, patient)
    return RedirectResponse(url=f'/consultation/{patient_id}', status_code=303)


@app.get('/mental', response_class=HTMLResponse)
def mental(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle mental GET request."""
    patient = repo.get(patient_id)
    return _render(
        'mental.html',
        request=request,
        patient_id=patient_id,
        lang=patient['meta'].get('lang', 'en'),
        patient_data=patient.get('patient', {}),
    )


@app.post('/mental')
def mental_post(
    patient_id: str,
    mental_health: str = Form(...),
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Handle mental POST request."""
    patient = repo.get(patient_id)
    patient['patient']['mental_health'] = mental_health
    repo.update(patient_id, patient)
    return RedirectResponse(url=f'/consultation/{patient_id}', status_code=303)


@app.get('/tests', response_class=HTMLResponse)
def tests(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle tests GET request."""
    patient = repo.get(patient_id)
    return _render(
        'tests.html',
        request=request,
        patient_id=patient_id,
        lang=patient['meta'].get('lang', 'en'),
        patient_data=patient.get('patient', {}),
    )


@app.post('/tests')
def tests_post(
    patient_id: str,
    previous_tests: str = Form(...),
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Handle tests POST request."""
    patient = repo.get(patient_id)
    patient['patient']['previous_tests'] = previous_tests
    repo.update(patient_id, patient)
    return RedirectResponse(url=f'/consultation/{patient_id}', status_code=303)


@app.get('/wearable', response_class=HTMLResponse)
def wearable(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle wearable GET data."""
    patient = repo.get(patient_id)
    return _render(
        'wearable.html',
        request=request,
        patient_id=patient_id,
        lang=patient['meta'].get('lang', 'en'),
        patient_data=patient.get('patient', {}),
    )


@app.post('/wearable', response_class=HTMLResponse)
def wearable_post(
    patient_id: str,
    file: UploadFile = File(...),
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle wearable data file upload POST request."""
    patient = repo.get(patient_id)
    context = {'patient_id': patient_id}
    # TODO: use depends to inject the extractor
    extractor = WearableDataFileExtractor()

    # check if file exists before trying to use it
    if file.size > 0:
        # uses sdx to check if file is supported
        if extractor.is_supported(file.file):
            # there's a possibility of having a malformatted/corrupted file
            # even if the file is supported so we should try to process it
            try:
                wearable_data = extractor.extract_wearable_data(file.file)
                patient['patient']['wearable_data'] = wearable_data
                repo.update(patient_id, patient)
                return RedirectResponse(
                    f'/consultation/{patient_id}', status_code=303
                )
            except WearableDataExtractorError as e:
                # if we catch an error, we should show the user the error
                # by adding it to contex
                context['error'] = str(e)
                return _render('wearable.html', **context)
        else:
            # in this case the file is not supported
            context['error'] = 'File is not supported.'
            return _render('wearable.html', **context)

    # if no file was uploaded, just continue to the next step
    return RedirectResponse(f'/consultation/{patient_id}', status_code=303)


@app.get('/diagnosis', response_class=HTMLResponse)
def diagnosis(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle diagnosis GET request."""
    patient = repo.get(patient_id)
    lang = patient['meta'].get('lang', 'en')
    ai = diag.differential(
        patient['patient'],
        language=lang,
        session_id=patient_id,
    )

    patient['ai_diag'] = ai.model_dump()
    repo.update(patient_id, patient)

    return _render(
        'diagnosis.html',
        request=request,
        patient_id=patient_id,
        summary=ai.summary,
        options=ai.options,
        lang=lang,
    )


@app.post('/diagnosis')
def diagnosis_post(
    request: Request,
    patient_id: str,
    selected: Optional[List[str]] = Form([]),
    custom: Optional[List[str]] = Form([]),
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Handle diagnosis POST request."""
    patient = repo.get(patient_id)
    patient['selected_diagnoses'] = selected
    patient.setdefault('evaluations', {})['ai_diag'] = {}

    form_data = anyio.run(request.form)

    if selected:
        # get evaluation only from selected diagnoses
        for diagnosis in selected:
            evaluation = {
                'ratings': {
                    'accuracy': None,
                    'relevance': None,
                    'usefulness': None,
                    'coherence': None,
                    'comments': None,
                }
            }

            # get form values for selected diagnosis
            for key, value in form_data.items():
                if key.startswith(diagnosis):
                    criteria = key.split('--')[1]
                    evaluation['ratings'][criteria] = (
                        int(value) if value.isdigit() else value
                    )

            # add diagnosis evaluation to record
            patient['evaluations']['ai_diag'][diagnosis] = evaluation

    if custom:
        patient['selected_diagnoses'].extend(custom)

    repo.update(patient_id, patient)
    return RedirectResponse(url=f'/consultation/{patient_id}', status_code=303)


@app.get('/exams', response_class=HTMLResponse)
def exams(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle exams GET request."""
    patient = repo.get(patient_id)
    lang = patient['meta'].get('lang', 'en')
    ai = diag.exams(
        patient['selected_diagnoses'],
        language=lang,
        session_id=patient_id,
    )

    patient['ai_exam'] = ai.model_dump()
    repo.update(patient_id, patient)

    return _render(
        'exams.html',
        request=request,
        patient_id=patient_id,
        summary=ai.summary,
        options=ai.options,
        lang=lang,
    )


@app.post('/exams')
def exams_post(
    request: Request,
    patient_id: str,
    selected: Optional[List[str]] = Form([]),
    custom: Optional[List[str]] = Form([]),
    deidentifier: Deidentifier = Depends(get_deidentifier),
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Handle exams POST request."""
    patient = repo.get(patient_id)
    patient['selected_exams'] = selected
    patient['meta']['timestamp'] = datetime.utcnow().isoformat(
        timespec='seconds'
    )
    patient.setdefault('evaluations', {})['ai_exam'] = {}

    form_data = anyio.run(request.form)

    if selected:
        # get evaluation only from selected exams
        for exam in selected:
            evaluation = {
                'ratings': {
                    'accuracy': None,
                    'relevance': None,
                    'usefulness': None,
                    'coherence': None,
                    'safety': None,
                    'comments': None,
                }
            }

            # get form values for selected exam
            for key, value in form_data.items():
                if key.startswith(exam):
                    criteria = key.split('--')[1]
                    evaluation['ratings'][criteria] = (
                        int(value) if value.isdigit() else value
                    )

            # add diagnosis evaluation to record
            patient['evaluations']['ai_exam'][exam] = evaluation

    if custom:
        patient['selected_exams'].extend(custom)

    # De-identify all relevant fields in the patient record before update.
    deidentified_patient_record = deidentify_patient_record(
        patient, deidentifier
    )

    repo.update(patient_id, deidentified_patient_record)
    return RedirectResponse(f'/done?patient_id={patient_id}', status_code=303)


@app.get('/done', response_class=HTMLResponse)
def done(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle done GET request."""
    patient = repo.get(patient_id)
    return _render(
        'done.html',
        request=request,
        record=patient,
        lang=patient['meta'].get('lang', 'en'),
    )


@app.get('/patient/{patient_id}', response_class=HTMLResponse)
def patient(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> HTMLResponse:
    """View a single patient record."""
    patient = repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')

    active_tab = request.query_params.get('active_tab', 'demographics')
    context = {
        'title': 'Patient',
        'patient': patient,
        'active_tab': active_tab,
    }

    return _render('patient.html', **context)


@app.post(
    '/delete-patient/{patient_id}',
    response_class=RedirectResponse,
    status_code=303,
)
def delete_patient(
    request: Request,
    patient_id: str,
    repo: PatientRepository = Depends(get_repository),
) -> RedirectResponse:
    """Delete one patient by id."""
    repo.delete(patient_id)
    return RedirectResponse(url='/', status_code=303)
