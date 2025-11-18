"""Database configuration and session management."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./backend.db')

# For SQLite in SQLAlchemy 2.x pass future flag via connect_args
connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args = {'check_same_thread': False}

engine = create_engine(
    DATABASE_URL, echo=False, future=True, connect_args=connect_args
)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)
Base = declarative_base()


def get_db():
    """Provide database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables based on SQLAlchemy models."""
    Base.metadata.create_all(bind=engine)
