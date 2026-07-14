"""
config.py - Central configuration for Smart Campus AI.

Loads environment variables, defines theme constants, and
provides shared settings used across the entire application.
"""

import os
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env file
# ---------------------------------------------------------------------------
load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Google Gemini
# ---------------------------------------------------------------------------
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_NAME: str = "Smart Campus AI"
APP_VERSION: str = "1.0.0"
APP_ICON: str = "🎓"

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR: str = os.path.join(BASE_DIR, "database")
ASSETS_DIR: str = os.path.join(BASE_DIR, "assets")
PAGES_DIR: str = os.path.join(BASE_DIR, "pages")

DB_USERS: str = os.path.join(DATABASE_DIR, "users.json")
DB_CHAT: str = os.path.join(DATABASE_DIR, "chat_history.json")
DB_ANNOUNCEMENTS: str = os.path.join(DATABASE_DIR, "announcements.json")
DB_ATTENDANCE: str = os.path.join(DATABASE_DIR, "attendance.json")
DB_TIMETABLE: str = os.path.join(DATABASE_DIR, "timetable.json")
DB_ASSIGNMENTS: str = os.path.join(DATABASE_DIR, "assignments.json")

# ---------------------------------------------------------------------------
# Theme colours
# ---------------------------------------------------------------------------
COLOR_PRIMARY: str = "#2563EB"
COLOR_SECONDARY: str = "#0EA5E9"
COLOR_SUCCESS: str = "#10B981"
COLOR_WARNING: str = "#F59E0B"
COLOR_DANGER: str = "#EF4444"
COLOR_BACKGROUND: str = "#F8FAFC"
COLOR_DARK_BG: str = "#0F172A"
COLOR_CARD: str = "rgba(255,255,255,0.08)"

# ---------------------------------------------------------------------------
# Session keys
# ---------------------------------------------------------------------------
SESSION_USER: str = "current_user"
SESSION_LOGGED_IN: str = "logged_in"
SESSION_THEME: str = "theme"
SESSION_PAGE: str = "current_page"

# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------
DEPARTMENTS: list[str] = [
    "Computer Science & Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Electronics & Communication",
    "Information Technology",
    "Biotechnology",
    "Chemical Engineering",
    "Aerospace Engineering",
    "Data Science & AI",
]

# ---------------------------------------------------------------------------
# Navigation pages
# ---------------------------------------------------------------------------
NAV_PAGES: list[dict] = [
    {"icon": "🏠", "label": "Dashboard",     "key": "dashboard"},
    {"icon": "👤", "label": "Profile",       "key": "profile"},
    {"icon": "📅", "label": "Attendance",    "key": "attendance"},
    {"icon": "📝", "label": "Assignments",   "key": "assignments"},
    {"icon": "📢", "label": "Announcements", "key": "announcements"},
    {"icon": "🗓️", "label": "Timetable",    "key": "timetable"},
    {"icon": "🤖", "label": "AI Assistant",  "key": "chatbot"},
    {"icon": "⚙️", "label": "Settings",     "key": "settings"},
]
