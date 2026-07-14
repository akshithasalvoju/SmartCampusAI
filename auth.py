"""
auth.py - Authentication utilities for Smart Campus AI.

Handles password hashing / verification using bcrypt and manages
Streamlit session_state for login / logout flows.
"""

import streamlit as st
import bcrypt

from config import SESSION_LOGGED_IN, SESSION_USER, SESSION_PAGE
from database import get_user_by_email, create_user, get_user_by_id


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """
    Hash *plain* using bcrypt.

    Parameters
    ----------
    plain : str
        Plain-text password.

    Returns
    -------
    str
        UTF-8 decoded bcrypt hash.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify *plain* against a bcrypt *hashed* password.

    Parameters
    ----------
    plain : str
    hashed : str

    Returns
    -------
    bool
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------


def init_session() -> None:
    """Initialise all required session_state keys if absent."""
    defaults: dict = {
        SESSION_LOGGED_IN: False,
        SESSION_USER: None,
        SESSION_PAGE: "login",
        "theme": "dark",
        "chat_messages": [],
        "notifications": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_user(email: str, password: str) -> tuple[bool, str]:
    """
    Attempt to authenticate a user.

    Parameters
    ----------
    email : str
    password : str

    Returns
    -------
    tuple[bool, str]
        ``(True, "")`` on success; ``(False, error_message)`` on failure.
    """
    if not email.strip() or not password.strip():
        return False, "Email and password are required."

    user = get_user_by_email(email)
    if user is None:
        return False, "No account found with this email address."

    if not verify_password(password, user.get("password_hash", "")):
        return False, "Incorrect password. Please try again."

    st.session_state[SESSION_LOGGED_IN] = True
    st.session_state[SESSION_USER] = user
    st.session_state[SESSION_PAGE] = "dashboard"
    return True, ""


def logout_user() -> None:
    """Clear the session and redirect to login."""
    for key in [SESSION_LOGGED_IN, SESSION_USER, "chat_messages"]:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state[SESSION_LOGGED_IN] = False
    st.session_state[SESSION_USER] = None
    st.session_state[SESSION_PAGE] = "login"


def register_user(
    name: str,
    email: str,
    phone: str,
    student_id: str,
    department: str,
    password: str,
    confirm_password: str,
) -> tuple[bool, str]:
    """
    Validate inputs and create a new user account.

    Parameters
    ----------
    name, email, phone, student_id, department, password, confirm_password : str

    Returns
    -------
    tuple[bool, str]
        ``(True, "")`` on success; ``(False, error_message)`` on failure.
    """
    # --- Field validation --------------------------------------------------
    if not all([name, email, phone, student_id, department, password, confirm_password]):
        return False, "All fields are required."

    if len(name.strip()) < 2:
        return False, "Full name must be at least 2 characters."

    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Please enter a valid email address."

    if not phone.strip().isdigit() or len(phone.strip()) < 10:
        return False, "Please enter a valid 10-digit mobile number."

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if password != confirm_password:
        return False, "Passwords do not match."

    if get_user_by_email(email):
        return False, "An account with this email already exists."

    # --- Create user -------------------------------------------------------
    password_hash = hash_password(password)
    create_user(
        name=name,
        email=email,
        phone=phone,
        student_id=student_id,
        department=department,
        password_hash=password_hash,
    )
    return True, ""


def is_authenticated() -> bool:
    """Return ``True`` when a user is logged in."""
    return bool(st.session_state.get(SESSION_LOGGED_IN, False))


def get_current_user() -> dict | None:
    """Return the current user's record or ``None``."""
    user = st.session_state.get(SESSION_USER)
    if user and isinstance(user, dict):
        # Refresh from DB to pick up any updates
        fresh = get_user_by_id(user.get("id", ""))
        if fresh:
            st.session_state[SESSION_USER] = fresh
            return fresh
    return user


def require_auth() -> bool:
    """
    Guard for pages that require authentication.

    Returns
    -------
    bool
        ``True`` if authenticated, ``False`` if redirected to login.
    """
    if not is_authenticated():
        st.session_state[SESSION_PAGE] = "login"
        return False
    return True
