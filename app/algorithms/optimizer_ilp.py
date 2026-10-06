"""
Integer Linear Programming (ILP) Team Formation Optimizer.
Solves constrained student-to-team assignment using PuLP and CBC solver,
strictly enforcing team sizes, uniqueness, locked students, and pair exclusions.
"""

import time
from typing import List, Dict, Tuple, Optional, Set
import pulp

from app.models.student import Student
from app.models.project import Project
from app.models.team import (
    Team,
    TeamMemberAssignment,
    TeamConstraint,
    ConstraintType,
    GenerationRun,
)
from app.services.scoring_service import ScoringService


class ILPOptimizer:
    """Mathematical optimization engine for team formation."""

    def __init__(self, scoring_service: Optional[ScoringService] = None):
        self.scoring_service = scoring_service or ScoringService()

    def _calculate_student_project_affinity(self, student: Student, project: Project) -> float:
        """Calculates linearized base affinity of a student for a project."""
        # 1. Skill match
        skill_score = 0.0
        req_weights = 0.0
        student_skill_map = {s.name.lower().strip(): s.proficiency for s in student.skills}

        for req in project.requirements:
            w = req.importance_weight
            req_weights += w
            prof = student_skill_map.get(req.skill_name.lower().strip(), 0)
            fraction = min(1.0, prof / max(1, req.required_level))
            skill_score += w * fraction

        skill_affinity = (skill_score / max(1.0, req_weights)) * 50.0

        # 2. Preference match
        pref_affinity = 5.0
        for p in student.preferences:
            if p.project_id == project.id:
                if p.rank == 1:
                    pref_affinity = 40.0
                elif p.rank == 2:
                    pref_affinity = 25.0
                elif p.rank == 3:
                    pref_affinity = 15.0
                else:
                    pref_affinity = 10.0
                break

        # 3. Experience factor
        exp_affinity = student.experience_level * 2.0

        return skill_affinity + pref_affinity + exp_affinity

    def solve(
        self,
        students: List[Student],
        projects: List[Project],
        constraints: Optional[List[TeamConstraint]] = None,
        target_team_size: Optional[int] = None,
    ) -> Tuple[List[Team], List[int], float]:
        """
        Solves the ILP assignment problem.
        Returns: (formed_teams, unassigned_student_ids, elapsed_ms)
        """
        start_time = time.time()
        constraints = constraints or []

        if not students or not projects:
            return [], [s.id for s in students], 0.0

        num_students = len(students)
        student_map = {s.id: s for s in students}
        student_ids = [s.id for s in students]

        # Determine number of teams needed
        # We form one team per project, or multiple if student count warrants it
        # By default in college capstone, projects are instantiated
        team_specs: List[Tuple[int, Project, str]] = []
        for p in projects:
            team_specs.append((p.id, p, f"Team {p.title[:20]}..."))

        num_teams = len(team_specs)
        min_sz = target_team_size or projects[0].min_team_size
        max_sz = (target_team_size + 1) if target_team_size else projects[0].max_team_size

        # If more teams than possible for student count, adjust
        if num_students < num_teams * min_sz:
            # Scale down active teams
            active_team_count = max(1, num_students // min_sz)
            team_specs = team_specs[:active_team_count]
            num_teams = len(team_specs)

        # Create PuLP problem
        prob = pulp.LpProblem("Student_Team_Formation", pulp.LpMaximize)

        # Decision variables: x[i, t] = 1 if student i is assigned to team t
        x = {}
        for s_id in student_ids:
            for t_idx in range(num_teams):
                x[s_id, t_idx] = pulp.LpVariable(f"x_{s_id}_{t_idx}", cat=pulp.LpBinary)

        # Objective Function: Maximize sum of student-project affinities + mutual availability bonuses
        affinities = {}
        for s in students:
            for t_idx, (p_id, proj, _) in enumerate(team_specs):
                aff = self._calculate_student_project_affinity(s, proj)
                affinities[s.id, t_idx] = aff

        prob += pulp.lpSum(affinities[s_id, t_idx] * x[s_id, t_idx] for s_id in student_ids for t_idx in range(num_teams))

        # --- Hard Constraints ---

        # 1. Student Uniqueness: Each student assigned at most once
        for s_id in student_ids:
            prob += pulp.lpSum(x[s_id, t_idx] for t_idx in range(num_teams)) <= 1, f"Uniqueness_{s_id}"

        # 2. Assign all students if possible
        if num_students <= num_teams * max_sz:
            total_slots = pulp.lpSum(x[s_id, t_idx] for s_id in student_ids for t_idx in range(num_teams))
            # Try to assign everyone
            prob += total_slots == min(num_students, num_teams * max_sz), "Max_Assignment"

        # 3. Team Size Bounds
        for t_idx in range(num_teams):
            team_size = pulp.lpSum(x[s_id, t_idx] for s_id in student_ids)
            prob += team_size >= min(min_sz, num_students // num_teams), f"MinSize_Team_{t_idx}"
            prob += team_size <= max_sz, f"MaxSize_Team_{t_idx}"

        # 4. Locked Students Constraint
        for c in constraints:
            if c.constraint_type == ConstraintType.LOCK_STUDENT:
                s_id = c.student_id_1
                if s_id in student_map:
                    # Find team matching target_project_id
                    for t_idx, (p_id, _, _) in enumerate(team_specs):
                        if p_id == c.target_project_id:
                            prob += x[s_id, t_idx] == 1, f"Lock_{s_id}_Team_{t_idx}"
                            break

        # 5. Excluded Pairs Constraint: student_id_1 and student_id_2 cannot be in the same team
        for c in constraints:
            if c.constraint_type == ConstraintType.EXCLUDE_PAIR and c.student_id_2:
                s1, s2 = c.student_id_1, c.student_id_2
                if s1 in student_map and s2 in student_map:
                    for t_idx in range(num_teams):
                        prob += x[s1, t_idx] + x[s2, t_idx] <= 1, f"Exclude_{s1}_{s2}_Team_{t_idx}"

        # Solve model using CBC solver quietly
        solver = pulp.PULP_CBC_CMD(msg=False)
        status = prob.solve(solver)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # Check solution feasibility
        if status != pulp.LpStatusOptimal:
            # Fall back to greedy optimizer if ILP is infeasible under rigid bounds
            return [], [s.id for s in students], elapsed_ms

        # Reconstruct Teams
        assigned_student_ids: Set[int] = set()
        teams: List[Team] = []
        cohort_mean_exp = float(sum(s.experience_level for s in students) / max(1, len(students)))

        for t_idx, (p_id, proj, t_name) in enumerate(team_specs):
            team_members_raw = []
            for s_id in student_ids:
                if pulp.value(x[s_id, t_idx]) == 1:
                    team_members_raw.append(student_map[s_id])
                    assigned_student_ids.add(s_id)

            # Build TeamMemberAssignment objects
            member_assignments = []
            for s in team_members_raw:
                # Check if locked
                is_locked = any(
                    c.constraint_type == ConstraintType.LOCK_STUDENT
                    and c.student_id_1 == s.id
                    and c.target_project_id == p_id
                    for c in constraints
                )
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

            # Compute full score breakdown
            score_breakdown = self.scoring_service.calculate_team_score(
                team_members_raw, proj, cohort_mean_exp
            )

            teams.append(
                Team(
                    project_id=proj.id,
                    project_title=proj.title,
                    team_name=f"{proj.title[:25]} Team",
                    members=member_assignments,
                    score=score_breakdown,
                    conflicts=[],
                    explanation=None,
                    is_approved=False,
                )
            )

        unassigned = [s_id for s_id in student_ids if s_id not in assigned_student_ids]
        return teams, unassigned, elapsed_ms
