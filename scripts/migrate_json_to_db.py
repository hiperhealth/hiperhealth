"""Script for migrating data from JSON files into the database."""

import json
import sys

from pathlib import Path

from research.app.database import SessionLocal
from research.models.repositories import ResearchRepository

# Add the project root to the Python path to allow for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


def migrate_data():
    """Migrate patient data from JSON to the database."""
    db = SessionLocal()
    repo = ResearchRepository(db_session=db)

    json_path = (
        project_root
        / 'research'
        / 'app'
        / 'data'
        / 'patients'
        / 'patients.json'
    )

    print(f'Loading data from {json_path}...')
    with open(json_path, 'r') as f:
        patient_records = json.load(f)

    print(f'Found {len(patient_records)} patient records to migrate.')

    for record in patient_records:
        patient_uuid = record.get('meta', {}).get('uuid')
        if not patient_uuid:
            print('Skipping record with no UUID.')
            continue

        # Check if patient already exists to prevent duplicates
        if repo.get_patient_by_uuid(patient_uuid):
            print(f'Patient {patient_uuid} already exists. Skipping.')
            continue

        print(f'Migrating patient {patient_uuid}...')
        try:
            # The repository methods are designed to handle
            # this dictionary format
            repo.create_patient_and_consultation(record)
            repo.update_consultation(patient_uuid, record)
        except Exception as e:
            print(f'  ERROR migrating patient {patient_uuid}: {e}')

    print('\nMigration complete.')
    db.close()


if __name__ == '__main__':
    migrate_data()
