"""
Team Review & Explainability View.
Interactive inspection of formed teams, radar score visualizations,
schedule heatmaps, and detailed 'Why this team?' & 'Why this student?' explanations.
"""

import streamlit as st
import pandas as pd
import json

from app.data.repository import DataRepository
from app.ui.components import render_radar_score_chart, render_schedule_heatmap


def render_team_review(repo: DataRepository):
    st.header("🔍 Team Review & Explainability")
    st.markdown(
        "Inspect formed teams, analyze multidimensional quality scores, and review "
        "transparent explanations answering **Why this team?** and **Why this student?**"
    )

    latest_run = repo.get_latest_generation_run()
    if not latest_run or not latest_run.teams:
        st.info("No teams generated yet. Please generate teams in the **Team Formation Studio** first.")
        return

    # Top level actions
    act_col1, act_col2, act_col3 = st.columns([2, 1, 1])
    with act_col1:
        st.subheader(f"Formed Teams ({len(latest_run.teams)}) — Run #{latest_run.id}")
    with act_col2:
        # Prepare CSV export
        export_rows = []
        for t in latest_run.teams:
            for m in t.members:
                export_rows.append(
                    {
                        "Team Name": t.team_name,
                        "Project Title": t.project_title,
                        "Student ID": m.student_id_str,
                        "Student Name": m.student_name,
                        "Assigned Role": m.assigned_role,
                        "Team Score": t.score.total_composite_score,
                        "Skill Coverage": t.score.skill_coverage,
                        "Common Slots": t.score.common_slots_count,
                    }
                )
        df_export = pd.DataFrame(export_rows)
        csv_data = df_export.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export CSV Roster", data=csv_data, file_name="team_rosters.csv", mime="text/csv")
    with act_col3:
        if st.button("✅ Approve All Teams", type="primary"):
            st.success("All teams officially approved and marked for project kickoff!")

    students = repo.get_all_students()
    student_map = {s.id: s for s in students}

    # Iterate over teams
    for t_idx, team in enumerate(latest_run.teams):
        with st.container():
            st.markdown(f"### 🚀 {team.team_name} — Project: *{team.project_title}*")
            
            c_score, c_chart, c_expl = st.columns([1.2, 1.5, 2.3])
            
            with c_score:
                st.metric("Total Quality Score", f"{team.score.total_composite_score}/100")
                st.caption(f"**Skill Coverage:** {team.score.skill_coverage}%")
                st.caption(f"**Complementarity:** {team.score.skill_complementarity}/100")
                st.caption(f"**Preference Sat:** {team.score.project_preference}%")
                st.caption(f"**Availability:** {team.score.availability}/100 ({team.score.common_slots_count} slots)")
                st.caption(f"**Work-Style:** {team.score.work_style}/100")
                st.caption(f"**Exp. Balance:** {team.score.experience_balance}/100")

            with c_chart:
                radar_fig = render_radar_score_chart(team.score)
                st.plotly_chart(radar_fig, use_container_width=True)

            with c_expl:
                st.markdown("**🧠 Why this team?**")
                if team.explanation:
                    st.write(team.explanation.summary)
                    if team.explanation.strengths:
                        st.markdown("**Key Strengths:**")
                        for s in team.explanation.strengths:
                            st.markdown(f"- ✅ {s}")
                    if team.explanation.tradeoffs:
                        st.markdown("**Considerations / Trade-offs:**")
                        for tr in team.explanation.tradeoffs:
                            st.markdown(f"- ⚠️ {tr}")
                else:
                    st.write("Balanced composite matching across skills and schedule.")

            # Roster & Why this student?
            st.markdown("#### 👥 Team Roster & Individual Contributions")
            m_cols = st.columns(len(team.members))
            
            for m_idx, member in enumerate(team.members):
                with m_cols[m_idx]:
                    st.markdown(f"**{member.student_name}**")
                    st.caption(f"ID: {member.student_id_str} | Exp: Level {member.experience_level}")
                    st.info(f"Role: {member.assigned_role}")

                    # Find student explanation
                    if team.explanation and team.explanation.student_explanations:
                        s_exp = next(
                            (se for se in team.explanation.student_explanations if se.student_id == member.student_id),
                            None,
                        )
                        if s_exp:
                            st.markdown("**Why this student?**")
                            for r in s_exp.reasons[:2]:
                                st.caption(f"• {r}")

            # Schedule Heatmap Accordion
            with st.expander(f"📅 View Collaboration Schedule Heatmap ({team.team_name})"):
                member_objs = [student_map[m.student_id] for m in team.members if m.student_id in student_map]
                hm_fig = render_schedule_heatmap(member_objs)
                if hm_fig:
                    st.plotly_chart(hm_fig, use_container_width=True)

            # Display conflicts if any
            if team.conflicts:
                st.markdown("**⚠️ Active Warnings & Conflicts:**")
                for c in team.conflicts:
                    st.warning(f"**{c.conflict_type.upper()}**: {c.description} — *{c.repair_suggestion}*")

            st.markdown("---")
