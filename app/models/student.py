"""
Student domain models and validation schemas.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class SkillSource(str, Enum):
    SELF_REPORTED = "self_reported"
    RESUME_DERIVED = "resume_derived"
    VALIDATED = "validated"
    INFERRED = "inferred"


class SkillCategory(str, Enum):
    PROGRAMMING_LANGUAGE = "programming_language"
    AI_ML = "ai_ml"
    DATA_DATABASE = "data_database"
    WEB_MOBILE = "web_mobile"
    CLOUD_DEVOPS = "cloud_devops"
    SYSTEMS_IOT = "systems_iot"
    SOFT_SKILL = "soft_skill"
    DOMAIN_EXPERIENCE = "domain_experience"


class StudentSkill(BaseModel):
    name: str = Field(..., description="Canonical skill name")
    category: SkillCategory = Field(default=SkillCategory.PROGRAMMING_LANGUAGE)
    proficiency: int = Field(default=3, ge=1, le=5, description="Proficiency rating 1-5")
    source: SkillSource = Field(default=SkillSource.SELF_REPORTED)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Estimated confidence score")


class TimeSlotAvailability(BaseModel):
    day: str = Field(..., description="Day of the week (e.g. Monday)")
    slot: str = Field(..., description="Time slot window")
    is_available: bool = Field(default=True)


class WorkStyle(BaseModel):
    primary_role: str = Field(default="Core Developer / Implementer")
    secondary_role: Optional[str] = Field(default=None)
    collaboration_mode: str = Field(default="Balanced (Independent tasks + frequent check-ins)")
    communication_preference: str = Field(default="Hybrid (Short standups + chat)")
    leadership_inclination: int = Field(default=3, ge=1, le=5, description="1=Prefers supporting, 5=Eager to lead")
    planning_orientation: int = Field(default=3, ge=1, le=5, description="1=Exploratory/Agile, 5=Structured/Detailed plan")


class StudentPreference(BaseModel):
    project_id: int
    rank: int = Field(..., ge=1, le=10, description="1 = First choice, 2 = Second choice, etc.")


class StudentCreate(BaseModel):
    student_id_str: str = Field(..., description="College Roll No or Student ID")
    name: str = Field(..., min_length=2)
    email: EmailStr
    department: str = Field(default="Computer Science")
    academic_year: str = Field(default="Senior (4th Year)")
    experience_level: int = Field(default=3, ge=1, le=5, description="Overall software/project experience (1-5)")
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0)
    bio: Optional[str] = Field(default="")
    skills: List[StudentSkill] = Field(default_factory=list)
    preferences: List[StudentPreference] = Field(default_factory=list)
    availability: List[TimeSlotAvailability] = Field(default_factory=list)
    work_style: WorkStyle = Field(default_factory=WorkStyle)
    resume_filename: Optional[str] = Field(default=None)


class Student(StudentCreate):
    id: int
