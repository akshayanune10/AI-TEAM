"""
Multi-format resume parser and skill extractor.
Supports PDF, DOCX, and plain text with section awareness and confidence estimation.
"""

from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple, Any
import io

from app.models.student import StudentSkill, SkillSource, SkillCategory
from app.ai.skill_taxonomy import SKILL_TAXONOMY, find_canonical_skill

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None


class ResumeParser:
    """Parses resume documents and extracts skills with calibrated confidence."""

    def __init__(self):
        self.taxonomy = SKILL_TAXONOMY

    def extract_text_from_bytes(self, file_bytes: bytes, filename: str) -> str:
        """Extracts text from raw file bytes based on file extension."""
        ext = Path(filename).suffix.lower()
        if ext == ".txt":
            return file_bytes.decode("utf-8", errors="ignore")
        elif ext == ".pdf":
            if PdfReader is None:
                raise ImportError("pypdf is required to parse PDF resumes.")
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(text_parts)
        elif ext in [".docx", ".doc"]:
            if docx is None:
                raise ImportError("python-docx is required to parse DOCX resumes.")
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([p.text for p in doc.paragraphs])
        else:
            raise ValueError(f"Unsupported file format: {ext}. Supported formats are .pdf, .docx, .txt")

    def extract_text_from_file(self, file_path: Path) -> str:
        """Reads and extracts text from a file on disk."""
        with open(file_path, "rb") as f:
            return self.extract_text_from_bytes(f.read(), file_path.name)

    def segment_sections(self, text: str) -> Dict[str, str]:
        """Segments resume into sections (skills, experience, projects, education)."""
        sections: Dict[str, str] = {
            "skills": "",
            "experience": "",
            "projects": "",
            "education": "",
            "general": "",
        }

        lines = text.split("\n")
        current_section = "general"

        section_patterns = {
            "skills": re.compile(r"^(skills|technical skills|technologies|proficiencies|competencies)", re.IGNORECASE),
            "experience": re.compile(r"^(experience|work experience|employment|internships)", re.IGNORECASE),
            "projects": re.compile(r"^(projects|academic projects|key projects|portfolio)", re.IGNORECASE),
            "education": re.compile(r"^(education|academic background|qualifications)", re.IGNORECASE),
        }

        buffer: Dict[str, List[str]] = {k: [] for k in sections}

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Check if this line is a section header (usually short, uppercase/bold-like)
            matched_section = None
            if len(stripped) < 40:
                for sec_name, pattern in section_patterns.items():
                    if pattern.search(stripped):
                        matched_section = sec_name
                        break

            if matched_section:
                current_section = matched_section
            else:
                buffer[current_section].append(stripped)

        return {k: "\n".join(v) for k, v in buffer.items()}

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extracts email and phone number heuristics."""
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        
        # Name heuristic: First non-empty short line
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        candidate_name = lines[0] if lines and len(lines[0]) < 35 and not "@" in lines[0] else None

        return {
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
            "name": candidate_name,
        }

    def parse_skills(self, text: str) -> List[StudentSkill]:
        """
        Extracts skills from text with calibrated confidence and estimated proficiency.
        Distinguishes between skills found in dedicated skills section vs body text.
        """
        sections = self.segment_sections(text)
        skills_text = sections.get("skills", "")
        projects_text = sections.get("projects", "") + "\n" + sections.get("experience", "")
        full_lower = text.lower()
        skills_lower = skills_text.lower()
        projects_lower = projects_text.lower()

        extracted_skills: List[StudentSkill] = []

        for canonical_name, data in self.taxonomy.items():
            category = data["category"]
            aliases = data["aliases"]
            keywords = data.get("keywords", [])

            # Check for matches
            in_skills_section = False
            in_projects_section = False
            total_mentions = 0

            for alias in aliases:
                # Word boundary matching
                escaped = re.escape(alias.lower())
                pattern = rf"\b{escaped}\b"
                
                if re.search(pattern, skills_lower):
                    in_skills_section = True
                if re.search(pattern, projects_lower):
                    in_projects_section = True
                
                matches = len(re.findall(pattern, full_lower))
                total_mentions += matches

            if total_mentions == 0:
                continue

            # Check co-occurring keywords
            co_occurring = 0
            for kw in keywords:
                if re.search(rf"\b{re.escape(kw.lower())}\b", full_lower):
                    co_occurring += 1

            # Estimate confidence:
            # - In dedicated skills section: +0.4
            # - In projects/work experience: +0.3
            # - Mentions frequency: min(0.2, total_mentions * 0.05)
            # - Related keywords co-occurrence: min(0.2, co_occurring * 0.05)
            confidence = 0.35
            if in_skills_section:
                confidence += 0.35
            if in_projects_section:
                confidence += 0.20
            confidence += min(0.10, total_mentions * 0.03)
            confidence = min(0.98, max(0.40, round(confidence, 2)))

            # Estimate proficiency (1-5):
            # 1: Novice, 2: Familiar, 3: Competent, 4: Advanced, 5: Expert
            base_prof = 2
            if in_skills_section and in_projects_section:
                base_prof = 3
            if total_mentions >= 3 or co_occurring >= 2:
                base_prof += 1
            if total_mentions >= 6 and co_occurring >= 3:
                base_prof += 1
            proficiency = min(5, max(1, base_prof))

            extracted_skills.append(
                StudentSkill(
                    name=canonical_name,
                    category=category,
                    proficiency=proficiency,
                    source=SkillSource.RESUME_DERIVED,
                    confidence=confidence,
                )
            )

        # Sort by proficiency and confidence descending
        extracted_skills.sort(key=lambda s: (s.proficiency, s.confidence), reverse=True)
        return extracted_skills

    def parse_full_resume(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Full extraction pipeline returning contact info, text, and skills."""
        text = self.extract_text_from_bytes(file_bytes, filename)
        contact = self.extract_contact_info(text)
        skills = self.parse_skills(text)
        return {
            "text": text,
            "contact": contact,
            "skills": skills,
            "filename": filename,
        }
