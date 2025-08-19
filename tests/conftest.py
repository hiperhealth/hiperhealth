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
from sdx.agents.extraction.wearable import WearableDataFileExtractor

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
    # Setup a temporary data file for tests
    test_data_dir = Path(__file__).parent / 'data' / 'patients'
    original_data_path = test_data_dir / 'patients.json'
    temp_data_path = test_data_dir / 'temp_patients.json'

    shutil.copyfile(original_data_path, temp_data_path)

    # Provide the repository instance with the correct path
    temporary_repository = PatientRepository(data_path=temp_data_path)
    yield temporary_repository

    # Teardown: remove the temporary file
    temp_data_path.unlink()


@pytest.fixture
def patient_id(patient_repository):
    """Patient ID fixture."""
    patients = patient_repository.all()
    return random.choice(patients)['meta']['uuid']


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def wearable_extractor():
    """Wearable data extractor fixture."""
    return WearableDataFileExtractor()
