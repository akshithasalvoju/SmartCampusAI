"""
pages/profile.py - Student profile page for Smart Campus AI.
"""

from __future__ import annotations

import streamlit as st

from auth import get_current_user, hash_password, verify_password
from database import update_user, get_attendance, get_assignments
from config import DEPARTMENTS, COLOR_PRIMARY, COLOR_SUCCESS
from utils import metric_card, attendance_donut, format_datetime


# Re-expose render_topbar from dashboard (avoids circular import)
from dashboard import render_topbar  # noqa: F401


def render_profile() -> None:
    """Render the student profile page."""
    render_topbar("👤 My Profile")

    user = get_current_user()
    if not user:
        st.error("Session expired. Please log in again.")
        return

    tab_info, tab_edit, tab_security, tab_stats = st.tabs(
        ["📋 Profile Info", "✏️ Edit Profile", "🔒 Security", "📊 My Stats"]
    )

    # ── Tab 1: Profile Info ───────────────────────────────────────────────
    with tab_info:
        col_avatar, col_details = st.columns([1, 2.5])

        with col_avatar:
            st.markdown(
                f"""
                <div class="profile-avatar-section">
                    <div class="profile-avatar-large">👤</div>
                    <div class="profile-name-large">{user.get('name', '')}</div>
                    <div class="profile-dept">{user.get('department', '')}</div>
                    <div class="profile-id">ID: {user.get('student_id', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_details:
            st.markdown('<div class="profile-details">', unsafe_allow_html=True)
            fields = [
                ("👤 Full Name", user.get("name", "—")),
                ("📧 Email", user.get("email", "—")),
                ("📱 Mobile", user.get("phone", "—")),
                ("🎓 Student ID", user.get("student_id", "—")),
                ("🏛️ Department", user.get("department", "—")),
                ("📝 Bio", user.get("bio", "No bio yet.")),
                (
                    "📅 Member Since",
                    format_datetime(user.get("created_at", ""), "%d %B %Y"),
                ),
            ]
            for label, value in fields:
                st.markdown(
                    f"""
                    <div class="profile-field">
                        <span class="field-label">{label}</span>
                        <span class="field-value">{value}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 2: Edit Profile ───────────────────────────────────────────────
    with tab_edit:
        with st.form("edit_profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name", value=user.get("name", ""))
                new_phone = st.text_input("Mobile Number", value=user.get("phone", ""))
                new_student_id = st.text_input("Student ID", value=user.get("student_id", ""))
            with col2:
                new_dept = st.selectbox(
                    "Department",
                    DEPARTMENTS,
                    index=DEPARTMENTS.index(user.get("department", DEPARTMENTS[0]))
                    if user.get("department") in DEPARTMENTS
                    else 0,
                )
                new_bio = st.text_area("Bio", value=user.get("bio", ""), height=120)

            save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if save_btn:
            if not new_name.strip():
                st.error("Name cannot be empty.")
            elif not new_phone.strip().isdigit() or len(new_phone.strip()) < 10:
                st.error("Please enter a valid 10-digit phone number.")
            else:
                success = update_user(
                    user["id"],
                    {
                        "name": new_name.strip(),
                        "phone": new_phone.strip(),
                        "student_id": new_student_id.strip(),
                        "department": new_dept,
                        "bio": new_bio.strip(),
                    },
                )
                if success:
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save changes.")

    # ── Tab 3: Security ───────────────────────────────────────────────────
    with tab_security:
        st.markdown("### 🔒 Change Password")
        with st.form("change_password_form"):
            current_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            change_btn = st.form_submit_button("🔄 Update Password", use_container_width=True)

        if change_btn:
            if not all([current_pw, new_pw, confirm_pw]):
                st.error("All fields are required.")
            elif not verify_password(current_pw, user.get("password_hash", "")):
                st.error("❌ Current password is incorrect.")
            elif len(new_pw) < 8:
                st.error("New password must be at least 8 characters.")
            elif new_pw != confirm_pw:
                st.error("New passwords do not match.")
            else:
                new_hash = hash_password(new_pw)
                success = update_user(user["id"], {"password_hash": new_hash})
                if success:
                    st.success("✅ Password updated successfully!")
                else:
                    st.error("❌ Failed to update password.")

        st.markdown("---")
        st.markdown("### 🔐 Account Security Tips")
        tips = [
            "🛡️ Use a strong password with letters, numbers, and symbols.",
            "🔑 Never share your password with anyone.",
            "📧 Keep your email address up to date.",
            "🔄 Change your password every 90 days.",
            "⚠️ Log out from shared computers.",
        ]
        for tip in tips:
            st.markdown(f"- {tip}")

    # ── Tab 4: My Stats ───────────────────────────────────────────────────
    with tab_stats:
        student_id = user.get("student_id", "")
        att_record = get_attendance(student_id)
        attendance_pct = att_record.get("attendance_percentage", 0.0) if att_record else 0.0
        assignments = get_assignments(student_id)

        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card(
                "Attendance",
                f"{attendance_pct}%",
                "📅",
                COLOR_SUCCESS if attendance_pct >= 75 else "#EF4444",
            )
        with col2:
            metric_card("Total Assignments", str(len(assignments)), "📝", COLOR_PRIMARY)
        with col3:
            completed = sum(1 for a in assignments if a.get("status") == "completed")
            metric_card("Completed", str(completed), "✅", COLOR_SUCCESS)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("#### 📅 Attendance Overview")
        fig = attendance_donut(attendance_pct)
        _, c, _ = st.columns([1, 1, 1])
        with c:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
