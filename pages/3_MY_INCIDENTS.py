import streamlit as st
import pandas as pd
import re

from src.auth.google_auth import require_login
from src.database.repository import (
    get_user_incidents,
    get_incident_detail,
    get_rca_results,
    get_investigation_metrics,
    get_investigation_logs,
    get_investigation_traces,
    get_investigation_evidence,
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
                "Completed",
                "No Data"
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
            key=f"view_{row['id']}_{row['issue_key']}"
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
    st.write("Investigation ID:", incident["id"])


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
    # AI INCIDENT INVESTIGATION

    investigation_id = int(
        incident["id"]
    )

    # =====================================================
    # LOAD DATA
    # =====================================================

    rca_df = get_rca_results(
        investigation_id
    )

    evidence_df = get_investigation_evidence(
        investigation_id
    )

    if not evidence_df.empty:
        evidence_df["evidence_type"] = (
            evidence_df["evidence_type"]
            .fillna("")
            .astype(str)
            .str.lower()
        )

    # =====================================================
    # EVIDENCE COUNTS
    # =====================================================

    metric_df = pd.DataFrame()
    log_df = pd.DataFrame()
    trace_df = pd.DataFrame()

    if not evidence_df.empty:

        metric_df = evidence_df[
            evidence_df["evidence_type"].str.contains(
                "metric",
                na=False
            )
        ]

        log_df = evidence_df[
            evidence_df["evidence_type"].str.contains(
                "log",
                na=False
            )
        ]

        trace_df = evidence_df[
            evidence_df["evidence_type"].str.contains(
                "trace",
                na=False
            )
        ]

    metric_count = len(metric_df)
    log_count = len(log_df)
    trace_count = len(trace_df)
    total_evidence = len(evidence_df)


    st.markdown("## 🤖 AI Incident Investigation")

    st.caption(
        "Understand what happened, why it happened, "
        "and what should be investigated next."
    )


    if rca_df.empty:

        st.info(
            "No RCA result was generated for this incident."
        )

    else:

        # =================================================
        # INCIDENT OVERVIEW
        # =================================================

        service_names = []

        for _, rca in rca_df.iterrows():

            service_names.append(
                str(
                    rca.get(
                        "service",
                        "Unknown service"
                    )
                )
            )

        affected_service = ", ".join(
            dict.fromkeys(service_names)
        )

        max_confidence = max(
            [
                float(
                    rca.get(
                        "confidence",
                        0
                    )
                )
                for _, rca in rca_df.iterrows()
            ]
            or [0]
        )


        st.markdown("### Investigation Overview")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "AI Confidence",
                f"{max_confidence:.0f}%"
            )

        with c2:
            st.metric(
                "Evidence",
                int(metric_count + log_count + trace_count)
            )

        with c3:
            st.metric(
                "Metrics",
                int(metric_count)
            )

        with c4:
            st.metric(
                "Traces",
                int(trace_count)
            )

        st.caption(
            f"Primary service investigated: **{affected_service}**"
        )


        # =================================================
        # TELEMETRY EVIDENCE
        # =================================================

        st.markdown("### 🔎 Telemetry Evidence")

        # =================================================
        # METRICS
        # =================================================

        st.markdown("#### 📊 Metrics")

        if metric_df.empty:

            st.info(
                "No significant metric anomaly was detected."
            )

        else:

            metric_rows = []

            metric_descriptions = {
                "cpu": "CPU utilization or CPU resource pressure of the service.",
                "memory": "Memory usage and memory pressure of the service.",
                "latency": "Time required for the service or operation to complete.",
                "duration": "Time required to process a request or operation.",
                "request duration": "Time required to complete a request.",
                "throughput": "Amount of traffic or data processed over time.",
                "error": "Number or rate of failed requests or operations.",
                "error rate": "Percentage of requests that result in an error.",
                "mrt": "Mean response time observed for the service.",
                "network": "Network traffic received or transmitted by the service.",
                "receive": "Network traffic received by the service.",
                "transmit": "Network traffic sent by the service.",
                "throttling": "Resource throttling indicating constrained service resources.",
            }

            def get_metric_description(metric_name, raw_description=""):
                name_lower = metric_name.lower()

                for keyword, description_text in metric_descriptions.items():
                    if keyword in name_lower:
                        return description_text

                if raw_description.strip():
                    return raw_description.strip()

                return "Abnormal telemetry signal detected for this service."

            for _, ev in metric_df.iterrows():

                metric_name = str(
                    ev.get(
                        "metric_name",
                        ev.get("name", "Metric")
                    )
                )

                value = ev.get("value", None)
                baseline = ev.get("baseline", None)

                deviation = None

                if (
                    pd.notna(value)
                    and pd.notna(baseline)
                    and float(baseline) != 0
                ):
                    deviation = (
                        (float(value) - float(baseline))
                        / abs(float(baseline))
                        * 100
                    )

                raw_description = str(
                    ev.get("description", "")
                )

                metric_rows.append(
                    {
                        "Metric": metric_name,
                        "Observed": (
                            f"{float(value):.3f}"
                            if pd.notna(value)
                            else "N/A"
                        ),
                        "Baseline": (
                            f"{float(baseline):.3f}"
                            if pd.notna(baseline)
                            else "N/A"
                        ),
                        "Deviation": (
                            f"{deviation:+.1f}%"
                            if deviation is not None
                            else "N/A"
                        ),
                        "Description": get_metric_description(
                            metric_name,
                            raw_description
                        ),
                    }
                )

            st.dataframe(
                pd.DataFrame(metric_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Metric": st.column_config.TextColumn(
                        "Metric",
                        width="medium"
                    ),
                    "Observed": st.column_config.TextColumn(
                        "Observed",
                        width="small"
                    ),
                    "Baseline": st.column_config.TextColumn(
                        "Baseline",
                        width="small"
                    ),
                    "Deviation": st.column_config.TextColumn(
                        "Deviation",
                        width="small"
                    ),
                    "Description": st.column_config.TextColumn(
                        "Description",
                        width="large"
                    ),
                },
            )
        # =================================================
        # LOGS
        # =================================================

        st.markdown("#### 📝 Logs")

        if log_df.empty:

            st.info(
                "No significant log anomaly was detected."
            )

        else:

            log_rows = []

            for _, ev in log_df.iterrows():

                log_name = str(
                    ev.get(
                        "log_name",
                        "Log evidence"
                    )
                )

                log_rows.append(
                    {
                        "Log": log_name,
                        "Status": "Relevant signal detected"
                    }
                )

            st.dataframe(
                pd.DataFrame(log_rows),
                use_container_width=True,
                hide_index=True,
            )

            for _, ev in log_df.iterrows():

                log_name = str(
                    ev.get(
                        "log_name",
                        "Log evidence"
                    )
                )

                value = ev.get("value", None)

                description = str(
                    ev.get("description", "")
                )

                with st.expander(
                    f"📝 {log_name}",
                    expanded=False
                ):

                    if pd.notna(value):

                        st.write(
                            str(value)
                        )

                    elif description.strip():

                        st.write(
                            description
                        )

                    else:

                        st.info(
                            "No additional log details available."
                        )


        # =================================================
        # TRACES
        # =================================================

        st.markdown("#### 🔗 Traces")

        if trace_df.empty:

            st.info(
                "No significant trace anomaly was detected."
            )

        else:

            trace_rows = []
            latency_values = []

            for index, (_, ev) in enumerate(
                trace_df.iterrows(),
                start=1
            ):

                operation = str(
                    ev.get(
                        "operation",
                        "Unknown operation"
                    )
                )

                operation_short = operation.split("/")[-1]

                if "." in operation_short:
                    operation_short = operation_short.split(".")[-1]

                value = ev.get("value", None)
                baseline = ev.get("baseline", None)

                deviation = None

                if (
                    pd.notna(value)
                    and pd.notna(baseline)
                    and float(baseline) != 0
                ):
                    deviation = (
                        (float(value) - float(baseline))
                        / abs(float(baseline))
                        * 100
                    )

                if pd.notna(value):
                    latency_values.append(float(value))

                trace_rows.append(
                    {
                        "Operation": (
                            f"{operation_short} #Trace-{index}"
                        ),
                        "Observed": (
                            f"{float(value):.3f} ms"
                            if pd.notna(value)
                            else "N/A"
                        ),
                        "Baseline": (
                            f"{float(baseline):.3f} ms"
                            if pd.notna(baseline)
                            else "N/A"
                        ),
                        "Deviation": (
                            f"{deviation:+.1f}%"
                            if deviation is not None
                            else "N/A"
                        ),
                    }
                )

            st.dataframe(
                pd.DataFrame(trace_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Operation": st.column_config.TextColumn(
                        "Operation",
                        width="large"
                    ),
                    "Observed": st.column_config.TextColumn(
                        "Observed",
                        width="small"
                    ),
                    "Baseline": st.column_config.TextColumn(
                        "Baseline",
                        width="small"
                    ),
                    "Deviation": st.column_config.TextColumn(
                        "Deviation",
                        width="small"
                    ),
                },
            )

            if latency_values:

                st.markdown("##### 📈 Latency Distribution")

                latency_df = pd.DataFrame(
                    {
                        "Trace": [
                            f"T{i}"
                            for i in range(
                                1,
                                len(latency_values) + 1
                            )
                        ],
                        "Latency (ms)": [
                            round(float(v), 2)
                            for v in latency_values
                        ],
                    }
                )

                st.line_chart(
                    latency_df.set_index("Trace"),
                    use_container_width=True,
                    height=300,
                )
        # =================================================
        # =================================================
        # RCA TYPOGRAPHY & CARD STYLES
        # =================================================

        st.markdown(
            """
            <style>

            /* ==============================
               Typography
            ============================== */

            .stApp {
                font-family:
                    "Inter",
                    -apple-system,
                    BlinkMacSystemFont,
                    "Segoe UI",
                    sans-serif;
            }

            h1 {
                font-size: 2rem !important;
                font-weight: 750 !important;
                letter-spacing: -0.02em !important;
            }

            h2 {
                font-size: 1.55rem !important;
                font-weight: 700 !important;
                letter-spacing: -0.015em !important;
            }

            h3 {
                font-size: 1.15rem !important;
                font-weight: 650 !important;
                letter-spacing: -0.005em !important;
            }

            p {
                font-size: 0.93rem;
                line-height: 1.55;
            }

            [data-testid="stCaptionContainer"] {
                font-size: 0.82rem;
                line-height: 1.45;
            }


            /* ==============================
               RCA Header
            ============================== */

            .rca-assessment-label {
                font-size: 0.72rem;
                font-weight: 650;
                letter-spacing: 0.04em;
                color: rgba(128, 128, 128, 0.85);
                margin-bottom: 3px;
            }

            .rca-service-name {
                font-size: 1.35rem;
                font-weight: 700;
                line-height: 1.3;
                margin-bottom: 4px;
            }


            /* ==============================
               Confidence
            ============================== */

            .confidence-label {
                font-size: 0.75rem;
                font-weight: 600;
                color: rgba(128, 128, 128, 0.85);
                margin-bottom: 2px;
            }

            .confidence-value {
                font-size: 1.65rem;
                font-weight: 750;
                line-height: 1.1;
            }


            /* ==============================
               Section Description
            ============================== */

            .section-description {
                font-size: 0.88rem;
                line-height: 1.5;
                color: rgba(128, 128, 128, 0.9);
                margin-top: -4px;
                margin-bottom: 12px;
            }


            /* ==============================
               Root Cause
            ============================== */

            .root-cause-label {
                font-size: 0.82rem;
                font-weight: 650;
                margin-bottom: 6px;
            }

            .root-cause-text {
                font-size: 0.95rem;
                line-height: 1.55;
            }

            </style>
            """,
            unsafe_allow_html=True
        )


        # AI CORRELATION
        # =================================================

        st.divider()

        st.markdown("### 🧠 Root Cause Analysis")

        st.markdown(
            '<div class="section-description">'
            'AI analyzes metrics, logs, and traces to identify the most likely root cause.'
            '</div>',
            unsafe_allow_html=True
        )

        for _, rca in rca_df.iterrows():

            service = str(
                rca.get(
                    "service",
                    "Unknown service"
                )
            )

            root_cause = str(
                rca.get(
                    "root_cause",
                    "Root cause unavailable."
                )
            )

            explanation = str(
                rca.get(
                    "explanation",
                    ""
                )
            )

            confidence = float(
                rca.get(
                    "confidence",
                    0
                )
            )

            # =================================================
            # RCA HEADER
            # =================================================

            h1, h2 = st.columns([4, 1])

            with h1:
                st.markdown(
                    '<div class="rca-assessment-label">'
                    'Root cause assessment'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="rca-service-name">{service}</div>',
                    unsafe_allow_html=True
                )

            with h2:
                confidence_level = (
                    "High"
                    if confidence >= 80
                    else "Medium"
                    if confidence >= 60
                    else "Low"
                )

                st.markdown(
                    '<div class="confidence-label">AI Confidence</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="confidence-value">'
                    f'{confidence:.0f}% · {confidence_level}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.progress(
                min(
                    max(confidence / 100, 0),
                    1
                )
            )

            # =================================================
            # =================================================
            # ROOT CAUSE
            # =================================================

            st.markdown("#### 🎯 Root Cause")

            # Clean legacy HTML that may already be stored
            # inside root_cause.
            clean_root_cause = re.sub(
                r"<[^>]+>",
                "",
                str(root_cause)
            )

            clean_root_cause = (
                clean_root_cause
                .replace("```html", "")
                .replace("```", "")
                .strip()
            )

            # -------------------------------------------------
            # Simplify the root cause for the UI
            # -------------------------------------------------

            simple_root_cause = clean_root_cause

            root_lower = clean_root_cause.lower()

            if (
                "performance degradation" in root_lower
                and "downstream" in root_lower
            ):
                simple_root_cause = (
                    f"{service} is slower than normal because "
                    "a dependent service or operation is taking "
                    "much longer than usual."
                )

            elif (
                "cpu throttling" in root_lower
                and "resource" in root_lower
            ):
                simple_root_cause = (
                    f"{service} is slower than normal because "
                    "it is experiencing CPU throttling and "
                    "limited resources."
                )

            elif (
                "high latency" in root_lower
                or "elevated latency" in root_lower
                or "latency degradation" in root_lower
            ):
                simple_root_cause = (
                    f"{service} is slower than normal because "
                    "some operations are taking much longer "
                    "than expected."
                )

            st.markdown(
                '<div class="root-cause-label">Primary finding</div>',
                unsafe_allow_html=True
            )

            st.info(simple_root_cause)

            # -------------------------------------------------
            # Why this happened
            # -------------------------------------------------

            st.markdown(
                '<div class="root-cause-label">Why this happened</div>',
                unsafe_allow_html=True
            )

            why_this_happened = ""

            # Try to derive a short explanation from the
            # original RCA explanation.
            if explanation:
                clean_explanation = re.sub(
                    r"<[^>]+>",
                    "",
                    str(explanation)
                )

                clean_explanation = (
                    clean_explanation
                    .replace("```html", "")
                    .replace("```", "")
                    .strip()
                )

                why_this_happened = clean_explanation

            # If the explanation is too long, use a simpler
            # explanation based on the root cause.
            if (
                not why_this_happened
                or len(why_this_happened) > 500
            ):
                if (
                    "downstream" in root_lower
                    or "dependent" in root_lower
                    or "dependency" in root_lower
                ):
                    why_this_happened = (
                        f"{service} depends on other services or "
                        "operations. When those dependencies became "
                        "slow, requests handled by the affected "
                        "service also took longer."
                    )

                elif (
                    "cpu" in root_lower
                    or "resource" in root_lower
                    or "throttling" in root_lower
                ):
                    why_this_happened = (
                        f"{service} did not have enough available "
                        "CPU resources to handle the workload "
                        "efficiently."
                    )

                elif (
                    "latency" in root_lower
                    or "duration" in root_lower
                    or "performance" in root_lower
                ):
                    why_this_happened = (
                        f"One or more operations handled by "
                        f"{service} became slower than normal, "
                        "which increased the overall response time."
                    )

                else:
                    why_this_happened = (
                        f"The available telemetry shows that "
                        f"{service} was performing slower than normal."
                    )

            st.markdown(
                f'<div class="section-description">'
                f'{why_this_happened}'
                f'</div>',
                unsafe_allow_html=True
            )

            # SUPPORTING EVIDENCE SUMMARY
            # =================================================

            st.markdown("### 🔎 Evidence Summary")

            total_evidence = (
                int(metric_count)
                + int(log_count)
                + int(trace_count)
            )

            e1, e2, e3, e4 = st.columns(4)

            with e1:
                st.metric(
                    "Total Evidence",
                    total_evidence
                )

            with e2:
                st.metric(
                    "Metrics",
                    int(metric_count)
                )

            with e3:
                st.metric(
                    "Logs",
                    int(log_count)
                )

            with e4:
                st.metric(
                    "Traces",
                    int(trace_count)
                )

            if (
                metric_count == 0
                and log_count == 0
                and trace_count == 0
            ):
                st.info(
                    "No telemetry evidence was available."
                )


            # =================================================
            # SUPPORTING EVIDENCE
            # =================================================

            st.markdown(
                '<div class="root-cause-label">'
                'Supporting evidence'
                '</div>',
                unsafe_allow_html=True
            )

            evidence_points = []

            # -------------------------------------------------
            # Metric evidence
            # -------------------------------------------------

            if metric_count > 0:
                evidence_points.append(
                    f"{service} has {int(metric_count)} metric "
                    "evidence record(s) showing abnormal performance."
                )

            # -------------------------------------------------
            # Trace evidence
            # -------------------------------------------------

            if trace_count > 0:
                evidence_points.append(
                    f"Trace data contains {int(trace_count)} "
                    "trace evidence record(s) showing abnormal "
                    "latency or operation duration."
                )

            # -------------------------------------------------
            # Log evidence
            # -------------------------------------------------

            if log_count > 0:
                evidence_points.append(
                    f"Log data contains {int(log_count)} "
                    "evidence record(s) related to the incident."
                )

            # -------------------------------------------------
            # Extract useful numbers from the explanation
            # -------------------------------------------------

            if explanation:
                explanation_text = re.sub(
                    r"<[^>]+>",
                    "",
                    str(explanation)
                )

                # Find latency / duration values from the
                # original RCA explanation.
                number_matches = re.findall(
                    r"(?:peak|up to|reached|spiked to|"
                    r"duration|latency)[^.;]{0,100}?"
                    r"([0-9]+(?:\.[0-9]+)?)\s*ms",
                    explanation_text,
                    flags=re.IGNORECASE
                )

                if number_matches:
                    unique_values = list(
                        dict.fromkeys(number_matches)
                    )

                    for value in unique_values[:3]:
                        evidence_points.append(
                            f"A latency or request duration "
                            f"of {value} ms was reported in the RCA evidence."
                        )

            # -------------------------------------------------
            # Fallback
            # -------------------------------------------------

            if not evidence_points:
                evidence_points.append(
                    "The available telemetry supports the "
                    "identified performance issue."
                )

            for point in evidence_points[:5]:
                st.markdown(
                    f"- {point}"
                )


            # =================================================
            # RECOMMENDED ACTIONS
            # =================================================

            st.markdown("### 🛠 Recommended Actions")

            root_lower = root_cause.lower()

            actions = []

            if any(
                word in root_lower
                for word in [
                    "latency",
                    "duration",
                    "performance",
                    "slow"
                ]
            ):
                actions.extend(
                    [
                        "Check the operations with the highest latency.",
                        "Check the dependent services for performance issues.",
                        "Monitor service latency after the issue is fixed.",
                    ]
                )

            if any(
                word in root_lower
                for word in [
                    "cpu",
                    "resource",
                    "throttling"
                ]
            ):
                actions.extend(
                    [
                        "Check CPU usage and CPU throttling for the affected service.",
                        "Increase CPU resources if throttling continues.",
                        "Monitor CPU usage after the change.",
                    ]
                )

            if not actions:
                actions.extend(
                    [
                        "Check the affected service for performance issues.",
                        "Check the services it depends on.",
                        "Monitor the service after the issue is fixed.",
                    ]
                )

            actions = list(dict.fromkeys(actions))

            for index, action in enumerate(
                actions,
                start=1
            ):
                st.markdown(
                    f"**{index}.** {action}"
                )

            # =================================================
            # TECHNICAL EVIDENCE
            # =================================================

            with st.expander(
                "🔧 Technical Evidence",
                expanded=True
            ):

                if explanation.strip():

                    st.markdown("##### Key Findings")

                    # Create short, user-friendly findings.
                    import re

                    clean_explanation = explanation.replace("\n", " ").strip()

                    # -------------------------------------------------
                    # Request performance
                    # -------------------------------------------------
                    st.markdown("**🔗 Request Performance**")

                    duration_match = re.search(
                        r"request duration.*?(?:peak of|reached)\s*"
                        r"([0-9]+(?:\.[0-9]+)?)\s*ms.*?"
                        r"(?:baseline of|baseline:)\s*"
                        r"([0-9]+(?:\.[0-9]+)?)\s*ms",
                        clean_explanation,
                        re.IGNORECASE,
                    )

                    mrt_match = re.search(
                        r"(?:mean response time|mrt).*?"
                        r"(?:spiked to|increased to|reached)\s*"
                        r"([0-9]+(?:\.[0-9]+)?)\s*ms.*?"
                        r"(?:baseline of|baseline:)\s*"
                        r"([0-9]+(?:\.[0-9]+)?)\s*ms",
                        clean_explanation,
                        re.IGNORECASE,
                    )

                    if duration_match:
                        current, baseline = duration_match.groups()
                        st.markdown(
                            f"- **Request time:** {current} ms, "
                            f"higher than the normal {baseline} ms."
                        )
                    else:
                        st.markdown(
                            "- The service is taking longer than normal to respond."
                        )

                    if mrt_match:
                        current, baseline = mrt_match.groups()
                        st.markdown(
                            f"- **Average response time:** {current} ms, "
                            f"higher than the normal {baseline} ms."
                        )

                    # -------------------------------------------------
                    # Overall performance
                    # -------------------------------------------------
                    st.markdown("**📊 Overall Performance**")

                    st.markdown(
                        f"- **{affected_service} became slower than normal.**"
                    )

                    # -------------------------------------------------
                    # Trace latency
                    # -------------------------------------------------
                    trace_pattern = re.compile(
                        r"(?:hipstershop\.)?"
                        r"(PaymentService/Charge|"
                        r"CartService/EmptyCart|"
                        r"EmailService/SendOrderConfirmation)"
                        r"\s*\((?:up to\s*)?"
                        r"([0-9]+(?:\.[0-9]+)?)\s*ms\s*vs\s*"
                        r"([0-9]+(?:\.[0-9]+)?)\s*ms\s*baseline\)",
                        re.IGNORECASE,
                    )

                    trace_matches = trace_pattern.findall(clean_explanation)

                    for operation, current, baseline in trace_matches:
                        st.markdown(
                            f"- **{operation}:** "
                            f"{current} ms vs {baseline} ms normally."
                        )

                    # -------------------------------------------------
                    # Keep raw AI reasoning available for technical users
                    # -------------------------------------------------
                    with st.expander(
                        "Show raw AI reasoning",
                        expanded=False
                    ):
                        st.write(explanation)

                else:
                    st.info(
                        "No additional technical details are available."
                    )
