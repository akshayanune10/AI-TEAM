"""
Tests for Explainability Engine.
"""

from app.services.explainability_service import ExplainabilityService
from app.services.scoring_service import ScoringService


def test_team_and_student_explanations(sample_students, sample_projects):
    scoring = ScoringService()
    explainer = ExplainabilityService(scoring)

    proj = sample_projects[0]
    team_members = sample_students[:4]
    score = scoring.calculate_team_score(team_members, proj)

    team_exp = explainer.explain_team(team_members, proj, score)
    assert team_exp.summary is not None
    assert len(team_exp.summary) > 20
    assert len(team_exp.strengths) > 0
    assert len(team_exp.student_explanations) == 4

    # Check student explanation
    s1_exp = team_exp.student_explanations[0]
    assert s1_exp.student_id == team_members[0].id
    assert len(s1_exp.reasons) > 0
