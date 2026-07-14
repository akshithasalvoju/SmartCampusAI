"""
utils.py - Shared utility functions for Smart Campus AI.

Covers CSS injection, metric card rendering, chart generation,
date/time helpers, and other reusable UI primitives.
"""

from __future__ import annotations

import os
import base64
from datetime import datetime, date
from typing import Any

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from config import (
    ASSETS_DIR,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
)


# ---------------------------------------------------------------------------
# CSS / styling helpers
# ---------------------------------------------------------------------------


def load_css(filepath: str = "styles.css") -> None:
    """
    Inject the contents of *filepath* into the Streamlit app as CSS.

    Parameters
    ----------
    filepath : str
        Path to the CSS file, relative to the project root.
    """
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)


def inject_custom_css(css: str) -> None:
    """Wrap *css* in a ``<style>`` tag and inject it."""
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------


def image_to_base64(path: str) -> str:
    """
    Convert an image file to a Base-64 string.

    Parameters
    ----------
    path : str

    Returns
    -------
    str
        Empty string if the file does not exist.
    """
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()


def get_asset_b64(filename: str) -> str:
    """Return the base-64 encoded content of an asset file."""
    return image_to_base64(os.path.join(ASSETS_DIR, filename))


# ---------------------------------------------------------------------------
# Metric / card UI helpers
# ---------------------------------------------------------------------------


def metric_card(
    label: str,
    value: str | int | float,
    icon: str = "📊",
    color: str = COLOR_PRIMARY,
    delta: str = "",
) -> None:
    """
    Render a glassmorphism metric card.

    Parameters
    ----------
    label : str
    value : str | int | float
    icon : str
    color : str
        CSS colour string for the card accent.
    delta : str
        Optional delta indicator text (e.g. "+5%").
    """
    delta_html = (
        f'<div class="metric-delta" style="color:{COLOR_SUCCESS};">{delta}</div>'
        if delta
        else ""
    )
    st.markdown(
        f"""
        <div class="metric-card" style="border-left: 4px solid {color};">
            <div class="metric-icon">{icon}</div>
            <div class="metric-content">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                {delta_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_card(title: str, body: str, icon: str = "ℹ️") -> None:
    """Render a simple info card."""
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-card-header">
                <span class="info-icon">{icon}</span>
                <span class="info-title">{title}</span>
            </div>
            <div class="info-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(text: str, color: str = COLOR_PRIMARY) -> str:
    """Return an HTML badge string."""
    return (
        f'<span class="badge" style="background:{color};color:#fff;'
        f'padding:2px 10px;border-radius:12px;font-size:0.75rem;">{text}</span>'
    )


def status_badge(status: str) -> str:
    """Return a colour-coded status badge."""
    colors = {
        "pending": COLOR_WARNING,
        "in_progress": COLOR_SECONDARY,
        "completed": COLOR_SUCCESS,
        "overdue": COLOR_DANGER,
    }
    labels = {
        "pending": "🕐 Pending",
        "in_progress": "⚡ In Progress",
        "completed": "✅ Completed",
        "overdue": "❌ Overdue",
    }
    color = colors.get(status, COLOR_PRIMARY)
    label = labels.get(status, status.replace("_", " ").title())
    return badge(label, color)


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------


def attendance_donut(percentage: float, student_name: str = "") -> go.Figure:
    """
    Build a donut chart for attendance percentage.

    Parameters
    ----------
    percentage : float
    student_name : str

    Returns
    -------
    go.Figure
    """
    color = (
        COLOR_SUCCESS if percentage >= 75 else COLOR_WARNING if percentage >= 60 else COLOR_DANGER
    )

    fig = go.Figure(
        go.Pie(
            values=[percentage, 100 - percentage],
            hole=0.72,
            marker_colors=[color, "rgba(255,255,255,0.08)"],
            textinfo="none",
            hoverinfo="none",
        )
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"<b>{percentage}%</b>",
                x=0.5,
                y=0.5,
                font=dict(size=22, color=color),
                showarrow=False,
            )
        ],
        height=200,
    )
    return fig


def weekly_activity_bar(data: dict[str, int]) -> go.Figure:
    """
    Create a bar chart for weekly activity.

    Parameters
    ----------
    data : dict[str, int]
        Map of day name → activity count.

    Returns
    -------
    go.Figure
    """
    days = list(data.keys())
    values = list(data.values())

    fig = go.Figure(
        go.Bar(
            x=days,
            y=values,
            marker=dict(
                color=values,
                colorscale=[[0, COLOR_SECONDARY], [1, COLOR_PRIMARY]],
                line=dict(width=0),
            ),
            text=values,
            textposition="outside",
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8"),
        xaxis=dict(showgrid=False, color="#94A3B8"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)", color="#94A3B8"),
        margin=dict(t=20, b=20, l=20, r=20),
        height=250,
    )
    return fig


def assignment_status_pie(pending: int, in_progress: int, completed: int) -> go.Figure:
    """
    Build a pie chart showing assignment status distribution.

    Parameters
    ----------
    pending, in_progress, completed : int

    Returns
    -------
    go.Figure
    """
    fig = go.Figure(
        go.Pie(
            labels=["Pending", "In Progress", "Completed"],
            values=[pending, in_progress, completed],
            hole=0.45,
            marker_colors=[COLOR_WARNING, COLOR_SECONDARY, COLOR_SUCCESS],
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8"),
        legend=dict(font=dict(color="#94A3B8")),
        margin=dict(t=10, b=10, l=10, r=10),
        height=250,
    )
    return fig


def attendance_bar_chart(subjects: list[str], percentages: list[float]) -> go.Figure:
    """
    Horizontal bar chart for subject-wise attendance.

    Parameters
    ----------
    subjects : list[str]
    percentages : list[float]

    Returns
    -------
    go.Figure
    """
    colors = [
        COLOR_SUCCESS if p >= 75 else COLOR_WARNING if p >= 60 else COLOR_DANGER
        for p in percentages
    ]
    fig = go.Figure(
        go.Bar(
            x=percentages,
            y=subjects,
            orientation="h",
            marker_color=colors,
            text=[f"{p}%" for p in percentages],
            textposition="outside",
        )
    )
    fig.add_vline(x=75, line_dash="dash", line_color=COLOR_WARNING, annotation_text="75% min")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8"),
        xaxis=dict(
            range=[0, 110],
            showgrid=True,
            gridcolor="rgba(255,255,255,0.07)",
            color="#94A3B8",
        ),
        yaxis=dict(showgrid=False, color="#94A3B8"),
        margin=dict(t=20, b=20, l=10, r=40),
        height=max(200, len(subjects) * 50),
    )
    return fig


# ---------------------------------------------------------------------------
# Date / time helpers
# ---------------------------------------------------------------------------


def format_datetime(iso_string: str, fmt: str = "%d %b %Y, %I:%M %p") -> str:
    """
    Format an ISO 8601 datetime string for display.

    Parameters
    ----------
    iso_string : str
    fmt : str

    Returns
    -------
    str
    """
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime(fmt)
    except (ValueError, TypeError):
        return iso_string


def days_until(date_str: str) -> int:
    """
    Return the number of days from today until *date_str* (YYYY-MM-DD).

    Negative values mean the date has passed.

    Parameters
    ----------
    date_str : str

    Returns
    -------
    int
    """
    try:
        target = date.fromisoformat(date_str)
        return (target - date.today()).days
    except (ValueError, TypeError):
        return 0


def get_greeting() -> str:
    """Return a time-appropriate greeting string."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


# ---------------------------------------------------------------------------
# Notification helpers
# ---------------------------------------------------------------------------


def push_notification(message: str, type_: str = "info") -> None:
    """
    Add a notification to the session notification queue.

    Parameters
    ----------
    message : str
    type_ : str
        One of ``info``, ``success``, ``warning``, ``error``.
    """
    if "notifications" not in st.session_state:
        st.session_state["notifications"] = []
    st.session_state["notifications"].append(
        {"message": message, "type": type_, "time": datetime.now().isoformat()}
    )


def show_toast(message: str, icon: str = "✅") -> None:
    """Display a Streamlit toast notification."""
    st.toast(message, icon=icon)
