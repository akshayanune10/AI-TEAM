"""
AI and NLP modules.
"""

from app.ai.skill_taxonomy import SKILL_TAXONOMY, find_canonical_skill
from app.ai.resume_parser import ResumeParser
from app.ai.requirement_analyzer import ProjectRequirementAnalyzer

__all__ = [
    "SKILL_TAXONOMY",
    "find_canonical_skill",
    "ResumeParser",
    "ProjectRequirementAnalyzer",
]
