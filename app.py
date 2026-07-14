"""
app.py - Main entry point and router for Smart Campus AI.
"""

import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(
    page_title="Smart Campus AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

from auth import init_session, is_authenticated, get_current_user
from database import seed_default_data
from utils import load_css
from config import SESSION_PAGE

# Seed default database values if empty
seed_default_data()

# Initialise session keys
init_session()

# Inject glassmorphism and custom panel styling
load_css("styles.css")

# --- Page Router ---
if not is_authenticated():
    current_page = st.session_state.get(SESSION_PAGE, "login")
    if current_page == "register":
        from views.register import render_register
        render_register()
    else:
        from views.login import render_login
        render_login()
else:
    # Ensure current page in session state is valid for logged-in user
    current_page = st.session_state.get(SESSION_PAGE, "dashboard")
    if current_page in ["login", "register"]:
        current_page = "dashboard"
        st.session_state[SESSION_PAGE] = "dashboard"

    # Render sidebar and capture navigation updates
    from dashboard import render_sidebar
    selected_page = render_sidebar(current_page)

    if selected_page != current_page:
        st.session_state[SESSION_PAGE] = selected_page
        st.rerun()

    # Get active user context
    user = get_current_user()
    if not user:
        st.error("User session mismatch. Please log out and log in again.")
        st.stop()

    # Route main panel content
    if selected_page == "dashboard":
        from dashboard import render_dashboard
        render_dashboard(user)
    elif selected_page == "profile":
        from views.profile import render_profile
        render_profile()
    elif selected_page == "attendance":
        from views.attendance import render_attendance
        render_attendance()
    elif selected_page == "assignments":
        from views.assignments import render_assignments
        render_assignments()
    elif selected_page == "announcements":
        from views.announcements import render_announcements
        render_announcements()
    elif selected_page == "timetable":
        from views.timetable import render_timetable
        render_timetable()
    elif selected_page == "chatbot":
        from views.chatbot import render_chatbot
        render_chatbot()
    elif selected_page == "settings":
        from views.settings import render_settings
        render_settings()
