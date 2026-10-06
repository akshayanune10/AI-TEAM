"""
Project Manager View.
Project creation, AI requirement analyzer with editable proposals,
and project requirement administration.
"""

import streamlit as st
import pandas as pd

from app.data.repository import DataRepository
from app.models.project import ProjectCreate, ProjectRequirement
from app.models.student import SkillCategory
from app.ai.requirement_analyzer import ProjectRequirementAnalyzer
from app.ai.skill_taxonomy import SKILL_TAXONOMY


def render_project_manager(repo: DataRepository):
    st.header("📋 Project & Requirement Studio")
    st.markdown(
        "Faculty can define projects and utilize the **AI Requirement Analyzer** to automatically "
        "identify technical and soft skills, review importance weights, and designate mandatory constraints."
    )

    tab_create, tab_manage = st.tabs(["➕ Create New Project", "📂 Existing Projects"])

    with tab_create:
        st.subheader("1. Project Details")
        col1, col2 = st.columns([2, 1])
        with col1:
            p_title = st.text_input(
                "Project Title *",
                value="Autonomous Drone Delivery Route Planner",
                placeholder="e.g. AI-Based Smart Traffic Management System",
            )
            p_desc = st.text_area(
                "Project Description / Problem Statement *",
                value="Develop an autonomous quadcopter routing and collision avoidance system using Python, computer vision obstacle detection, and embedded flight microcontrollers. Requires robust technical documentation and project presentation.",
                height=120,
            )
        with col2:
            p_domain = st.selectbox(
                "Domain",
                ["Artificial Intelligence", "Computer Vision & IoT", "Web & Cloud Systems", "Robotics & Systems", "Data Science & Analytics", "Cybersecurity"],
            )
            target_sz = st.slider("Target Team Size", 2, 8, 4)
            min_sz = max(2, target_sz - 1)
            max_sz = target_sz + 1

        st.subheader("2. AI Requirement Analyzer")
        st.caption("AI suggestions are advisory. Faculty retains full review and editing authority before saving.")

        if "suggested_reqs" not in st.session_state:
            st.session_state["suggested_reqs"] = []

        if st.button("🔍 Analyze Requirements with AI", type="secondary"):
            if len(p_title) < 3 or len(p_desc) < 10:
                st.error("Please provide a valid project title and description before analyzing.")
            else:
                analyzer = ProjectRequirementAnalyzer()
                with st.spinner("Analyzing project title and description..."):
                    reqs = analyzer.analyze(p_title, p_desc)
                    st.session_state["suggested_reqs"] = reqs
                st.success(f"Identified {len(reqs)} recommended skill requirements!")

        reqs_to_show = st.session_state.get("suggested_reqs", [])

        st.markdown("#### Review & Edit Skill Requirements")
        if not reqs_to_show:
            st.info("Click 'Analyze Requirements with AI' above, or add requirements manually below.")
        else:
            edited_reqs = []
            for idx, r in enumerate(reqs_to_show):
                r_col1, r_col2, r_col3, r_col4 = st.columns([2, 1, 1, 1])
                with r_col1:
                    sk_name = st.text_input(f"Skill #{idx+1}", value=r.skill_name, key=f"req_name_{idx}")
                with r_col2:
                    imp = st.slider(f"Importance (1-5)", 1, 5, r.importance_weight, key=f"req_imp_{idx}")
                with r_col3:
                    lvl = st.slider(f"Min Level (1-5)", 1, 5, r.required_level, key=f"req_lvl_{idx}")
                with r_col4:
                    mand = st.checkbox(f"Mandatory?", value=r.is_mandatory, key=f"req_mand_{idx}")

                cat = SKILL_TAXONOMY.get(sk_name, {}).get("category", SkillCategory.PROGRAMMING_LANGUAGE)
                edited_reqs.append(
                    ProjectRequirement(
                        skill_name=sk_name,
                        category=cat,
                        required_level=lvl,
                        importance_weight=imp,
                        is_mandatory=mand,
                    )
                )

        st.markdown("---")
        if st.button("💾 Create Project & Save Requirements", type="primary"):
            final_reqs = edited_reqs if reqs_to_show else [
                ProjectRequirement(skill_name="Python", category=SkillCategory.PROGRAMMING_LANGUAGE, required_level=3, importance_weight=4, is_mandatory=True),
                ProjectRequirement(skill_name="Technical Documentation", category=SkillCategory.SOFT_SKILL, required_level=2, importance_weight=2, is_mandatory=False),
            ]
            try:
                new_proj = ProjectCreate(
                    title=p_title,
                    description=p_desc,
                    domain=p_domain,
                    target_team_size=target_sz,
                    min_team_size=min_sz,
                    max_team_size=max_sz,
                    requirements=final_reqs,
                )
                saved_p = repo.create_project(new_proj)
                st.session_state["suggested_reqs"] = []
                st.success(f"Project '{saved_p.title}' successfully registered with {len(final_reqs)} requirements!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create project: {str(e)}")

    with tab_manage:
        projects = repo.get_all_projects()
        st.subheader(f"Active Projects ({len(projects)})")
        if not projects:
            st.info("No projects created yet.")
        else:
            for p in projects:
                with st.expander(f"📌 {p.title} (Domain: {p.domain}) — Target Size: {p.target_team_size}"):
                    st.write(p.description)
                    st.markdown("**Configured Requirements:**")
                    req_data = [
                        {
                            "Skill": r.skill_name,
                            "Category": r.category.value,
                            "Min Level (1-5)": r.required_level,
                            "Importance (1-5)": r.importance_weight,
                            "Mandatory": "Yes" if r.is_mandatory else "No",
                        }
                        for r in p.requirements
                    ]
                    st.dataframe(pd.DataFrame(req_data), use_container_width=True)
                    if st.button(f"🗑️ Delete Project #{p.id}", key=f"del_p_{p.id}"):
                        repo.delete_project(p.id)
                        st.success(f"Project #{p.id} deleted.")
                        st.rerun()
