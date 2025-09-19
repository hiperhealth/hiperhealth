"""Pytest configuration for the sdx package tests."""

import json

from pathlib import Path

import pytest

from sdx.agents.extraction.wearable import WearableDataFileExtractor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from research.models.repositories import ResearchRepository

# Use an in-memory SQLite database for testing
TEST_DB_URL = 'sqlite:///:memory:'

engine = create_engine(TEST_DB_URL, connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope='function')
def db_session():
    """Create a new database session for a test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope='function')
def test_repo(db_session):
    """Fixture to create a ResearchRepository with a test session."""
    return ResearchRepository(db_session)


@pytest.fixture(scope='session')
def patients_json() -> list[dict]:
    """Load the test patients JSON data."""
    path = Path(__file__).parent / 'data' / 'patients' / 'patients.json'
    return json.loads(path.read_text())


@pytest.fixture
def wearable_extractor():
    """Provide a WearableDataFileExtractor instance for tests."""
    return WearableDataFileExtractor()
