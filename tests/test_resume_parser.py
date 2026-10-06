"""
Tests for AI Resume Parser and Skill Extractor.
"""

from app.ai.resume_parser import ResumeParser
from app.models.student import SkillSource


def test_resume_parser_skills_and_confidence():
    parser = ResumeParser()
    sample_resume = """
    Alex Johnson
    alex.johnson@college.edu | (555) 123-4567

    TECHNICAL SKILLS:
    Languages: Python, TypeScript, SQL, C++
    Frameworks & Tools: PyTorch, Docker, PostgreSQL, React

    PROJECTS:
    - Smart Traffic Vision: Built real-time object tracking using Computer Vision, OpenCV, and PyTorch.
    - Distributed Pipeline: Implemented streaming data ingestion with Docker, PostgreSQL, and Python.

    EXPERIENCE:
    ML Research Intern: Developed deep learning models for anomaly detection with PyTorch and Python.
    """

    res = parser.parse_full_resume(sample_resume.encode("utf-8"), "resume.txt")
    assert res["contact"]["email"] == "alex.johnson@college.edu"
    assert res["contact"]["name"] == "Alex Johnson"

    skills = res["skills"]
    assert len(skills) >= 5

    skill_names = [s.name for s in skills]
    assert "Python" in skill_names
    assert "PyTorch" in skill_names
    assert "Computer Vision" in skill_names
    assert "Docker" in skill_names

    # Check that Python has high confidence and resume_derived source
    python_skill = next(s for s in skills if s.name == "Python")
    assert python_skill.source == SkillSource.RESUME_DERIVED
    assert python_skill.confidence >= 0.85
    assert python_skill.proficiency >= 3


def test_resume_parser_section_awareness():
    parser = ResumeParser()
    text = """
    SKILLS
    Machine Learning, React

    PROJECTS
    Built a website with React.
    """
    sections = parser.segment_sections(text)
    assert "skills" in sections
    assert "Machine Learning" in sections["skills"]
    assert "projects" in sections
    assert "React" in sections["projects"]
