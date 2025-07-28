"""Pytest configuration for the sdx package tests."""

from __future__ import annotations

import os
import random
import shutil
import warnings

from pathlib import Path

import pytest

from dotenv import dotenv_values, load_dotenv
from fastapi.testclient import TestClient

from research.app.main import app
from research.models.repositories import PatientRepository


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
def test_data_dir() -> Path:
    """Fixture providing the path to the test data directory."""
    return Path(__file__).parent / 'data'


@pytest.fixture
def reports_pdf_dir(test_data_dir: Path) -> Path:
    """Fixture for the directory containing PDF report files."""
    pdf_dir = test_data_dir / 'reports' / 'pdf_reports'
    if not pdf_dir.exists():
        pdf_dir.mkdir(parents=True, exist_ok=True)
    return pdf_dir


@pytest.fixture
def reports_image_dir(test_data_dir: Path) -> Path:
    """Fixture for the directory containing image report files."""
    image_dir = test_data_dir / 'reports' / 'image_reports'
    if not image_dir.exists():
        image_dir.mkdir(parents=True, exist_ok=True)
    return image_dir


@pytest.fixture
def api_key_openai(env: dict[str, str | None]) -> str:
    """Fixture providing the OpenAI API key from environment variables."""
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise EnvironmentError(
            'Please set the OPENAI_API_KEY environment variable in your .env '
            'file or system environment for testing.'
        )

    return api_key


@pytest.fixture
def patient_repository():
    """Temporary patient repository fixture."""
    # patch DATA_PATH to test data path
    TEST_DATA_PATH = Path(__file__).parent / 'data/patients'
    PATIENTS_DATA_PATH = TEST_DATA_PATH / 'patients.json'
    TEMP_DATA_PATH = TEST_DATA_PATH / 'temp_patients.json'

    shutil.copyfile(PATIENTS_DATA_PATH, TEMP_DATA_PATH)

    # patch DATA_PATH to test data path
    PatientRepository.DATA_PATH = TEMP_DATA_PATH
    temporary_repository = PatientRepository()

    yield temporary_repository

    # clean up, delete TEMP_DATA_PATH
    TEMP_DATA_PATH.unlink()


@pytest.fixture
def patient_id(patient_repository):
    """Patient ID fixture."""
    patients = patient_repository.all()
    return random.choice(patients)['meta']['uuid']


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)
