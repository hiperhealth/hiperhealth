"""Unit tests for the research schema module."""

from sqlalchemy import create_engine, inspect

# The path to the database file we configured in alembic.ini
DB_PATH = 'research/app/data/db.sqlite'


def test_database_schema_creation():
    """Connects to the DB and checks if the new research tables exist."""
    engine = create_engine(f'sqlite:///{DB_PATH}')
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    # Assert that all your new, normalized tables were created
    assert 'patients' in tables
    assert 'consultations' in tables
    assert 'diagnoses' in tables
    assert 'exams' in tables
    assert 'consultation_diagnoses' in tables
    assert 'consultation_exams' in tables
