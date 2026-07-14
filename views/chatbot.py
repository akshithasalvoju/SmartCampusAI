"""
pages/chatbot.py - AI Assistant chatbot page for Smart Campus AI.
"""

import streamlit as st
from auth import get_current_user
from chatbot import build_chat_interface
from dashboard import render_topbar
from database import clear_chat_history

def render_chatbot() -> None:
    """Render the AI Assistant chatbot page."""
    render_topbar("🤖 AI Assistant")

    user = get_current_user()
    if not user:
        st.error("Session expired.")
        return

    email = user.get("email", "")

    # Top layout with a clear chat option
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(
            "Ask questions about campus services, assignment planning, coding help, or exam topics."
        )
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True, key="clear_chat_btn"):
            if clear_chat_history(email):
                if "chat_messages" in st.session_state:
                    st.session_state["chat_messages"] = []
                st.success("Chat history cleared!")
                st.rerun()
            else:
                st.error("Failed to clear chat history.")

    st.markdown("---")

    # Render full chat interface
    build_chat_interface(email)
