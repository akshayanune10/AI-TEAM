"""
Academic Benchmark Analytics View.
Rigorous empirical evaluation comparing Proposed Hybrid Optimization against
Baseline A (Random Allocation) and Baseline B (Skill-Only Matching).
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from app.data.repository import DataRepository
from app.services.simulation_service import SimulationService


def render_benchmark_analytics(repo: DataRepository):
    st.header("📈 Academic Benchmarking & Analytics")
    st.markdown(
        "To ensure the system is **technically defensible** and provides measurable research value, "
        "this view benchmarks the proposed **Hybrid Optimization** against classical baseline heuristics."
    )

    students = repo.get_all_students()
    projects = repo.get_all_projects()

    if len(students) < 4 or len(projects) == 0:
        st.warning("Please load or register at least 4 students and projects to run empirical benchmarks.")
        return

    sim_service = SimulationService()

    if st.button("🧪 Run Comparative Empirical Evaluation", type="primary"):
        with st.spinner("Executing comparative trials across Random, Skill-Only, and Proposed algorithms..."):
            benchmark_data = sim_service.run_benchmark_comparison(students, projects)

        st.session_state["benchmark_data"] = benchmark_data
        st.success("Benchmark evaluation completed!")

    data = st.session_state.get("benchmark_data")
    if not data:
        st.info("Click 'Run Comparative Empirical Evaluation' to generate baseline comparison metrics.")
        return

    st.subheader("1. Empirical Comparison Table")
    df_bench = pd.DataFrame(data)
    st.dataframe(df_bench, use_container_width=True)

    st.subheader("2. Visual Quality Metrics Comparison")
    # Melt dataframe for multi-bar visualization
    metrics_to_plot = ["Skill Coverage (%)", "Preference Sat. (%)", "Common Slots / Team", "Avg Quality Score"]
    df_melted = df_bench.melt(
        id_vars=["Method"],
        value_vars=[m for m in metrics_to_plot if m in df_bench.columns],
        var_name="Metric",
        value_name="Score",
    )

    fig = px.bar(
        df_melted,
        x="Metric",
        y="Score",
        color="Method",
        barmode="group",
        title="Comparative Evaluation: Baseline vs Proposed",
        color_discrete_sequence=["#9E9E9E", "#FF9800", "#1976D2"],
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("3. Academic Findings & Discussion")
    st.markdown(
        """
        - **Baseline A (Random)** forms teams without awareness of skill requirements or schedule constraints, 
          typically leading to severe availability bottlenecks (near zero common collaboration slots) and unmet mandatory skills.
        - **Baseline B (Skill-Only)** maximizes technical competencies but sacrifices collaboration schedules, 
          leading to student schedule conflicts and ignoring project preferences.
        - **Proposed (Hybrid AI + Optimization)** balances skill coverage and complementarity with 
          schedule availability, team diversity, and student preferences, while strictly enforcing hard constraints 
          and providing verifiable natural language explanations.
        """
    )
