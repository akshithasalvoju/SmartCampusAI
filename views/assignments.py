"""
pages/assignments.py - Assignment manager page for Smart Campus AI.
"""

from __future__ import annotations

from datetime import date
import streamlit as st

from auth import get_current_user
from database import get_assignments, add_assignment, update_assignment_status
from dashboard import render_topbar
from utils import status_badge, days_until, format_datetime
from config import COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_SECONDARY, COLOR_PRIMARY

DEFAULT_SUBJECTS = [
    "Data Structures",
    "Operating Systems",
    "DBMS",
    "Computer Networks",
    "Machine Learning",
    "Software Engineering",
    "Algorithms",
    "Theory of Computation",
]


def render_assignments() -> None:
    """Render the assignment manager page."""
    render_topbar("📝 Assignments")

    user = get_current_user()
    if not user:
        st.error("Session expired.")
        return

    student_id = user.get("student_id", "")

    tab_list, tab_add, tab_summarize = st.tabs(
        ["📋 My Assignments", "➕ Add Assignment", "🤖 AI Summarizer"]
    )

    # ── Assignment List ───────────────────────────────────────────────────
    with tab_list:
        assignments = get_assignments(student_id)

        # Status filter
        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            status_filter = st.selectbox(
                "Filter",
                ["All", "Pending", "In Progress", "Completed"],
                key="assign_filter",
                label_visibility="collapsed",
            )

        status_map = {
            "All": None,
            "Pending": "pending",
            "In Progress": "in_progress",
            "Completed": "completed",
        }
        filter_val = status_map.get(status_filter)
        if filter_val:
            assignments = [a for a in assignments if a.get("status") == filter_val]

        if not assignments:
            st.info("No assignments found. Add one using the '➕ Add Assignment' tab.")
        else:
            for a in sorted(assignments, key=lambda x: x.get("due_date", "")):
                due = a.get("due_date", "")
                days = days_until(due)
                status = a.get("status", "pending")

                # Overdue check
                if days < 0 and status != "completed":
                    status_html = status_badge("overdue")
                    days_html = f'<span style="color:{COLOR_DANGER};">⚠️ {abs(days)} days overdue</span>'
                elif days == 0 and status != "completed":
                    days_html = f'<span style="color:{COLOR_WARNING};">🔥 Due today!</span>'
                    status_html = status_badge(status)
                elif days <= 3 and status != "completed":
                    days_html = f'<span style="color:{COLOR_WARNING};">⏰ {days} days left</span>'
                    status_html = status_badge(status)
                else:
                    days_html = (
                        f'<span style="color:#94A3B8;">{days} days left</span>'
                        if status != "completed"
                        else '<span style="color:#10B981;">✅ Done</span>'
                    )
                    status_html = status_badge(status)

                with st.expander(f"📝 {a.get('title', 'Untitled')} — {a.get('subject', '')}", expanded=False):
                    card_html = (
                        f'<div class="assignment-detail">'
                        f'<div class="assign-row">'
                        f'<b>Subject:</b> {a.get("subject", "")}'
                        f'&nbsp;|&nbsp;'
                        f'<b>Due:</b> {due}'
                        f'&nbsp;|&nbsp;'
                        f'{days_html}'
                        f'</div>'
                        f'<div class="assign-status-row">'
                        f'<b>Status:</b> {status_html}'
                        f'</div>'
                        f'<div class="assign-desc">{a.get("description", "No description.")}</div>'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                    # Status update
                    new_status = st.selectbox(
                        "Update Status",
                        ["pending", "in_progress", "completed"],
                        index=["pending", "in_progress", "completed"].index(
                            a.get("status", "pending")
                        ),
                        key=f"status_{a['id']}",
                    )
                    if st.button("💾 Save Status", key=f"save_{a['id']}"):
                        update_assignment_status(a["id"], new_status)
                        st.success("Status updated!")
                        st.rerun()

    # ── Add Assignment ────────────────────────────────────────────────────
    with tab_add:
        st.markdown("### ➕ Add New Assignment")
        with st.form("add_assignment_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Assignment Title", placeholder="e.g. Implement BST")
                subject = st.selectbox("Subject", DEFAULT_SUBJECTS)
            with col2:
                due_date = st.date_input("Due Date", min_value=date.today())
                status_init = st.selectbox("Initial Status", ["pending", "in_progress"])

            description = st.text_area(
                "Description / Instructions",
                placeholder="Describe the assignment requirements…",
                height=120,
            )
            submit = st.form_submit_button("✅ Add Assignment", use_container_width=True)

        if submit:
            if not title.strip():
                st.error("Assignment title is required.")
            else:
                success = add_assignment(
                    student_id,
                    title.strip(),
                    subject,
                    str(due_date),
                    description.strip(),
                )
                if success:
                    st.success("✅ Assignment added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add assignment.")

    # ── AI Summarizer ─────────────────────────────────────────────────────
    with tab_summarize:
        st.markdown("### 🤖 AI Assignment Summarizer")
        st.markdown(
            "Paste your assignment description below and the AI will break it down "
            "into clear tasks and suggest an approach."
        )

        assignment_text = st.text_area(
            "Paste assignment description here…",
            height=180,
            key="summarizer_input",
        )

        if st.button("🚀 Summarize & Plan", use_container_width=True, key="summarize_btn"):
            if not assignment_text.strip():
                st.warning("Please paste some assignment text first.")
            else:
                from chatbot import get_ai_response_stream

                prompt = (
                    f"I have the following assignment:\n\n{assignment_text}\n\n"
                    "Please:\n"
                    "1. Summarise what is being asked in 2–3 bullet points.\n"
                    "2. Break it down into clear steps I should follow.\n"
                    "3. Suggest any relevant resources or concepts I should study.\n"
                    "4. Estimate the time required to complete it."
                )
                st.markdown("---")
                st.markdown("#### 📋 AI Analysis")
                with st.chat_message("assistant", avatar="🤖"):
                    response = st.write_stream(get_ai_response_stream(prompt, user.get("email", "")))

                # Save to database if not an error message
                if response and not response.startswith(("⚠️", "❌", "🔑", "⏳", "🤖")):
                    from database import save_chat_message
                    save_chat_message(user.get("email", ""), prompt, response)
