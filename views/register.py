"""
pages/register.py - Registration page for Smart Campus AI.
"""

import streamlit as st

from auth import register_user
from config import SESSION_PAGE, APP_NAME, APP_ICON, DEPARTMENTS


def render_register() -> None:
    """Render the registration form and handle new user creation."""
    _, col, _ = st.columns([0.5, 2, 0.5])

    with col:
        st.markdown(
            f"""
            <div class="auth-card">
                <div class="auth-logo">{APP_ICON}</div>
                <div class="auth-title">Create Account</div>
                <div class="auth-subtitle">Join {APP_NAME} – your smart campus portal</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("register_form", clear_on_submit=False):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="form-label">👤 Full Name</div>', unsafe_allow_html=True)
                name = st.text_input(
                    "Full Name",
                    placeholder="John Doe",
                    label_visibility="collapsed",
                )

                st.markdown('<div class="form-label">📧 Email Address</div>', unsafe_allow_html=True)
                email = st.text_input(
                    "Email",
                    placeholder="you@university.edu",
                    label_visibility="collapsed",
                )

                st.markdown('<div class="form-label">📱 Mobile Number</div>', unsafe_allow_html=True)
                phone = st.text_input(
                    "Mobile",
                    placeholder="9876543210",
                    label_visibility="collapsed",
                )

                st.markdown('<div class="form-label">🎓 Student ID</div>', unsafe_allow_html=True)
                student_id = st.text_input(
                    "Student ID",
                    placeholder="CS2021001",
                    label_visibility="collapsed",
                )

            with col2:
                st.markdown(
                    '<div class="form-label">🏛️ Department</div>', unsafe_allow_html=True
                )
                department = st.selectbox(
                    "Department",
                    DEPARTMENTS,
                    label_visibility="collapsed",
                )

                st.markdown(
                    '<div class="form-label">🔒 Password</div>', unsafe_allow_html=True
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Min 8 characters",
                    label_visibility="collapsed",
                )

                st.markdown(
                    '<div class="form-label">🔒 Confirm Password</div>', unsafe_allow_html=True
                )
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Repeat your password",
                    label_visibility="collapsed",
                )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                agree = st.checkbox("I agree to the Terms & Conditions")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("✅ Create Account", use_container_width=True)

        if submit:
            if not agree:
                st.warning("⚠️ Please agree to the Terms & Conditions.")
            else:
                with st.spinner("Creating your account…"):
                    success, message = register_user(
                        name, email, phone, student_id, department, password, confirm_password
                    )
                if success:
                    st.success(
                        "🎉 Account created successfully! Please sign in with your credentials."
                    )
                    st.balloons()
                    import time
                    time.sleep(2)
                    st.session_state[SESSION_PAGE] = "login"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-divider"><span>Already have an account?</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("🔑 Sign In", use_container_width=True, key="go_login"):
            st.session_state[SESSION_PAGE] = "login"
            st.rerun()
