"""Script to clear and seed the research app database with patient data.

This script reads patient records from a JSON file and populates the database.
It is idempotent and can be safely re-run to reset the database.
"""

import json
import os
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from research.app import db
from research.models.repositories import PatientRepository

SEED_DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / 'tests'
    / 'data'
    / 'patients'
    / 'patients.json'
)
DB_PATH = (
    Path(__file__).resolve().parent.parent
    / 'research'
    / 'app'
    / 'research_app.db'
)


def seed_database():
    """Clear and seed the database with patient data from a JSON file.

    This script is idempotent and can be run multiple times safely.
    """
    # 1. Delete the old database file if it exists to ensure a clean start.
    if os.path.exists(DB_PATH):
        print(f'Removing existing database at {DB_PATH}...')
        os.remove(DB_PATH)
        print('Database file removed.')
    else:
        print('No existing database file found, proceeding.')

    print('Seeding new database...')
    db.create_db_and_tables()

    repo = PatientRepository()
    session = next(db.get_session())

    try:
        with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
            patients_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f'Error reading seed data file: {e}')
        return

    seen_uuids = set()
    for patient_record in patients_data:
        patient_uuid = patient_record.get('meta', {}).get('uuid')
        if not patient_uuid:
            print('Skipping record with missing UUID.')
            continue

        if patient_uuid in seen_uuids:
            print(
                f'Duplicate UUID found in seed data: {patient_uuid} - '
                f'skipping duplicate.'
            )
            continue
        seen_uuids.add(patient_uuid)

        print(f' - Seeding patient: {patient_uuid}')
        try:
            repo.create(patient_record, session=session)
        except Exception as e:
            print(f'Error inserting patient {patient_uuid}: {e}')
            session.rollback()

    try:
        session.commit()
    except Exception as e:
        print(f'Error committing session: {e}')
        session.rollback()
    finally:
        session.close()

    print('Database seeding complete.')


if __name__ == '__main__':
    seed_database()
