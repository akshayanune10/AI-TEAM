"""
Multi-objective scoring engine calculating the 6-factor composite quality score.
"""

from typing import List, Dict, Tuple, Set, Optional
import numpy as np

from app.models.student import Student
from app.models.project import Project, ProjectRequirement
from app.models.team import TeamScoreBreakdown
from app.config import DEFAULT_WEIGHTS


class ScoringService:
    """Calculates granular and composite scores for student teams assigned to projects."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self._normalize_weights()

    def _normalize_weights(self):
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def calculate_skill_coverage(
        self, members: List[Student], project: Project
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculates skill coverage (0-100), returning covered skills and missing mandatory skills.
        """
        if not project.requirements:
            return 100.0, [], []

        covered_skills: List[str] = []
        missing_mandatory_skills: List[str] = []
        weighted_coverage_sum = 0.0
        total_weight = 0.0

        for req in project.requirements:
            req_name = req.skill_name.lower().strip()
            total_weight += req.importance_weight

            # Find best proficiency among members
            best_prof = 0
            for student in members:
                for sk in student.skills:
                    if sk.name.lower().strip() == req_name:
                        if sk.proficiency > best_prof:
                            best_prof = sk.proficiency

            if best_prof >= req.required_level:
                covered_skills.append(req.skill_name)
                weighted_coverage_sum += req.importance_weight * 1.0
            elif best_prof > 0:
                fraction = best_prof / max(1, req.required_level)
                weighted_coverage_sum += req.importance_weight * fraction
                if req.is_mandatory and fraction < 0.5:
                    missing_mandatory_skills.append(req.skill_name)
                else:
                    covered_skills.append(f"{req.skill_name} (Partial {best_prof}/{req.required_level})")
            else:
                if req.is_mandatory:
                    missing_mandatory_skills.append(req.skill_name)

        if total_weight == 0:
            coverage_pct = 100.0
        else:
            coverage_pct = (weighted_coverage_sum / total_weight) * 100.0

        # Mandatory skill penalty
        if missing_mandatory_skills:
            penalty = len(missing_mandatory_skills) * 15.0
            coverage_pct = max(0.0, coverage_pct - penalty)

        return round(coverage_pct, 2), covered_skills, missing_mandatory_skills

    def calculate_skill_complementarity(
        self, members: List[Student], project: Project
    ) -> float:
        """
        Calculates complementarity (0-100).
        Rewards teams where different members fill different requirement gaps,
        penalizing redundant duplicate skillsets that leave project requirements unfulfilled.
        """
        if not members or not project.requirements:
            return 100.0

        req_names = {r.skill_name.lower().strip(): r for r in project.requirements}
        num_reqs = len(req_names)

        # Track which requirements each member covers (proficiency >= 3)
        member_contributions: Dict[int, Set[str]] = {s.id: set() for s in members}
        for s in members:
            for sk in s.skills:
                sk_clean = sk.name.lower().strip()
                if sk_clean in req_names and sk.proficiency >= 3:
                    member_contributions[s.id].add(sk_clean)

        # 1. Breadth of unique requirements covered by members
        all_covered_reqs = set().union(*member_contributions.values()) if member_contributions else set()
        breadth_ratio = len(all_covered_reqs) / max(1, num_reqs)

        # 2. Member contribution balance: avoids one student doing 100% while others do 0%
        counts = [len(skills) for skills in member_contributions.values()]
        active_contributors = sum(1 for c in counts if c > 0)
        contributor_ratio = active_contributors / max(1, len(members))

        # 3. Redundancy control
        total_covered_instances = sum(counts)
        unique_instances = len(all_covered_reqs)
        uniqueness_ratio = (unique_instances / max(1, total_covered_instances)) if total_covered_instances > 0 else 0.5

        # Weighted combination
        score = (breadth_ratio * 0.50 + contributor_ratio * 0.30 + uniqueness_ratio * 0.20) * 100.0
        return round(min(100.0, max(10.0, score)), 2)

    def calculate_project_preference(self, members: List[Student], project: Project) -> float:
        """
        Calculates average project preference satisfaction (0-100).
        """
        if not members:
            return 0.0

        scores = []
        for s in members:
            rank = None
            for p in s.preferences:
                if p.project_id == project.id:
                    rank = p.rank
                    break

            if rank == 1:
                scores.append(100.0)
            elif rank == 2:
                scores.append(75.0)
            elif rank == 3:
                scores.append(50.0)
            elif rank is not None:
                scores.append(25.0)
            else:
                scores.append(10.0)  # Unranked / fallback

        return round(float(np.mean(scores)), 2)

    def calculate_availability_overlap(self, members: List[Student]) -> Tuple[float, int]:
        """
        Calculates schedule overlap (0-100) and counts common mutual slots.
        """
        if not members:
            return 0.0, 0

        # Build set of (day, slot) for each member
        member_slots: List[Set[Tuple[str, str]]] = []
        for s in members:
            avail = {
                (a.day, a.slot)
                for a in s.availability
                if a.is_available
            }
            member_slots.append(avail)

        if not member_slots:
            return 0.0, 0

        # Common slots across all members
        common = set.intersection(*member_slots)
        common_count = len(common)

        # Partial slots (available to at least len(members)-1)
        all_slots_flat = [slot for s_slots in member_slots for slot in s_slots]
        from collections import Counter
        counts = Counter(all_slots_flat)
        partial_count = sum(1 for slot, c in counts.items() if c >= len(members) - 1 and slot not in common)

        # Baseline: 3 common slots = 75 points, 4+ common slots = 90-100 points
        score = (common_count * 25.0) + (partial_count * 5.0)
        return round(min(100.0, max(0.0, score)), 2), common_count

    def calculate_work_style_compatibility(self, members: List[Student]) -> float:
        """
        Calculates work-style and team-role compatibility (0-100).
        Evaluates role diversity (leadership, execution, QA/docs) and collaborative harmony.
        """
        if not members:
            return 0.0

        # 1. Leadership balance: ideally 1 leader/planner (3-4 points), not 0 and not all
        lead_scores = [s.work_style.leadership_inclination for s in members]
        eager_leaders = sum(1 for l in lead_scores if l >= 4)
        if eager_leaders == 1:
            lead_balance = 100.0
        elif eager_leaders == 2 and len(members) >= 4:
            lead_balance = 85.0
        elif eager_leaders == 0:
            lead_balance = 60.0  # Leadership vacuum
        else:
            lead_balance = max(30.0, 100.0 - (eager_leaders - 1) * 25.0)  # Too many chiefs

        # 2. Role diversity
        roles = {s.work_style.primary_role for s in members}
        role_diversity = min(100.0, (len(roles) / max(1, len(members))) * 100.0)

        # 3. Collaboration mode consensus
        collab_modes = [s.work_style.collaboration_mode for s in members]
        from collections import Counter
        mode_counts = Counter(collab_modes)
        dominant_mode_ratio = mode_counts.most_common(1)[0][1] / len(members)
        collab_harmony = dominant_mode_ratio * 100.0

        score = (lead_balance * 0.40) + (role_diversity * 0.35) + (collab_harmony * 0.25)
        return round(min(100.0, max(20.0, score)), 2)

    def calculate_experience_balance(
        self, members: List[Student], cohort_mean_exp: float = 3.2
    ) -> float:
        """
        Calculates experience balance (0-100).
        Penalizes stacking all high-experience students together or all novices together.
        """
        if not members:
            return 0.0

        team_mean_exp = float(np.mean([s.experience_level for s in members]))
        # Difference from cohort mean
        diff = abs(team_mean_exp - cohort_mean_exp)
        score = max(0.0, 100.0 - (diff * 35.0))
        return round(score, 2)

    def calculate_team_score(
        self,
        members: List[Student],
        project: Project,
        cohort_mean_exp: float = 3.2,
    ) -> TeamScoreBreakdown:
        """
        Computes the complete composite 6-factor score for a team.
        """
        s_cov, covered, missing = self.calculate_skill_coverage(members, project)
        s_comp = self.calculate_skill_complementarity(members, project)
        s_pref = self.calculate_project_preference(members, project)
        s_avail, common_count = self.calculate_availability_overlap(members)
        s_style = self.calculate_work_style_compatibility(members)
        s_exp = self.calculate_experience_balance(members, cohort_mean_exp)

        composite = (
            self.weights["skill_coverage"] * s_cov
            + self.weights["skill_complementarity"] * s_comp
            + self.weights["project_preference"] * s_pref
            + self.weights["availability"] * s_avail
            + self.weights["work_style"] * s_style
            + self.weights["experience_balance"] * s_exp
        )

        return TeamScoreBreakdown(
            skill_coverage=s_cov,
            skill_complementarity=s_comp,
            project_preference=s_pref,
            availability=s_avail,
            work_style=s_style,
            experience_balance=s_exp,
            total_composite_score=round(composite, 2),
            common_slots_count=common_count,
            covered_skills=covered,
            missing_mandatory_skills=missing,
        )
