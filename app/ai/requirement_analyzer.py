"""
Project Requirement Analyzer.
Analyzes project titles and descriptions to recommend required skills,
suggesting importance levels and mandatory status while preserving faculty editability.
"""

import re
import json
from typing import List, Dict, Any, Optional
import os

from app.models.project import ProjectRequirement
from app.models.student import SkillCategory
from app.ai.skill_taxonomy import SKILL_TAXONOMY
from app.config import GEMINI_API_KEY


class ProjectRequirementAnalyzer:
    """Extracts candidate project requirements from title and description."""

    def __init__(self):
        self.taxonomy = SKILL_TAXONOMY
        self.gemini_api_key = GEMINI_API_KEY

    def analyze_heuristic(self, title: str, description: str) -> List[ProjectRequirement]:
        """Deterministic ontology-based requirement extractor."""
        combined_text = f"{title}\n{description}".lower()
        title_lower = title.lower()

        extracted: List[ProjectRequirement] = []

        for canonical_name, data in self.taxonomy.items():
            category = data["category"]
            aliases = data["aliases"]
            keywords = data.get("keywords", [])

            # Match score
            score = 0
            is_in_title = False

            # Check aliases
            for alias in aliases:
                escaped = re.escape(alias.lower())
                pattern = rf"\b{escaped}\b"
                if re.search(pattern, title_lower):
                    is_in_title = True
                    score += 5
                elif re.search(pattern, combined_text):
                    score += 4

            # Check domain keywords
            for kw in keywords:
                escaped = re.escape(kw.lower())
                pattern = rf"\b{escaped}\b"
                if re.search(pattern, combined_text):
                    score += 1

            if score > 0:
                # Determine importance weight (1-5)
                importance = min(5, max(1, 2 + (score // 2)))
                if is_in_title:
                    importance = max(importance, 4)

                # Determine required level (1-5)
                required_level = 3 if importance >= 4 else 2

                # Flag mandatory if prominent in title or high keyword density
                is_mandatory = is_in_title or score >= 4

                extracted.append(
                    ProjectRequirement(
                        skill_name=canonical_name,
                        category=category,
                        required_level=required_level,
                        importance_weight=importance,
                        is_mandatory=is_mandatory,
                    )
                )

        # Ensure essential foundational requirements (e.g. presentation & documentation)
        soft_skills_present = [r for r in extracted if r.category == SkillCategory.SOFT_SKILL]
        if not soft_skills_present:
            extracted.append(
                ProjectRequirement(
                    skill_name="Technical Documentation",
                    category=SkillCategory.SOFT_SKILL,
                    required_level=2,
                    importance_weight=2,
                    is_mandatory=False,
                )
            )
            extracted.append(
                ProjectRequirement(
                    skill_name="Presentation & Communication",
                    category=SkillCategory.SOFT_SKILL,
                    required_level=2,
                    importance_weight=2,
                    is_mandatory=False,
                )
            )

        # Sort by importance and mandatory status descending
        extracted.sort(key=lambda r: (r.is_mandatory, r.importance_weight), reverse=True)
        return extracted

    def analyze_with_gemini(self, title: str, description: str) -> Optional[List[ProjectRequirement]]:
        """Optional LLM enhancement via Gemini API if key is available."""
        if not self.gemini_api_key:
            return None

        try:
            import requests

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            prompt = f"""
            Analyze the following college student capstone project title and description:
            Title: {title}
            Description: {description}

            Extract 4 to 8 required technical and soft skills needed for a student team to succeed.
            Return ONLY a valid JSON array of objects with the following keys:
            - "skill_name": string (canonical skill name like "Python", "Machine Learning", "React", "PostgreSQL", "Computer Vision", "Technical Documentation")
            - "category": string (one of "programming_language", "ai_ml", "data_database", "web_mobile", "cloud_devops", "systems_iot", "soft_skill")
            - "required_level": integer between 1 and 5
            - "importance_weight": integer between 1 and 5
            - "is_mandatory": boolean (true if the project cannot function without this skill)
            """

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "response_mime_type": "application/json"},
            }
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                data = res.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(content)
                requirements = []
                for item in parsed:
                    requirements.append(
                        ProjectRequirement(
                            skill_name=item.get("skill_name"),
                            category=SkillCategory(item.get("category", "programming_language")),
                            required_level=int(item.get("required_level", 3)),
                            importance_weight=int(item.get("importance_weight", 3)),
                            is_mandatory=bool(item.get("is_mandatory", False)),
                        )
                    )
                return requirements
        except Exception:
            # Gracefully fallback to deterministic analyzer
            pass
        return None

    def analyze(self, title: str, description: str) -> List[ProjectRequirement]:
        """Main analysis entrypoint: tries LLM if configured, falls back to ontology."""
        llm_result = self.analyze_with_gemini(title, description)
        if llm_result:
            return llm_result
        return self.analyze_heuristic(title, description)
