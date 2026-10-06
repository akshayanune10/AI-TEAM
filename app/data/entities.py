"""
SQLAlchemy ORM Entity definitions for relational persistence.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.data.database import Base


class StudentEntity(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id_str = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    department = Column(String(100), default="Computer Science")
    academic_year = Column(String(50), default="Senior (4th Year)")
    experience_level = Column(Integer, default=3)
    gpa = Column(Float, nullable=True)
    bio = Column(Text, nullable=True)
    resume_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    skills = relationship("SkillEntity", back_populates="student", cascade="all, delete-orphan")
    availabilities = relationship("AvailabilityEntity", back_populates="student", cascade="all, delete-orphan")
    work_style = relationship("WorkStyleEntity", back_populates="student", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("PreferenceEntity", back_populates="student", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMemberEntity", back_populates="student")


class SkillEntity(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), default="programming_language")
    proficiency = Column(Integer, default=3)
    source = Column(String(50), default="self_reported")
    confidence = Column(Float, default=0.8)

    student = relationship("StudentEntity", back_populates="skills")


class AvailabilityEntity(Base):
    __tablename__ = "student_availability"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    day = Column(String(20), nullable=False)
    slot = Column(String(50), nullable=False)
    is_available = Column(Boolean, default=True)

    student = relationship("StudentEntity", back_populates="availabilities")


class WorkStyleEntity(Base):
    __tablename__ = "student_work_style"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=False)
    primary_role = Column(String(100), default="Core Developer / Implementer")
    secondary_role = Column(String(100), nullable=True)
    collaboration_mode = Column(String(100), default="Balanced")
    communication_preference = Column(String(100), default="Hybrid")
    leadership_inclination = Column(Integer, default=3)
    planning_orientation = Column(Integer, default=3)

    student = relationship("StudentEntity", back_populates="work_style")


class PreferenceEntity(Base):
    __tablename__ = "student_preferences"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    rank = Column(Integer, nullable=False)

    student = relationship("StudentEntity", back_populates="preferences")
    project = relationship("ProjectEntity", back_populates="preferences")


class ProjectEntity(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    domain = Column(String(100), default="Artificial Intelligence")
    target_team_size = Column(Integer, default=4)
    min_team_size = Column(Integer, default=3)
    max_team_size = Column(Integer, default=5)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    requirements = relationship("RequirementEntity", back_populates="project", cascade="all, delete-orphan")
    preferences = relationship("PreferenceEntity", back_populates="project")
    teams = relationship("TeamEntity", back_populates="project")


class RequirementEntity(Base):
    __tablename__ = "project_requirements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    category = Column(String(50), default="programming_language")
    required_level = Column(Integer, default=3)
    importance_weight = Column(Integer, default=3)
    is_mandatory = Column(Boolean, default=False)

    project = relationship("ProjectEntity", back_populates="requirements")


class GenerationRunEntity(Base):
    __tablename__ = "generation_runs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    algorithm = Column(String(50), nullable=False)
    weights_json = Column(Text, nullable=False)
    average_score = Column(Float, default=0.0)
    fairness_std_dev = Column(Float, default=0.0)
    runtime_ms = Column(Float, default=0.0)
    is_finalized = Column(Boolean, default=False)

    teams = relationship("TeamEntity", back_populates="run", cascade="all, delete-orphan")


class TeamEntity(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("generation_runs.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    team_name = Column(String(150), nullable=False)
    score_json = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False)

    run = relationship("GenerationRunEntity", back_populates="teams")
    project = relationship("ProjectEntity", back_populates="teams")
    members = relationship("TeamMemberEntity", back_populates="team", cascade="all, delete-orphan")
    conflicts = relationship("TeamConflictEntity", back_populates="team", cascade="all, delete-orphan")
    explanation = relationship("TeamExplanationEntity", back_populates="team", uselist=False, cascade="all, delete-orphan")


class TeamMemberEntity(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    is_locked = Column(Boolean, default=False)
    assigned_role = Column(String(100), default="Core Developer")

    team = relationship("TeamEntity", back_populates="members")
    student = relationship("StudentEntity", back_populates="team_memberships")


class TeamConflictEntity(Base):
    __tablename__ = "team_conflicts"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    conflict_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="warning")
    description = Column(Text, nullable=False)
    repair_suggestion = Column(Text, nullable=False)

    team = relationship("TeamEntity", back_populates="conflicts")


class TeamExplanationEntity(Base):
    __tablename__ = "team_explanations"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True, nullable=False)
    summary = Column(Text, nullable=False)
    strengths_json = Column(Text, nullable=False)
    tradeoffs_json = Column(Text, nullable=False)
    student_explanations_json = Column(Text, nullable=False)

    team = relationship("TeamEntity", back_populates="explanation")


class TeamConstraintEntity(Base):
    __tablename__ = "team_constraints"

    id = Column(Integer, primary_key=True, index=True)
    constraint_type = Column(String(50), nullable=False)
    student_id_1 = Column(Integer, nullable=False)
    student_id_2 = Column(Integer, nullable=True)
    target_project_id = Column(Integer, nullable=True)
    note = Column(String(255), nullable=True)


class PeerFeedbackEntity(Base):
    __tablename__ = "peer_feedback"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    evaluator_student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    target_student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    collaboration_rating = Column(Integer, nullable=False)
    communication_rating = Column(Integer, nullable=False)
    task_completion_rating = Column(Integer, nullable=False)
    overall_satisfaction = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
