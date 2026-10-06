"""
Project domain models and requirement schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.student import SkillCategory


class ProjectRequirement(BaseModel):
    id: Optional[int] = None
    skill_name: str = Field(..., description="Canonical or extracted skill name")
    category: SkillCategory = Field(default=SkillCategory.PROGRAMMING_LANGUAGE)
    required_level: int = Field(default=3, ge=1, le=5, description="Minimum expected proficiency 1-5")
    importance_weight: int = Field(default=3, ge=1, le=5, description="Priority weight 1-5")
    is_mandatory: bool = Field(default=False, description="Must at least one member possess this skill?")


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    domain: str = Field(default="Artificial Intelligence")
    target_team_size: int = Field(default=4, ge=2, le=8)
    min_team_size: int = Field(default=3, ge=2, le=8)
    max_team_size: int = Field(default=5, ge=2, le=10)
    requirements: List[ProjectRequirement] = Field(default_factory=list)


class Project(ProjectCreate):
    id: int
    status: str = Field(default="active")
