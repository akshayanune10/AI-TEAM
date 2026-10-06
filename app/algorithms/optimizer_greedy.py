"""
Greedy Heuristic Optimizer with 2-Opt Local Search Swapping.
Enforces hard constraints (locks, exclusions, team sizes) while directly
optimizing the full non-linear 6-factor composite quality score.
"""

import time
import random
from typing import List, Dict, Tuple, Optional, Set
import numpy as np

from app.models.student import Student
from app.models.project import Project
from app.models.team import (
    Team,
    TeamMemberAssignment,
    TeamConstraint,
    ConstraintType,
)
from app.services.scoring_service import ScoringService


class GreedyOptimizer:
    """Heuristic optimizer with constraint propagation and 2-opt local search."""

    def __init__(self, scoring_service: Optional[ScoringService] = None):
        self.scoring_service = scoring_service or ScoringService()

    def solve(
        self,
        students: List[Student],
        projects: List[Project],
        constraints: Optional[List[TeamConstraint]] = None,
        target_team_size: Optional[int] = None,
    ) -> Tuple[List[Team], List[int], float]:
        start_time = time.time()
        constraints = constraints or []

        if not students or not projects:
            return [], [s.id for s in students], 0.0

        num_students = len(students)
        student_map = {s.id: s for s in students}
        cohort_mean_exp = float(np.mean([s.experience_level for s in students]))

        # Target team size and bounds
        min_sz = target_team_size or projects[0].min_team_size
        max_sz = (target_team_size + 1) if target_team_size else projects[0].max_team_size

        # Determine number of teams
        active_team_count = max(1, min(len(projects), num_students // min_sz))
        active_projects = projects[:active_team_count]

        # Build exclusions lookup: set of frozenset({s1, s2})
        excluded_pairs: Set[frozenset] = set()
        for c in constraints:
            if c.constraint_type == ConstraintType.EXCLUDE_PAIR and c.student_id_2:
                excluded_pairs.add(frozenset([c.student_id_1, c.student_id_2]))

        # Team assignment state: project_id -> list of student_ids
        team_assignments: Dict[int, List[int]] = {p.id: [] for p in active_projects}
        assigned_students: Set[int] = set()

        # Step 1: Assign locked students
        for c in constraints:
            if c.constraint_type == ConstraintType.LOCK_STUDENT:
                s_id = c.student_id_1
                p_id = c.target_project_id
                if s_id in student_map and p_id in team_assignments:
                    if len(team_assignments[p_id]) < max_sz and s_id not in assigned_students:
                        team_assignments[p_id].append(s_id)
                        assigned_students.add(s_id)

        # Step 2: Seed unassigned projects with best fit anchor students
        unassigned_pool = [s_id for s_id in student_map if s_id not in assigned_students]

        for p in active_projects:
            if not team_assignments[p.id] and unassigned_pool:
                best_s_id = None
                best_fit = -1.0
                for s_id in unassigned_pool:
                    s = student_map[s_id]
                    # Score coverage individually
                    sc, _, _ = self.scoring_service.calculate_skill_coverage([s], p)
                    if sc > best_fit:
                        best_fit = sc
                        best_s_id = s_id
                if best_s_id:
                    team_assignments[p.id].append(best_s_id)
                    assigned_students.add(best_s_id)
                    unassigned_pool.remove(best_s_id)

        # Step 3: Greedily fill remaining slots to satisfy min_sz then up to max_sz
        # Sort unassigned students to prioritize those with project preferences
        unassigned_pool.sort(key=lambda s_id: student_map[s_id].experience_level, reverse=True)

        for s_id in list(unassigned_pool):
            s = student_map[s_id]
            best_p_id = None
            best_marginal_gain = -9999.0

            for p in active_projects:
                current_members = team_assignments[p.id]
                if len(current_members) >= max_sz:
                    continue

                # Check exclusion constraint
                has_exclusion_conflict = any(
                    frozenset([s_id, existing_id]) in excluded_pairs
                    for existing_id in current_members
                )
                if has_exclusion_conflict:
                    continue

                # Evaluate current team score vs new team score
                curr_objs = [student_map[m_id] for m_id in current_members]
                curr_score = (
                    self.scoring_service.calculate_team_score(curr_objs, p, cohort_mean_exp).total_composite_score
                    if curr_objs
                    else 0.0
                )

                new_objs = curr_objs + [s]
                new_score = self.scoring_service.calculate_team_score(
                    new_objs, p, cohort_mean_exp
                ).total_composite_score

                gain = new_score - curr_score

                # Bonus for filling undersized teams (< min_sz)
                if len(current_members) < min_sz:
                    gain += 30.0

                if gain > best_marginal_gain:
                    best_marginal_gain = gain
                    best_p_id = p.id

            if best_p_id is not None:
                team_assignments[best_p_id].append(s_id)
                assigned_students.add(s_id)
                unassigned_pool.remove(s_id)

        # Step 4: 2-Opt Local Search Swapping
        # Attempt to swap student pairs between teams to improve overall composite score
        locked_set = {
            c.student_id_1
            for c in constraints
            if c.constraint_type == ConstraintType.LOCK_STUDENT
        }

        improved = True
        iterations = 0
        max_iterations = 25

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1

            for p1_idx, p1 in enumerate(active_projects):
                for p2_idx, p2 in enumerate(active_projects):
                    if p1.id >= p2.id:
                        continue

                    members1 = list(team_assignments[p1.id])
                    members2 = list(team_assignments[p2.id])

                    for s1_id in members1:
                        if s1_id in locked_set:
                            continue
                        for s2_id in members2:
                            if s2_id in locked_set:
                                continue

                            # Check exclusion constraints for hypothetical swap
                            # s1 going to p2:
                            hypo_p2_members = [m for m in members2 if m != s2_id] + [s1_id]
                            if any(frozenset([s1_id, m]) in excluded_pairs for m in hypo_p2_members if m != s1_id):
                                continue

                            # s2 going to p1:
                            hypo_p1_members = [m for m in members1 if m != s1_id] + [s2_id]
                            if any(frozenset([s2_id, m]) in excluded_pairs for m in hypo_p1_members if m != s2_id):
                                continue

                            # Calculate current combined score
                            obj1_curr = [student_map[m] for m in members1]
                            obj2_curr = [student_map[m] for m in members2]
                            score_curr = (
                                self.scoring_service.calculate_team_score(obj1_curr, p1, cohort_mean_exp).total_composite_score
                                + self.scoring_service.calculate_team_score(obj2_curr, p2, cohort_mean_exp).total_composite_score
                            )

                            # Calculate swapped combined score
                            obj1_new = [student_map[m] for m in hypo_p1_members]
                            obj2_new = [student_map[m] for m in hypo_p2_members]
                            score_new = (
                                self.scoring_service.calculate_team_score(obj1_new, p1, cohort_mean_exp).total_composite_score
                                + self.scoring_service.calculate_team_score(obj2_new, p2, cohort_mean_exp).total_composite_score
                            )

                            # If swap improves global score, commit swap
                            if score_new > score_curr + 0.5:
                                team_assignments[p1.id] = hypo_p1_members
                                team_assignments[p2.id] = hypo_p2_members
                                improved = True
                                break
                        if improved:
                            break
                    if improved:
                        break

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # Build output Team structures
        teams: List[Team] = []
        for p in active_projects:
            m_ids = team_assignments[p.id]
            m_objs = [student_map[m_id] for m_id in m_ids]

            member_assignments = []
            for s in m_objs:
                is_locked = s.id in locked_set
                member_assignments.append(
                    TeamMemberAssignment(
                        student_id=s.id,
                        student_name=s.name,
                        student_id_str=s.student_id_str,
                        is_locked=is_locked,
                        assigned_role=s.work_style.primary_role,
                        experience_level=s.experience_level,
                    )
                )

            score_breakdown = self.scoring_service.calculate_team_score(
                m_objs, p, cohort_mean_exp
            )

            teams.append(
                Team(
                    project_id=p.id,
                    project_title=p.title,
                    team_name=f"{p.title[:25]} Team",
                    members=member_assignments,
                    score=score_breakdown,
                    conflicts=[],
                    explanation=None,
                    is_approved=False,
                )
            )

        unassigned = [s_id for s_id in student_map if s_id not in assigned_students]
        return teams, unassigned, elapsed_ms
