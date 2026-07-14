"""
pages/settings.py - Settings page for Smart Campus AI.
"""

import streamlit as st
from auth import get_current_user
from dashboard import render_topbar
from database import clear_chat_history

def render_settings() -> None:
    """Render the settings page."""
    render_topbar("⚙️ Settings")

    user = get_current_user()
    if not user:
        st.error("Session expired.")
        return

    # Custom Settings UI
    tab_prefs, tab_notif, tab_data = st.tabs([
        "🎨 Appearance",
        "🔔 Notifications",
        "⚙️ Data Management"
    ])

    with tab_prefs:
        st.markdown("### 🎨 UI Preferences")
        theme_val = st.selectbox(
            "Select Theme",
            ["Dark Mode (Default)", "Light Mode"],
            index=0 if st.session_state.get("theme", "dark") == "dark" else 1
        )
        
        font_size = st.slider("Font Scale", 80, 120, 100, step=5, format="%d%%")
        
        save_prefs = st.button("💾 Save Preferences", key="save_prefs_btn")
        if save_prefs:
            st.session_state["theme"] = "dark" if "Dark" in theme_val else "light"
            st.success("✅ Preferences saved successfully!")
            st.rerun()

    with tab_notif:
        st.markdown("### 🔔 Notification Channels")
        st.checkbox("Email Alerts for New Announcements", value=True)
        st.checkbox("SMS Reminders for Assignments", value=False)
        st.checkbox("Push Notifications for Class Timings", value=True)
        
        save_notifs = st.button("💾 Save Notification Settings", key="save_notif_btn")
        if save_notifs:
            st.success("✅ Notification settings updated!")

    with tab_data:
        st.markdown("### ⚙️ Account & Data Controls")
        
        st.markdown("#### Download User Archive")
        st.markdown("Download a full backup of your registered information, attendance history, and assignment records.")
        if st.button("⬇️ Export My Data", key="export_data_btn"):
            st.info("Preparing data archive...")
            # Simulated archive
            import json
            archive = {
                "user": {
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "student_id": user.get("student_id"),
                    "department": user.get("department")
                },
                "system_status": "Active"
            }
            st.download_button(
                label="📥 Download JSON Archive",
                data=json.dumps(archive, indent=2),
                file_name=f"student_archive_{user.get('student_id')}.json",
                mime="application/json"
            )

        st.markdown("---")
        st.markdown("#### Database Reset")
        st.markdown("This will clear all accumulated data records. Use with caution.")
        
        reset_col1, reset_col2 = st.columns(2)
        with reset_col1:
            if st.button("🗑️ Reset Chat History", use_container_width=True, key="reset_chat_data_btn"):
                if clear_chat_history(user.get("email", "")):
                    if "chat_messages" in st.session_state:
                        st.session_state["chat_messages"] = []
                    st.success("Chat history cleared!")
                else:
                    st.error("Failed to clear chat history.")
        with reset_col2:
            if st.button("🚨 Reset All Session State", use_container_width=True, key="reset_session_data_btn"):
                st.session_state.clear()
                st.success("Session state cleared! Rerunning...")
                st.rerun()
