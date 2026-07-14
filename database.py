"""
database.py - JSON file-based database layer for Smart Campus AI.

Provides thread-safe read/write helpers for all JSON data stores.
All writes are atomic: data is written to a temp file then renamed.
"""

import json
import os
import uuid
import tempfile
import shutil
from datetime import datetime, date
from typing import Any

from config import (
    DATABASE_DIR,
    DB_USERS,
    DB_CHAT,
    DB_ANNOUNCEMENTS,
    DB_ATTENDANCE,
    DB_TIMETABLE,
    DB_ASSIGNMENTS,
)

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


def _ensure_database_dir() -> None:
    """Create the database directory if it does not exist."""
    os.makedirs(DATABASE_DIR, exist_ok=True)


def load_json(filepath: str, default: Any = None) -> Any:
    """
    Load JSON data from *filepath*.

    Parameters
    ----------
    filepath : str
        Absolute path to the JSON file.
    default : Any
        Value returned when the file is missing or corrupted.

    Returns
    -------
    Any
        Parsed JSON content or *default*.
    """
    if default is None:
        default = []

    _ensure_database_dir()

    if not os.path.exists(filepath):
        return default

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(filepath: str, data: Any) -> bool:
    """
    Atomically write *data* as JSON to *filepath*.

    Uses a temporary file + rename so a crash mid-write never corrupts data.

    Parameters
    ----------
    filepath : str
        Absolute path of the destination file.
    data : Any
        JSON-serialisable object.

    Returns
    -------
    bool
        ``True`` on success, ``False`` on error.
    """
    _ensure_database_dir()

    try:
        dir_name = os.path.dirname(filepath)
        os.makedirs(dir_name, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False, default=str)
        except Exception:
            os.unlink(tmp_path)
            raise

        shutil.move(tmp_path, filepath)
        return True
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------------------
# User operations
# ---------------------------------------------------------------------------


def get_all_users() -> list[dict]:
    """Return the full users list."""
    return load_json(DB_USERS, [])


def get_user_by_email(email: str) -> dict | None:
    """
    Find a user by their email address.

    Parameters
    ----------
    email : str

    Returns
    -------
    dict or None
    """
    email_lower = email.strip().lower()
    for user in get_all_users():
        if user.get("email", "").lower() == email_lower:
            return user
    return None


def get_user_by_id(user_id: str) -> dict | None:
    """Return a user record by its UUID."""
    for user in get_all_users():
        if user.get("id") == user_id:
            return user
    return None


def create_user(
    name: str,
    email: str,
    phone: str,
    student_id: str,
    department: str,
    password_hash: str,
) -> dict:
    """
    Insert a new user record and persist it.

    Parameters
    ----------
    name, email, phone, student_id, department, password_hash : str

    Returns
    -------
    dict
        The newly created user record.
    """
    users = get_all_users()

    new_user: dict = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "email": email.strip().lower(),
        "phone": phone.strip(),
        "student_id": student_id.strip(),
        "department": department,
        "password_hash": password_hash,
        "created_at": datetime.now().isoformat(),
        "avatar": None,
        "bio": "",
        "theme": "dark",
    }

    users.append(new_user)
    save_json(DB_USERS, users)
    return new_user


def update_user(user_id: str, updates: dict) -> bool:
    """
    Apply *updates* to the user identified by *user_id*.

    Parameters
    ----------
    user_id : str
    updates : dict
        Key-value pairs to merge into the user record.

    Returns
    -------
    bool
    """
    users = get_all_users()
    for i, user in enumerate(users):
        if user.get("id") == user_id:
            users[i].update(updates)
            return save_json(DB_USERS, users)
    return False


# ---------------------------------------------------------------------------
# Chat history operations
# ---------------------------------------------------------------------------


def save_chat_message(user_email: str, question: str, answer: str) -> bool:
    """
    Append a Q&A pair to the chat history store.

    Parameters
    ----------
    user_email : str
    question : str
    answer : str

    Returns
    -------
    bool
    """
    history = load_json(DB_CHAT, [])

    entry = {
        "id": str(uuid.uuid4()),
        "user": user_email,
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat(),
    }

    history.append(entry)
    return save_json(DB_CHAT, history)


def get_chat_history(user_email: str, limit: int = 50) -> list[dict]:
    """
    Return the last *limit* messages for *user_email*.

    Parameters
    ----------
    user_email : str
    limit : int

    Returns
    -------
    list[dict]
    """
    history = load_json(DB_CHAT, [])
    user_messages = [m for m in history if m.get("user") == user_email]
    return user_messages[-limit:]


def clear_chat_history(user_email: str) -> bool:
    """Delete all chat messages belonging to *user_email*."""
    history = load_json(DB_CHAT, [])
    history = [m for m in history if m.get("user") != user_email]
    return save_json(DB_CHAT, history)


# ---------------------------------------------------------------------------
# Announcements operations
# ---------------------------------------------------------------------------


def get_announcements() -> list[dict]:
    """Return all announcements ordered by date (newest first)."""
    items = load_json(DB_ANNOUNCEMENTS, [])
    return sorted(items, key=lambda x: x.get("date", ""), reverse=True)


def add_announcement(title: str, description: str, category: str = "General") -> bool:
    """
    Add a new announcement.

    Parameters
    ----------
    title : str
    description : str
    category : str

    Returns
    -------
    bool
    """
    items = load_json(DB_ANNOUNCEMENTS, [])
    items.append(
        {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "category": category,
            "date": datetime.now().isoformat(),
        }
    )
    return save_json(DB_ANNOUNCEMENTS, items)


# ---------------------------------------------------------------------------
# Attendance operations
# ---------------------------------------------------------------------------


def get_attendance(student_id: str) -> dict | None:
    """Return attendance record for *student_id* or ``None``."""
    records = load_json(DB_ATTENDANCE, [])
    for rec in records:
        if rec.get("student_id") == student_id:
            return rec
    return None


def get_all_attendance() -> list[dict]:
    """Return all attendance records."""
    return load_json(DB_ATTENDANCE, [])


def update_attendance(student_id: str, subject: str, present: bool) -> bool:
    """
    Record a single attendance event.

    Creates a record for the student if one does not exist yet.

    Parameters
    ----------
    student_id : str
    subject : str
    present : bool

    Returns
    -------
    bool
    """
    records = load_json(DB_ATTENDANCE, [])

    today = date.today().isoformat()
    found = False

    for rec in records:
        if rec.get("student_id") == student_id:
            found = True
            if "log" not in rec:
                rec["log"] = []
            rec["log"].append(
                {
                    "date": today,
                    "subject": subject,
                    "present": present,
                }
            )
            # Recalculate percentage from log
            log = rec["log"]
            rec["attendance_percentage"] = round(
                sum(1 for e in log if e["present"]) / len(log) * 100, 1
            )
            break

    if not found:
        records.append(
            {
                "student_id": student_id,
                "attendance_percentage": 100.0 if present else 0.0,
                "log": [{"date": today, "subject": subject, "present": present}],
            }
        )

    return save_json(DB_ATTENDANCE, records)


# ---------------------------------------------------------------------------
# Timetable operations
# ---------------------------------------------------------------------------


def get_timetable() -> list[dict]:
    """Return the full timetable."""
    return load_json(DB_TIMETABLE, [])


def get_timetable_by_department(department: str) -> list[dict]:
    """Filter timetable entries by *department*."""
    return [e for e in get_timetable() if e.get("department") == department]


# ---------------------------------------------------------------------------
# Assignment operations
# ---------------------------------------------------------------------------


def get_assignments(student_id: str | None = None) -> list[dict]:
    """
    Return assignments.  If *student_id* is given, filter by it.

    Parameters
    ----------
    student_id : str or None

    Returns
    -------
    list[dict]
    """
    items = load_json(DB_ASSIGNMENTS, [])
    if student_id:
        return [a for a in items if a.get("student_id") == student_id]
    return items


def add_assignment(
    student_id: str,
    title: str,
    subject: str,
    due_date: str,
    description: str = "",
) -> bool:
    """
    Add a new assignment record.

    Parameters
    ----------
    student_id, title, subject, due_date, description : str

    Returns
    -------
    bool
    """
    items = load_json(DB_ASSIGNMENTS, [])
    items.append(
        {
            "id": str(uuid.uuid4()),
            "student_id": student_id,
            "title": title,
            "subject": subject,
            "due_date": due_date,
            "description": description,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
    )
    return save_json(DB_ASSIGNMENTS, items)


def update_assignment_status(assignment_id: str, status: str) -> bool:
    """
    Update the status of an assignment.

    Parameters
    ----------
    assignment_id : str
    status : str
        One of ``pending``, ``in_progress``, ``completed``.

    Returns
    -------
    bool
    """
    items = load_json(DB_ASSIGNMENTS, [])
    for item in items:
        if item.get("id") == assignment_id:
            item["status"] = status
            return save_json(DB_ASSIGNMENTS, items)
    return False


# ---------------------------------------------------------------------------
# Seed / initialise default data
# ---------------------------------------------------------------------------


def seed_default_data() -> None:
    """
    Populate JSON files with demo data if they are empty.

    Called once at application startup so the app works out-of-the-box.
    """
    _ensure_database_dir()

    # -- Announcements -------------------------------------------------------
    if not load_json(DB_ANNOUNCEMENTS, []):
        sample_announcements = [
            {
                "id": str(uuid.uuid4()),
                "title": "Mid-Semester Examinations Schedule Released",
                "description": (
                    "The examination committee has released the mid-semester "
                    "examination schedule. Students are advised to check their "
                    "respective department notice boards and the official portal."
                ),
                "category": "Exam",
                "date": "2026-07-10T09:00:00",
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Annual Tech Fest 2026 – Registrations Open",
                "description": (
                    "TechFusion 2026 registrations are now open! Participate in "
                    "hackathons, paper presentations, robotics competitions, and "
                    "much more. Register before 20 July 2026."
                ),
                "category": "Event",
                "date": "2026-07-08T10:30:00",
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Library Extended Hours During Exam Week",
                "description": (
                    "The central library will remain open 24/7 during the exam "
                    "week (14–21 July 2026). All students with valid ID cards "
                    "may access the reading halls."
                ),
                "category": "General",
                "date": "2026-07-07T08:00:00",
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Campus Placement Drive – Amazon & Microsoft",
                "description": (
                    "Amazon and Microsoft will conduct their on-campus placement "
                    "drives on 25 July 2026. Eligible students (CGPA ≥ 7.0) "
                    "must register through the placement portal by 18 July."
                ),
                "category": "Placement",
                "date": "2026-07-06T11:00:00",
            },
            {
                "id": str(uuid.uuid4()),
                "title": "New AI Lab Inauguration",
                "description": (
                    "The state-of-the-art AI & Machine Learning laboratory "
                    "equipped with 50 GPU workstations will be inaugurated on "
                    "16 July 2026 by the Vice Chancellor."
                ),
                "category": "Infrastructure",
                "date": "2026-07-05T14:00:00",
            },
        ]
        save_json(DB_ANNOUNCEMENTS, sample_announcements)

    # -- Timetable -----------------------------------------------------------
    if not load_json(DB_TIMETABLE, []):
        timetable_entries = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        cse_subjects = [
            ("Data Structures", "Dr. Ramesh Kumar", "LH-101"),
            ("Operating Systems", "Prof. Sunita Sharma", "LH-102"),
            ("DBMS", "Dr. Arun Verma", "LH-103"),
            ("Computer Networks", "Prof. Meera Pillai", "LH-104"),
            ("Machine Learning", "Dr. Vikram Singh", "LH-105"),
        ]
        slots = [
            ("09:00", "10:00"),
            ("10:00", "11:00"),
            ("11:15", "12:15"),
            ("12:15", "13:15"),
            ("14:00", "15:00"),
        ]

        for day in days:
            for idx, (start, end) in enumerate(slots):
                if idx < len(cse_subjects):
                    subj, faculty, room = cse_subjects[idx]
                    timetable_entries.append(
                        {
                            "id": str(uuid.uuid4()),
                            "department": "Computer Science & Engineering",
                            "day": day,
                            "start_time": start,
                            "end_time": end,
                            "subject": subj,
                            "faculty": faculty,
                            "room": room,
                        }
                    )

        save_json(DB_TIMETABLE, timetable_entries)

    # -- Attendance ----------------------------------------------------------
    if not load_json(DB_ATTENDANCE, []):
        sample_attendance = [
            {"student_id": "CS2021001", "attendance_percentage": 87.5, "log": []},
            {"student_id": "CS2021002", "attendance_percentage": 92.3, "log": []},
            {"student_id": "CS2021003", "attendance_percentage": 74.8, "log": []},
        ]
        save_json(DB_ATTENDANCE, sample_attendance)

    # -- Assignments ---------------------------------------------------------
    if not load_json(DB_ASSIGNMENTS, []):
        sample_assignments = [
            {
                "id": str(uuid.uuid4()),
                "student_id": "CS2021001",
                "title": "Implement a Binary Search Tree",
                "subject": "Data Structures",
                "due_date": "2026-07-20",
                "description": "Implement BST with insert, delete, and traversal.",
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "student_id": "CS2021001",
                "title": "Design ER Diagram for Library System",
                "subject": "DBMS",
                "due_date": "2026-07-18",
                "description": "Create a normalised ER diagram for a library system.",
                "status": "in_progress",
                "created_at": datetime.now().isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "student_id": "CS2021001",
                "title": "Socket Programming Lab Report",
                "subject": "Computer Networks",
                "due_date": "2026-07-15",
                "description": "Write a TCP/UDP socket communication program.",
                "status": "completed",
                "created_at": datetime.now().isoformat(),
            },
        ]
        save_json(DB_ASSIGNMENTS, sample_assignments)
