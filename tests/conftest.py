"""Pytest configuration for the sdx package tests."""

from __future__ import annotations

import json
import os
import warnings

from pathlib import Path

import pytest

from dotenv import dotenv_values, load_dotenv
from fastapi.testclient import TestClient

# Import these directly since they are always required
from sdx.agents.extraction.medical_reports import MedicalReportFileExtractor
from sdx.agents.extraction.wearable import WearableDataFileExtractor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from research.app.main import app
from research.models.repositories import ResearchRepository


@pytest.fixture
def env() -> dict[str, str | None]:
    """Return a fixture for the environment variables from .env file."""
    dotenv_path = Path(__file__).parents[1] / '.envs' / '.env'
    if not dotenv_path.exists():
        warnings.warn(
            f"'.env' file not found at {dotenv_path}. Some "
            'tests requiring environment variables might fail or be skipped.'
        )
        return {}
    load_dotenv(dotenv_path=dotenv_path)
    return dotenv_values(dotenv_path)


@pytest.fixture
def api_key_openai(env: dict[str, str | None]) -> str | None:
    """Fixture providing the OpenAI API key. Skips test if not found."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        pytest.skip('OpenAI API key not available')
    return api_key


@pytest.fixture
def test_data_dir() -> Path:
    """Fixture providing the path to the test data directory."""
    return Path(__file__).parent / 'data'


@pytest.fixture
def reports_pdf_dir(test_data_dir: Path) -> Path:
    """Fixture for the directory containing PDF report files."""
    return test_data_dir / 'reports' / 'pdf_reports'


@pytest.fixture
def reports_image_dir(test_data_dir: Path) -> Path:
    """Fixture for the directory containing image report files."""
    return test_data_dir / 'reports' / 'image_reports'


@pytest.fixture(scope='session')
def patients_json() -> list[dict]:
    """Load the test patients JSON data."""
    path = Path(__file__).parent / 'data' / 'patients' / 'patients.json'
    return json.loads(path.read_text())


@pytest.fixture
def wearable_extractor():
    """Provide a WearableDataFileExtractor instance for tests."""
    return WearableDataFileExtractor()


@pytest.fixture
def medical_extractor():
    """Provide a MedicalReportFileExtractor instance for tests."""
    return MedicalReportFileExtractor()


@pytest.fixture
def dicom_extractor():
    """Provide a DicomExtractor instance for tests."""
    # Import lazily and skip gracefully if not available
    pytest.importorskip('pydicom')
    try:
        from sdx.agents.extraction.dicom import DicomExtractor
    except ImportError as e:
        pytest.skip(f'DICOM extractor unavailable: {e}')
    return DicomExtractor()


@pytest.fixture
def sample_dicom_file(test_data_dir: Path) -> Path:
    """Path to the sample DICOM file used across tests."""
    path = test_data_dir / 'dicom' / 'ID_0000_AGE_0060_CONTRAST_1_CT.dcm'
    if not path.exists():
        pytest.skip(
            'Sample DICOM file not found; skipping DICOM-related tests.'
        )
    return path


# In-memory SQLite DB for isolated tests
TEST_DB_URL = 'sqlite:///:memory:'
engine = create_engine(TEST_DB_URL, connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope='function')
def db_session():
    """Create a new database session for each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope='function')
def test_repo(db_session):
    """Provide a ResearchRepository instance with a test database session."""
    return ResearchRepository(db_session)


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)
