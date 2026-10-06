"""
Tests for Constrained Team Formation Optimization (ILP & Greedy).
"""

from app.algorithms.optimizer_ilp import ILPOptimizer
from app.algorithms.optimizer_greedy import GreedyOptimizer
from app.models.team import TeamConstraint, ConstraintType


def test_greedy_optimizer_satisfies_team_size_and_uniqueness(sample_students, sample_projects):
    optimizer = GreedyOptimizer()
    teams, unassigned, elapsed = optimizer.solve(sample_students, sample_projects, target_team_size=4)

    assert len(teams) > 0
    assigned_ids = set()

    for t in teams:
        assert len(t.members) >= 3  # min_size
        assert len(t.members) <= 5  # max_size
        for m in t.members:
            assert m.student_id not in assigned_ids, "Student assigned multiple times!"
            assigned_ids.add(m.student_id)

    assert len(assigned_ids) + len(unassigned) == len(sample_students)


def test_optimization_locked_student_constraint(sample_students, sample_projects):
    s_target = sample_students[0]
    p_target = sample_projects[1]

    lock_constraint = TeamConstraint(
        constraint_type=ConstraintType.LOCK_STUDENT,
        student_id_1=s_target.id,
        target_project_id=p_target.id,
        note="Test locked assignment",
    )

    optimizer = GreedyOptimizer()
    teams, unassigned, _ = optimizer.solve(
        sample_students, sample_projects, constraints=[lock_constraint], target_team_size=4
    )

    # Find the team assigned to p_target
    target_team = next((t for t in teams if t.project_id == p_target.id), None)
    assert target_team is not None
    member_ids = [m.student_id for m in target_team.members]
    assert s_target.id in member_ids, "Locked student was not assigned to target project!"


def test_optimization_excluded_pair_constraint(sample_students, sample_projects):
    s1 = sample_students[0]
    s2 = sample_students[1]

    exclude_constraint = TeamConstraint(
        constraint_type=ConstraintType.EXCLUDE_PAIR,
        student_id_1=s1.id,
        student_id_2=s2.id,
        note="Test pair exclusion",
    )

    optimizer = GreedyOptimizer()
    teams, _, _ = optimizer.solve(
        sample_students, sample_projects, constraints=[exclude_constraint], target_team_size=4
    )

    # Verify s1 and s2 are never in the same team
    for t in teams:
        m_ids = [m.student_id for m in t.members]
        assert not (s1.id in m_ids and s2.id in m_ids), "Excluded pair assigned to same team!"


def test_ilp_optimizer_basic_execution(sample_students, sample_projects):
    optimizer = ILPOptimizer()
    teams, unassigned, elapsed = optimizer.solve(sample_students, sample_projects, target_team_size=4)

    if teams:  # If feasible under strict CBC formulation
        assigned_ids = set()
        for t in teams:
            for m in t.members:
                assert m.student_id not in assigned_ids
                assigned_ids.add(m.student_id)
        assert elapsed >= 0.0
