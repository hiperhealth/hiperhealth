"""Database configuration and session management for the research app."""

from sqlmodel import Session, SQLModel, create_engine

# Define the database URL for SQLite
DATABASE_URL = 'sqlite:///./research_app.db'

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create the database and all tables defined by SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get a database session for each request."""
    with Session(engine) as session:
        yield session
