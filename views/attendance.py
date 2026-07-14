"""
pages/attendance.py - Attendance tracking page for Smart Campus AI.
"""

from __future__ import annotations

import io
import streamlit as st
import pandas as pd

from auth import get_current_user
from database import get_attendance, get_all_attendance, update_attendance
from dashboard import render_topbar
from utils import attendance_donut, attendance_bar_chart
from config import COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER

# Default subjects per department (simplified to CSE for demo)
DEFAULT_SUBJECTS = [
    "Data Structures",
    "Operating Systems",
    "DBMS",
    "Computer Networks",
    "Machine Learning",
]


def render_attendance() -> None:
    """Render the attendance tracking page."""
    render_topbar("📅 Attendance Tracker")

    user = get_current_user()
    if not user:
        st.error("Session expired.")
        return

    student_id = user.get("student_id", "")

    tab_overview, tab_mark, tab_download = st.tabs(
        ["📊 Overview", "✅ Mark Attendance", "⬇️ Download Report"]
    )

    # ── Overview ──────────────────────────────────────────────────────────
    with tab_overview:
        att_record = get_attendance(student_id)
        overall_pct = att_record.get("attendance_percentage", 0.0) if att_record else 0.0

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("#### 📅 Overall Attendance")
            fig = attendance_donut(overall_pct)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            att_color = COLOR_SUCCESS if overall_pct >= 75 else COLOR_DANGER
            status_text = "✅ Good Standing" if overall_pct >= 75 else "⚠️ Below Minimum (75%)"
            st.markdown(
                f'<div style="text-align:center;color:{att_color};font-weight:600;">'
                f"{status_text}</div>",
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown("#### 📚 Subject-wise Attendance")
            # Generate simulated subject-wise data around the overall percentage
            import random
            subjects = DEFAULT_SUBJECTS
            base = overall_pct if overall_pct > 0 else 80.0
            pcts = [
                round(min(100, max(0, base + random.uniform(-12, 12))), 1)
                for _ in subjects
            ]
            fig2 = attendance_bar_chart(subjects, pcts)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        # Attendance log table
        if att_record and att_record.get("log"):
            st.markdown("#### 📋 Attendance Log")
            log = att_record["log"]
            df = pd.DataFrame(log)
            df["present"] = df["present"].map({True: "✅ Present", False: "❌ Absent"})
            df.columns = [c.capitalize() for c in df.columns]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No attendance log entries yet. Mark attendance using the 'Mark Attendance' tab.")

    # ── Mark Attendance ───────────────────────────────────────────────────
    with tab_mark:
        st.markdown("### ✅ Mark Today's Attendance")
        with st.form("mark_attendance_form"):
            subject = st.selectbox("Subject", DEFAULT_SUBJECTS)
            status = st.radio(
                "Attendance Status",
                ["Present ✅", "Absent ❌"],
                horizontal=True,
            )
            submit = st.form_submit_button("📥 Submit Attendance", use_container_width=True)

        if submit:
            present = status.startswith("Present")
            success = update_attendance(student_id, subject, present)
            if success:
                label = "✅ Attendance marked as Present." if present else "❌ Attendance marked as Absent."
                st.success(label)
                st.rerun()
            else:
                st.error("Failed to record attendance.")

    # ── Download Report ───────────────────────────────────────────────────
    with tab_download:
        st.markdown("### ⬇️ Download Attendance Report")
        att_record = get_attendance(student_id)

        if not att_record or not att_record.get("log"):
            st.warning("No attendance data to export yet.")
        else:
            log = att_record["log"]
            df = pd.DataFrame(log)
            df["student_id"] = student_id
            df["name"] = user.get("name", "")
            df["department"] = user.get("department", "")
            df["present"] = df["present"].map({True: "Present", False: "Absent"})

            col_csv, col_excel = st.columns(2)
            with col_csv:
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📄 Download CSV",
                    data=csv_data,
                    file_name=f"attendance_{student_id}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col_excel:
                excel_buf = io.BytesIO()
                df.to_excel(excel_buf, index=False, engine="openpyxl")
                excel_buf.seek(0)
                st.download_button(
                    "📊 Download Excel",
                    data=excel_buf,
                    file_name=f"attendance_{student_id}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            st.markdown("#### 📋 Preview")
            st.dataframe(df, use_container_width=True, hide_index=True)
