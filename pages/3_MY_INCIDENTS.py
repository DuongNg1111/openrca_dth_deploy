import streamlit as st
import pandas as pd

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
                }
            )

        st.dataframe(
            pd.DataFrame(metric_rows),
            use_container_width=True,
            hide_index=True,
        )

        for _, ev in metric_df.iterrows():

            metric_name = str(
                ev.get(
                    "metric_name",
                    ev.get("name", "Metric")
                )
            )

            value = ev.get("value", None)
            baseline = ev.get("baseline", None)

            description = str(
                ev.get("description", "")
            )

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

            with st.expander(
                f"📊 {metric_name}",
                expanded=False
            ):

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.metric(
                        "Observed",
                        (
                            f"{float(value):.3f}"
                            if pd.notna(value)
                            else "N/A"
                        )
                    )

                with c2:

                    st.metric(
                        "Baseline",
                        (
                            f"{float(baseline):.3f}"
                            if pd.notna(baseline)
                            else "N/A"
                        )
                    )

                with c3:

                    st.metric(
                        "Deviation",
                        (
                            f"{deviation:+.1f}%"
                            if deviation is not None
                            else "N/A"
                        )
                    )

                if deviation is not None:

                    if deviation >= 0:

                        st.warning(
                            f"Metric increased by "
                            f"{deviation:.1f}% above baseline."
                        )

                    else:

                        st.info(
                            f"Metric decreased by "
                            f"{abs(deviation):.1f}% from baseline."
                        )

                if description.strip():

                    st.markdown("**Technical explanation**")

                    st.write(
                        description
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

        for _, ev in trace_df.iterrows():

            operation = str(
                ev.get(
                    "operation",
                    "Unknown operation"
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

            trace_rows.append(
                {
                    "Operation": operation,
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
        )

        for _, ev in trace_df.iterrows():

            operation = str(
                ev.get(
                    "operation",
                    "Unknown operation"
                )
            )

            value = ev.get("value", None)
            baseline = ev.get("baseline", None)
            trace_id = ev.get("trace_id", None)

            description = str(
                ev.get("description", "")
            )

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

            with st.expander(
                f"🔗 {operation}",
                expanded=False
            ):

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.metric(
                        "Observed",
                        (
                            f"{float(value):.3f} ms"
                            if pd.notna(value)
                            else "N/A"
                        )
                    )

                with c2:

                    st.metric(
                        "Baseline",
                        (
                            f"{float(baseline):.3f} ms"
                            if pd.notna(baseline)
                            else "N/A"
                        )
                    )

                with c3:

                    st.metric(
                        "Deviation",
                        (
                            f"{deviation:+.1f}%"
                            if deviation is not None
                            else "N/A"
                        )
                    )

                if description.strip():

                    st.markdown(
                        "**Explanation**"
                    )

                    st.write(
                        description
                    )

                if pd.notna(trace_id):

                    with st.expander(
                        "Technical trace details"
                    ):

                        st.caption(
                            f"Trace ID: {trace_id}"
                        )






    # =================================================
    # RCA CARD STYLES
    # =================================================

    st.markdown(
        """
        <style>
        .rca-card {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            padding: 18px 20px 14px 20px;
            margin-top: 10px;
            margin-bottom: 8px;
            background: rgba(128, 128, 128, 0.06);
        }

        .rca-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
        }

        .rca-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            opacity: 0.65;
            margin-bottom: 4px;
        }

        .rca-service {
            font-size: 1.35rem;
            font-weight: 700;
        }

        .rca-confidence {
            text-align: right;
            min-width: 100px;
        }

        .confidence-value {
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1;
        }

        .confidence-label {
            font-size: 0.72rem;
            opacity: 0.65;
            margin-top: 5px;
        }

        .root-cause-box {
            border-left: 4px solid #ff4b4b;
            border-radius: 8px;
            padding: 14px 16px;
            margin: 8px 0 18px 0;
            background: rgba(255, 75, 75, 0.06);
        }

        .root-cause-title {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            opacity: 0.65;
            margin-bottom: 6px;
        }

        .root-cause-text {
            font-size: 1rem;
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

    st.caption(
        "The Reasoning Agent correlates metric, log, and trace "
        "evidence to determine the most likely cause."
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
        # =================================================
        # RCA HEADER
        # =================================================

        h1, h2 = st.columns([4, 1])

        with h1:
            st.caption("ROOT-CAUSE ASSESSMENT")
            st.markdown(
                f"### `{service}`"
            )

        with h2:
            st.metric(
                "AI confidence",
                f"{confidence:.0f}%"
            )

        st.progress(
            min(
                max(confidence / 100, 0),
                1
            )
        )

        # =================================================
        # EVIDENCE
        # =================================================

        st.markdown("##### 🔎 Supporting Evidence")

        e1, e2, e3 = st.columns(3)

        with e1:
            st.metric(
                "Metrics",
                int(metric_count)
            )

        with e2:
            st.metric(
                "Logs",
                int(log_count)
            )

        with e3:
            st.metric(
                "Traces",
                int(trace_count)
            )

        # =================================================
        # REASONING
        # =================================================

        st.markdown("##### 🧠 Reasoning")

        if metric_count > 0:
            st.markdown(
                f"**Metrics:** {metric_count} abnormal "
                "signal(s) indicate degraded service performance."
            )

        if trace_count > 0:
            st.markdown(
                f"**Traces:** {trace_count} abnormal "
                "operation(s) indicate elevated latency "
                "along the request path."
            )

        if log_count > 0:
            st.markdown(
                f"**Logs:** {log_count} relevant "
                "log signal(s) provide additional context."
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
        # ROOT CAUSE
        # =================================================

        st.markdown("##### 🎯 Most Likely Root Cause")

        st.markdown(
            f"""
            <div class="root-cause-box">
                <div class="root-cause-title">
                    Primary finding
                </div>
                <div class="root-cause-text">
                    {root_cause}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # =================================================
        # RECOMMENDED ACTIONS
        # =================================================

        st.markdown("##### 🛠 Recommended Actions")

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
                    "Review abnormal latency against the established baseline.",
                    "Investigate the affected request and operation path.",
                    "Check downstream service dependencies.",
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
                    "Review CPU utilization and resource limits.",
                    "Check container CPU throttling.",
                ]
            )

        if not actions:
            actions.extend(
                [
                    "Review abnormal behaviour against the baseline.",
                    "Investigate the affected service and dependencies.",
                    "Monitor the service after remediation.",
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
            expanded=False
        ):

            if explanation.strip():

                st.markdown(
                    "**Raw AI reasoning**"
                )

                st.write(
                    explanation
                )

            else:

                st.info(
                    "No detailed AI explanation is available."
                )
