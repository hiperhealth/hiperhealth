"""Pytest configuration for the sdx package tests."""

from __future__ import annotations

import importlib
import json
import os
import warnings

from pathlib import Path
from typing import Dict, Optional

import pytest

from dotenv import dotenv_values, load_dotenv
from fastapi.testclient import TestClient
from sdx.agents.extraction.medical_reports import MedicalReportFileExtractor
from sdx.agents.extraction.wearable import WearableDataFileExtractor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from research.app.main import app
from research.models.repositories import ResearchRepository
from research.models.ui import Base


def pytest_collection_modifyitems(config, items) -> None:
    """Skip HF-marked tests unless RUN_HF_TESTS=1 is set."""
    run_hf = os.getenv('RUN_HF_TESTS', '0') == '1'
    if run_hf:
        return
    skip_hf = pytest.mark.skip(
        reason='Set RUN_HF_TESTS=1 to run Hugging Face integration tests.'
    )
    for item in items:
        if 'hf' in item.keywords:
            item.add_marker(skip_hf)


# OpenTelemetry hard-disable for the whole test session
def _setenv_many(pairs: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Set several env vars; return previous values to allow restore."""
    prev: Dict[str, Optional[str]] = {}
    for key, value in pairs.items():
        prev[key] = os.environ.get(key)
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    return prev


@pytest.fixture()
def reload_client_module(monkeypatch):
    """(Re)load the client with given env vars applied."""

    def _loader(**env):
        for key, val in env.items():
            if val is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, str(val))
        import sdx.agents.client as client

        importlib.reload(client)
        return client

    return _loader


@pytest.fixture
def env() -> dict[str, str | None]:
    """Return a fixture for the environment variables from .env file."""
    # This assumes a .envs/.env file at the project root
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


# Use an in-memory SQLite database for fast, isolated tests
TEST_DB_URL = 'sqlite:///:memory:'
engine = create_engine(TEST_DB_URL, connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope='function')
def db_session():
    """Create a new database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def test_repo(db_session):
    """Provide a ResearchRepository instance with a test database session."""
    return ResearchRepository(db_session)


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)
