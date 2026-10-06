"""
Realistic sample data generator for college student cohorts and multidisciplinary projects.
Provides 24 realistic students with resumes, varied skills, preferences, schedules,
and 6 diverse capstone projects.
"""

from typing import List
from app.models.student import (
    StudentCreate,
    StudentSkill,
    SkillCategory,
    SkillSource,
    TimeSlotAvailability,
    WorkStyle,
    StudentPreference,
)
from app.models.project import (
    ProjectCreate,
    ProjectRequirement,
)
from app.config import DAYS_OF_WEEK, TIME_SLOTS
from app.data.repository import DataRepository


def generate_sample_projects() -> List[ProjectCreate]:
    """Generates 6 multidisciplinary capstone projects."""
    return [
        ProjectCreate(
            title="AI-Based Smart Traffic Management System",
            description="Build an intelligent camera-based traffic signal optimizer that processes live CCTV video streams, predicts congestion bottlenecks, and controls light timing using reinforcement learning and IoT microcontrollers.",
            domain="Computer Vision & IoT",
            target_team_size=4,
            min_team_size=3,
            max_team_size=5,
            requirements=[
                ProjectRequirement(skill_name="Python", category=SkillCategory.PROGRAMMING_LANGUAGE, required_level=4, importance_weight=5, is_mandatory=True),
                ProjectRequirement(skill_name="Computer Vision", category=SkillCategory.AI_ML, required_level=3, importance_weight=5, is_mandatory=True),
                ProjectRequirement(skill_name="Machine Learning", category=SkillCategory.AI_ML, required_level=3, importance_weight=4, is_mandatory=False),
                ProjectRequirement(skill_name="IoT / Embedded Systems", category=SkillCategory.SYSTEMS_IOT, required_level=3, importance_weight=4, is_mandatory=False),
                ProjectRequirement(skill_name="PostgreSQL", category=SkillCategory.DATA_DATABASE, required_level=2, importance_weight=3, is_mandatory=False),
                ProjectRequirement(skill_name="Technical Documentation", category=SkillCategory.SOFT_SKILL, required_level=2, importance_weight=2, is_mandatory=False),
            ],
        ),
        ProjectCreate(
            title="Healthcare Patient Portal & Telemedicine Platform",
            description="Design and implement a HIPAA-compliant web portal enabling encrypted video consultations, real-time vital sign tracking, and electronic health record management for community clinics.",
            domain="Web & Cybersecurity",
            target_team_size=4,
            min_team_size=3,
            max_team_size=5,
            requirements=[
                ProjectRequirement(skill_name="React", category=SkillCategory.WEB_MOBILE, required_level=4, importance_weight=5, is_mandatory=True),
                ProjectRequirement(skill_name="FastAPI", category=SkillCategory.WEB_MOBILE, required_level=3, importance_weight=4, is_mandatory=True),
                ProjectRequirement(skill_name="PostgreSQL", category=SkillCategory.DATA_DATABASE, required_level=3, importance_weight=4, is_mandatory=False),
                ProjectRequirement(skill_name="Cybersecurity", category=SkillCategory.SYSTEMS_IOT, required_level=3, importance_weight=4, is_mandatory=False),
                ProjectRequirement(skill_name="Docker", category=SkillCategory.CLOUD_DEVOPS, required_level=2, importance_weight=3, is_mandatory=False),
                ProjectRequirement(skill_name="Presentation & Communication", category=SkillCategory.SOFT_SKILL, required_level=2, importance_weight=2, is_mandatory=False),
            ],
        ),
        ProjectCreate(
            title="Autonomous Campus Delivery Robot Navigation",
            description="Develop real-time sensor fusion, SLAM navigation, and obstacle avoidance algorithms for an autonomous ground delivery robot operating across university pedestrian paths.",
            domain="Robotics & Embedded Systems",
            target_team_size=4,
            min_team_size=3,
            max_team_size=5,
            requirements=[
                ProjectRequirement(skill_name="C++", category=SkillCategory.PROGRAMMING_LANGUAGE, required_level=4, importance_weight=5, is_mandatory=True),
                ProjectRequirement(skill_name="Computer Vision", category=SkillCategory.AI_ML, required_level=3, importance_weight=4, is_mandatory=True),
                ProjectRequirement(skill_name="IoT / Embedded Systems", category=SkillCategory.SYSTEMS_IOT, required_level=4, importance_weight=5, is_mandatory=True),
                ProjectRequirement(skill_name="Python", category=SkillCategory.PROGRAMMING_LANGUAGE, required_level=3, importance_weight=3, is_mandatory=False),
                ProjectRequirement(skill_name="Project Leadership", category=SkillCategory.SOFT_SKILL, required_level=3, importance_weight=3, is_mandatory=False),
            ],
        ),
        ProjectCreate(
            title="FinTech Fraud Detection & Streaming Analytics",
            description="Build a high-throughput streaming pipeline analyzing financial transaction graphs in real time to flag anomalous money transfers, credit card fraud, and synthetic identity rings.",
            domain="Data Engineering & ML",
            target_team_size=4,
            min_team_size=3,
            max_team_size=5,
            requirements=[
                ProjectRequirement(skill_name="Python", category=SkillCategory.PROGRAMMING_LANGUAGE, required_level=4, importance_weight=5, is_mandatory=True),
                ProjectRequirement(skill_name="Data Engineering", category=SkillCategory.DATA_DATABASE, required_level=4, importance_weight=5, is_mandatory=True),
                ProjectRequirement(skill_name="Machine Learning", category=SkillCategory.AI_ML, required_level=3, importance_weight=4, is_mandatory=False),
                ProjectRequirement(skill_name="SQL", category=SkillCategory.PROGRAMMING_LANGUAGE, required_level=3, importance_weight=4, is_mandatory=False),
                ProjectRequirement(skill_name="Redis", category=SkillCategory.DATA_DATABASE, required_level=2, importance_weight=3, is_mandatory=False),
                ProjectRequirement(skill_name="Technical Documentation", category=SkillCategory.SOFT_SKILL, required_level=2, importance_weight=2, is_mandatory=False),
            ],
        ),
        ProjectCreate(
            title="Collaborative Code Review & Mentorship Platform",
            description="Develop an automated developer tooling platform integrating Git webhooks, automated style/lint checks, code duplication detection, and interactive peer pairing rooms.",
            domain="Full-Stack & DevOps",
            target_team_size=4,
            min_team_size=3,
            max_team_size=5,
            requirements=[
                ProjectRequirement(skill_name="TypeScript", category=SkillCategory.PROGRAMMING_LANGUAGE, required_level=3, importance_weight=4, is_mandatory=True),
                ProjectRequirement(skill_name="React", category=SkillCategory.WEB_MOBILE, required_level=4, importance_weight=5, is_mandatory=True),
                ProjectRequirement(skill_name="Node.js", category=SkillCategory.WEB_MOBILE, required_level=3, importance_weight=4, is_mandatory=False),
                ProjectRequirement(skill_name="CI/CD", category=SkillCategory.CLOUD_DEVOPS, required_level=3, importance_weight=4, is_mandatory=False),
                ProjectRequirement(skill_name="Docker", category=SkillCategory.CLOUD_DEVOPS, required_level=3, importance_weight=3, is_mandatory=False),
            ],
        ),
        ProjectCreate(
            title="EcoTrack: Campus Energy & Carbon Footprint Monitor",
            description="Deploy networked ambient energy and temperature sensors across campus buildings, aggregating environmental telemetry into an interactive sustainability dashboard with automated HVAC recommendations.",
            domain="IoT & Data Analytics",
            target_team_size=4,
            min_team_size=3,
            max_team_size=5,
            requirements=[
                ProjectRequirement(skill_name="Python", category=SkillCategory.PROGRAMMING_LANGUAGE, required_level=3, importance_weight=4, is_mandatory=True),
                ProjectRequirement(skill_name="Data Analysis", category=SkillCategory.DATA_DATABASE, required_level=4, importance_weight=5, is_mandatory=True),
                ProjectRequirement(skill_name="IoT / Embedded Systems", category=SkillCategory.SYSTEMS_IOT, required_level=3, importance_weight=4, is_mandatory=False),
                ProjectRequirement(skill_name="PostgreSQL", category=SkillCategory.DATA_DATABASE, required_level=2, importance_weight=3, is_mandatory=False),
                ProjectRequirement(skill_name="Presentation & Communication", category=SkillCategory.SOFT_SKILL, required_level=3, importance_weight=3, is_mandatory=False),
            ],
        ),
    ]


def _build_schedule(available_days: List[str], available_slots: List[str]) -> List[TimeSlotAvailability]:
    schedule = []
    for day in DAYS_OF_WEEK:
        for slot in TIME_SLOTS:
            is_avail = (day in available_days) and (slot in available_slots)
            schedule.append(TimeSlotAvailability(day=day, slot=slot, is_available=is_avail))
    return schedule


def generate_sample_students(project_ids: List[int]) -> List[StudentCreate]:
    """Generates 24 realistic students with diverse skill profiles, schedules, and preferences."""
    p1, p2, p3, p4, p5, p6 = project_ids[:6]

    students_raw = [
        # Student 1 - Strong ML/CV Lead
        {
            "id_str": "CS2026-001",
            "name": "Aarav Sharma",
            "email": "aarav.sharma@college.edu",
            "gpa": 3.88,
            "exp": 4,
            "bio": "Passionate about computer vision, deep learning models, and real-time inference.",
            "skills": [
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("Computer Vision", SkillCategory.AI_ML, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("Machine Learning", SkillCategory.AI_ML, 4, SkillSource.RESUME_DERIVED, 0.92),
                ("PyTorch", SkillCategory.AI_ML, 4, SkillSource.SELF_REPORTED, 0.85),
                ("Project Leadership", SkillCategory.SOFT_SKILL, 4, SkillSource.SELF_REPORTED, 0.80),
            ],
            "prefs": [(p1, 1), (p3, 2), (p4, 3)],
            "days": ["Monday", "Wednesday", "Friday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Late Afternoon (15:00 - 18:00)"],
            "role": "Technical Lead / Architect",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 4,
            "plan": 4,
        },
        # Student 2 - Embedded / IoT Specialist
        {
            "id_str": "CS2026-002",
            "name": "Bhavna Patel",
            "email": "bhavna.patel@college.edu",
            "gpa": 3.72,
            "exp": 4,
            "bio": "Hardware enthusiast, Arduino & Raspberry Pi developer with C++ experience.",
            "skills": [
                ("C++", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("IoT / Embedded Systems", SkillCategory.SYSTEMS_IOT, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.75),
                ("Technical Documentation", SkillCategory.SOFT_SKILL, 3, SkillSource.SELF_REPORTED, 0.80),
            ],
            "prefs": [(p1, 1), (p3, 2), (p6, 3)],
            "days": ["Monday", "Wednesday", "Friday", "Saturday"],
            "slots": ["Late Afternoon (15:00 - 18:00)", "Evening (18:00 - 21:00)"],
            "role": "Core Developer / Implementer",
            "collab": "Highly Collaborative (Pair/Mob programming)",
            "comm": "Synchronous Meetings (Video/In-person)",
            "lead": 2,
            "plan": 3,
        },
        # Student 3 - Database & Backend
        {
            "id_str": "CS2026-003",
            "name": "Chetan Verma",
            "email": "chetan.verma@college.edu",
            "gpa": 3.45,
            "exp": 3,
            "bio": "Backend engineer experienced in PostgreSQL, relational schema design, and Docker.",
            "skills": [
                ("SQL", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("PostgreSQL", SkillCategory.DATA_DATABASE, 4, SkillSource.RESUME_DERIVED, 0.85),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.70),
                ("Docker", SkillCategory.CLOUD_DEVOPS, 3, SkillSource.SELF_REPORTED, 0.75),
            ],
            "prefs": [(p1, 1), (p4, 2), (p2, 3)],
            "days": ["Monday", "Wednesday", "Thursday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Late Afternoon (15:00 - 18:00)"],
            "role": "Core Developer / Implementer",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Written / Asynchronous (Slack/Discord/Docs)",
            "lead": 2,
            "plan": 4,
        },
        # Student 4 - Communicator & Documentation
        {
            "id_str": "CS2026-004",
            "name": "Divya Rao",
            "email": "divya.rao@college.edu",
            "gpa": 3.65,
            "exp": 3,
            "bio": "Proficient in Python scripting, API testing, technical writing, and team presentations.",
            "skills": [
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.80),
                ("Technical Documentation", SkillCategory.SOFT_SKILL, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("Presentation & Communication", SkillCategory.SOFT_SKILL, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("Data Analysis", SkillCategory.DATA_DATABASE, 3, SkillSource.SELF_REPORTED, 0.70),
            ],
            "prefs": [(p1, 1), (p2, 2), (p6, 3)],
            "days": ["Monday", "Wednesday", "Friday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Late Afternoon (15:00 - 18:00)"],
            "role": "QA & Documentation Specialist",
            "collab": "Highly Collaborative (Pair/Mob programming)",
            "comm": "Synchronous Meetings (Video/In-person)",
            "lead": 3,
            "plan": 5,
        },

        # Student 5 - React Frontend Wizard
        {
            "id_str": "CS2026-005",
            "name": "Eshan Mukherjee",
            "email": "eshan.m@college.edu",
            "gpa": 3.80,
            "exp": 4,
            "bio": "Frontend developer specializing in React, Next.js, state management, and modern CSS.",
            "skills": [
                ("JavaScript", SkillCategory.PROGRAMMING_LANGUAGE, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("TypeScript", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("React", SkillCategory.WEB_MOBILE, 5, SkillSource.RESUME_DERIVED, 0.96),
                ("UI/UX Design", SkillCategory.WEB_MOBILE, 4, SkillSource.SELF_REPORTED, 0.85),
            ],
            "prefs": [(p2, 1), (p5, 2), (p1, 3)],
            "days": ["Tuesday", "Thursday", "Saturday"],
            "slots": ["Morning (09:00 - 12:00)", "Afternoon (12:00 - 15:00)"],
            "role": "UI/UX & Frontend Developer",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 3,
            "plan": 3,
        },
        # Student 6 - FastAPI & Cloud Security
        {
            "id_str": "CS2026-006",
            "name": "Farhan Qureshi",
            "email": "farhan.q@college.edu",
            "gpa": 3.75,
            "exp": 4,
            "bio": "Building high-performance REST APIs with FastAPI, OAuth2, and secure infrastructure.",
            "skills": [
                ("FastAPI", SkillCategory.WEB_MOBILE, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("Cybersecurity", SkillCategory.SYSTEMS_IOT, 4, SkillSource.RESUME_DERIVED, 0.85),
                ("Docker", SkillCategory.CLOUD_DEVOPS, 3, SkillSource.SELF_REPORTED, 0.80),
            ],
            "prefs": [(p2, 1), (p5, 2), (p4, 3)],
            "days": ["Tuesday", "Thursday", "Saturday"],
            "slots": ["Morning (09:00 - 12:00)", "Afternoon (12:00 - 15:00)"],
            "role": "Technical Lead / Architect",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 4,
            "plan": 4,
        },
        # Student 7 - Relational Database & QA
        {
            "id_str": "CS2026-007",
            "name": "Geeta Nair",
            "email": "geeta.nair@college.edu",
            "gpa": 3.50,
            "exp": 3,
            "bio": "Focus on database optimization, schema integrity, and automated regression testing.",
            "skills": [
                ("PostgreSQL", SkillCategory.DATA_DATABASE, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("SQL", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.85),
                ("Presentation & Communication", SkillCategory.SOFT_SKILL, 3, SkillSource.SELF_REPORTED, 0.75),
            ],
            "prefs": [(p2, 1), (p4, 2), (p6, 3)],
            "days": ["Tuesday", "Thursday", "Saturday"],
            "slots": ["Morning (09:00 - 12:00)", "Afternoon (12:00 - 15:00)"],
            "role": "QA & Documentation Specialist",
            "collab": "Highly Collaborative (Pair/Mob programming)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 2,
            "plan": 4,
        },
        # Student 8 - Fullstack Junior
        {
            "id_str": "CS2026-008",
            "name": "Harish Iyer",
            "email": "harish.iyer@college.edu",
            "gpa": 3.30,
            "exp": 2,
            "bio": "Eager learner with basics in JavaScript, Python, and frontend components.",
            "skills": [
                ("JavaScript", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.70),
                ("React", SkillCategory.WEB_MOBILE, 3, SkillSource.RESUME_DERIVED, 0.75),
                ("Docker", SkillCategory.CLOUD_DEVOPS, 2, SkillSource.SELF_REPORTED, 0.60),
            ],
            "prefs": [(p2, 1), (p5, 2), (p1, 3)],
            "days": ["Tuesday", "Thursday", "Saturday"],
            "slots": ["Morning (09:00 - 12:00)", "Afternoon (12:00 - 15:00)"],
            "role": "Core Developer / Implementer",
            "collab": "Highly Collaborative (Pair/Mob programming)",
            "comm": "Synchronous Meetings (Video/In-person)",
            "lead": 2,
            "plan": 3,
        },

        # Student 9 - C++ & Robotics Architect
        {
            "id_str": "CS2026-009",
            "name": "Ishaan Gupta",
            "email": "ishaan.g@college.edu",
            "gpa": 3.92,
            "exp": 5,
            "bio": "Experienced C++ systems programmer, ROS2, point-cloud processing, and robotics lead.",
            "skills": [
                ("C++", SkillCategory.PROGRAMMING_LANGUAGE, 5, SkillSource.RESUME_DERIVED, 0.98),
                ("Computer Vision", SkillCategory.AI_ML, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("IoT / Embedded Systems", SkillCategory.SYSTEMS_IOT, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("Project Leadership", SkillCategory.SOFT_SKILL, 5, SkillSource.RESUME_DERIVED, 0.92),
            ],
            "prefs": [(p3, 1), (p1, 2), (p4, 3)],
            "days": ["Monday", "Tuesday", "Thursday"],
            "slots": ["Late Afternoon (15:00 - 18:00)", "Evening (18:00 - 21:00)"],
            "role": "Technical Lead / Architect",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Synchronous Meetings (Video/In-person)",
            "lead": 5,
            "plan": 5,
        },
        # Student 10 - Embedded Systems & Sensors
        {
            "id_str": "CS2026-010",
            "name": "Janani Rangarajan",
            "email": "janani.r@college.edu",
            "gpa": 3.68,
            "exp": 3,
            "bio": "Sensor calibration, microcontroller firmware, and embedded driver development.",
            "skills": [
                ("IoT / Embedded Systems", SkillCategory.SYSTEMS_IOT, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("C++", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.RESUME_DERIVED, 0.82),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.75),
            ],
            "prefs": [(p3, 1), (p6, 2), (p1, 3)],
            "days": ["Monday", "Tuesday", "Thursday"],
            "slots": ["Late Afternoon (15:00 - 18:00)", "Evening (18:00 - 21:00)"],
            "role": "Core Developer / Implementer",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 2,
            "plan": 4,
        },
        # Student 11 - Deep Learning & Vision
        {
            "id_str": "CS2026-011",
            "name": "Karan Malhotra",
            "email": "karan.m@college.edu",
            "gpa": 3.70,
            "exp": 3,
            "bio": "YOLO object detection, OpenCV pipelines, and edge-device deep learning deployment.",
            "skills": [
                ("Computer Vision", SkillCategory.AI_ML, 4, SkillSource.RESUME_DERIVED, 0.89),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.85),
                ("Deep Learning", SkillCategory.AI_ML, 4, SkillSource.SELF_REPORTED, 0.80),
            ],
            "prefs": [(p3, 1), (p1, 2), (p4, 3)],
            "days": ["Monday", "Tuesday", "Thursday"],
            "slots": ["Late Afternoon (15:00 - 18:00)", "Evening (18:00 - 21:00)"],
            "role": "Data & ML Specialist",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Written / Asynchronous (Slack/Discord/Docs)",
            "lead": 3,
            "plan": 3,
        },
        # Student 12 - Documentation & Test Pilot
        {
            "id_str": "CS2026-012",
            "name": "Lavanya Joshi",
            "email": "lavanya.j@college.edu",
            "gpa": 3.40,
            "exp": 2,
            "bio": "Testing protocol creation, field testing, data collection, and project documentation.",
            "skills": [
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.70),
                ("Technical Documentation", SkillCategory.SOFT_SKILL, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("Presentation & Communication", SkillCategory.SOFT_SKILL, 4, SkillSource.RESUME_DERIVED, 0.90),
            ],
            "prefs": [(p3, 1), (p6, 2), (p2, 3)],
            "days": ["Monday", "Tuesday", "Thursday"],
            "slots": ["Late Afternoon (15:00 - 18:00)", "Evening (18:00 - 21:00)"],
            "role": "QA & Documentation Specialist",
            "collab": "Highly Collaborative (Pair/Mob programming)",
            "comm": "Synchronous Meetings (Video/In-person)",
            "lead": 2,
            "plan": 4,
        },

        # Student 13 - Big Data & Streaming Pipeline
        {
            "id_str": "CS2026-013",
            "name": "Manish Kulkarni",
            "email": "manish.k@college.edu",
            "gpa": 3.85,
            "exp": 4,
            "bio": "Kafka, Spark, and real-time streaming architectures with heavy Python & SQL.",
            "skills": [
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("Data Engineering", SkillCategory.DATA_DATABASE, 5, SkillSource.RESUME_DERIVED, 0.94),
                ("SQL", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("Redis", SkillCategory.DATA_DATABASE, 4, SkillSource.RESUME_DERIVED, 0.85),
            ],
            "prefs": [(p4, 1), (p1, 2), (p6, 3)],
            "days": ["Wednesday", "Friday", "Sunday"],
            "slots": ["Morning (09:00 - 12:00)", "Afternoon (12:00 - 15:00)"],
            "role": "Technical Lead / Architect",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 4,
            "plan": 4,
        },
        # Student 14 - Machine Learning Modeler
        {
            "id_str": "CS2026-014",
            "name": "Neha Singhal",
            "email": "neha.s@college.edu",
            "gpa": 3.78,
            "exp": 4,
            "bio": "Anomaly detection, XGBoost, feature store creation, and model monitoring.",
            "skills": [
                ("Machine Learning", SkillCategory.AI_ML, 4, SkillSource.RESUME_DERIVED, 0.92),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("Data Analysis", SkillCategory.DATA_DATABASE, 4, SkillSource.RESUME_DERIVED, 0.85),
                ("Technical Documentation", SkillCategory.SOFT_SKILL, 3, SkillSource.SELF_REPORTED, 0.75),
            ],
            "prefs": [(p4, 1), (p1, 2), (p6, 3)],
            "days": ["Wednesday", "Friday", "Sunday"],
            "slots": ["Morning (09:00 - 12:00)", "Afternoon (12:00 - 15:00)"],
            "role": "Data & ML Specialist",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 3,
            "plan": 4,
        },
        # Student 15 - SQL & Cache Engineer
        {
            "id_str": "CS2026-015",
            "name": "Omkar Deshmukh",
            "email": "omkar.d@college.edu",
            "gpa": 3.52,
            "exp": 3,
            "bio": "Relational query optimization, Redis caching patterns, and database replication.",
            "skills": [
                ("SQL", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("Redis", SkillCategory.DATA_DATABASE, 4, SkillSource.RESUME_DERIVED, 0.86),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.75),
            ],
            "prefs": [(p4, 1), (p2, 2), (p5, 3)],
            "days": ["Wednesday", "Friday", "Sunday"],
            "slots": ["Morning (09:00 - 12:00)", "Afternoon (12:00 - 15:00)"],
            "role": "Core Developer / Implementer",
            "collab": "Asynchronous / Autonomous (Milestone-based syncs)",
            "comm": "Written / Asynchronous (Slack/Discord/Docs)",
            "lead": 2,
            "plan": 3,
        },
        # Student 16 - Technical Writer & Coordinator
        {
            "id_str": "CS2026-016",
            "name": "Pooja Hegde",
            "email": "pooja.h@college.edu",
            "gpa": 3.60,
            "exp": 3,
            "bio": "Technical documentation, agile sprint tracking, presentation visuals, and data reports.",
            "skills": [
                ("Technical Documentation", SkillCategory.SOFT_SKILL, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("Presentation & Communication", SkillCategory.SOFT_SKILL, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("Data Analysis", SkillCategory.DATA_DATABASE, 3, SkillSource.SELF_REPORTED, 0.70),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 2, SkillSource.SELF_REPORTED, 0.60),
            ],
            "prefs": [(p4, 1), (p2, 2), (p6, 3)],
            "days": ["Wednesday", "Friday", "Sunday"],
            "slots": ["Morning (09:00 - 12:00)", "Afternoon (12:00 - 15:00)"],
            "role": "Project Manager / Coordinator",
            "collab": "Highly Collaborative (Pair/Mob programming)",
            "comm": "Synchronous Meetings (Video/In-person)",
            "lead": 4,
            "plan": 5,
        },

        # Student 17 - Fullstack TypeScript Lead
        {
            "id_str": "CS2026-017",
            "name": "Quentin D'Souza",
            "email": "quentin.d@college.edu",
            "gpa": 3.90,
            "exp": 5,
            "bio": "TypeScript, React, Node.js microservices, and Dockerized deployment workflows.",
            "skills": [
                ("TypeScript", SkillCategory.PROGRAMMING_LANGUAGE, 5, SkillSource.RESUME_DERIVED, 0.96),
                ("React", SkillCategory.WEB_MOBILE, 4, SkillSource.RESUME_DERIVED, 0.92),
                ("Node.js", SkillCategory.WEB_MOBILE, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("CI/CD", SkillCategory.CLOUD_DEVOPS, 4, SkillSource.SELF_REPORTED, 0.85),
                ("Project Leadership", SkillCategory.SOFT_SKILL, 4, SkillSource.SELF_REPORTED, 0.85),
            ],
            "prefs": [(p5, 1), (p2, 2), (p3, 3)],
            "days": ["Monday", "Thursday", "Friday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Evening (18:00 - 21:00)"],
            "role": "Technical Lead / Architect",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 4,
            "plan": 4,
        },
        # Student 18 - DevOps & Docker Specialist
        {
            "id_str": "CS2026-018",
            "name": "Rohan Bhatia",
            "email": "rohan.b@college.edu",
            "gpa": 3.65,
            "exp": 4,
            "bio": "DevOps enthusiast: GitHub Actions, Docker multi-stage builds, and cloud automation.",
            "skills": [
                ("Docker", SkillCategory.CLOUD_DEVOPS, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("CI/CD", SkillCategory.CLOUD_DEVOPS, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("Node.js", SkillCategory.WEB_MOBILE, 3, SkillSource.RESUME_DERIVED, 0.80),
                ("TypeScript", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.75),
            ],
            "prefs": [(p5, 1), (p2, 2), (p4, 3)],
            "days": ["Monday", "Thursday", "Friday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Evening (18:00 - 21:00)"],
            "role": "Core Developer / Implementer",
            "collab": "Asynchronous / Autonomous (Milestone-based syncs)",
            "comm": "Written / Asynchronous (Slack/Discord/Docs)",
            "lead": 2,
            "plan": 4,
        },
        # Student 19 - React & Frontend UI
        {
            "id_str": "CS2026-019",
            "name": "Sneha Ghosh",
            "email": "sneha.g@college.edu",
            "gpa": 3.70,
            "exp": 3,
            "bio": "Modern web interfaces, component libraries, Storybook, and responsive layouts.",
            "skills": [
                ("React", SkillCategory.WEB_MOBILE, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("JavaScript", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("TypeScript", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.75),
                ("UI/UX Design", SkillCategory.WEB_MOBILE, 4, SkillSource.RESUME_DERIVED, 0.85),
            ],
            "prefs": [(p5, 1), (p2, 2), (p6, 3)],
            "days": ["Monday", "Thursday", "Friday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Evening (18:00 - 21:00)"],
            "role": "UI/UX & Frontend Developer",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 3,
            "plan": 3,
        },
        # Student 20 - Backend Support & QA
        {
            "id_str": "CS2026-020",
            "name": "Tarun Kapoor",
            "email": "tarun.k@college.edu",
            "gpa": 3.35,
            "exp": 2,
            "bio": "REST API development, unit testing with Jest, and technical documentation.",
            "skills": [
                ("Node.js", SkillCategory.WEB_MOBILE, 3, SkillSource.RESUME_DERIVED, 0.78),
                ("JavaScript", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.70),
                ("Technical Documentation", SkillCategory.SOFT_SKILL, 3, SkillSource.SELF_REPORTED, 0.75),
            ],
            "prefs": [(p5, 1), (p2, 2), (p1, 3)],
            "days": ["Monday", "Thursday", "Friday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Evening (18:00 - 21:00)"],
            "role": "QA & Documentation Specialist",
            "collab": "Highly Collaborative (Pair/Mob programming)",
            "comm": "Synchronous Meetings (Video/In-person)",
            "lead": 2,
            "plan": 3,
        },

        # Student 21 - Environmental Data Lead
        {
            "id_str": "CS2026-021",
            "name": "Urvashi Sen",
            "email": "urvashi.s@college.edu",
            "gpa": 3.82,
            "exp": 4,
            "bio": "Data analysis in Python, statistical modeling, time-series forecasting, and sustainability.",
            "skills": [
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 4, SkillSource.RESUME_DERIVED, 0.92),
                ("Data Analysis", SkillCategory.DATA_DATABASE, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("Project Leadership", SkillCategory.SOFT_SKILL, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("PostgreSQL", SkillCategory.DATA_DATABASE, 3, SkillSource.SELF_REPORTED, 0.75),
            ],
            "prefs": [(p6, 1), (p4, 2), (p1, 3)],
            "days": ["Tuesday", "Thursday", "Sunday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Late Afternoon (15:00 - 18:00)"],
            "role": "Technical Lead / Architect",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 4,
            "plan": 5,
        },
        # Student 22 - IoT & Microcontroller Engineer
        {
            "id_str": "CS2026-022",
            "name": "Varun Reddy",
            "email": "varun.r@college.edu",
            "gpa": 3.62,
            "exp": 3,
            "bio": "ESP32, MQTT protocols, environmental sensors, and low-power telemetry transmission.",
            "skills": [
                ("IoT / Embedded Systems", SkillCategory.SYSTEMS_IOT, 4, SkillSource.RESUME_DERIVED, 0.90),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.78),
                ("C++", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.72),
            ],
            "prefs": [(p6, 1), (p1, 2), (p3, 3)],
            "days": ["Tuesday", "Thursday", "Sunday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Late Afternoon (15:00 - 18:00)"],
            "role": "Core Developer / Implementer",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Hybrid (Short standups + chat)",
            "lead": 2,
            "plan": 3,
        },
        # Student 23 - Database & Analytics Visualizer
        {
            "id_str": "CS2026-023",
            "name": "Wendy D'Almeida",
            "email": "wendy.d@college.edu",
            "gpa": 3.55,
            "exp": 3,
            "bio": "PostgreSQL time-series tables, Plotly dashboards, and data visualization.",
            "skills": [
                ("PostgreSQL", SkillCategory.DATA_DATABASE, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("Data Analysis", SkillCategory.DATA_DATABASE, 4, SkillSource.RESUME_DERIVED, 0.85),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 3, SkillSource.SELF_REPORTED, 0.75),
            ],
            "prefs": [(p6, 1), (p4, 2), (p2, 3)],
            "days": ["Tuesday", "Thursday", "Sunday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Late Afternoon (15:00 - 18:00)"],
            "role": "Data & ML Specialist",
            "collab": "Balanced (Independent tasks + frequent check-ins)",
            "comm": "Written / Asynchronous (Slack/Discord/Docs)",
            "lead": 2,
            "plan": 4,
        },
        # Student 24 - Presentation & Outreach Specialist
        {
            "id_str": "CS2026-024",
            "name": "Yashwant Sinha",
            "email": "yashwant.s@college.edu",
            "gpa": 3.48,
            "exp": 2,
            "bio": "Project presentations, campus sustainability stakeholder interviews, and technical reports.",
            "skills": [
                ("Presentation & Communication", SkillCategory.SOFT_SKILL, 5, SkillSource.RESUME_DERIVED, 0.95),
                ("Technical Documentation", SkillCategory.SOFT_SKILL, 4, SkillSource.RESUME_DERIVED, 0.88),
                ("Data Analysis", SkillCategory.DATA_DATABASE, 2, SkillSource.SELF_REPORTED, 0.65),
                ("Python", SkillCategory.PROGRAMMING_LANGUAGE, 2, SkillSource.SELF_REPORTED, 0.60),
            ],
            "prefs": [(p6, 1), (p1, 2), (p2, 3)],
            "days": ["Tuesday", "Thursday", "Sunday"],
            "slots": ["Afternoon (12:00 - 15:00)", "Late Afternoon (15:00 - 18:00)"],
            "role": "Project Manager / Coordinator",
            "collab": "Highly Collaborative (Pair/Mob programming)",
            "comm": "Synchronous Meetings (Video/In-person)",
            "lead": 3,
            "plan": 4,
        },
    ]

    students: List[StudentCreate] = []
    for s in students_raw:
        skills_obj = [
            StudentSkill(
                name=sk[0],
                category=sk[1],
                proficiency=sk[2],
                source=sk[3],
                confidence=sk[4],
            )
            for sk in s["skills"]
        ]
        prefs_obj = [StudentPreference(project_id=pr[0], rank=pr[1]) for pr in s["prefs"]]
        avail_obj = _build_schedule(s["days"], s["slots"])
        ws_obj = WorkStyle(
            primary_role=s["role"],
            collaboration_mode=s["collab"],
            communication_preference=s["comm"],
            leadership_inclination=s["lead"],
            planning_orientation=s["plan"],
        )

        students.append(
            StudentCreate(
                student_id_str=s["id_str"],
                name=s["name"],
                email=s["email"],
                department="Computer Science & Engineering",
                academic_year="Senior (4th Year)",
                experience_level=s["exp"],
                gpa=s["gpa"],
                bio=s["bio"],
                skills=skills_obj,
                preferences=prefs_obj,
                availability=avail_obj,
                work_style=ws_obj,
                resume_filename=f"{s['id_str']}_resume.pdf",
            )
        )

    return students


def seed_database(repo: DataRepository) -> None:
    """Seeds the database with 6 projects and 24 students."""
    # Check if already seeded
    existing_projects = repo.get_all_projects()
    if existing_projects:
        return

    # Seed projects
    created_projects = []
    for p_in in generate_sample_projects():
        created_p = repo.create_project(p_in)
        created_projects.append(created_p)

    project_ids = [p.id for p in created_projects]

    # Seed students
    sample_students = generate_sample_students(project_ids)
    for s_in in sample_students:
        repo.create_student(s_in)
