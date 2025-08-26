"""Database configuration and session management for the research app."""

from pathlib import Path
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, Session, SQLModel, create_engine


class ResearchPatientRecord(SQLModel, table=True):
    """Represent a single patient record in the research database."""

    id: str = Field(primary_key=True)
    data: Any = Field(sa_column=Column(JSON))


APP_DIR = Path(__file__).parent
# Define the database URL for SQLite
DATABASE_URL = f'sqlite:///{APP_DIR}/research_app.db'

# Create the database engine
engine = create_engine(
    DATABASE_URL, connect_args={'check_same_thread': False}, echo=True
)


def create_db_and_tables():
    """Create the database and all tables defined by SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get a database session for each request."""
    with Session(engine) as session:
        yield session
