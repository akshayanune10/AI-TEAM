"""
Application configuration and global constants.
"""

from pathlib import Path
import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DATABASE_PATH = DATA_DIR / "team_formation.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Default Scoring Weights (Configurable by Faculty, must sum to 1.0)
DEFAULT_WEIGHTS: Dict[str, float] = {
    "skill_coverage": float(os.getenv("WEIGHT_SKILL_COVERAGE", 0.30)),
    "skill_complementarity": float(os.getenv("WEIGHT_SKILL_COMPLEMENTARITY", 0.20)),
    "project_preference": float(os.getenv("WEIGHT_PROJECT_PREFERENCE", 0.15)),
    "availability": float(os.getenv("WEIGHT_AVAILABILITY", 0.15)),
    "work_style": float(os.getenv("WEIGHT_WORK_STYLE", 0.10)),
    "experience_balance": float(os.getenv("WEIGHT_EXPERIENCE_BALANCE", 0.10)),
}

# Standard Weekly Schedule Blocks
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIME_SLOTS = [
    "Morning (09:00 - 12:00)",
    "Afternoon (12:00 - 15:00)",
    "Late Afternoon (15:00 - 18:00)",
    "Evening (18:00 - 21:00)",
]

# Team Roles & Work-Style Dimensions
ROLE_ORIENTATIONS = [
    "Technical Lead / Architect",
    "Core Developer / Implementer",
    "Data & ML Specialist",
    "UI/UX & Frontend Developer",
    "Project Manager / Coordinator",
    "QA & Documentation Specialist",
]

COLLABORATION_MODES = [
    "Highly Collaborative (Pair/Mob programming)",
    "Balanced (Independent tasks + frequent check-ins)",
    "Asynchronous / Autonomous (Milestone-based syncs)",
]

COMMUNICATION_PREFERENCES = [
    "Synchronous Meetings (Video/In-person)",
    "Hybrid (Short standups + chat)",
    "Written / Asynchronous (Slack/Discord/Docs)",
]
