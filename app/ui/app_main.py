"""
AI Project Team Formation System - Main Streamlit Application.
A hybrid AI + optimization-based, explainable decision support system for college student team formation.
"""

import sys
from pathlib import Path

# Add project root to sys.path so modules import reliably
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from app.data.database import init_db
from app.data.repository import DataRepository
from app.data.sample_data import seed_database
from app.config import GEMINI_API_KEY
from app.ui.views import (
    render_student_portal,
    render_project_manager,
    render_team_studio,
    render_team_review,
    render_conflict_manager,
    render_what_if_simulator,
    render_benchmark_analytics,
    render_feedback_view,
)


def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Modern academic styling */
        .main {
            background-color: #FAFAFA;
        }
        .stMetric {
            background-color: #FFFFFF;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #E0E0E0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        div[data-testid="stExpander"] {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            background-color: #FFFFFF;
        }
        .badge-mandatory {
            background-color: #FFEBEE;
            color: #C62828;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-optional {
            background-color: #E8F5E9;
            color: #2E7D32;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title="AI Project Team Formation System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_styles()
    init_db()
    repo = DataRepository()

    # Sidebar Navigation & Management
    with st.sidebar:
        st.title("🎓 Team Formation AI")
        st.caption("College Decision-Support System")
        st.markdown("---")

        nav_choice = st.radio(
            "Navigation Menu",
            [
                "⚡ Team Formation Studio",
                "🔍 Team Review & Explainability",
                "🛡️ Conflict Manager & Overrides",
                "🧪 What-If Simulator",
                "📈 Academic Benchmarks",
                "🎓 Student Skills & Profiles",
                "📋 Project & Requirement Studio",
                "🔄 Peer Feedback Loop",
            ],
            index=0,
        )

        st.markdown("---")
        st.subheader("🛠️ Cohort Demo Tools")

        students = repo.get_all_students()
        projects = repo.get_all_projects()

        if st.button("📥 Load Realistic Demo Cohort", use_container_width=True):
            with st.spinner("Seeding 24 students with resumes and 6 multidisciplinary projects..."):
                seed_database(repo)
            st.success("Seeded 24 students and 6 projects!")
            st.rerun()

        if st.button("🧹 Clear All Database Data", use_container_width=True):
            repo.clear_database()
            st.warning("Database cleared.")
            st.rerun()

        st.markdown("---")
        st.subheader("System Telemetry")
        st.caption(f"Students in DB: **{len(students)}**")
        st.caption(f"Projects in DB: **{len(projects)}**")
        st.caption(f"Database: **SQLite Local**")
        llm_status = "Active" if GEMINI_API_KEY else "Local NLP Heuristic"
        st.caption(f"AI Engine: **{llm_status}**")
        st.caption("Environment: **Python 3.11**")

    # Route view
    if nav_choice == "⚡ Team Formation Studio":
        render_team_studio(repo)
    elif nav_choice == "🔍 Team Review & Explainability":
        render_team_review(repo)
    elif nav_choice == "🛡️ Conflict Manager & Overrides":
        render_conflict_manager(repo)
    elif nav_choice == "🧪 What-If Simulator":
        render_what_if_simulator(repo)
    elif nav_choice == "📈 Academic Benchmarks":
        render_benchmark_analytics(repo)
    elif nav_choice == "🎓 Student Skills & Profiles":
        render_student_portal(repo)
    elif nav_choice == "📋 Project & Requirement Studio":
        render_project_manager(repo)
    elif nav_choice == "🔄 Peer Feedback Loop":
        render_feedback_view(repo)


if __name__ == "__main__":
    main()
