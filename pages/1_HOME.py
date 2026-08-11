import streamlit as st
import pandas as pd

from src.auth.google_auth import require_login

from src.database.repository import (
    get_dashboard_summary,
    get_incident_trend,
    get_recent_incidents
)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)


# ==========================================================
# AUTHENTICATION
# ==========================================================

require_login()


# ==========================================================
# CURRENT USER
# ==========================================================

reporter_email = st.user.email


# ==========================================================
# PAGE TITLE
# ==========================================================

st.title(
    "🏠 OpenRCA Dashboard"
)

st.caption(
    "Your Root Cause Analysis Dashboard"
)

st.divider()


# ==========================================================
# LOAD DATA
# ==========================================================

summary = get_dashboard_summary(
    reporter_email
)

trend = get_incident_trend(
    reporter_email
)

recent = get_recent_incidents(
    reporter_email,
    limit=5
)


# ==========================================================
# KPI CARDS
# ==========================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="Total Incidents",
        value=int(
            summary["total_incidents"]
        )
    )


with col2:

    st.metric(
        label="Created",
        value=int(
            summary["created"]
        )
    )


with col3:

    st.metric(
        label="Processing",
        value=int(
            summary["processing"]
        )
    )


with col4:

    st.metric(
        label="Completed",
        value=int(
            summary["completed"]
        )
    )


st.divider()


# ==========================================================
# INCIDENT TREND
# ==========================================================

st.subheader(
    "📈 My Incident Trend"
)


if trend.empty:

    st.info(
        "No incident data available yet."
    )

else:

    trend["incident_date"] = pd.to_datetime(
        trend["incident_date"]
    )

    trend = trend.set_index(
        "incident_date"
    )

    st.line_chart(
        trend["incidents"]
    )


st.divider()


# ==========================================================
# RECENT INCIDENTS
# ==========================================================

st.subheader(
    "📋 Recent Incidents"
)


if recent.empty:

    st.info(
        "You have not submitted any incidents yet."
    )

else:

    recent["created_at"] = pd.to_datetime(
        recent["created_at"]
    )


    recent_display = recent.copy()


    recent_display["created_at"] = (
        recent_display["created_at"]
        .dt.strftime("%Y-%m-%d %H:%M")
    )


    recent_display = recent_display.rename(
        columns={
            "issue_key": "Ticket",
            "created_at": "Created Date",
            "affected_system": "Affected System",
            "status": "Status"
        }
    )


    recent_display = recent_display[
        [
            "Ticket",
            "Created Date",
            "Affected System",
            "Status"
        ]
    ]


    st.dataframe(
        recent_display,
        use_container_width=True,
        hide_index=True
    )


