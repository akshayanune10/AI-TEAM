"""
Post-Project Peer Feedback View.
Captures peer collaboration ratings, communication effectiveness,
deliverable completion, and student satisfaction to build a historical dataset.
"""

import streamlit as st
import pandas as pd

from app.data.repository import DataRepository
from app.models.feedback import PeerFeedbackCreate


def render_feedback_view(repo: DataRepository):
    st.header("🔄 Post-Project Peer Feedback Loop")
    st.markdown(
        "Continuous improvement requires verifiable post-project outcomes. "
        "Students submit peer evaluations assessing teammate collaboration, communication, "
        "and milestone delivery."
    )

    latest_run = repo.get_latest_generation_run()
    if not latest_run or not latest_run.teams:
        st.info("Teams must be formed before collecting post-project evaluations.")
        return

    tab_submit, tab_history = st.tabs(["📝 Submit Peer Evaluation", "📊 Historical Review Data"])

    with tab_submit:
        team_options = {t.team_name: t for t in latest_run.teams}
        sel_team_name = st.selectbox("Select Team", list(team_options.keys()))
        sel_team = team_options[sel_team_name]

        member_options = {f"{m.student_name} ({m.student_id_str})": m.student_id for m in sel_team.members}

        col1, col2 = st.columns(2)
        with col1:
            evaluator_label = st.selectbox("Your Name (Evaluator)", list(member_options.keys()), key="evaluator_sel")
        with col2:
            target_label = st.selectbox(
                "Teammate Being Evaluated",
                [k for k in member_options.keys() if k != evaluator_label],
                key="target_sel",
            )

        st.subheader("Evaluation Criteria (1 = Poor, 5 = Exemplary)")
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            collab_r = st.slider("Teamwork & Collaboration", 1, 5, 4)
            comm_r = st.slider("Communication & Responsiveness", 1, 5, 4)
        with r_col2:
            task_r = st.slider("Task Completion & Quality", 1, 5, 4)
            sat_r = st.slider("Overall Satisfaction Working Together", 1, 5, 4)

        comments = st.text_area("Constructive Comments & Observations", placeholder="Shared clear status updates and delivered core ML module on time.")

        if st.button("Submit Peer Feedback", type="primary"):
            evaluator_id = member_options[evaluator_label]
            target_id = member_options[target_label]

            fb = PeerFeedbackCreate(
                team_id=sel_team.id or 1,
                evaluator_student_id=evaluator_id,
                target_student_id=target_id,
                collaboration_rating=collab_r,
                communication_rating=comm_r,
                task_completion_rating=task_r,
                overall_satisfaction=sat_r,
                comments=comments,
            )
            repo.create_peer_feedback(fb)
            st.success(f"Peer review successfully recorded for {target_label}!")
            st.rerun()

    with tab_history:
        st.subheader("Historical Feedback Records")
        all_feedback = repo.get_feedback_for_team(sel_team.id or 1)
        if not all_feedback:
            st.info("No feedback submissions recorded for this team yet.")
        else:
            fb_rows = [
                {
                    "Evaluator ID": fb.evaluator_student_id,
                    "Target Student ID": fb.target_student_id,
                    "Collaboration (1-5)": fb.collaboration_rating,
                    "Communication (1-5)": fb.communication_rating,
                    "Task Completion (1-5)": fb.task_completion_rating,
                    "Satisfaction (1-5)": fb.overall_satisfaction,
                    "Comments": fb.comments,
                    "Date": fb.created_at[:10],
                }
                for fb in all_feedback
            ]
            st.dataframe(pd.DataFrame(fb_rows), use_container_width=True)
