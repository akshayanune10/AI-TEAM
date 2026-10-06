"""
Baseline B: Skill-Only Matching Algorithm.
Assigns students solely on technical skill overlap, ignoring project preferences,
availability schedules, work styles, and diversity balance.
Used for academic benchmarking and evaluation against proposed methods.
"""

import time
from typing import List, Tuple, Optional, Set
import numpy as np

from app.models.student import Student
from app.models.project import Project
from app.models.team import Team, TeamMemberAssignment
from app.services.scoring_service import ScoringService


class BaselineSkillOnlyOptimizer:
    """Greedy matching considering only skill coverage without holistic trade-offs."""

    def __init__(self, scoring_service: Optional[ScoringService] = None):
        self.scoring_service = scoring_service or ScoringService()

    def solve(
        self,
        students: List[Student],
        projects: List[Project],
        target_team_size: Optional[int] = None,
    ) -> Tuple[List[Team], List[int], float]:
        start_time = time.time()

        if not students or not projects:
            return [], [s.id for s in students], 0.0

        min_sz = target_team_size or projects[0].min_team_size
        max_sz = (target_team_size + 1) if target_team_size else projects[0].max_team_size

        num_teams = max(1, min(len(projects), len(students) // min_sz))
        active_projects = projects[:num_teams]
        cohort_mean_exp = float(np.mean([s.experience_level for s in students]))

        student_pool = list(students)
        team_members: dict = {p.id: [] for p in active_projects}

        # For each project, greedily pick the student who maximizes skill coverage
        while len(student_pool) > 0:
            assigned_this_round = False
            for p in active_projects:
                if len(team_members[p.id]) >= max_sz:
                    continue
                if not student_pool:
                    break

                best_student = None
                best_score = -1.0

                for s in student_pool:
                    curr_team = team_members[p.id] + [s]
                    cov, _, _ = self.scoring_service.calculate_skill_coverage(curr_team, p)
                    if cov > best_score:
                        best_score = cov
                        best_student = s

                if best_student:
                    team_members[p.id].append(best_student)
                    student_pool.remove(best_student)
                    assigned_this_round = True

            if not assigned_this_round:
                break

        teams: List[Team] = []
        for p in active_projects:
            members = team_members[p.id]
            member_assignments = [
                TeamMemberAssignment(
                    student_id=s.id,
                    student_name=s.name,
                    student_id_str=s.student_id_str,
                    is_locked=False,
                    assigned_role=s.work_style.primary_role,
                    experience_level=s.experience_level,
                )
                for s in members
            ]

            score = self.scoring_service.calculate_team_score(
                members, p, cohort_mean_exp
            )

            teams.append(
                Team(
                    project_id=p.id,
                    project_title=p.title,
                    team_name=f"[Baseline Skill-Only] {p.title[:20]}",
                    members=member_assignments,
                    score=score,
                    conflicts=[],
                    explanation=None,
                    is_approved=False,
                )
            )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        unassigned = [s.id for s in student_pool]

        return teams, unassigned, elapsed_ms
