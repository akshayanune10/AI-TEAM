"""
Tests for Faculty Overrides and Constrained Re-Optimization.
"""

from app.services.override_service import OverrideService
from app.models.team import ConstraintType


def test_override_service_flow(in_memory_repo, sample_students, sample_projects):
    override_svc = OverrideService(in_memory_repo)
    s1 = sample_students[0]
    p1 = sample_projects[2]

    # Add lock
    c = override_svc.lock_student_to_project(s1.id, p1.id)
    assert c.id is not None
    assert c.constraint_type == ConstraintType.LOCK_STUDENT

    # Reoptimize
    new_run = override_svc.reoptimize_with_constraints(sample_students, sample_projects)
    assert len(new_run.teams) > 0

    # Verify locked student is in p1 team
    p1_team = next(t for t in new_run.teams if t.project_id == p1.id)
    p1_member_ids = [m.student_id for m in p1_team.members]
    assert s1.id in p1_member_ids
