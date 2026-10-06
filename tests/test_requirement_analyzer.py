"""
Tests for Project Requirement Analyzer.
"""

from app.ai.requirement_analyzer import ProjectRequirementAnalyzer


def test_project_requirement_analyzer_heuristic():
    analyzer = ProjectRequirementAnalyzer()
    title = "AI-Based Smart Traffic Management System"
    desc = "Build a camera-based system using Python, computer vision, and machine learning to optimize city traffic lights with IoT microcontrollers."

    reqs = analyzer.analyze_heuristic(title, desc)
    req_names = [r.skill_name for r in reqs]

    assert "Python" in req_names
    assert "Computer Vision" in req_names
    assert "Machine Learning" in req_names

    # Check that prominent skills are marked mandatory or high importance
    cv_req = next(r for r in reqs if r.skill_name == "Computer Vision")
    assert cv_req.importance_weight >= 4

    # Check soft skill inclusion
    assert any("Documentation" in r.skill_name or "Communication" in r.skill_name for r in reqs)
