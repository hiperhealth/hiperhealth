"""Script for migrating data from JSON files into the database."""

import json
import logging
import sys

from pathlib import Path

# Add the project root to the Python path to allow for imports
# BEFORE local imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from research.app.database import SessionLocal  # noqa: E402
from research.models.repositories import ResearchRepository  # noqa: E402

logger = logging.getLogger(__name__)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure logging for the migration script."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )


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

    logger.info('Loading data from %s...', json_path)
    with open(json_path, 'r') as f:
        patient_records = json.load(f)

    logger.info('Found %d patient records to migrate.', len(patient_records))

    for record in patient_records:
        patient_uuid = record.get('meta', {}).get('uuid')
        if not patient_uuid:
            logger.warning('Skipping record with no UUID.')
            continue

        # Check if patient already exists to prevent duplicates
        if repo.get_patient_by_uuid(patient_uuid):
            logger.info('Patient %s already exists. Skipping.', patient_uuid)
            continue

        logger.info('Migrating patient %s...', patient_uuid)
        try:
            # The repository methods are designed to handle
            # this dictionary format
            repo.create_patient_and_consultation(record)
            repo.update_consultation(patient_uuid, record)
        except Exception:
            db.rollback()
            logger.exception('ERROR migrating patient %s', patient_uuid)

    logger.info('Migration complete.')
    db.close()


if __name__ == '__main__':
    configure_logging()
    migrate_data()
