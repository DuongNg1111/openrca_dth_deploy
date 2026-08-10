import streamlit as st
import pandas as pd

from src.auth.google_auth import require_login
from src.database.repository import (
    get_user_incidents,
    get_incident_detail,
get_rca_results
)


# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="My Incidents",
    page_icon="📋",
    layout="wide"
)


require_login()


# ==========================
# SESSION
# ==========================

if "selected_ticket" not in st.session_state:
    st.session_state.selected_ticket = None



# ==========================
# LOAD DATA
# ==========================

incidents = get_user_incidents(
    st.user.email
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



    if incidents.empty:

        st.info(
            "No incidents found."
        )

        st.stop()



    # ==========================
    # FILTER
    # ==========================

    col1, col2, col3, col4 = st.columns(
        4,
        gap="small"
    )


    # --------------------------
    # STATUS
    # --------------------------

    with col1:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "Created",
                "Processing",
                "Completed"
            ]
        )


    # --------------------------
    # AFFECTED SYSTEM
    # --------------------------

    with col2:

        system_options = [
            "All"
        ] + sorted(
            incidents["affected_system"]
            .dropna()
            .unique()
            .tolist()
        )


        system_filter = st.selectbox(
            "Affected System",
            system_options
        )


    # --------------------------
    # CREATED FROM
    # --------------------------

    with col3:

        date_from = st.date_input(
            "Created From"
        )


    # --------------------------
    # CREATED TO
    # --------------------------

    with col4:

        date_to = st.date_input(
            "Created To"
        )



    # ==========================
    # FILTER LOGIC
    # ==========================

    filtered = incidents.copy()



    if status_filter != "All":

        filtered = filtered[
            filtered["status"]
            == status_filter
        ]



    if system_filter != "All":

        filtered = filtered[
            filtered["affected_system"]
            == system_filter
        ]



    filtered["created_at"] = pd.to_datetime(
        filtered["created_at"]
    )



    filtered = filtered[
        (
            filtered["created_at"]
            .dt.date >= date_from
        )
        &
        (
            filtered["created_at"]
            .dt.date <= date_to
        )
    ]
    # ==========================
    # TABLE HEADER
    # ==========================

    st.subheader(
        "Incident List"
    )


    header = st.columns(
        [2,2,3,2,1]
    )


    header[0].markdown(
        "**Ticket**"
    )

    header[1].markdown(
        "**Created Date**"
    )

    header[2].markdown(
        "**Affected System**"
    )

    header[3].markdown(
        "**Status**"
    )

    header[4].markdown(
        "**Action**"
    )


    st.divider()



    # ==========================
    # TABLE ROW
    # ==========================

    for _, row in filtered.iterrows():


        col1, col2, col3, col4, col5 = st.columns(
            [2,2,3,2,1]
        )


        col1.write(
            row["issue_key"]
        )


        col2.write(
            row["created_at"]
            .strftime("%Y-%m-%d %H:%M")
        )


        col3.write(
            row["affected_system"]
        )


        col4.write(
            row["status"]
        )



        if col5.button(
            "View",
            key=f"view_{row['issue_key']}"
        ):

            st.session_state.selected_ticket = (
                row["issue_key"]
            )

            st.rerun()





# ==========================================================
# INCIDENT DETAIL
# ==========================================================

else:


    ticket = st.session_state.selected_ticket


    incident_df = get_incident_detail(
        ticket
    )


    if incident_df.empty:

        st.error(
            "Incident not found."
        )

        st.session_state.selected_ticket = None

        st.stop()



    incident = incident_df.iloc[0]
    st.write("DEBUG investigation ID:", incident["id"])


    if st.button(
        "← Back to My Incidents"
    ):

        st.session_state.selected_ticket = None

        st.rerun()



    st.title(
        "📄 Incident Details"
    )


    st.caption(
        "View detailed information for the selected incident."
    )


    st.divider()



    col1, col2 = st.columns(2)



    with col1:

        st.markdown(
            "**Ticket ID**"
        )

        st.write(
            incident["issue_key"]
        )


        st.markdown(
            "**Affected System**"
        )

        st.write(
            incident["affected_system"]
        )


        st.markdown(
            "**Status**"
        )

        st.write(
            incident["status"]
        )



    with col2:


        st.markdown(
            "**Environment**"
        )

        st.write(
            incident["environment"]
        )


        st.markdown(
            "**Incident Time**"
        )

        st.write(
            incident["incident_time"]
        )



    st.divider()


    st.markdown(
        "### Description"
    )


    st.write(
        incident["incident_description"]
    )



    st.divider()


    st.subheader(
        "Investigation Progress"
    )


    status = incident["status"]


    if status == "Created":

        st.info(
            """
🟢 Incident Created

⏳ Waiting for RCA investigation
"""
        )


    elif status == "Processing":

        st.info(
            """
🟢 Incident Created

🟡 RCA Investigation Running
"""
        )


    elif status == "Completed":

        st.success(
            """
🟢 Incident Created

🟢 RCA Investigation Completed
"""
        )


    else:

        st.warning(
            f"Current status: {status}"
        )

    # =====================================================
    # RCA RESULTS
    # =====================================================

    st.divider()

    st.subheader("🔍 Root Cause Analysis")

    rca_df = get_rca_results(
        int(incident["id"])
    )
    if rca_df.empty:

        st.info(
            "RCA results are not available yet."
        )

    else:

        st.success(
            f"RCA completed — {len(rca_df)} service(s) analyzed."
        )

        for _, rca in rca_df.iterrows():

            st.markdown(
                f"### 🔧 {rca['root_cause']}"
            )

            col1, col2 = st.columns([4, 1])

            with col1:

                st.markdown("**Root Cause**")

                st.write(
                    rca["root_cause"]
                )

