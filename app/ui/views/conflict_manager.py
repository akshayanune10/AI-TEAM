"""
Conflict Management & Faculty Overrides View.
Displays active team risks and provides administrative controls:
pinning/locking students, excluding incompatible pairs, moving members,
and re-optimizing with strict constraint preservation.
"""

import streamlit as st
import pandas as pd

from app.data.repository import DataRepository
from app.services.override_service import OverrideService
from app.models.team import ConstraintType


def render_conflict_manager(repo: DataRepository):
    st.header("🛡️ Conflict Manager & Faculty Overrides")
    st.markdown(
        "AI recommendations must never override faculty authority. Inspect detected conflicts, "
        "lock students to specific projects, enforce pair exclusions, and re-optimize teams."
    )

    override_svc = OverrideService(repo)
    latest_run = repo.get_latest_generation_run()
    students = repo.get_all_students()
    projects = repo.get_all_projects()

    if not students or not projects:
        st.warning("Please ensure students and projects are registered.")
        return

    student_options = {f"{s.name} ({s.student_id_str})": s.id for s in students}
    project_options = {f"{p.id}: {p.title}": p.id for p in projects}

    tab_conflicts, tab_overrides, tab_reopt = st.tabs(
        ["⚠️ Active Conflicts", "🔒 Manage Constraints & Overrides", "🔄 Re-Optimize"]
    )

    with tab_conflicts:
        st.subheader("Detected Team Risks & Warnings")
        all_conflicts = []
        if latest_run and latest_run.teams:
            for t in latest_run.teams:
                for c in t.conflicts:
                    all_conflicts.append(
                        {
                            "Team": t.team_name,
                            "Severity": c.severity.value.upper(),
                            "Type": c.conflict_type,
                            "Description": c.description,
                            "Actionable Suggestion": c.repair_suggestion,
                        }
                    )
        if not all_conflicts:
            st.success("🎉 No active conflicts or warnings detected across current teams!")
        else:
            st.dataframe(pd.DataFrame(all_conflicts), use_container_width=True)

    with tab_overrides:
        st.subheader("1. Add Lock or Exclusion Constraint")
        col_lock, col_exclude = st.columns(2)

        with col_lock:
            st.markdown("#### 📌 Lock Student to Project")
            st.caption("Pin a specific student permanently to a required project.")
            lock_s_label = st.selectbox("Select Student to Lock", list(student_options.keys()), key="lock_s")
            lock_p_label = st.selectbox("Target Project", list(project_options.keys()), key="lock_p")
            if st.button("Lock Student Assignment"):
                s_id = student_options[lock_s_label]
                p_id = project_options[lock_p_label]
                override_svc.lock_student_to_project(s_id, p_id)
                st.success(f"Locked {lock_s_label} to {lock_p_label}!")
                st.rerun()

        with col_exclude:
            st.markdown("#### 🚫 Exclude Incompatible Pair")
            st.caption("Prevent two students from being assigned to the same team.")
            ex_s1_label = st.selectbox("First Student", list(student_options.keys()), key="ex_s1")
            ex_s2_label = st.selectbox("Second Student", list(student_options.keys()), key="ex_s2", index=min(1, len(student_options) - 1))
            ex_reason = st.text_input("Administrative Reason", value="Incompatible schedule / conflicting role preferences")
            if st.button("Enforce Pair Exclusion"):
                s1_id = student_options[ex_s1_label]
                s2_id = student_options[ex_s2_label]
                if s1_id == s2_id:
                    st.error("Cannot exclude a student from themselves.")
                else:
                    override_svc.exclude_pair(s1_id, s2_id, ex_reason)
                    st.success(f"Excluded pair {ex_s1_label} and {ex_s2_label}!")
                    st.rerun()

        st.markdown("---")
        st.subheader("2. Current Active Constraints")
        active_constraints = repo.get_all_constraints()
        if not active_constraints:
            st.info("No manual constraints currently active.")
        else:
            c_rows = []
            student_id_map = {s.id: s.name for s in students}
            for c in active_constraints:
                s1_name = student_id_map.get(c.student_id_1, f"#{c.student_id_1}")
                target = f"Project #{c.target_project_id}" if c.target_project_id else student_id_map.get(c.student_id_2, f"#{c.student_id_2}")
                c_rows.append(
                    {
                        "ID": c.id,
                        "Type": c.constraint_type.value,
                        "Student": s1_name,
                        "Target / Partner": target,
                        "Note": c.note,
                    }
                )
            st.dataframe(pd.DataFrame(c_rows), use_container_width=True)

            del_id = st.selectbox("Select constraint ID to remove:", [c.id for c in active_constraints])
            if st.button("🗑️ Remove Constraint"):
                repo.delete_constraint(del_id)
                st.success(f"Removed constraint #{del_id}.")
                st.rerun()

    with tab_reopt:
        st.subheader("Constrained Re-Optimization")
        st.markdown(
            "Re-run the optimization engine. Any locked assignments and pair exclusions "
            "will be **strictly enforced** as hard constraints during this run."
        )
        if st.button("⚡ Re-Optimize Teams with Active Constraints", type="primary"):
            with st.spinner("Re-optimizing teams while preserving all manual constraints..."):
                new_run = override_svc.reoptimize_with_constraints(students, projects)
            st.success(f"Re-optimization complete! Formed {len(new_run.teams)} teams in {new_run.runtime_ms} ms.")
            st.rerun()
