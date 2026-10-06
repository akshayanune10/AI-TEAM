"""
Conflict and risk detection service.
Proactively identifies bottlenecks, schedule mismatches, skill gaps,
and role imbalances, generating actionable repair suggestions.
"""

from typing import List, Dict, Set, Tuple
from app.models.student import Student
from app.models.project import Project
from app.models.team import Team, TeamConflict, ConflictSeverity, TeamScoreBreakdown


class ConflictService:
    """Diagnoses team risks and formulates actionable repair guidance."""

    def detect_conflicts(
        self,
        members: List[Student],
        project: Project,
        score: TeamScoreBreakdown,
    ) -> List[TeamConflict]:
        conflicts: List[TeamConflict] = []

        if not members:
            return conflicts

        # 1. Schedule Conflict Check
        if score.common_slots_count == 0:
            conflicts.append(
                TeamConflict(
                    conflict_type="schedule_conflict",
                    severity=ConflictSeverity.CRITICAL,
                    description="Zero common collaboration windows found across all team members.",
                    repair_suggestion="Consider swapping one member whose schedule conflicts with the team, or designate an asynchronous workflow.",
                )
            )
        elif score.common_slots_count == 1:
            conflicts.append(
                TeamConflict(
                    conflict_type="schedule_conflict",
                    severity=ConflictSeverity.WARNING,
                    description="Only 1 common collaboration window available this week.",
                    repair_suggestion="Encourage members to open additional mutual hours on weekends or evenings.",
                )
            )

        # 2. Skill Gap Check
        if score.missing_mandatory_skills:
            conflicts.append(
                TeamConflict(
                    conflict_type="skill_gap",
                    severity=ConflictSeverity.CRITICAL,
                    description=f"Missing mandatory requirements: {', '.join(score.missing_mandatory_skills)}.",
                    repair_suggestion=f"Swap in a student with competence in {score.missing_mandatory_skills[0]} to prevent project stalling.",
                )
            )
        elif score.skill_coverage < 60.0:
            conflicts.append(
                TeamConflict(
                    conflict_type="skill_gap",
                    severity=ConflictSeverity.WARNING,
                    description=f"Low technical skill coverage ({score.skill_coverage}%).",
                    repair_suggestion="Review secondary project requirements or assign a mentor to bolster technical gaps.",
                )
            )

        # 3. Preference Conflict Check
        if score.project_preference < 40.0:
            conflicts.append(
                TeamConflict(
                    conflict_type="preference_conflict",
                    severity=ConflictSeverity.WARNING,
                    description="Low student preference satisfaction. Multiple members did not select this project in their top 2 choices.",
                    repair_suggestion="Check if students can be swapped with teams matching their higher preference rank.",
                )
            )

        # 4. Leadership & Work-Style Imbalance
        lead_count = sum(1 for s in members if s.work_style.leadership_inclination >= 4)
        if lead_count == 0:
            conflicts.append(
                TeamConflict(
                    conflict_type="work_style_imbalance",
                    severity=ConflictSeverity.WARNING,
                    description="Leadership Vacuum: No member indicates a strong willingness to coordinate or lead.",
                    repair_suggestion="Appoint a designated student coordinator or swap in a member with project management inclination.",
                )
            )
        elif lead_count >= 3 and len(members) <= 5:
            conflicts.append(
                TeamConflict(
                    conflict_type="work_style_friction",
                    severity=ConflictSeverity.INFO,
                    description=f"Multiple strong leaders ({lead_count} members). Potential for conflicting technical visions.",
                    repair_suggestion="Clearly delineate architectural vs project management responsibilities at kickoff.",
                )
            )

        # 5. Experience Imbalance
        exp_levels = [s.experience_level for s in members]
        if max(exp_levels) - min(exp_levels) >= 3 and len(members) >= 4:
            conflicts.append(
                TeamConflict(
                    conflict_type="experience_gap",
                    severity=ConflictSeverity.INFO,
                    description="Wide experience disparity between senior/lead members and junior members.",
                    repair_suggestion="Establish explicit peer-mentoring pairing within the team.",
                )
            )

        return conflicts
