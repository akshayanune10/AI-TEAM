"""
Tests for Conflict and Risk Detector.
"""

from app.services.conflict_service import ConflictService
from app.models.team import TeamScoreBreakdown, ConflictSeverity
from app.models.project import Project, ProjectRequirement
from app.models.student import Student, WorkStyle


def test_conflict_detector_schedule_and_skill_gap():
    detector = ConflictService()
    project = Project(
        id=1,
        title="Conflict Test Project",
        description="Testing conflict detection.",
        requirements=[
            ProjectRequirement(skill_name="Python", required_level=4, is_mandatory=True)
        ],
    )
    members = [
        Student(id=1, student_id_str="S1", name="Alice", email="a@c.edu", work_style=WorkStyle(leadership_inclination=2)),
        Student(id=2, student_id_str="S2", name="Bob", email="b@c.edu", work_style=WorkStyle(leadership_inclination=2)),
    ]

    # Score indicating 0 common slots and missing mandatory skill
    score = TeamScoreBreakdown(
        skill_coverage=40.0,
        common_slots_count=0,
        missing_mandatory_skills=["Python"],
    )

    conflicts = detector.detect_conflicts(members, project, score)
    c_types = [c.conflict_type for c in conflicts]

    assert "schedule_conflict" in c_types
    assert "skill_gap" in c_types
    assert "work_style_imbalance" in c_types  # Because 0 leaders

    # Verify actionable repair suggestion
    sched_c = next(c for c in conflicts if c.conflict_type == "schedule_conflict")
    assert sched_c.severity == ConflictSeverity.CRITICAL
    assert len(sched_c.repair_suggestion) > 10
