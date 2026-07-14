"""
pages/login.py - Login page for Smart Campus AI.
"""

import streamlit as st

from auth import login_user
from config import SESSION_PAGE, APP_NAME, APP_ICON


def render_login() -> None:
    """Render the login form and handle authentication."""
    # Centered layout
    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        st.markdown(
            f"""
            <div class="auth-card">
                <div class="auth-logo">{APP_ICON}</div>
                <div class="auth-title">{APP_NAME}</div>
                <div class="auth-subtitle">Sign in to your student portal</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            st.markdown(
                '<div class="form-label">📧 Email Address</div>', unsafe_allow_html=True
            )
            email = st.text_input(
                "Email",
                placeholder="you@university.edu",
                label_visibility="collapsed",
            )

            st.markdown(
                '<div class="form-label">🔒 Password</div>', unsafe_allow_html=True
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                label_visibility="collapsed",
            )

            col_r, col_f = st.columns([1, 1])
            with col_r:
                remember = st.checkbox("Remember me")
            # (Remember-me persists the email in session for UX only)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 Sign In", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                with st.spinner("Authenticating…"):
                    success, message = login_user(email, password)
                if success:
                    if remember:
                        st.session_state["remembered_email"] = email
                    st.success("Login successful! Redirecting…")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

        # Pre-fill email if remembered
        if "remembered_email" in st.session_state and not email:
            st.info(f"💡 Remembered email: {st.session_state['remembered_email']}")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-divider"><span>Don\'t have an account?</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("📝 Create Account", use_container_width=True, key="go_register"):
            st.session_state[SESSION_PAGE] = "register"
            st.rerun()

        # Demo credentials info
        st.markdown(
            """
            <div class="demo-info">
                <b>🎓 Demo Account</b><br>
                Register a new account to get started!<br>
                All fields accept any valid inputs.
            </div>
            """,
            unsafe_allow_html=True,
        )
