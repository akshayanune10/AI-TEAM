"""
Team, scoring, conflict, and explanation domain models.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum


class ConflictSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class TeamConflict(BaseModel):
    conflict_type: str = Field(..., description="E.g. schedule_conflict, skill_gap, imbalance, exclusion_violation")
    severity: ConflictSeverity = Field(default=ConflictSeverity.WARNING)
    description: str
    repair_suggestion: str


class StudentExplanation(BaseModel):
    student_id: int
    student_name: str
    reasons: List[str]
    primary_contribution: str


class TeamExplanation(BaseModel):
    summary: str
    strengths: List[str]
    tradeoffs: List[str]
    student_explanations: List[StudentExplanation] = Field(default_factory=list)


class TeamScoreBreakdown(BaseModel):
    skill_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    skill_complementarity: float = Field(default=0.0, ge=0.0, le=100.0)
    project_preference: float = Field(default=0.0, ge=0.0, le=100.0)
    availability: float = Field(default=0.0, ge=0.0, le=100.0)
    work_style: float = Field(default=0.0, ge=0.0, le=100.0)
    experience_balance: float = Field(default=0.0, ge=0.0, le=100.0)
    total_composite_score: float = Field(default=0.0, ge=0.0, le=100.0)
    common_slots_count: int = Field(default=0)
    covered_skills: List[str] = Field(default_factory=list)
    missing_mandatory_skills: List[str] = Field(default_factory=list)


class TeamMemberAssignment(BaseModel):
    student_id: int
    student_name: str
    student_id_str: str
    is_locked: bool = Field(default=False)
    assigned_role: str = Field(default="Core Developer")
    experience_level: int = Field(default=3)


class Team(BaseModel):
    id: Optional[int] = None
    project_id: int
    project_title: str
    team_name: str
    members: List[TeamMemberAssignment] = Field(default_factory=list)
    score: TeamScoreBreakdown = Field(default_factory=TeamScoreBreakdown)
    conflicts: List[TeamConflict] = Field(default_factory=list)
    explanation: Optional[TeamExplanation] = None
    is_approved: bool = Field(default=False)


class ConstraintType(str, Enum):
    LOCK_STUDENT = "lock_student"
    EXCLUDE_PAIR = "exclude_pair"


class TeamConstraint(BaseModel):
    id: Optional[int] = None
    constraint_type: ConstraintType
    student_id_1: int
    student_id_2: Optional[int] = None
    target_project_id: Optional[int] = None
    note: Optional[str] = None


class GenerationRun(BaseModel):
    id: Optional[int] = None
    timestamp: str
    algorithm: str
    weights: Dict[str, float]
    teams: List[Team] = Field(default_factory=list)
    unassigned_students: List[int] = Field(default_factory=list)
    average_score: float = 0.0
    fairness_std_dev: float = 0.0
    runtime_ms: float = 0.0
    is_finalized: bool = False
