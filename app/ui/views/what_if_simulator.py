"""
What-If Scenario Simulation View.
Enables faculty to test hypothetical team sizes and scoring weight variations,
inspecting side-by-side metric deltas and student reallocation logs.
"""

import streamlit as st
import pandas as pd

from app.data.repository import DataRepository
from app.services.simulation_service import SimulationService


def render_what_if_simulator(repo: DataRepository):
    st.header("🧪 What-If Scenario Simulator")
    st.markdown(
        "Experiment with hypothetical parameter changes (e.g. increasing team size, "
        "raising availability importance) and inspect **why** resulting team configurations shift."
    )

    latest_run = repo.get_latest_generation_run()
    students = repo.get_all_students()
    projects = repo.get_all_projects()

    if not latest_run or not latest_run.teams:
        st.info("Please generate an initial set of teams in the **Team Formation Studio** before running What-If simulations.")
        return

    sim_service = SimulationService()

    st.subheader("1. Configure Hypothetical Parameters")
    col1, col2 = st.columns(2)
    with col1:
        hypo_team_size = st.slider("Hypothetical Team Size", 2, 6, 4)
        hypo_w_cov = st.slider("Skill Coverage Weight (%)", 0, 60, int(latest_run.weights.get("skill_coverage", 0.30) * 100))
        hypo_w_comp = st.slider("Skill Complementarity Weight (%)", 0, 50, int(latest_run.weights.get("skill_complementarity", 0.20) * 100))
    with col2:
        hypo_w_pref = st.slider("Preference Satisfaction Weight (%)", 0, 50, int(latest_run.weights.get("project_preference", 0.15) * 100))
        hypo_w_avail = st.slider("Availability Overlap Weight (%)", 0, 50, int(latest_run.weights.get("availability", 0.15) * 100))
        hypo_w_style = st.slider("Work-Style Weight (%)", 0, 40, int(latest_run.weights.get("work_style", 0.10) * 100))
        hypo_w_exp = st.slider("Experience Balance Weight (%)", 0, 40, int(latest_run.weights.get("experience_balance", 0.10) * 100))

    hypo_weights = {
        "skill_coverage": hypo_w_cov / 100.0,
        "skill_complementarity": hypo_w_comp / 100.0,
        "project_preference": hypo_w_pref / 100.0,
        "availability": hypo_w_avail / 100.0,
        "work_style": hypo_w_style / 100.0,
        "experience_balance": hypo_w_exp / 100.0,
    }

    if st.button("🔬 Execute What-If Simulation", type="primary"):
        with st.spinner("Simulating hypothetical scenario..."):
            sim_result = sim_service.run_what_if(
                students=students,
                projects=projects,
                base_teams=latest_run.teams,
                new_weights=hypo_weights,
                new_team_size=hypo_team_size,
            )

        st.markdown("---")
        st.subheader("📊 Scenario Comparison & Impact Analysis")
        st.info(sim_result["explanation"])

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Avg Quality Score", f"{sim_result['new_average_score']}/100", f"{sim_result['score_delta']:+} pts")
        with m2:
            st.metric("Skill Coverage Delta", f"{sim_result['coverage_delta']:+}%")
        with m3:
            st.metric("Common Slots Delta", f"{sim_result['availability_delta']:+} slots")
        with m4:
            st.metric("Fairness Std Dev", f"±{sim_result['new_fairness_std']}")

        # Reallocations log
        st.markdown("#### 🔄 Student Movement Log")
        moved = sim_result["moved_students"]
        if not moved:
            st.write("No students moved teams under this configuration.")
        else:
            st.caption(f"{len(moved)} students were reallocated to different teams:")
            st.dataframe(pd.DataFrame(moved), use_container_width=True)
