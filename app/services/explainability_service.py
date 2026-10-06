"""
Explainability Engine.
Generates human-readable, transparent justifications for "Why this team?" and "Why this student?"
grounded directly in the actual mathematical scores and constraint factors.
"""

from typing import List, Dict, Tuple, Optional
from app.models.student import Student
from app.models.project import Project
from app.models.team import (
    Team,
    TeamExplanation,
    StudentExplanation,
    TeamScoreBreakdown,
)
from app.services.scoring_service import ScoringService


class ExplainabilityService:
    """Produces explainable insights for recommendations."""

    def __init__(self, scoring_service: Optional[ScoringService] = None):
        self.scoring_service = scoring_service or ScoringService()

    def explain_student(
        self,
        student: Student,
        team_members: List[Student],
        project: Project,
    ) -> StudentExplanation:
        """Explains why a specific student was assigned to this team and project."""
        reasons = []

        # 1. Project requirement match
        student_skills = {s.name.lower().strip(): s for s in student.skills}
        matching_reqs = []
        for req in project.requirements:
            req_name = req.skill_name.lower().strip()
            if req_name in student_skills:
                sk = student_skills[req_name]
                if sk.proficiency >= req.required_level:
                    matching_reqs.append(f"{req.skill_name} (Proficiency {sk.proficiency}/5)")

        if matching_reqs:
            reasons.append(f"Directly satisfies project requirements: {', '.join(matching_reqs[:3])}.")

        # 2. Check if student fills a unique gap on the team
        other_members = [m for m in team_members if m.id != student.id]
        unique_skills = []
        for sk_name, sk in student_skills.items():
            if sk.proficiency >= 3:
                others_have = any(
                    any(m_sk.name.lower().strip() == sk_name and m_sk.proficiency >= 3 for m_sk in m.skills)
                    for m in other_members
                )
                if not others_have:
                    unique_skills.append(sk.name)

        if unique_skills:
            reasons.append(f"Provides complementary capability gap filling for: {', '.join(unique_skills[:3])}.")

        # 3. Preference satisfaction
        for pref in student.preferences:
            if pref.project_id == project.id:
                if pref.rank == 1:
                    reasons.append("Assigned to 1st choice preferred project.")
                elif pref.rank == 2:
                    reasons.append("Assigned to 2nd choice preferred project.")
                elif pref.rank == 3:
                    reasons.append("Assigned to 3rd choice preferred project.")
                break

        # 4. Role and leadership
        role = student.work_style.primary_role
        if student.work_style.leadership_inclination >= 4:
            reasons.append(f"Acts as technical/leadership anchor in role: {role}.")
        else:
            reasons.append(f"Fulfills core execution role: {role}.")

        primary_contribution = (
            f"Core skill coverage in {matching_reqs[0]}" if matching_reqs
            else f"Team role in {role}"
        )

        return StudentExplanation(
            student_id=student.id,
            student_name=student.name,
            reasons=reasons,
            primary_contribution=primary_contribution,
        )

    def explain_team(
        self,
        members: List[Student],
        project: Project,
        score: TeamScoreBreakdown,
    ) -> TeamExplanation:
        """Explains why this entire team was formed."""
        strengths = []
        tradeoffs = []

        # Skill coverage
        if score.skill_coverage >= 80.0:
            strengths.append(f"High technical skill coverage ({score.skill_coverage}% of project requirements met).")
        elif score.skill_coverage >= 60.0:
            strengths.append(f"Moderate technical skill coverage ({score.skill_coverage}%).")
        else:
            tradeoffs.append(f"Sub-optimal technical coverage ({score.skill_coverage}%). Review missing skills.")

        # Covered skills
        if score.covered_skills:
            strengths.append(f"Covers key competencies: {', '.join(score.covered_skills[:4])}.")

        # Missing mandatory skills
        if score.missing_mandatory_skills:
            tradeoffs.append(f"Missing mandatory requirements: {', '.join(score.missing_mandatory_skills)}.")

        # Complementarity
        if score.skill_complementarity >= 75.0:
            strengths.append("High skill complementarity: distinct members cover distinct technical areas.")
        else:
            tradeoffs.append("Skill overlap: multiple members duplicate capabilities while some areas are thin.")

        # Availability
        if score.common_slots_count >= 3:
            strengths.append(f"Strong schedule overlap with {score.common_slots_count} common weekly collaboration windows.")
        elif score.common_slots_count >= 1:
            strengths.append(f"Sufficient collaboration windows ({score.common_slots_count} common slot).")
        else:
            tradeoffs.append("Schedule bottleneck: No mutually free weekly window found across all members.")

        # Preference
        if score.project_preference >= 75.0:
            strengths.append("High preference alignment: majority of students received top choices.")
        elif score.project_preference < 50.0:
            tradeoffs.append("Preference compromise: some students assigned outside their top 2 choices.")

        # Work style
        if score.work_style >= 75.0:
            strengths.append("Balanced work-style profile with complementary leadership and execution roles.")
        else:
            tradeoffs.append("Potential work-style friction: check leadership distribution and communication modes.")

        summary = (
            f"Team formed with an overall composite quality score of {score.total_composite_score}/100. "
            f"Achieves {score.skill_coverage}% skill coverage across {len(project.requirements)} requirements "
            f"with {score.common_slots_count} shared collaboration slots."
        )

        # Build student-level explanations
        student_exps = [
            self.explain_student(s, members, project)
            for s in members
        ]

        return TeamExplanation(
            summary=summary,
            strengths=strengths,
            tradeoffs=tradeoffs,
            student_explanations=student_exps,
        )
