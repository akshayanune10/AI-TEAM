"""
Tests for 6-Factor Composite Scoring Engine.
"""

from app.services.scoring_service import ScoringService
from app.models.student import Student, StudentSkill, TimeSlotAvailability, WorkStyle, StudentPreference
from app.models.project import Project, ProjectRequirement


def test_skill_coverage_and_missing_mandatory():
    scoring = ScoringService()
    project = Project(
        id=1,
        title="Test Project",
        description="Testing skill coverage calculation.",
        requirements=[
            ProjectRequirement(skill_name="Python", required_level=3, importance_weight=5, is_mandatory=True),
            ProjectRequirement(skill_name="PostgreSQL", required_level=3, importance_weight=4, is_mandatory=True),
        ],
    )

    # Student 1 has Python 4, but neither has PostgreSQL
    s1 = Student(
        id=1, student_id_str="S1", name="Alice", email="a@c.edu", experience_level=3,
        skills=[StudentSkill(name="Python", proficiency=4)],
    )
    s2 = Student(
        id=2, student_id_str="S2", name="Bob", email="b@c.edu", experience_level=3,
        skills=[StudentSkill(name="React", proficiency=4)],
    )

    score, covered, missing = scoring.calculate_skill_coverage([s1, s2], project)
    assert "PostgreSQL" in missing
    assert "Python" in covered
    assert score < 60.0  # Penalized for missing mandatory requirement

    # Add student with PostgreSQL
    s3 = Student(
        id=3, student_id_str="S3", name="Charlie", email="c@c.edu", experience_level=3,
        skills=[StudentSkill(name="PostgreSQL", proficiency=4)],
    )
    score_full, covered_full, missing_full = scoring.calculate_skill_coverage([s1, s2, s3], project)
    assert not missing_full
    assert score_full >= 90.0


def test_availability_overlap_calculation():
    scoring = ScoringService()
    # Alice and Bob both free Monday Morning and Wednesday Afternoon
    s1 = Student(
        id=1, student_id_str="S1", name="Alice", email="a@c.edu", experience_level=3,
        availability=[
            TimeSlotAvailability(day="Monday", slot="Morning (09:00 - 12:00)", is_available=True),
            TimeSlotAvailability(day="Wednesday", slot="Afternoon (12:00 - 15:00)", is_available=True),
        ],
    )
    s2 = Student(
        id=2, student_id_str="S2", name="Bob", email="b@c.edu", experience_level=3,
        availability=[
            TimeSlotAvailability(day="Monday", slot="Morning (09:00 - 12:00)", is_available=True),
            TimeSlotAvailability(day="Wednesday", slot="Afternoon (12:00 - 15:00)", is_available=True),
            TimeSlotAvailability(day="Friday", slot="Morning (09:00 - 12:00)", is_available=True),
        ],
    )

    score, common_count = scoring.calculate_availability_overlap([s1, s2])
    assert common_count == 2
    assert score >= 50.0


def test_project_preference_satisfaction():
    scoring = ScoringService()
    proj = Project(id=10, title="Target Project", description="Target description.")
    s1 = Student(
        id=1, student_id_str="S1", name="Alice", email="a@c.edu", experience_level=3,
        preferences=[StudentPreference(project_id=10, rank=1)],
    )
    s2 = Student(
        id=2, student_id_str="S2", name="Bob", email="b@c.edu", experience_level=3,
        preferences=[StudentPreference(project_id=10, rank=2)],
    )

    pref_score = scoring.calculate_project_preference([s1, s2], proj)
    # Alice=100, Bob=75 => Mean=87.5
    assert pref_score == 87.5
