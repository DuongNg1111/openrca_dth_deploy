import streamlit as st
import pandas as pd

from src.auth.google_auth import require_login

require_login()

# ==========================
# SESSION
# ==========================

if "selected_ticket" not in st.session_state:
    st.session_state.selected_ticket = None


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
        "Description": [
            "Product page is unavailable.",
            "Checkout is very slow.",
            "Payment failed for multiple users.",
        ],
    }
)


# ==========================================================
# INCIDENT LIST
# ==========================================================

if st.session_state.selected_ticket is None:

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
        date_from = st.date_input("From Date")

    with col4:
        date_to = st.date_input("To Date")

    # ==========================
    # FILTER LOGIC
    # ==========================

    filtered = incidents.copy()

    if status_filter != "All":
        filtered = filtered[
            filtered["Status"] == status_filter
        ]

    if system_filter != "All":
        filtered = filtered[
            filtered["Affected System"] == system_filter
        ]

    filtered["Date"] = pd.to_datetime(filtered["Date"])

    filtered = filtered[
        (filtered["Date"].dt.date >= date_from)
        &
        (filtered["Date"].dt.date <= date_to)
    ]

    # ==========================
    # DISPLAY
    # ==========================

    st.subheader("Incident List")

    header = st.columns([2, 2, 3, 2, 1])

    header[0].markdown("**Ticket**")
    header[1].markdown("**Date**")
    header[2].markdown("**Affected System**")
    header[3].markdown("**Status**")
    header[4].markdown("**Action**")

    st.divider()

    for _, row in filtered.iterrows():

        col1, col2, col3, col4, col5 = st.columns(
            [2, 2, 3, 2, 1]
        )

        col1.write(row["Ticket"])
        col2.write(row["Date"].strftime("%Y-%m-%d %H:%M"))
        col3.write(row["Affected System"])
        col4.write(row["Status"])

        if col5.button(
            "View",
            key=row["Ticket"]
        ):
            st.session_state.selected_ticket = row["Ticket"]
            st.rerun()


# ==========================================================
# INCIDENT DETAILS
# ==========================================================

else:

    ticket = st.session_state.selected_ticket

    incident = incidents[
        incidents["Ticket"] == ticket
    ].iloc[0]

    if st.button("← Back to My Incidents"):
        st.session_state.selected_ticket = None
        st.rerun()

    st.title("📄 Incident Details")

    st.caption(
        "View detailed information for the selected incident."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Ticket**")
        st.write(incident["Ticket"])

        st.markdown("**Affected System**")
        st.write(incident["Affected System"])

        st.markdown("**Status**")
        st.write(incident["Status"])

    with col2:
        st.markdown("**Incident Time**")
        st.write(incident["Date"])

    st.markdown("### Description")

    st.write(
        incident["Description"]
    )

    st.divider()

    st.subheader("Investigation Progress")

    if incident["Status"] == "Created":
        st.info("🟢 Created")

    elif incident["Status"] == "Processing":
        st.info(
            """
🟢 Created

🟡 Processing
"""
        )

    else:
        st.success(
            """
🟢 Created

🟢 Processing

🟢 Done
"""
        )