"""
Shared pytest fixtures for integration and e2e tests.

Unit tests in tests/unit/ do NOT use these fixtures — they rely only on
unittest.mock and never touch the database.

Test database
-------------
Integration and e2e tests run against a dedicated PostgreSQL database
(default: medistock_test). The conftest creates it automatically if it
does not exist, creates all ORM tables at session start, and truncates
every table after each individual test so tests are fully isolated.

Override the connection URL with the TEST_DATABASE_URL environment variable.
"""
import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from medistock.infrastructure.database import get_db
from medistock.infrastructure.orm.models import Base
from medistock.interfaces.api.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:1234@localhost:5432/medistock_test",
)


def _ensure_test_database(url: str) -> None:
    """Create the test database if it does not already exist."""
    db_name = url.rsplit("/", 1)[-1]
    admin_url = url.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).fetchone()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    admin_engine.dispose()


@pytest.fixture(scope="session")
def test_engine():
    """Session-scoped engine: create tables once, drop them after the session."""
    _ensure_test_database(TEST_DATABASE_URL)
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    """Function-scoped SQLAlchemy session backed by the test database."""
    Session = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session, test_engine):
    """
    FastAPI TestClient wired to the test database.

    * Overrides get_db so every route uses the test db_session.
    * Truncates all domain tables after the test completes.
    """
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()

    # Truncate in FK-safe order (child tables first)
    with test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
