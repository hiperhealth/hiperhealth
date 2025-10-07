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

import io
import sys
import uuid

from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

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

# Now import the project-specific modules
from sdx.agents.diagnostics import core as diag
from sdx.agents.extraction.wearable import WearableDataFileExtractor
from sdx.models.sqla.research import Patient
from sdx.privacy.deidenitfier import (
    Deidentifier,
    deidentify_patient_record,
)
from sqlalchemy.orm import Session

from research.app.database import SessionLocal
from research.models.repositories import ResearchRepository

# Add the project's 'src' and 'research' directories to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT / 'src'))
sys.path.append(str(PROJECT_ROOT))

APP_DIR = Path(__file__).parent
TEMPLATES = Environment(
    loader=FileSystemLoader(APP_DIR / 'templates'),
    autoescape=select_autoescape(),
)


# --- Database Dependency Setup ---
def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache(maxsize=None)
def get_deidentifier() -> Deidentifier:
    """Get a cached deidentifier instance."""
    return Deidentifier()


def get_repository(
    db: Session = Depends(get_db),
) -> ResearchRepository:
    """Get a repository instance with a database session."""
    return ResearchRepository(db_session=db)


# --- App Initialization ---
_STATIC = StaticFiles(directory=APP_DIR / 'static')
app = FastAPI(title='TeleHealthCareAI â€" Physician Portal')
app.mount('/static', _STATIC, name='static')


# --- Helper Functions ---
def _render(template: str, **context: Any) -> HTMLResponse:
    tpl = TEMPLATES.get_template(template)
    return HTMLResponse(tpl.render(**context))


def patient_to_dict(patient: Patient) -> Dict[str, Any]:
    """Convert a Patient ORM object to a dictionary for template rendering."""
    if not patient:
        return {}

    consultation = patient.consultations[-1] if patient.consultations else None

    patient_dict = {
        'meta': {
            'uuid': patient.uuid,
            'lang': consultation.lang if consultation else None,
            'timestamp': (
                consultation.timestamp.isoformat()
                if consultation and consultation.timestamp
                else None
            ),
        },
        'patient': {
            'age': patient.age,
            'gender': patient.gender,
        },
        'selected_diagnoses': [
            assoc.diagnosis.name for assoc in consultation.selected_diagnoses
        ]
        if consultation
        else [],
        'selected_exams': [
            assoc.exam.name for assoc in consultation.selected_exams
        ]
        if consultation
        else [],
        'ai_diag': consultation.ai_diag_raw if consultation else {},
        'ai_exam': consultation.ai_exam_raw if consultation else {},
        'evaluations': {
            'ai_diag': {
                assoc.diagnosis.name: {
                    'ratings': {
                        'accuracy': assoc.accuracy,
                        'relevance': assoc.relevance,
                        'usefulness': assoc.usefulness,
                        'coherence': assoc.coherence,
                        'comments': assoc.comments,
                    }
                }
                for assoc in consultation.selected_diagnoses
            }
            if consultation
            else {},
            'ai_exam': {
                assoc.exam.name: {
                    'ratings': {
                        'accuracy': assoc.accuracy,
                        'relevance': assoc.relevance,
                        'usefulness': assoc.usefulness,
                        'coherence': assoc.coherence,
                        'safety': assoc.safety,
                        'comments': assoc.comments,
                    }
                }
                for assoc in consultation.selected_exams
            }
            if consultation
            else {},
        },
    }

    if consultation:
        consultation_fields = [
            'weight_kg',
            'height_cm',
            'diet',
            'sleep_hours',
            'physical_activity',
            'mental_exercises',
            'symptoms',
            'mental_health',
            'previous_tests',
            'wearable_data',
        ]
        for field in consultation_fields:
            if hasattr(consultation, field):
                patient_dict['patient'][field] = getattr(consultation, field)

    return patient_dict


def _get_next_step(patient: Patient) -> str:
    """Determine the next step by checking for missing data."""
    if not patient.consultations:
        return 'demographics'

    consultation = patient.consultations[-1]

    if patient.age is None:
        return 'demographics'
    if consultation.diet is None:
        return 'lifestyle'
    if consultation.symptoms is None:
        return 'symptoms'
    if consultation.mental_health is None:
        return 'mental'
    # 'tests' step is a placeholder in this version
    if consultation.wearable_data is None:
        return 'wearable'
    if not consultation.selected_diagnoses:
        return 'diagnosis'
    if not consultation.selected_exams:
        return 'exams'
    return 'complete'


# --- FastAPI Endpoints ---


@app.get('/', response_class=HTMLResponse)
def dashboard(
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display the main dashboard with a list of patients."""
    patients = repo.list_patients()
    patients_with_status = []
    for p in patients:
        next_step = _get_next_step(p)
        is_complete = next_step == 'complete'
        patients_with_status.append(
            {'record': patient_to_dict(p), 'is_complete': is_complete}
        )
    context = {
        'title': 'Dashboard',
        'patients_with_status': patients_with_status,
    }
    return _render('dashboard.html', **context)


@app.get('/select_language', response_class=HTMLResponse)
def select_language(request: Request):
    """Display the language selection page."""
    return _render('language.html', request=request)


@app.post('/start', response_class=RedirectResponse, status_code=303)
def start_new_consultation(
    lang: str = Form(...),
    repo: ResearchRepository = Depends(get_repository),
) -> RedirectResponse:
    """Start a new consultation and redirect to the first step."""
    patient_uuid = str(uuid.uuid4())
    new_patient_record = {
        'meta': {'uuid': patient_uuid, 'lang': lang},
        'patient': {},
    }
    repo.create_patient_and_consultation(new_patient_record)
    return RedirectResponse(
        url=f'/consultation/{patient_uuid}', status_code=303
    )


@app.get('/consultation/{patient_id}', response_class=RedirectResponse)
def consultation_gatekeeper(
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> RedirectResponse:
    """Redirect user to the correct step in the consultation wizard."""
    patient = repo.get_patient_by_uuid(patient_id)
    if not patient:
        raise HTTPException(
            status_code=404, detail='Patient record not found.'
        )

    next_step = _get_next_step(patient)
    if next_step == 'complete':
        return RedirectResponse(url=f'/patient/{patient_id}', status_code=303)

    return RedirectResponse(
        f'/{next_step}?patient_id={patient_id}', status_code=303
    )


# --- Form Step Endpoints ---


@app.get('/demographics', response_class=HTMLResponse)
def demographics(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display the demographics form."""
    patient = repo.get_patient_by_uuid(patient_id)
    record = patient_to_dict(patient)
    return _render(
        'demographics.html',
        request=request,
        patient_id=patient_id,
        lang=record['meta']['lang'],
        patient_data=record['patient'],
    )


@app.post('/demographics')
def demographics_post(
    patient_id: str,
    age: int = Form(...),
    gender: str = Form(...),
    weight_kg: float = Form(...),
    height_cm: float = Form(...),
    repo: ResearchRepository = Depends(get_repository),
) -> RedirectResponse:
    """Save demographics data."""
    patient = repo.get_patient_by_uuid(patient_id)
    patient.age = age
    patient.gender = gender
    consultation = patient.consultations[-1]
    consultation.weight_kg = weight_kg
    consultation.height_cm = height_cm
    repo.db.commit()
    return RedirectResponse(f'/consultation/{patient_id}', status_code=303)


@app.get('/lifestyle', response_class=HTMLResponse)
def lifestyle(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display the lifestyle form."""
    patient = repo.get_patient_by_uuid(patient_id)
    record = patient_to_dict(patient)
    return _render(
        'lifestyle.html',
        request=request,
        patient_id=patient_id,
        lang=record['meta']['lang'],
        patient_data=record['patient'],
    )


@app.post('/lifestyle')
def lifestyle_post(
    patient_id: str,
    diet: str = Form(...),
    sleep_hours: float = Form(...),
    physical_activity: str = Form(...),
    mental_exercises: str = Form(...),
    repo: ResearchRepository = Depends(get_repository),
) -> RedirectResponse:
    """Save lifestyle data."""
    patient = repo.get_patient_by_uuid(patient_id)
    consultation = patient.consultations[-1]
    consultation.diet = diet
    consultation.sleep_hours = sleep_hours
    consultation.physical_activity = physical_activity
    consultation.mental_exercises = mental_exercises
    repo.db.commit()
    return RedirectResponse(f'/consultation/{patient_id}', status_code=303)


@app.get('/symptoms', response_class=HTMLResponse)
def symptoms(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display the symptoms form."""
    patient = repo.get_patient_by_uuid(patient_id)
    record = patient_to_dict(patient)
    return _render(
        'symptoms.html',
        request=request,
        patient_id=patient_id,
        lang=record['meta']['lang'],
        patient_data=record['patient'],
    )


@app.post('/symptoms')
def symptoms_post(
    patient_id: str,
    symptoms: str = Form(...),
    repo: ResearchRepository = Depends(get_repository),
) -> RedirectResponse:
    """Save symptoms data."""
    patient = repo.get_patient_by_uuid(patient_id)
    consultation = patient.consultations[-1]
    consultation.symptoms = symptoms
    repo.db.commit()
    return RedirectResponse(f'/consultation/{patient_id}', status_code=303)


@app.get('/mental', response_class=HTMLResponse)
def mental(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display the mental health form."""
    patient = repo.get_patient_by_uuid(patient_id)
    record = patient_to_dict(patient)
    return _render(
        'mental.html',
        request=request,
        patient_id=patient_id,
        lang=record['meta']['lang'],
        patient_data=record['patient'],
    )


@app.post('/mental')
def mental_post(
    patient_id: str,
    mental_health: str = Form(...),
    repo: ResearchRepository = Depends(get_repository),
) -> RedirectResponse:
    """Save mental health data."""
    patient = repo.get_patient_by_uuid(patient_id)
    consultation = patient.consultations[-1]
    consultation.mental_health = mental_health
    repo.db.commit()
    return RedirectResponse(f'/consultation/{patient_id}', status_code=303)


@app.get('/tests', response_class=HTMLResponse)
def tests(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display the previous tests form."""
    patient = repo.get_patient_by_uuid(patient_id)
    record = patient_to_dict(patient)
    return _render(
        'tests.html',
        request=request,
        patient_id=patient_id,
        lang=record['meta']['lang'],
        patient_data=record['patient'],
    )


@app.post('/tests')
async def tests_post(
    patient_id: str = Form(...),
    has_reports: str = Form(...),
    repo: ResearchRepository = Depends(get_repository),
) -> RedirectResponse:
    """Handle previous tests data (placeholder)."""
    return RedirectResponse(f'/consultation/{patient_id}', status_code=303)


@app.get('/wearable', response_class=HTMLResponse)
def wearable(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display the wearable data upload form."""
    patient = repo.get_patient_by_uuid(patient_id)
    record = patient_to_dict(patient)
    return _render(
        'wearable.html',
        request=request,
        patient_id=patient_id,
        lang=record['meta']['lang'],
        patient_data=record['patient'],
    )


@app.post('/wearable')
async def wearable_post(
    patient_id: str,
    file: Optional[UploadFile] = File(None),
    skip: Optional[str] = Form(None),
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Handle wearable data upload or skip."""
    patient = repo.get_patient_by_uuid(patient_id)
    consultation = patient.consultations[-1]

    if skip:
        consultation.wearable_data = []  # Mark as skipped
        repo.db.commit()
        return RedirectResponse(f'/consultation/{patient_id}', status_code=303)

    if file and file.size > 0:
        extractor = WearableDataFileExtractor()
        try:
            file_content = await file.read()
            wearable_data = extractor.extract_wearable_data(
                io.BytesIO(file_content)
            )
            consultation.wearable_data = wearable_data
            repo.db.commit()
            return RedirectResponse(
                f'/consultation/{patient_id}', status_code=303
            )
        except Exception as e:
            record = patient_to_dict(patient)
            context = {
                'patient_id': patient_id,
                'lang': record['meta']['lang'],
                'patient_data': record['patient'],
                'error': str(e),
            }
            return _render('wearable.html', **context)

    record = patient_to_dict(patient)
    context = {
        'patient_id': patient_id,
        'lang': record['meta']['lang'],
        'patient_data': record['patient'],
        'error': 'Please either upload a file or skip this step.',
    }
    return _render('wearable.html', **context)


@app.get('/diagnosis', response_class=HTMLResponse)
def diagnosis(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display AI-generated diagnosis suggestions."""
    patient = repo.get_patient_by_uuid(patient_id)
    record = patient_to_dict(patient)
    lang = record['meta']['lang']

    ai = diag.differential(
        record['patient'], language=lang, session_id=patient_id
    )

    consultation = patient.consultations[-1]
    consultation.ai_diag_raw = ai.model_dump()
    repo.db.commit()

    return _render(
        'diagnosis.html',
        request=request,
        patient_id=patient_id,
        summary=ai.summary,
        options=ai.options,
        lang=lang,
    )


@app.post('/diagnosis')
async def diagnosis_post(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> RedirectResponse:
    """Save selected diagnoses and evaluations."""
    form_data = await request.form()
    selected = form_data.getlist('selected')
    custom = form_data.getlist('custom')

    record = patient_to_dict(repo.get_patient_by_uuid(patient_id))
    record['selected_diagnoses'] = selected + custom
    record['evaluations'] = {'ai_diag': {}, 'ai_exam': {}}

    for diagnosis in selected:
        record['evaluations']['ai_diag'][diagnosis] = {
            'ratings': {
                'accuracy': form_data.get(f'{diagnosis}--accuracy'),
                'relevance': form_data.get(f'{diagnosis}--relevance'),
                'usefulness': form_data.get(f'{diagnosis}--usefulness'),
                'coherence': form_data.get(f'{diagnosis}--coherence'),
                'comments': form_data.get(f'{diagnosis}--comments'),
            }
        }

    repo.update_consultation(patient_id, record)
    return RedirectResponse(f'/consultation/{patient_id}', status_code=303)


@app.get('/exams', response_class=HTMLResponse)
def exams(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display AI-generated exam suggestions."""
    patient = repo.get_patient_by_uuid(patient_id)
    record = patient_to_dict(patient)
    lang = record['meta']['lang']

    ai = diag.exams(
        record['selected_diagnoses'], language=lang, session_id=patient_id
    )

    consultation = patient.consultations[-1]
    consultation.ai_exam_raw = ai.model_dump()
    repo.db.commit()

    return _render(
        'exams.html',
        request=request,
        patient_id=patient_id,
        summary=ai.summary,
        options=ai.options,
        lang=lang,
    )


@app.post('/exams')
async def exams_post(
    request: Request,
    patient_id: str,
    deidentifier: Deidentifier = Depends(get_deidentifier),
    repo: ResearchRepository = Depends(get_repository),
) -> RedirectResponse:
    """Save selected exams, evaluations, and finalize the record."""
    form_data = await request.form()
    selected = form_data.getlist('selected')
    custom = form_data.getlist('custom')

    record = patient_to_dict(repo.get_patient_by_uuid(patient_id))
    record['selected_exams'] = selected + custom
    record['meta']['timestamp'] = datetime.utcnow().isoformat()

    for exam in selected:
        record['evaluations']['ai_exam'][exam] = {
            'ratings': {
                'accuracy': form_data.get(f'{exam}--accuracy'),
                'relevance': form_data.get(f'{exam}--relevance'),
                'usefulness': form_data.get(f'{exam}--usefulness'),
                'coherence': form_data.get(f'{exam}--coherence'),
                'safety': form_data.get(f'{exam}--safety'),
                'comments': form_data.get(f'{exam}--comments'),
            }
        }

    deidentified_record = deidentify_patient_record(record, deidentifier)
    repo.update_consultation(patient_id, deidentified_record)
    return RedirectResponse(f'/done?patient_id={patient_id}', status_code=303)


@app.get('/done', response_class=HTMLResponse)
def done(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display the final confirmation page."""
    patient = repo.get_patient_by_uuid(patient_id)
    return _render(
        'done.html',
        request=request,
        record=patient_to_dict(patient),
        lang=patient.consultations[-1].lang,
    )


@app.get('/patient/{patient_id}', response_class=HTMLResponse)
def patient(
    request: Request,
    patient_id: str,
    repo: ResearchRepository = Depends(get_repository),
) -> HTMLResponse:
    """Display the full details of a completed patient record."""
    patient = repo.get_patient_by_uuid(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')

    active_tab = request.query_params.get('active_tab', 'demographics')
    context = {
        'title': 'Patient',
        'patient': patient_to_dict(patient),
        'active_tab': active_tab,
    }
    return _render('patient.html', **context)


@app.post(
    '/delete-patient/{patient_id}',
    response_class=RedirectResponse,
    status_code=303,
)
def delete_patient(
    patient_id: str, repo: ResearchRepository = Depends(get_repository)
) -> RedirectResponse:
    """Delete a patient record."""
    repo.delete_patient(patient_id)
    return RedirectResponse(url='/', status_code=303)
