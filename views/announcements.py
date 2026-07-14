"""
pages/announcements.py - Announcements page for Smart Campus AI.
"""

import streamlit as st

from database import get_announcements, add_announcement
from dashboard import render_topbar
from utils import format_datetime
from config import COLOR_DANGER, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_PRIMARY, COLOR_WARNING


CATEGORY_CONFIG: dict[str, dict] = {
    "Exam":           {"icon": "📋", "color": COLOR_DANGER},
    "Event":          {"icon": "🎉", "color": COLOR_SECONDARY},
    "Placement":      {"icon": "💼", "color": COLOR_SUCCESS},
    "General":        {"icon": "📢", "color": COLOR_PRIMARY},
    "Infrastructure": {"icon": "🏛️", "color": COLOR_WARNING},
}


def render_announcements() -> None:
    """Render the announcements page."""
    render_topbar("📢 Announcements")

    tab_all, tab_add = st.tabs(["📋 All Announcements", "➕ Add Announcement"])

    # ── All Announcements ─────────────────────────────────────────────────
    with tab_all:
        announcements = get_announcements()

        # Category filter
        categories = ["All"] + list(CATEGORY_CONFIG.keys())
        selected_cat = st.selectbox(
            "Filter by Category",
            categories,
            key="ann_filter",
            label_visibility="collapsed",
        )

        if selected_cat != "All":
            announcements = [a for a in announcements if a.get("category") == selected_cat]

        if not announcements:
            st.info("No announcements found.")
        else:
            for ann in announcements:
                cat = ann.get("category", "General")
                cfg = CATEGORY_CONFIG.get(cat, {"icon": "📢", "color": COLOR_PRIMARY})
                st.markdown(
                    f"""
                    <div class="announcement-card" style="border-left:4px solid {cfg['color']};">
                        <div class="ann-card-header">
                            <span class="ann-cat-badge" style="background:{cfg['color']};">
                                {cfg['icon']} {cat}
                            </span>
                            <span class="ann-card-date">
                                📅 {format_datetime(ann.get('date',''), '%d %b %Y, %I:%M %p')}
                            </span>
                        </div>
                        <div class="ann-card-title">{ann.get('title','')}</div>
                        <div class="ann-card-desc">{ann.get('description','')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ── Add Announcement ──────────────────────────────────────────────────
    with tab_add:
        st.markdown("### 📝 Post New Announcement")
        with st.form("add_announcement_form"):
            title = st.text_input("Title", placeholder="Announcement title…")
            category = st.selectbox("Category", list(CATEGORY_CONFIG.keys()))
            description = st.text_area(
                "Description",
                placeholder="Write the full announcement here…",
                height=150,
            )
            submit = st.form_submit_button("📢 Post Announcement", use_container_width=True)

        if submit:
            if not title.strip() or not description.strip():
                st.error("Title and description are required.")
            else:
                success = add_announcement(title.strip(), description.strip(), category)
                if success:
                    st.success("✅ Announcement posted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to post announcement.")
