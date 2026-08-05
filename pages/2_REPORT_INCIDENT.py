import streamlit as st
from datetime import datetime

from src.auth.google_auth import require_login
from src.jira.jira_client import create_issue
from src.database.repository import create_investigation


require_login()


st.set_page_config(
    page_title="Report Incident Form",
    page_icon="🚨",
    layout="wide"
)


# =====================================================
# HEADER
# =====================================================

st.markdown(
    """
    <style>
    .incident-title {
        background-color: #EAF4FF;
        border: 1px solid #D9D9D9;
        border-radius: 8px;
        padding: 20px 24px;
    }

    .incident-title h1 {
        color: #1F4E79;
        margin: 0;
        font-size: 32px;
        font-weight: 700;
        text-align: left;
    }

    .incident-title p {
        color: #666;
        margin: 8px 0 0 0;
        font-size: 16px;
        font-style: italic;
        text-align: left;
    }
    </style>

    <div class="incident-title">
        <h1>INCIDENT REPORT FORM</h1>
        <p>Please provide the incident details using the form below.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# FORM
# =====================================================

with st.form(
    "incident_form",
    clear_on_submit=True
):

    # ==========================
    # Environment & Affected System
    # ==========================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Environment *")

        st.caption(
            "Select the deployment environment."
        )

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

        st.caption(
            "Select the affected business system."
        )

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

        st.caption(
            "Select the incident date."
        )

        incident_date = st.date_input(
            label="",
            label_visibility="collapsed"
        )


    with col2:

        st.markdown("### Incident Time *")

        st.caption(
            "Select the incident time."
        )

        incident_time = st.time_input(
            label="",
            label_visibility="collapsed"
        )


    incident_datetime = datetime.combine(
        incident_date,
        incident_time
    )


    st.write("")


    # ==========================
    # Incident Description (MOVED DOWN)
    # ==========================

    st.divider()

    st.markdown("### Incident Description")

    st.caption(
        "Please describe the incident in English if you have any details."
    )

    incident_description = st.text_area(
        label="",
        placeholder="e.g., Cannot find product AAA or payment service timeout.",
        height=180,
        label_visibility="collapsed"
    )


    st.write("")


    # ==========================
    # SUBMIT BUTTON
    # ==========================

    st.markdown(
        """
        <style>
        div[data-testid="stFormSubmitButton"] button {
            background-color:#1F4E79;
            color:white;
            border-radius:8px;
            padding:12px 45px;
            font-size:25px;
            font-weight:600;
            border:none;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            background-color:#163A5C;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
        
    left, button_col = st.columns([4, 1])

    with button_col:
        submitted = st.form_submit_button(
            "**SUBMIT INCIDENT**",
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

        investigation_id = create_investigation(
        issue_key=issue_key,
        environment=environment,
        affected_system=affected_system,
        dataset="",
        incident_time=incident_datetime,
        window_start=None,
        window_end=None,
        incident_description=incident_description,
        reporter=st.user.name,
        reporter_email=st.user.email
    )
        st.success(
            "✅ Incident submitted successfully!"
        )


        st.info(
            f"""
        **Ticket ID:** `{issue_key}`

        Your incident has been recorded successfully.

        Track its progress in **My Incidents**.
        """
        )