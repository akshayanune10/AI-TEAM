"""
Baseline A: Random Team Formation Algorithm.
Randomly distributes students into teams respecting only team size bounds.
Used for academic benchmarking and evaluation against proposed methods.
"""

import time
import random
from typing import List, Tuple, Optional
import numpy as np

from app.models.student import Student
from app.models.project import Project
from app.models.team import Team, TeamMemberAssignment
from app.services.scoring_service import ScoringService


class BaselineRandomOptimizer:
    """Assigns students uniformly at random to available projects."""

    def __init__(self, scoring_service: Optional[ScoringService] = None):
        self.scoring_service = scoring_service or ScoringService()

    def solve(
        self,
        students: List[Student],
        projects: List[Project],
        target_team_size: Optional[int] = None,
        seed: int = 42,
    ) -> Tuple[List[Team], List[int], float]:
        start_time = time.time()
        random.seed(seed)

        if not students or not projects:
            return [], [s.id for s in students], 0.0

        min_sz = target_team_size or projects[0].min_team_size
        max_sz = (target_team_size + 1) if target_team_size else projects[0].max_team_size

        num_teams = max(1, min(len(projects), len(students) // min_sz))
        active_projects = projects[:num_teams]

        # Shuffle student list randomly
        shuffled = list(students)
        random.shuffle(shuffled)

        cohort_mean_exp = float(np.mean([s.experience_level for s in students]))
        teams: List[Team] = []

        # Partition evenly
        for t_idx, proj in enumerate(active_projects):
            start_idx = t_idx * min_sz
            end_idx = min(len(shuffled), start_idx + min_sz)
            team_students = shuffled[start_idx:end_idx]

            member_assignments = [
                TeamMemberAssignment(
                    student_id=s.id,
                    student_name=s.name,
                    student_id_str=s.student_id_str,
                    is_locked=False,
                    assigned_role=s.work_style.primary_role,
                    experience_level=s.experience_level,
                )
                for s in team_students
            ]

            score = self.scoring_service.calculate_team_score(
                team_students, proj, cohort_mean_exp
            )

            teams.append(
                Team(
                    project_id=proj.id,
                    project_title=proj.title,
                    team_name=f"[Baseline Random] {proj.title[:20]}",
                    members=member_assignments,
                    score=score,
                    conflicts=[],
                    explanation=None,
                    is_approved=False,
                )
            )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        assigned_ids = {m.student_id for t in teams for m in t.members}
        unassigned = [s.id for s in students if s.id not in assigned_ids]

        return teams, unassigned, elapsed_ms
