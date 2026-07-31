import streamlit as st
from datetime import datetime

from src.auth.google_auth import require_login
from src.jira.jira_client import create_issue


require_login()

st.set_page_config(
    page_title="Report Incident Form",
    page_icon="🚨",
    layout="wide"
)

st.markdown(
    """
    <h1 style="
        text-align:center;
        margin-bottom:0;
        padding-left:18px;
    ">
        REPORT INCIDENT FORM
    </h1>

    <p style="
        text-align:center;
        font-style:italic;
        color:gray;
        margin-top:8px;
    ">
        Please provide the incident details using the form below.
    </p>

    <hr style="margin-top:25px; margin-bottom:30px;">
    """,
    unsafe_allow_html=True
)

with st.form(
    "incident_form",
    clear_on_submit=True
):

    # ==========================
    # Incident Description
    # ==========================

    st.markdown("#### Incident Description")

    st.caption(
        "Please describe the incident in English if you have any details."
    )

    incident_description = st.text_area(
        label="",
        placeholder="e.g., Cannot find product AAA or payment service timeout.",
        height=180,
        label_visibility="collapsed"
    )

    st.divider()

    # ==========================
    # Environment & Affected System
    # ==========================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Environment *")
        st.caption("Select the deployment environment.")

        environment = st.selectbox(
            label="",
            options=[
                "-- Select Environment --",
                "Cloud A",
                "Cloud B"
            ],
            label_visibility="collapsed"
        )

    with col2:

        st.markdown("### Affected System *")
        st.caption("Select the affected business system.")

        affected_system = st.selectbox(
            label="",
            options=[
                "-- Select Affected System --",
                "Website / Application",
                "Products",
                "Search Products",
                "Shopping Cart",
                "Order",
                "Shipping & Delivery",
                "Payment",
                "Billing & Invoice",
                "Prices",
                "Email Notifications",
                "Promotions"
            ],
            label_visibility="collapsed"
        )

    st.write("")

    # ==========================
    # Incident Date & Time
    # ==========================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Incident Date *")
        st.caption("Select the incident date.")

        incident_date = st.date_input(
            label="",
            label_visibility="collapsed"
        )

    with col2:

        st.markdown("### Incident Time *")
        st.caption("Select the incident time.")

        incident_time = st.time_input(
            label="",
            label_visibility="collapsed"
        )

    incident_datetime = datetime.combine(
        incident_date,
        incident_time
    )

    st.write("")

    submitted = st.form_submit_button(
        "SUBMIT INCIDENT",
        use_container_width=True,
        type="primary"
    )


# =====================================================
# FORM VALIDATION
# =====================================================

if submitted:

    if environment == "-- Select Environment --":

        st.error(
            "Please select an environment."
        )

    elif affected_system == "-- Select Affected System --":

        st.error(
            "Please select the affected system."
        )

    else:

        issue_key = create_issue(
            incident_description=incident_description,
            environment=environment,
            affected_system=affected_system,
            incident_time=incident_datetime,
            reporter_name=st.user.name,
            reporter_email=st.user.email
        )
        st.success("✅ Incident submitted successfully!")

        st.info(
            f"""
        **Ticket ID:** `{issue_key}`

        Your incident has been recorded successfully.

        Track its progress in **My Incidents**.
        """
        )