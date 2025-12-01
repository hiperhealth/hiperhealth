"""FastAPI backend for patient data management and wearable file uploads."""

import os

from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from . import crud, database, models, schemas, utils

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
utils.ensure_upload_dir(UPLOAD_DIR)

app = FastAPI(title='research-poc backend')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def on_startup():
    """Initialize database tables on startup."""
    database.create_tables()


def get_db():
    """Provide database session for dependency injection."""
    yield from database.get_db()


@app.post(
    '/api/v1/patients', response_model=schemas.PatientOut, status_code=201
)
def create_patient(
    payload: schemas.PatientCreate, db: Session = Depends(get_db)
):
    """Create a new patient record."""
    patient = crud.create_patient(db, name=payload.name)
    # if demographics were provided inline, upsert
    demo = {}
    if (
        payload.age is not None
        or payload.gender
        or payload.weight is not None
        or payload.height is not None
    ):
        demo = {
            k: v
            for k, v in {
                'age': payload.age,
                'gender': payload.gender,
                'weight': payload.weight,
                'height': payload.height,
            }.items()
            if v is not None
        }
        if demo:
            crud.upsert_demographics(db, patient.id, demo)

    # build response minimal
    out = schemas.PatientOut.from_orm(patient)
    return out


@app.get('/api/v1/patients', response_model=List[schemas.PatientOut])
def list_patients(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    """List all patients with pagination."""
    items = crud.list_patients(db, skip=skip, limit=limit)
    return [schemas.PatientOut.from_orm(i) for i in items]


@app.get('/api/v1/patients/{patient_id}', response_model=schemas.PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Retrieve a single patient record with all related data."""
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail='Patient not found')

    # attach related records
    dem = db.get(models.Demographics, patient_id)
    life = db.get(models.Lifestyle, patient_id)
    notes = (
        db.execute(
            models.ClinicalNote.__table__.select().where(
                models.ClinicalNote.patient_id == patient_id
            )
        )
        .scalars()
        .all()
    )
    wearables = crud.list_wearables_for_patient(db, patient_id)

    out = schemas.PatientOut.from_orm(p)
    out.demographics = dem
    out.lifestyle = life
    out.notes = [
        schemas.ClinicalNoteCreate(note_type=n.note_type, content=n.content)
        for n in notes
    ]
    out.wearable_files = wearables
    return out


@app.get('/api/v1/dashboard/stats')
def dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics: totals and recent patients."""
    stats = crud.get_dashboard_stats(db)
    # convert recent patients to simple dicts
    recent = []
    for p in stats.get('recent_patients', []):
        recent.append(
            {
                'id': p.id,
                'name': p.name,
                'created_at': p.created_at.isoformat()
                if p.created_at
                else None,
            }
        )
    return {
        'total_patients': stats['total_patients'],
        'active_records': stats['active_records'],
        'this_month': stats['this_month'],
        'recent_patients': recent,
    }


@app.delete('/api/v1/patients/{patient_id}', status_code=204)
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    """Delete a patient and all related records."""
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail='Patient not found')
    crud.delete_patient(db, patient_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put(
    '/api/v1/patients/{patient_id}/demographics',
    response_model=schemas.DemographicsBase,
)
def put_demographics(
    patient_id: str,
    payload: schemas.DemographicsBase,
    db: Session = Depends(get_db),
):
    """Update patient demographics."""
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail='Patient not found')
    obj = crud.upsert_demographics(
        db, patient_id, payload.dict(exclude_none=True)
    )
    return obj


@app.put(
    '/api/v1/patients/{patient_id}/lifestyle',
    response_model=schemas.LifestyleBase,
)
def put_lifestyle(
    patient_id: str,
    payload: schemas.LifestyleBase,
    db: Session = Depends(get_db),
):
    """Update patient lifestyle information."""
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail='Patient not found')
    obj = crud.upsert_lifestyle(
        db, patient_id, payload.dict(exclude_none=True)
    )
    return obj


@app.post('/api/v1/patients/{patient_id}/notes', status_code=201)
def post_note(
    patient_id: str,
    payload: schemas.ClinicalNoteCreate,
    db: Session = Depends(get_db),
):
    """Add a clinical note for a patient."""
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail='Patient not found')
    note = crud.add_clinical_note(
        db, patient_id, payload.note_type, payload.content
    )
    return {'id': note.id, 'created_at': note.created_at}


@app.post('/api/v1/patients/{patient_id}/wearable/upload', status_code=201)
def upload_wearable(
    patient_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and store wearable device file for a patient."""
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail='Patient not found')

    # validate extension
    filename = file.filename
    _, ext = os.path.splitext(filename.lower())
    if ext not in ('.csv', '.json'):
        raise HTTPException(status_code=415, detail='Unsupported file type')

    # read file bytes into memory
    file_content = file.file.read()
    size = len(file_content)

    # optionally also save to disk for backup/archival
    storage_name = f'{patient_id}_{filename}'
    storage_path = os.path.join(UPLOAD_DIR, storage_name)
    with open(storage_path, 'wb') as fh:
        fh.write(file_content)

    # parse lightweight
    rows, summary = utils.parse_wearable_file(storage_path)

    # store file content + metadata in DB
    meta = crud.create_wearable_metadata(
        db,
        patient_id,
        filename,
        file.content_type,
        size,
        file_content=file_content,  # store raw bytes
        storage_path=storage_path,  # also store path for optional disk access
        parsed_rows=rows,
        parsed_summary=summary,
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'id': meta.id,
            'filename': meta.filename,
            'parsed_rows': meta.parsed_rows,
            'parsed_summary': meta.parsed_summary,
        },
    )
