"""
UI Views package.
"""

from app.ui.views.student_portal import render_student_portal
from app.ui.views.project_manager import render_project_manager
from app.ui.views.team_studio import render_team_studio
from app.ui.views.team_review import render_team_review
from app.ui.views.conflict_manager import render_conflict_manager
from app.ui.views.what_if_simulator import render_what_if_simulator
from app.ui.views.benchmark_analytics import render_benchmark_analytics
from app.ui.views.feedback_view import render_feedback_view

__all__ = [
    "render_student_portal",
    "render_project_manager",
    "render_team_studio",
    "render_team_review",
    "render_conflict_manager",
    "render_what_if_simulator",
    "render_benchmark_analytics",
    "render_feedback_view",
]
