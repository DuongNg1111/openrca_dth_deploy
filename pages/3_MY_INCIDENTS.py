import streamlit as st
import pandas as pd
import streamlit as st

from src.auth.google_auth import require_login


require_login()

st.title("📋 My Incidents")

st.caption(
    "View incidents that you have submitted."
)


st.divider()


# ==========================
# FILTER
# ==========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    status_filter = st.selectbox(
        "Status",
        [
            "All",
            "Created",
            "Processing",
            "Done",
        ]
    )


with col2:
    system_filter = st.selectbox(
        "Affected System",
        [
            "All",
            "productcatalogservice",
            "checkoutservice",
            "paymentservice",
        ]
    )


with col3:
    date_from = st.date_input(
        "From Date",
    )


with col4:
    date_to = st.date_input(
        "To Date",
    )

# ==========================
# INCIDENT DATA (TEMP)
# ==========================

incidents = pd.DataFrame(
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


# ==========================
# FILTER LOGIC
# ==========================

filtered = incidents.copy()


# Status filter
if status_filter != "All":
    filtered = filtered[
        filtered["Status"] == status_filter
    ]


# System filter
if system_filter != "All":
    filtered = filtered[
        filtered["Affected System"] == system_filter
    ]


# Date range filter
filtered["Date"] = pd.to_datetime(
    filtered["Date"]
)


filtered = filtered[
    (filtered["Date"].dt.date >= date_from)
    &
    (filtered["Date"].dt.date <= date_to)
]

# ==========================
# DISPLAY
# ==========================

st.subheader("Incident List")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
)