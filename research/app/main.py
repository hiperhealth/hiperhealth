"""
FastAPI application exposing a multi-step consultation wizard for physicians.

The workflow reproduces *exactly* the CLI steps:

    1. Demographics
    2. Lifestyle
    3. Symptoms
    4. Mental health
    5. Previous tests
    6. AI differential diagnosis  → physician selects
    7. AI exam suggestions        → physician selects
    8. Persist record & show confirmation

State is kept server-side in a simple in-memory store (`_SESSIONS`);
swap in Redis or a DB for production.
"""

from __future__ import annotations

import uuid

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sdx.agents.diagnostics import core as diag  # OpenAI helpers
from sdx.agents.extraction.wearable import (
    WearableDataExtractorError,
    WearableDataFileExtractor,
)

from research.models.repositories import PatientRepository

APP_DIR = Path(__file__).parent
TEMPLATES = Environment(
    loader=FileSystemLoader(APP_DIR / 'templates'),
    autoescape=select_autoescape(),
)


_STATIC = StaticFiles(directory=APP_DIR / 'static')
_SESSIONS: Dict[str, Dict[str, Any]] = {}  # swap with redis if needed

app = FastAPI(title='TeleHealthCareAI — Physician Portal')
app.mount('/static', _STATIC, name='static')


@app.get('/', response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    """Dashboard page view with all recorded patients."""
    repo = PatientRepository()
    patients = repo.all()

    context = {'title': 'Dashboard', 'patients': patients}

    return _render('dashboard.html', **context)


@app.get('/start', response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    """Show language selector."""
    return _render('language.html', request=request)


@app.post('/start', response_class=RedirectResponse, status_code=303)
def start_with_language(lang: str = Form(...)) -> RedirectResponse:
    """Create a session after the physician chooses a language."""
    sid = str(uuid.uuid4())
    _SESSIONS[sid] = {
        'patient': {},
        'meta': {'uuid': sid, 'lang': lang},
    }
    return RedirectResponse(url=f'/demographics?sid={sid}', status_code=303)


def _render(template: str, **context: Any) -> HTMLResponse:
    """Render a Jinja template located in *templates/*."""
    tpl = TEMPLATES.get_template(template)
    return HTMLResponse(tpl.render(**context))


@app.get('/select-language', response_class=HTMLResponse)
def select_language(request: Request) -> HTMLResponse:
    """Display language selection form."""
    return _render('language.html', request=request)


def _session_or_404(sid: str) -> Dict[str, Any]:
    """Return the session dict or raise 404."""
    if sid not in _SESSIONS:
        raise HTTPException(status_code=404, detail='Session expired')
    return _SESSIONS[sid]


@app.get('/demographics', response_class=HTMLResponse)
def demographics(request: Request, sid: str) -> HTMLResponse:
    """Render demographics form."""
    sess = _session_or_404(sid)
    return _render(
        'demographics.html',
        request=request,
        sid=sid,
        lang=sess['meta'].get('lang', 'en'),
    )


@app.post('/demographics')
def demographics_post(
    sid: str,
    age: int = Form(...),
    gender: str = Form(...),
    weight_kg: float = Form(...),
    height_cm: float = Form(...),
) -> RedirectResponse:
    """Handle demographics POST."""
    sess = _session_or_404(sid)
    sess['patient'].update(
        age=age, gender=gender, weight_kg=weight_kg, height_cm=height_cm
    )
    return RedirectResponse(f'/lifestyle?sid={sid}', status_code=303)


@app.get('/lifestyle', response_class=HTMLResponse)
def lifestyle(request: Request, sid: str) -> HTMLResponse:
    """Handle lifestyle GET request."""
    sess = _session_or_404(sid)
    return _render(
        'lifestyle.html',
        request=request,
        sid=sid,
        lang=sess['meta'].get('lang', 'en'),
    )


@app.post('/lifestyle')
def lifestyle_post(
    sid: str,
    diet: str = Form(...),
    sleep_hours: float = Form(...),
    physical_activity: str = Form(...),
    mental_exercises: str = Form(...),
) -> RedirectResponse:
    """Handle lifestyle POST request."""
    sess = _session_or_404(sid)
    sess['patient'].update(
        diet=diet,
        sleep_hours=sleep_hours,
        physical_activity=physical_activity,
        mental_exercises=mental_exercises,
    )
    return RedirectResponse(f'/symptoms?sid={sid}', status_code=303)


@app.get('/symptoms', response_class=HTMLResponse)
def symptoms(request: Request, sid: str) -> HTMLResponse:
    """Handle symptoms GET request."""
    sess = _session_or_404(sid)
    return _render(
        'symptoms.html',
        request=request,
        sid=sid,
        lang=sess['meta'].get('lang', 'en'),
    )


@app.post('/symptoms')
def symptoms_post(sid: str, symptoms: str = Form(...)) -> RedirectResponse:
    """Handle symptoms POST request."""
    sess = _session_or_404(sid)
    sess['patient']['symptoms'] = symptoms
    return RedirectResponse(f'/mental?sid={sid}', status_code=303)


@app.get('/mental', response_class=HTMLResponse)
def mental(request: Request, sid: str) -> HTMLResponse:
    """Handle mental GET request."""
    sess = _session_or_404(sid)
    return _render(
        'mental.html',
        request=request,
        sid=sid,
        lang=sess['meta'].get('lang', 'en'),
    )


@app.post('/mental')
def mental_post(sid: str, mental_health: str = Form(...)) -> RedirectResponse:
    """Handle mental POST request."""
    sess = _session_or_404(sid)
    sess['patient']['mental_health'] = mental_health
    return RedirectResponse(f'/tests?sid={sid}', status_code=303)


@app.get('/tests', response_class=HTMLResponse)
def tests(request: Request, sid: str) -> HTMLResponse:
    """Handle tests GET request."""
    sess = _session_or_404(sid)
    return _render(
        'tests.html',
        request=request,
        sid=sid,
        lang=sess['meta'].get('lang', 'en'),
    )


@app.post('/tests')
def tests_post(sid: str, previous_tests: str = Form(...)) -> RedirectResponse:
    """Handle tests POST request."""
    sess = _session_or_404(sid)
    sess['patient']['previous_tests'] = previous_tests
    return RedirectResponse(f'/wearable?sid={sid}', status_code=303)


@app.get('/wearable', response_class=HTMLResponse)
def wearable(sid: str) -> HTMLResponse:
    """Handle wearable GET request."""
    return _render('wearable.html', sid=sid)


@app.post('/wearable', response_class=HTMLResponse)
def wearable_post(sid: str, file: UploadFile = File(...)) -> HTMLResponse:
    """Handle wearable data file upload POST request."""
    # sess = _session_or_404(sid)
    sess = _session_or_404(sid)
    context = {'sid': sid}
    extractor = WearableDataFileExtractor()

    # check if file exists before trying to use it
    if file.size > 0:
        # uses sdx to check if file is supported
        if extractor.is_supported(file.file):
            # there's a possibility of having a malformatted/corrupted file
            # even if the file is supported so we should try to process it
            try:
                wearable_data = extractor.extract_wearable_data(file.file)
                sess['wearable_data'] = wearable_data
                return RedirectResponse(
                    f'/diagnosis?sid={sid}', status_code=303
                )
            except WearableDataExtractorError as e:
                # if we catch an error, we should show the user the error
                # by adding it to context
                context['error'] = str(e)
                return _render('wearable.html', **context)
        else:
            # in this case the file is not supported
            context['error'] = 'File is not supported.'
            return _render('wearable.html', **context)

    # if no file was uploaded, just continue to the next step
    return RedirectResponse(f'/diagnosis?sid={sid}', status_code=303)


@app.get('/diagnosis', response_class=HTMLResponse)
def diagnosis(request: Request, sid: str) -> HTMLResponse:
    """Handle diagnosis GET request."""
    sess = _session_or_404(sid)
    lang = sess['meta'].get('lang', 'en')
    ai = diag.differential(sess['patient'], language=lang, session_id=sid)
    sess['ai_diag'] = ai.model_dump()
    return _render(
        'diagnosis.html',
        request=request,
        sid=sid,
        summary=ai.summary,
        options=ai.options,
        lang=lang,
    )


@app.post('/diagnosis')
def diagnosis_post(
    request: Request,
    sid: str,
    selected: Optional[List[str]] = Form([]),
    custom: Optional[List[str]] = Form([]),
) -> RedirectResponse:
    """Handle diagnosis POST request."""
    sess = _session_or_404(sid)
    sess['selected_diagnoses'] = selected
    sess.setdefault('evaluations', {})
    sess['evaluations']['ai_diag'] = {}

    # get form data from request from async to sync
    form = anyio.run(request.form)

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
            for key, value in form.items():
                if key.startswith(diagnosis):
                    criteria = key.split('--')[1]
                    evaluation['ratings'][criteria] = (
                        int(value) if value.isdigit() else value
                    )

            # add diagnosis evaluation to record
            sess['evaluations']['ai_diag'][diagnosis] = evaluation

    if custom:
        sess['selected_diagnoses'].extend(custom)

    return RedirectResponse(f'/exams?sid={sid}', status_code=303)


@app.get('/exams', response_class=HTMLResponse)
def exams(request: Request, sid: str) -> HTMLResponse:
    """Handle exams GET request."""
    sess = _session_or_404(sid)
    lang = sess['meta'].get('lang', 'en')
    ai = diag.exams(sess['selected_diagnoses'], language=lang, session_id=sid)
    sess['ai_exam'] = ai.model_dump()
    return _render(
        'exams.html',
        request=request,
        session_id=sid,
        summary=ai.summary,
        options=ai.options,
        lang=lang,
    )


@app.post('/exams')
def exams_post(
    request: Request,
    sid: str,
    selected: Optional[List[str]] = Form([]),
    custom: Optional[List[str]] = Form([]),
) -> RedirectResponse:
    """Handle exams POST request."""
    sess = _session_or_404(sid)
    sess['selected_exams'] = selected
    sess['meta']['timestamp'] = datetime.utcnow().isoformat(timespec='seconds')
    sess.setdefault('evaluations', {})
    sess['evaluations']['ai_exam'] = {}

    # get form data from request from async to sync
    form = anyio.run(request.form)

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
            for key, value in form.items():
                if key.startswith(exam):
                    criteria = key.split('--')[1]
                    evaluation['ratings'][criteria] = (
                        int(value) if value.isdigit() else value
                    )

            # add diagnosis evaluation to record
            sess['evaluations']['ai_exam'][exam] = evaluation

    if custom:
        sess['selected_exams'].extend(custom)

    repo = PatientRepository()
    repo.create(sess)
    return RedirectResponse(f'/done?sid={sid}', status_code=303)


@app.get('/done', response_class=HTMLResponse)
def done(request: Request, sid: str) -> HTMLResponse:
    """Handle done GET request."""
    sess = _session_or_404(sid)
    return _render(
        'done.html',
        request=request,
        record=sess,
        lang=sess['meta'].get('lang', 'en'),
    )


@app.get('/patient/{patient_id}', response_class=HTMLResponse)
def patient(request: Request, patient_id: str) -> HTMLResponse:
    """View all patients."""
    repo = PatientRepository()
    patient = repo.get(patient_id)
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
def delete_patient(request: Request, patient_id: str) -> RedirectResponse:
    """Delete one patient by id."""
    # The page the request came from
    referer = request.headers.get('referer')
    repo = PatientRepository()
    repo.delete(patient_id)

    return RedirectResponse(referer, status_code=303)
