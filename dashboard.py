"""
dashboard.py - Main dashboard rendering logic for Smart Campus AI.

Renders the top navbar, sidebar navigation, and the main content area
for the authenticated dashboard experience.
"""

from __future__ import annotations

import streamlit as st
from datetime import datetime, date
import random

from config import (
    APP_NAME,
    APP_ICON,
    NAV_PAGES,
    SESSION_PAGE,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_SECONDARY,
)
from auth import get_current_user, logout_user
from database import (
    get_attendance,
    get_assignments,
    get_announcements,
    get_timetable_by_department,
    get_all_attendance,
)
from utils import (
    metric_card,
    attendance_donut,
    weekly_activity_bar,
    assignment_status_pie,
    get_greeting,
    format_datetime,
    days_until,
    status_badge,
)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------


def render_sidebar(current_page: str) -> str:
    """
    Render the sidebar navigation and return the selected page key.

    Parameters
    ----------
    current_page : str

    Returns
    -------
    str
        The newly selected page key.
    """
    with st.sidebar:
        # Logo / app title
        st.markdown(
            f"""
            <div class="sidebar-logo">
                <div class="logo-icon">{APP_ICON}</div>
                <div class="logo-text">
                    <div class="logo-title">{APP_NAME}</div>
                    <div class="logo-subtitle">Student Portal</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # User avatar & name
        user = get_current_user()
        if user:
            st.markdown(
                f"""
                <div class="sidebar-user">
                    <div class="sidebar-avatar">👤</div>
                    <div class="sidebar-user-info">
                        <div class="sidebar-user-name">{user.get('name', 'Student')}</div>
                        <div class="sidebar-user-dept">{user.get('department', '')[:30]}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # Navigation
        selected = current_page
        for page in NAV_PAGES:
            is_active = page["key"] == current_page
            btn_class = "nav-btn-active" if is_active else "nav-btn"
            if st.button(
                f'{page["icon"]}  {page["label"]}',
                key=f'nav_{page["key"]}',
                use_container_width=True,
            ):
                selected = page["key"]

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # Logout
        if st.button("🚪  Logout", key="sidebar_logout", use_container_width=True):
            logout_user()
            st.rerun()

        # Theme info at the bottom
        st.markdown(
            """
            <div class="sidebar-footer">
                <div class="sidebar-version">Smart Campus AI v1.0</div>
                <div class="sidebar-copy">© 2026 Campus Tech</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected


# ---------------------------------------------------------------------------
# Topbar
# ---------------------------------------------------------------------------


def render_topbar(page_title: str) -> None:
    """Render the top navigation bar."""
    user = get_current_user()
    greeting = get_greeting()
    name = user.get("name", "Student").split()[0] if user else "Student"

    st.markdown(
        f"""
        <div class="topbar">
            <div class="topbar-left">
                <div class="topbar-title">{page_title}</div>
                <div class="topbar-greeting">{greeting}, {name}! 👋</div>
            </div>
            <div class="topbar-right">
                <div class="topbar-date">{datetime.now().strftime('%A, %d %B %Y')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Dashboard page
# ---------------------------------------------------------------------------


def render_dashboard(user: dict) -> None:
    """
    Render the main dashboard page.

    Parameters
    ----------
    user : dict
        Currently logged-in user record.
    """
    render_topbar("🏠 Dashboard")

    student_id = user.get("student_id", "")
    department = user.get("department", "")

    # ── Top metric cards ──────────────────────────────────────────────────
    att_record = get_attendance(student_id)
    attendance_pct = att_record.get("attendance_percentage", 85.0) if att_record else 85.0

    assignments = get_assignments(student_id)
    total_assignments = len(assignments)
    pending = sum(1 for a in assignments if a.get("status") == "pending")
    completed = sum(1 for a in assignments if a.get("status") == "completed")
    in_progress_count = sum(1 for a in assignments if a.get("status") == "in_progress")

    announcements = get_announcements()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Attendance", f"{attendance_pct}%", "📅", COLOR_SUCCESS, "+2% this week")
    with col2:
        metric_card("Assignments", str(total_assignments), "📝", COLOR_PRIMARY)
    with col3:
        metric_card("Pending Tasks", str(pending), "⏳", COLOR_WARNING)
    with col4:
        metric_card("Announcements", str(len(announcements)), "📢", COLOR_SECONDARY)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Row 2: Charts ─────────────────────────────────────────────────────
    col_left, col_mid, col_right = st.columns([1, 1.2, 1.2])

    with col_left:
        st.markdown(
            '<div class="card-header">📅 Attendance</div>', unsafe_allow_html=True
        )
        fig = attendance_donut(attendance_pct)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        att_color = COLOR_SUCCESS if attendance_pct >= 75 else COLOR_DANGER
        st.markdown(
            f'<div class="att-status" style="color:{att_color};text-align:center;">'
            f'{"✅ Good standing" if attendance_pct >= 75 else "⚠️ Below minimum"}</div>',
            unsafe_allow_html=True,
        )

    with col_mid:
        st.markdown(
            '<div class="card-header">📊 Weekly Activity</div>', unsafe_allow_html=True
        )
        weekly_data = {
            "Mon": random.randint(3, 8),
            "Tue": random.randint(3, 8),
            "Wed": random.randint(3, 8),
            "Thu": random.randint(3, 8),
            "Fri": random.randint(3, 8),
            "Sat": random.randint(1, 4),
            "Sun": random.randint(0, 3),
        }
        fig2 = weekly_activity_bar(weekly_data)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.markdown(
            '<div class="card-header">📝 Assignment Status</div>', unsafe_allow_html=True
        )
        if total_assignments:
            fig3 = assignment_status_pie(pending, in_progress_count, completed)
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No assignments yet.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Row 3: Recent Announcements & Timetable ───────────────────────────
    col_ann, col_tt = st.columns([1.2, 1])

    with col_ann:
        st.markdown(
            '<div class="card-header">📢 Recent Announcements</div>', unsafe_allow_html=True
        )
        if announcements:
            for ann in announcements[:3]:
                category = ann.get("category", "General")
                cat_colors = {
                    "Exam": COLOR_DANGER,
                    "Event": COLOR_SECONDARY,
                    "Placement": COLOR_SUCCESS,
                    "General": COLOR_PRIMARY,
                    "Infrastructure": COLOR_WARNING,
                }
                cat_color = cat_colors.get(category, COLOR_PRIMARY)
                st.markdown(
                    f"""
                    <div class="announcement-item">
                        <div class="ann-badge" style="background:{cat_color};">{category}</div>
                        <div class="ann-title">{ann.get('title', '')}</div>
                        <div class="ann-date">{format_datetime(ann.get('date', ''), '%d %b %Y')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No announcements available.")

    with col_tt:
        st.markdown(
            '<div class="card-header">🗓️ Today\'s Classes</div>', unsafe_allow_html=True
        )
        today_name = datetime.now().strftime("%A")
        tt = get_timetable_by_department(department)
        today_classes = [c for c in tt if c.get("day") == today_name]

        if today_classes:
            for cls in sorted(today_classes, key=lambda x: x.get("start_time", "")):
                st.markdown(
                    f"""
                    <div class="class-item">
                        <div class="class-time">{cls.get('start_time')} – {cls.get('end_time')}</div>
                        <div class="class-subject">{cls.get('subject')}</div>
                        <div class="class-faculty">{cls.get('faculty')} · {cls.get('room')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No classes scheduled for today.")

    # ── Row 4: AI Suggestions & Quick Actions ─────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    col_ai, col_qa = st.columns([1.4, 1])

    with col_ai:
        st.markdown(
            '<div class="card-header">🤖 AI Suggestions</div>', unsafe_allow_html=True
        )
        suggestions = [
            ("📚", "Review Data Structures topics: Trees and Graphs for upcoming exams."),
            ("⏰", f"You have {pending} pending assignment(s). Start with the earliest due date."),
            (
                "📊",
                f"Your attendance is {attendance_pct}%. "
                + ("Keep it up! 🌟" if attendance_pct >= 75 else "Try to attend more classes! ⚠️"),
            ),
            ("🧠", "Use the Pomodoro technique: 25 min study, 5 min break for better retention."),
        ]
        for icon, tip in suggestions:
            st.markdown(
                f"""
                <div class="ai-suggestion">
                    <span class="suggestion-icon">{icon}</span>
                    <span class="suggestion-text">{tip}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_qa:
        st.markdown(
            '<div class="card-header">⚡ Quick Actions</div>', unsafe_allow_html=True
        )
        if st.button("🤖 Ask AI Assistant", use_container_width=True, key="qa_chatbot"):
            st.session_state[SESSION_PAGE] = "chatbot"
            st.rerun()
        if st.button("📝 View Assignments", use_container_width=True, key="qa_assign"):
            st.session_state[SESSION_PAGE] = "assignments"
            st.rerun()
        if st.button("📅 Check Attendance", use_container_width=True, key="qa_attend"):
            st.session_state[SESSION_PAGE] = "attendance"
            st.rerun()
        if st.button("📢 Announcements", use_container_width=True, key="qa_ann"):
            st.session_state[SESSION_PAGE] = "announcements"
            st.rerun()
