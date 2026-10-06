"""
Faculty manual overrides and re-optimization management.
Handles student pins, moves, pair exclusions, and constraint preservation.
"""

from typing import List, Optional, Tuple
from app.models.student import Student
from app.models.project import Project
from app.models.team import Team, TeamConstraint, ConstraintType, GenerationRun
from app.data.repository import DataRepository
from app.algorithms.optimizer_greedy import GreedyOptimizer
from app.services.scoring_service import ScoringService
from app.services.explainability_service import ExplainabilityService
from app.services.conflict_service import ConflictService


class OverrideService:
    """Manages faculty manual adjustments and constrained re-generation."""

    def __init__(
        self,
        repository: DataRepository,
        scoring_service: Optional[ScoringService] = None,
        explainability_service: Optional[ExplainabilityService] = None,
        conflict_service: Optional[ConflictService] = None,
    ):
        self.repo = repository
        self.scoring = scoring_service or ScoringService()
        self.explainer = explainability_service or ExplainabilityService(self.scoring)
        self.conflicts = conflict_service or ConflictService()

    def lock_student_to_project(self, student_id: int, project_id: int) -> TeamConstraint:
        """Pins a student permanently to a project."""
        constraint = TeamConstraint(
            constraint_type=ConstraintType.LOCK_STUDENT,
            student_id_1=student_id,
            target_project_id=project_id,
            note=f"Faculty locked student #{student_id} to project #{project_id}",
        )
        return self.repo.add_constraint(constraint)

    def exclude_pair(self, student_id_1: int, student_id_2: int, reason: str = "") -> TeamConstraint:
        """Forbids two students from being assigned to the same team."""
        constraint = TeamConstraint(
            constraint_type=ConstraintType.EXCLUDE_PAIR,
            student_id_1=student_id_1,
            student_id_2=student_id_2,
            note=reason or f"Excluded pair: #{student_id_1} and #{student_id_2}",
        )
        return self.repo.add_constraint(constraint)

    def remove_constraint(self, constraint_id: int) -> bool:
        """Removes a specific constraint."""
        return self.repo.delete_constraint(constraint_id)

    def reoptimize_with_constraints(
        self,
        students: List[Student],
        projects: List[Project],
        weights: Optional[dict] = None,
        target_team_size: Optional[int] = None,
    ) -> GenerationRun:
        """
        Runs optimization strictly respecting all active faculty constraints.
        """
        constraints = self.repo.get_all_constraints()
        scoring = ScoringService(weights)
        optimizer = GreedyOptimizer(scoring)
        explainer = ExplainabilityService(scoring)
        conflict_detector = ConflictService()

        teams, unassigned, elapsed_ms = optimizer.solve(
            students, projects, constraints=constraints, target_team_size=target_team_size
        )

        student_map = {s.id: s for s in students}
        project_map = {p.id: p for p in projects}

        # Enrich teams with explanations and conflicts
        enriched_teams = []
        for t in teams:
            proj = project_map.get(t.project_id)
            if not proj:
                continue

            member_objs = [student_map[m.student_id] for m in t.members if m.student_id in student_map]
            conflicts = conflict_detector.detect_conflicts(member_objs, proj, t.score)
            explanation = explainer.explain_team(member_objs, proj, t.score)

            t.conflicts = conflicts
            t.explanation = explanation
            enriched_teams.append(t)

        scores = [t.score.total_composite_score for t in enriched_teams]
        avg_score = float(sum(scores) / max(1, len(scores)))
        import numpy as np
        std_dev = float(np.std(scores)) if scores else 0.0

        run = GenerationRun(
            timestamp="",
            algorithm="Greedy + 2-Opt (Constrained)",
            weights=scoring.weights,
            teams=enriched_teams,
            unassigned_students=unassigned,
            average_score=round(avg_score, 2),
            fairness_std_dev=round(std_dev, 2),
            runtime_ms=elapsed_ms,
            is_finalized=False,
        )

        return self.repo.save_generation_run(run)
