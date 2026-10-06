"""
Simulation and Academic Benchmarking Service.
Supports What-If scenario experiments (team size, weights) and
comparative evaluation against Baseline A (Random) and Baseline B (Skill-Only).
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np

from app.models.student import Student
from app.models.project import Project
from app.models.team import Team, GenerationRun
from app.algorithms.optimizer_ilp import ILPOptimizer
from app.algorithms.optimizer_greedy import GreedyOptimizer
from app.algorithms.baseline_random import BaselineRandomOptimizer
from app.algorithms.baseline_skill_only import BaselineSkillOnlyOptimizer
from app.services.scoring_service import ScoringService


class SimulationService:
    """Runs What-If parameter experiments and benchmark comparisons."""

    def __init__(self):
        self.scoring = ScoringService()

    def run_what_if(
        self,
        students: List[Student],
        projects: List[Project],
        base_teams: List[Team],
        new_weights: Dict[str, float],
        new_team_size: int,
    ) -> Dict[str, Any]:
        """
        Simulates a What-If scenario and calculates diff against baseline run.
        """
        new_scoring = ScoringService(new_weights)
        optimizer = GreedyOptimizer(new_scoring)

        new_teams, unassigned, elapsed_ms = optimizer.solve(
            students, projects, target_team_size=new_team_size
        )

        # Baseline metrics
        base_scores = [t.score.total_composite_score for t in base_teams]
        base_covs = [t.score.skill_coverage for t in base_teams]
        base_avails = [t.score.common_slots_count for t in base_teams]
        base_prefs = [t.score.project_preference for t in base_teams]

        # New metrics
        new_scores = [t.score.total_composite_score for t in new_teams]
        new_covs = [t.score.skill_coverage for t in new_teams]
        new_avails = [t.score.common_slots_count for t in new_teams]
        new_prefs = [t.score.project_preference for t in new_teams]

        # Student movement diff
        base_assignment: Dict[int, int] = {}
        for t in base_teams:
            for m in t.members:
                base_assignment[m.student_id] = t.project_id

        moved_students = []
        student_map = {s.id: s for s in students}
        for t in new_teams:
            for m in t.members:
                prev_proj = base_assignment.get(m.student_id)
                if prev_proj is not None and prev_proj != t.project_id:
                    s_name = student_map.get(m.student_id).name if m.student_id in student_map else f"#{m.student_id}"
                    moved_students.append(
                        {
                            "student_name": s_name,
                            "from_project": prev_proj,
                            "to_project": t.project_title,
                        }
                    )

        score_delta = round(float(np.mean(new_scores)) - float(np.mean(base_scores)), 2) if base_scores and new_scores else 0.0
        cov_delta = round(float(np.mean(new_covs)) - float(np.mean(base_covs)), 2) if base_covs and new_covs else 0.0
        avail_delta = round(float(np.mean(new_avails)) - float(np.mean(base_avails)), 2) if base_avails and new_avails else 0.0

        explanation = (
            f"Changing target team size to {new_team_size} and adjusting factor weights "
            f"resulted in {len(moved_students)} student reallocations. "
            f"Average team quality shifted by {score_delta:+} points, "
            f"skill coverage shifted by {cov_delta:+}%, and "
            f"average shared collaboration slots shifted by {avail_delta:+}. "
        )

        return {
            "new_teams": new_teams,
            "moved_students": moved_students,
            "score_delta": score_delta,
            "coverage_delta": cov_delta,
            "availability_delta": avail_delta,
            "explanation": explanation,
            "new_average_score": round(float(np.mean(new_scores)), 2) if new_scores else 0.0,
            "new_fairness_std": round(float(np.std(new_scores)), 2) if new_scores else 0.0,
            "runtime_ms": elapsed_ms,
        }

    def run_benchmark_comparison(
        self,
        students: List[Student],
        projects: List[Project],
        target_team_size: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Executes and compares:
        1. Baseline A: Random Allocation
        2. Baseline B: Skill-Only Matching
        3. Proposed: Hybrid Multi-Objective Optimization
        """
        scoring = ScoringService()

        # 1. Baseline A: Random
        random_opt = BaselineRandomOptimizer(scoring)
        teams_rand, _, time_rand = random_opt.solve(students, projects, target_team_size=target_team_size)

        # 2. Baseline B: Skill-Only
        skill_opt = BaselineSkillOnlyOptimizer(scoring)
        teams_skill, _, time_skill = skill_opt.solve(students, projects, target_team_size=target_team_size)

        # 3. Proposed: Hybrid Constrained Optimizer
        proposed_opt = GreedyOptimizer(scoring)
        teams_prop, _, time_prop = proposed_opt.solve(students, projects, target_team_size=target_team_size)

        def compute_summary(name: str, teams: List[Team], elapsed: float) -> Dict[str, Any]:
            if not teams:
                return {"method": name, "avg_score": 0, "coverage": 0, "complementarity": 0, "pref": 0, "avail": 0, "std_dev": 0, "runtime_ms": elapsed}

            scores = [t.score.total_composite_score for t in teams]
            covs = [t.score.skill_coverage for t in teams]
            comps = [t.score.skill_complementarity for t in teams]
            prefs = [t.score.project_preference for t in teams]
            avails = [t.score.common_slots_count for t in teams]
            missing_mandatory = sum(len(t.score.missing_mandatory_skills) for t in teams)

            return {
                "Method": name,
                "Avg Quality Score": round(float(np.mean(scores)), 2),
                "Skill Coverage (%)": round(float(np.mean(covs)), 2),
                "Complementarity": round(float(np.mean(comps)), 2),
                "Preference Sat. (%)": round(float(np.mean(prefs)), 2),
                "Common Slots / Team": round(float(np.mean(avails)), 2),
                "Fairness (Std Dev)": round(float(np.std(scores)), 2),
                "Unmet Mandatory Reqs": missing_mandatory,
                "Runtime (ms)": elapsed,
            }

        return [
            compute_summary("Baseline A (Random Allocation)", teams_rand, time_rand),
            compute_summary("Baseline B (Skill-Only Matching)", teams_skill, time_skill),
            compute_summary("Proposed (Hybrid Multi-Objective AI)", teams_prop, time_prop),
        ]
