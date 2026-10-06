"""
Pytest test fixtures providing isolated SQLite in-memory databases,
test student cohorts, and projects.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.data.database import Base
from app.data.repository import DataRepository
from app.data.sample_data import generate_sample_projects, generate_sample_students
from app.models.student import Student, StudentCreate
from app.models.project import Project, ProjectCreate


@pytest.fixture
def in_memory_repo():
    """Provides a fresh, isolated in-memory SQLite repository for tests."""
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    repo = DataRepository(db_session=session)
    yield repo
    session.close()


@pytest.fixture
def sample_projects(in_memory_repo) -> list[Project]:
    """Creates 6 sample projects in the test database."""
    created = []
    for p_in in generate_sample_projects():
        p = in_memory_repo.create_project(p_in)
        created.append(p)
    return created


@pytest.fixture
def sample_students(in_memory_repo, sample_projects) -> list[Student]:
    """Creates 24 sample students in the test database."""
    proj_ids = [p.id for p in sample_projects]
    created = []
    for s_in in generate_sample_students(proj_ids):
        s = in_memory_repo.create_student(s_in)
        created.append(s)
    return created
