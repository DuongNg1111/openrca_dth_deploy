import streamlit as st
import pandas as pd

from src.auth.google_auth import require_login


st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)


require_login()

# ==========================
# PAGE TITLE
# ==========================

st.title("🏠 OpenRCA Dashboard")
st.caption("Root Cause Analysis Monitoring Dashboard")

st.divider()

# ==========================
# KPI CARDS
# ==========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Incidents",
        value=25
    )

with col2:
    st.metric(
        label="Created",
        value=6
    )

with col3:
    st.metric(
        label="Processing",
        value=4
    )

with col4:
    st.metric(
        label="Done",
        value=15
    )

st.divider()

# ==========================
# INCIDENT TREND
# ==========================

st.subheader("📈 Incident Trend")

trend = pd.DataFrame(
    {
        "Incidents": [3, 5, 4, 6, 2, 4, 1]
    },
    index=[
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ],
)

st.line_chart(trend)

st.divider()

# ==========================
# RECENT INCIDENTS
# ==========================

st.subheader("📋 Recent Incidents")

recent = pd.DataFrame(
    {
        "Ticket": [
            "RCA-001",
            "RCA-002",
            "RCA-003",
        ],
        "Date": [
            "2026-07-28 15:42",
            "2026-07-28 14:10",
            "2026-07-27 18:25",
        ],
        "Affected System": [
            "productcatalogservice",
            "checkoutservice",
            "paymentservice",
        ],
        "Status": [
            "Created",
            "Processing",
            "Done",
        ],
    }
)

st.dataframe(
    recent,
    use_container_width=True,
    hide_index=True,
)

# ==========================
# SYSTEM HEALTH
# ==========================

st.subheader("🖥️ System Health")

c1, c2 = st.columns(2)

with c1:
    st.success("🟢 PostgreSQL Connected")
    st.success("🟢 Dataset Ready")

with c2:
    st.warning("🟡 Jira Waiting")
    st.success("🟢 Pipeline Ready")