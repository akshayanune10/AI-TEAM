"""
Tests for Data Models, Validation Schemas, and Repository Persistence.
"""

import pytest
from pydantic import ValidationError
from app.models.student import StudentCreate, StudentSkill, SkillCategory, SkillSource
from app.models.project import ProjectCreate, ProjectRequirement


def test_student_model_validation():
    # Valid student
    s = StudentCreate(
        student_id_str="CS-TEST-1",
        name="Test User",
        email="test.user@college.edu",
        experience_level=4,
    )
    assert s.student_id_str == "CS-TEST-1"
    assert s.experience_level == 4

    # Invalid proficiency level (> 5)
    with pytest.raises(ValidationError):
        StudentSkill(
            name="Python",
            category=SkillCategory.PROGRAMMING_LANGUAGE,
            proficiency=6,
        )

    # Invalid email
    with pytest.raises(ValidationError):
        StudentCreate(
            student_id_str="CS-TEST-2",
            name="Invalid Email",
            email="not-an-email",
        )


def test_project_model_validation():
    # Valid project
    p = ProjectCreate(
        title="Valid Test Project",
        description="A comprehensive description that exceeds ten characters.",
        target_team_size=4,
    )
    assert p.target_team_size == 4

    # Invalid short description
    with pytest.raises(ValidationError):
        ProjectCreate(
            title="Short",
            description="Too short",
        )


def test_repository_crud(in_memory_repo):
    p = in_memory_repo.create_project(
        ProjectCreate(
            title="Database Test Project",
            description="Testing database CRUD operations end to end.",
            requirements=[
                ProjectRequirement(skill_name="Python", required_level=4, importance_weight=5, is_mandatory=True)
            ],
        )
    )
    assert p.id is not None
    assert len(p.requirements) == 1

    s = in_memory_repo.create_student(
        StudentCreate(
            student_id_str="ST-001",
            name="CRUD Student",
            email="crud.student@college.edu",
            skills=[
                StudentSkill(name="Python", proficiency=4, source=SkillSource.SELF_REPORTED, confidence=0.85)
            ],
        )
    )
    assert s.id is not None
    assert len(s.skills) == 1

    fetched_student = in_memory_repo.get_student_by_id(s.id)
    assert fetched_student.name == "CRUD Student"
    assert fetched_student.skills[0].name == "Python"
