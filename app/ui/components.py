"""
Reusable Streamlit UI visual components, Plotly charts, and badges.
"""

from typing import List, Dict, Any, Optional
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from app.models.team import Team, TeamScoreBreakdown, ConflictSeverity
from app.models.student import Student


def render_radar_score_chart(score: TeamScoreBreakdown) -> go.Figure:
    """Renders a radar chart of the 6 score dimensions."""
    categories = [
        "Skill Coverage",
        "Complementarity",
        "Preference Sat.",
        "Availability Overlap",
        "Work-Style Harmony",
        "Experience Balance",
    ]
    values = [
        score.skill_coverage,
        score.skill_complementarity,
        score.project_preference,
        score.availability,
        score.work_style,
        score.experience_balance,
    ]
    # Close the radar loop
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(33, 150, 243, 0.25)",
            line=dict(color="#1976D2", width=2),
            name="Team Quality",
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
        ),
        showlegend=False,
        margin=dict(l=35, r=35, t=25, b=25),
        height=280,
    )
    return fig


def render_schedule_heatmap(members: List[Student]) -> Optional[go.Figure]:
    """Renders a weekly heatmap of mutual schedule availability."""
    from app.config import DAYS_OF_WEEK, TIME_SLOTS

    if not members:
        return None

    z_matrix = []
    num_members = len(members)

    for slot in TIME_SLOTS:
        row = []
        for day in DAYS_OF_WEEK:
            avail_count = sum(
                1
                for s in members
                if any(a.day == day and a.slot == slot and a.is_available for a in s.availability)
            )
            row.append(avail_count)
        z_matrix.append(row)

    fig = go.Figure(
        data=go.Heatmap(
            z=z_matrix,
            x=DAYS_OF_WEEK,
            y=TIME_SLOTS,
            colorscale="Blues",
            zmin=0,
            zmax=num_members,
            colorbar=dict(title="Free Members"),
        )
    )
    fig.update_layout(
        title=f"Collaboration Windows Heatmap ({num_members} members)",
        margin=dict(l=40, r=40, t=40, b=30),
        height=280,
    )
    return fig


def render_metric_card(title: str, value: Any, delta: Optional[str] = None, delta_color: str = "normal"):
    """Displays a clean metric card."""
    st.metric(label=title, value=value, delta=delta, delta_color=delta_color)
