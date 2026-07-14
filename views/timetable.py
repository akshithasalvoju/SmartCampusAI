"""
pages/timetable.py - Timetable page for Smart Campus AI.
"""

import streamlit as st
from auth import get_current_user
from database import get_timetable_by_department
from dashboard import render_topbar

def render_timetable() -> None:
    """Render the timetable page."""
    render_topbar("🗓️ Class Timetable")

    user = get_current_user()
    if not user:
        st.error("Session expired.")
        return

    dept = user.get("department", "Computer Science & Engineering")
    
    st.markdown(
        f"""
        <div style="background: rgba(255, 255, 255, 0.02); padding: 16px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 20px;">
            <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 500; text-transform: uppercase;">Current Department</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #38BDF8; margin-top: 2px;">🏛️ {dept}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    timetable = get_timetable_by_department(dept)
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    tabs = st.tabs([f"📅 {day}" for day in days])

    for tab, day in zip(tabs, days):
        with tab:
            day_classes = [c for c in timetable if c.get("day") == day]
            if not day_classes:
                st.info(f"No classes scheduled for {day}.")
            else:
                # Sort classes by start time
                day_classes_sorted = sorted(day_classes, key=lambda x: x.get("start_time", ""))
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    for cls in day_classes_sorted:
                        st.markdown(
                            f"""
                            <div class="class-item" style="margin-bottom: 16px; padding: 16px; background: rgba(255,255,255,0.01); border-radius: 0 12px 12px 0;">
                                <div class="class-time" style="font-size: 0.85rem; font-weight: 600;">⏰ {cls.get('start_time')} – {cls.get('end_time')}</div>
                                <div class="class-subject" style="font-size: 1.15rem; font-weight: 700; margin-top: 4px; color: #FFFFFF;">{cls.get('subject')}</div>
                                <div class="class-faculty" style="font-size: 0.82rem; color: #94A3B8; margin-top: 6px;">
                                    👤 {cls.get('faculty')} &nbsp;·&nbsp; 🏛️ Room {cls.get('room')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                with col2:
                    st.markdown(
                        """
                        <div class="info-card">
                            <div class="info-card-header">
                                <span class="info-icon">💡</span>
                                <span class="info-title">Schedule Info</span>
                            </div>
                            <div class="info-body">
                                Attendance is mandatory. Maintaining a minimum of 75% attendance is required to be eligible for final semester examinations. Contact department head for any scheduling concerns.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
