"""
Team Formation Studio View.
Algorithm selection, multi-objective weight configuration,
team generation execution, and optimization summary.
"""

import streamlit as st
import numpy as np

from app.data.repository import DataRepository
from app.config import DEFAULT_WEIGHTS
from app.services.scoring_service import ScoringService
from app.services.explainability_service import ExplainabilityService
from app.services.conflict_service import ConflictService
from app.algorithms.optimizer_ilp import ILPOptimizer
from app.algorithms.optimizer_greedy import GreedyOptimizer
from app.algorithms.baseline_random import BaselineRandomOptimizer
from app.algorithms.baseline_skill_only import BaselineSkillOnlyOptimizer
from app.models.team import GenerationRun


def render_team_studio(repo: DataRepository):
    st.header("⚡ Team Formation Studio")
    st.markdown(
        "Form optimal student teams by balancing technical skill coverage, complementarity, "
        "project preferences, schedule availability, work styles, and diversity."
    )

    students = repo.get_all_students()
    projects = repo.get_all_projects()
    constraints = repo.get_all_constraints()

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Registered Students", len(students))
    with col_stat2:
        st.metric("Available Projects", len(projects))
    with col_stat3:
        st.metric("Active Constraints", len(constraints))

    if len(students) < 3 or len(projects) == 0:
        st.warning("Insufficient data to generate teams. Please ensure at least 3 students and 1 project are created, or load the demo cohort from the sidebar.")
        return

    st.subheader("1. Optimization Parameters & Algorithm")
    opt_col1, opt_col2 = st.columns(2)
    with opt_col1:
        algorithm_choice = st.selectbox(
            "Optimization Engine",
            [
                "Hybrid Integer Linear Programming (PuLP ILP)",
                "Greedy Heuristic + 2-Opt Local Search",
                "Baseline A: Random Allocation",
                "Baseline B: Skill-Only Greedy Matching",
            ],
            index=0,
            help="PuLP ILP optimizes mathematical assignment with strict CBC solver constraints. Greedy provides fast local-search climbing.",
        )
    with opt_col2:
        target_team_size = st.slider("Target Team Size", 2, 6, 4)

    st.subheader("2. Multi-Objective Scoring Weights")
    st.caption("Adjust the importance of each factor. Weights are automatically normalized to 100%.")

    w_col1, w_col2, w_col3 = st.columns(3)
    with w_col1:
        w_cov = st.slider("Skill Coverage Weight (%)", 0, 60, int(DEFAULT_WEIGHTS["skill_coverage"] * 100), step=5)
        w_comp = st.slider("Skill Complementarity Weight (%)", 0, 50, int(DEFAULT_WEIGHTS["skill_complementarity"] * 100), step=5)
    with w_col2:
        w_pref = st.slider("Project Preference Weight (%)", 0, 50, int(DEFAULT_WEIGHTS["project_preference"] * 100), step=5)
        w_avail = st.slider("Availability Overlap Weight (%)", 0, 50, int(DEFAULT_WEIGHTS["availability"] * 100), step=5)
    with w_col3:
        w_style = st.slider("Work-Style Harmony Weight (%)", 0, 40, int(DEFAULT_WEIGHTS["work_style"] * 100), step=5)
        w_exp = st.slider("Experience Balance Weight (%)", 0, 40, int(DEFAULT_WEIGHTS["experience_balance"] * 100), step=5)

    weights_dict = {
        "skill_coverage": w_cov / 100.0,
        "skill_complementarity": w_comp / 100.0,
        "project_preference": w_pref / 100.0,
        "availability": w_avail / 100.0,
        "work_style": w_style / 100.0,
        "experience_balance": w_exp / 100.0,
    }

    if constraints:
        with st.expander(f"🔒 Active Constraints ({len(constraints)})"):
            for c in constraints:
                st.write(f"- **{c.constraint_type.value}**: Student #{c.student_id_1} (Target: {c.target_project_id or c.student_id_2}) — *{c.note}*")

    st.markdown("---")
    if st.button("🚀 Generate Teams", type="primary", use_container_width=True):
        scoring = ScoringService(weights_dict)
        explainer = ExplainabilityService(scoring)
        conflict_detector = ConflictService()

        with st.spinner("Executing constrained team formation algorithm..."):
            if "Integer Linear Programming" in algorithm_choice:
                optimizer = ILPOptimizer(scoring)
                teams, unassigned, elapsed_ms = optimizer.solve(
                    students, projects, constraints=constraints, target_team_size=target_team_size
                )
                algo_name = "PuLP ILP Optimizer"
                # If ILP returns empty due to tight constraints, fall back to greedy with notice
                if not teams:
                    st.warning("ILP model encountered tight feasibility bounds. Falling back to robust Greedy + 2-Opt optimizer...")
                    greedy = GreedyOptimizer(scoring)
                    teams, unassigned, elapsed_ms = greedy.solve(
                        students, projects, constraints=constraints, target_team_size=target_team_size
                    )
                    algo_name = "Greedy + 2-Opt (Fallback)"
            elif "Greedy" in algorithm_choice:
                optimizer = GreedyOptimizer(scoring)
                teams, unassigned, elapsed_ms = optimizer.solve(
                    students, projects, constraints=constraints, target_team_size=target_team_size
                )
                algo_name = "Greedy + 2-Opt Optimizer"
            elif "Random" in algorithm_choice:
                optimizer = BaselineRandomOptimizer(scoring)
                teams, unassigned, elapsed_ms = optimizer.solve(students, projects, target_team_size=target_team_size)
                algo_name = "Baseline Random"
            else:
                optimizer = BaselineSkillOnlyOptimizer(scoring)
                teams, unassigned, elapsed_ms = optimizer.solve(students, projects, target_team_size=target_team_size)
                algo_name = "Baseline Skill-Only"

        # Enrich teams with explanations and conflicts
        student_map = {s.id: s for s in students}
        project_map = {p.id: p for p in projects}
        enriched_teams = []

        for t in teams:
            proj = project_map.get(t.project_id)
            if not proj:
                continue

            member_objs = [student_map[m.student_id] for m in t.members if m.student_id in student_map]
            conflicts = conflict_detector.detect_conflicts(member_objs, proj, t.score)
            explanation = explainer.explain_team(member_objs, proj, t.score)

            t.conflicts = conflicts
            t.explanation = explanation
            enriched_teams.append(t)

        scores = [t.score.total_composite_score for t in enriched_teams]
        avg_score = float(np.mean(scores)) if scores else 0.0
        std_dev = float(np.std(scores)) if scores else 0.0

        run = GenerationRun(
            timestamp="",
            algorithm=algo_name,
            weights=scoring.weights,
            teams=enriched_teams,
            unassigned_students=unassigned,
            average_score=round(avg_score, 2),
            fairness_std_dev=round(std_dev, 2),
            runtime_ms=elapsed_ms,
            is_finalized=False,
        )

        saved_run = repo.save_generation_run(run)
        st.session_state["latest_run"] = saved_run

        st.success(f"Successfully generated {len(enriched_teams)} teams in {elapsed_ms} ms!")
        st.rerun()

    # If run exists in database, show current run summary
    latest_run = repo.get_latest_generation_run()
    if latest_run:
        st.subheader("📊 Latest Team Generation Summary")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Avg Quality Score", f"{latest_run.average_score}/100")
        with m_col2:
            st.metric("Fairness (Std Dev)", f"±{latest_run.fairness_std_dev}")
        with m_col3:
            total_assigned = sum(len(t.members) for t in latest_run.teams)
            st.metric("Assigned Students", f"{total_assigned}/{len(students)}")
        with m_col4:
            st.metric("Runtime", f"{latest_run.runtime_ms} ms")

        st.info(f"Generated with **{latest_run.algorithm}**. Navigate to **Team Review & Explainability** tab to inspect teams in detail.")
