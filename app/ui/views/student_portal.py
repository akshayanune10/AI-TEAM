"""
Student Portal View.
Profile creation, resume parsing with calibrated confidence estimates,
weekly availability matrix, work-style survey, and project preference ranking.
"""

from pathlib import Path
import streamlit as st
import pandas as pd

from app.data.repository import DataRepository
from app.models.student import (
    StudentCreate,
    StudentSkill,
    SkillCategory,
    SkillSource,
    TimeSlotAvailability,
    WorkStyle,
    StudentPreference,
)
from app.ai.resume_parser import ResumeParser
from app.ai.skill_taxonomy import SKILL_TAXONOMY
from app.config import (
    DAYS_OF_WEEK,
    TIME_SLOTS,
    ROLE_ORIENTATIONS,
    COLLABORATION_MODES,
    COMMUNICATION_PREFERENCES,
    UPLOAD_DIR,
)


def render_student_portal(repo: DataRepository):
    st.header("🎓 Student Profile & Skills Portal")
    st.markdown(
        "Students can provide technical skills, upload resumes for AI skill extraction, "
        "set collaboration availability, select work styles, and rank preferred projects."
    )

    tab_register, tab_directory = st.tabs(["📝 Register / Update Profile", "👥 Student Directory"])

    with tab_register:
        st.subheader("1. Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            roll_no = st.text_input("Roll No / Student ID *", value="CS2026-099")
            full_name = st.text_input("Full Name *", value="Alex Morgan")
            email = st.text_input("Institutional Email *", value="alex.morgan@college.edu")
        with col2:
            dept = st.selectbox("Department", ["Computer Science", "Information Technology", "AI & Data Science", "Electrical & Computer Engineering"])
            year = st.selectbox("Academic Year", ["Senior (4th Year)", "Junior (3rd Year)", "Graduate Student"])
            exp_level = st.slider("Overall Software Experience Level (1 = Beginner, 5 = Advanced Lead)", 1, 5, 3)

        st.subheader("2. AI Resume & Skill Extraction")
        st.caption("Upload a PDF, DOCX, or TXT resume. The system extracts skills with estimated confidence ratings for review.")

        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
        extracted_skills = []

        if uploaded_file is not None:
            parser = ResumeParser()
            try:
                file_bytes = uploaded_file.read()
                result = parser.parse_full_resume(file_bytes, uploaded_file.name)
                extracted_skills = result["skills"]

                # Save file to upload directory
                save_path = UPLOAD_DIR / f"{roll_no}_{uploaded_file.name}"
                with open(save_path, "wb") as f:
                    f.write(file_bytes)

                st.success(f"Resume parsed successfully! Extracted {len(extracted_skills)} candidate skills.")
                
                # Display extracted skills table
                if extracted_skills:
                    skill_rows = [
                        {
                            "Skill": s.name,
                            "Category": s.category.value,
                            "Est. Proficiency (1-5)": s.proficiency,
                            "Source": s.source.value,
                            "Est. Confidence": f"{int(s.confidence * 100)}%",
                        }
                        for s in extracted_skills
                    ]
                    st.dataframe(pd.DataFrame(skill_rows), use_container_width=True)
            except Exception as e:
                st.error(f"Error parsing resume: {str(e)}")

        st.markdown("#### Add or Refine Skills")
        all_canonical_skills = sorted(list(SKILL_TAXONOMY.keys()))
        selected_manual_skills = st.multiselect(
            "Select skills to add / adjust:",
            all_canonical_skills,
            default=[s.name for s in extracted_skills[:4]] if extracted_skills else ["Python", "SQL", "Technical Documentation"],
        )

        final_skills = []
        if selected_manual_skills:
            st.write("Adjust proficiency for selected skills:")
            skill_cols = st.columns(min(3, len(selected_manual_skills)))
            for idx, sk_name in enumerate(selected_manual_skills):
                col = skill_cols[idx % len(skill_cols)]
                with col:
                    # Find default proficiency from extracted or 3
                    def_prof = 3
                    for es in extracted_skills:
                        if es.name == sk_name:
                            def_prof = es.proficiency
                            break
                    prof = st.slider(f"{sk_name} Proficiency", 1, 5, def_prof, key=f"prof_{sk_name}")
                    tax_info = SKILL_TAXONOMY.get(sk_name, {})
                    cat = tax_info.get("category", SkillCategory.PROGRAMMING_LANGUAGE)
                    final_skills.append(
                        StudentSkill(
                            name=sk_name,
                            category=cat,
                            proficiency=prof,
                            source=SkillSource.RESUME_DERIVED if any(es.name == sk_name for es in extracted_skills) else SkillSource.SELF_REPORTED,
                            confidence=0.9 if any(es.name == sk_name for es in extracted_skills) else 0.8,
                        )
                    )

        st.subheader("3. Project Preferences")
        projects = repo.get_all_projects()
        if not projects:
            st.warning("No projects registered yet. Please add projects in the Project Studio.")
            preferences = []
        else:
            proj_options = {f"{p.id}: {p.title}": p.id for p in projects}
            st.caption("Rank your top project preferences (1 = Most preferred):")
            pref_col1, pref_col2, pref_col3 = st.columns(3)
            with pref_col1:
                p1_choice = st.selectbox("1st Choice Project", list(proj_options.keys()), index=0)
            with pref_col2:
                p2_choice = st.selectbox("2nd Choice Project", list(proj_options.keys()), index=min(1, len(projects) - 1))
            with pref_col3:
                p3_choice = st.selectbox("3rd Choice Project", list(proj_options.keys()), index=min(2, len(projects) - 1))

            preferences = [
                StudentPreference(project_id=proj_options[p1_choice], rank=1),
                StudentPreference(project_id=proj_options[p2_choice], rank=2),
                StudentPreference(project_id=proj_options[p3_choice], rank=3),
            ]

        st.subheader("4. Weekly Collaboration Availability")
        st.caption("Select the blocks where you are available for mutual teamwork:")
        availability_list = []
        
        # Grid display for availability
        days_cols = st.columns(7)
        for d_idx, day in enumerate(DAYS_OF_WEEK):
            with days_cols[d_idx]:
                st.markdown(f"**{day[:3]}**")
                for slot in TIME_SLOTS:
                    slot_label = slot.split()[0]
                    is_avail = st.checkbox(slot_label, value=(day in ["Monday", "Wednesday", "Friday"]), key=f"avail_{day}_{slot}")
                    availability_list.append(
                        TimeSlotAvailability(day=day, slot=slot, is_available=is_avail)
                    )

        st.subheader("5. Work-Style & Team Role Preferences")
        ws_col1, ws_col2 = st.columns(2)
        with ws_col1:
            primary_role = st.selectbox("Preferred Team Role", ROLE_ORIENTATIONS)
            collab_mode = st.selectbox("Preferred Collaboration Mode", COLLABORATION_MODES)
        with ws_col2:
            comm_pref = st.selectbox("Communication Style", COMMUNICATION_PREFERENCES)
            lead_inc = st.slider("Leadership Inclination (1 = Prefers Supporting, 5 = Eager to Lead)", 1, 5, 3)

        work_style = WorkStyle(
            primary_role=primary_role,
            collaboration_mode=collab_mode,
            communication_preference=comm_pref,
            leadership_inclination=lead_inc,
            planning_orientation=3,
        )

        st.markdown("---")
        if st.button("💾 Save Student Profile", type="primary"):
            try:
                new_student = StudentCreate(
                    student_id_str=roll_no,
                    name=full_name,
                    email=email,
                    department=dept,
                    academic_year=year,
                    experience_level=exp_level,
                    bio="Registered via web portal.",
                    skills=final_skills,
                    preferences=preferences,
                    availability=availability_list,
                    work_style=work_style,
                    resume_filename=uploaded_file.name if uploaded_file else None,
                )
                saved = repo.create_student(new_student)
                st.success(f"Student profile for {saved.name} ({saved.student_id_str}) successfully registered!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save student: {str(e)}")

    with tab_directory:
        students = repo.get_all_students()
        st.subheader(f"Registered Students ({len(students)})")
        if not students:
            st.info("No students registered yet. Click 'Load Realistic Demo Cohort' in the sidebar or register above.")
        else:
            data = []
            for s in students:
                skill_summary = ", ".join([f"{sk.name} ({sk.proficiency})" for sk in s.skills[:3]])
                data.append(
                    {
                        "ID": s.id,
                        "Roll No": s.student_id_str,
                        "Name": s.name,
                        "Role": s.work_style.primary_role,
                        "Exp": s.experience_level,
                        "Key Skills": skill_summary,
                        "Top Preference": f"Project #{s.preferences[0].project_id}" if s.preferences else "None",
                    }
                )
            st.dataframe(pd.DataFrame(data), use_container_width=True)
