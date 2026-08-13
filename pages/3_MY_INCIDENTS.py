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


# =========================================================
# HUMAN-READABLE TELEMETRY LABELS
# =========================================================

def _humanize_service_name(value):
    """Convert technical service names into user-friendly labels."""
    if value is None:
        return "Unknown Service"

    value = str(value).strip()

    if not value:
        return "Unknown Service"

    replacements = {
        "productcatalogservice": "Product Catalog Service",
        "recommendationservice": "Recommendation Service",
        "checkoutservice": "Checkout Service",
        "cartservice": "Cart Service",
        "paymentservice": "Payment Service",
        "currencyservice": "Currency Service",
        "shippingservice": "Shipping Service",
        "emailservice": "Email Service",
        "frontend": "Frontend",
        "adservice": "Ad Service",
    }

    key = value.lower()

    if key in replacements:
        return replacements[key]

    return value.replace("_", " ").replace("-", " ").title()


def _humanize_operation_name(value):
    """Convert technical operation names into readable labels."""
    if value is None:
        return "Unknown Operation"

    value = str(value).strip()

    if not value:
        return "Unknown Operation"

    if "/" in value:
        parts = value.split("/")
        return " / ".join(
            part.replace("_", " ").replace("-", " ").title()
            for part in parts
            if part
        )

    return value.replace("_", " ").replace("-", " ").title()


def _humanize_metric_name(value):
    """Convert technical metric names into readable labels."""
    if value is None:
        return "Unknown Metric"

    value = str(value).strip()

    if not value:
        return "Unknown Metric"

    replacements = {
        "request_duration": "Request Duration",
        "request_latency": "Request Latency",
        "response_time": "Response Time",
        "cpu_usage": "CPU Usage",
        "cpu_utilization": "CPU Utilization",
        "memory_usage": "Memory Usage",
        "error_rate": "Error Rate",
        "request_rate": "Request Rate",
        "throughput": "Throughput",
    }

    key = value.lower()

    if key in replacements:
        return replacements[key]

    return value.replace("_", " ").replace("-", " ").title()



# =========================================================
# HUMAN-READABLE ANOMALY CHART LABELS
# =========================================================

def _humanize_chart_label(value):
    """
    Convert technical telemetry strings into labels that
    non-technical users can understand.

    This only affects UI labels. Raw telemetry remains unchanged.
    """
    if value is None:
        return "Unknown anomaly"

    value = str(value).strip()

    if not value:
        return "Unknown anomaly"

    # -----------------------------------------------------
    # Split "service / operation"
    # -----------------------------------------------------
    if " / " in value:
        service_raw, metric_raw = value.split(" / ", 1)
    else:
        service_raw = ""
        metric_raw = value

    # -----------------------------------------------------
    # Service
    # -----------------------------------------------------
    service = _humanize_service_name(service_raw) if service_raw else ""

    # -----------------------------------------------------
    # Normalize metric string
    # -----------------------------------------------------
    metric = metric_raw.strip()

    lower = metric.lower()

    # -----------------------------------------------------
    # Istio request duration
    # Examples:
    # Istio Request Duration Milliseconds.Grpc.200.0.0
    # Istio Request Duration Milliseconds.Http.202.
    # -----------------------------------------------------
    if "request duration" in lower:
        label = "Request Duration"

        qualifiers = []

        if ".grpc." in lower:
            qualifiers.append("gRPC")
        elif ".http." in lower:
            qualifiers.append("HTTP")

        # HTTP/gRPC status code
        import re as _re

        status_match = _re.search(
            r"\.(?:grpc|http)\.(\d{3})(?:\.|$)",
            lower,
        )

        if status_match:
            qualifiers.append(f"HTTP {status_match.group(1)}")

        if qualifiers:
            # Avoid "gRPC • HTTP 200" being redundant with HTTP-only.
            if qualifiers[0] == "gRPC":
                suffix = " • ".join(qualifiers)
            else:
                suffix = qualifiers[-1]

            metric_label = f"{label} — {suffix}"
        else:
            metric_label = label

    # -----------------------------------------------------
    # Istio request bytes
    # -----------------------------------------------------
    elif "request bytes" in lower:
        label = "Request Data"

        import re as _re

        qualifiers = []

        if ".grpc." in lower:
            qualifiers.append("gRPC")
        elif ".http." in lower:
            qualifiers.append("HTTP")

        status_match = _re.search(
            r"\.(?:grpc|http)\.(\d{3})(?:\.|$)",
            lower,
        )

        if status_match:
            qualifiers.append(f"HTTP {status_match.group(1)}")

        metric_label = label

        if qualifiers:
            metric_label += " — " + " • ".join(qualifiers)

    # -----------------------------------------------------
    # Network receive
    # -----------------------------------------------------
    elif "network receive" in lower:
        import re as _re

        interface_match = _re.search(
            r"\.([a-z]+\d+)$",
            lower,
        )

        if interface_match:
            metric_label = (
                "Network Receive — "
                f"Interface {interface_match.group(1)}"
            )
        else:
            metric_label = "Network Receive"

    # -----------------------------------------------------
    # Network transmit
    # -----------------------------------------------------
    elif "network transmit" in lower:
        import re as _re

        interface_match = _re.search(
            r"\.([a-z]+\d+)$",
            lower,
        )

        if interface_match:
            metric_label = (
                "Network Transmit — "
                f"Interface {interface_match.group(1)}"
            )
        else:
            metric_label = "Network Transmit"

    # -----------------------------------------------------
    # CPU throttling
    # -----------------------------------------------------
    elif "cpu cfs throttled seconds" in lower:
        metric_label = "CPU Throttling — Time"

    elif "cpu cfs throttled periods" in lower:
        metric_label = "CPU Throttling — Periods"

    elif "cpu throttled seconds" in lower:
        metric_label = "CPU Throttling — Time"

    elif "cpu throttled periods" in lower:
        metric_label = "CPU Throttling — Periods"

    # -----------------------------------------------------
    # CPU usage
    # -----------------------------------------------------
    elif "cpu" in lower and (
        "usage" in lower
        or "utilization" in lower
    ):
        metric_label = "CPU Usage"

    # -----------------------------------------------------
    # Memory
    # -----------------------------------------------------
    elif "memory" in lower:
        metric_label = "Memory Usage"

    # -----------------------------------------------------
    # Error rate
    # -----------------------------------------------------
    elif "error rate" in lower:
        metric_label = "Error Rate"

    # -----------------------------------------------------
    # Request rate
    # -----------------------------------------------------
    elif "request rate" in lower:
        metric_label = "Request Rate"

    # -----------------------------------------------------
    # Generic fallback
    # -----------------------------------------------------
    else:
        metric_label = (
            metric
            .replace("_", " ")
            .replace("-", " ")
            .replace(".", " ")
        )

        import re as _re

        metric_label = _re.sub(
            r"\s+",
            " ",
            metric_label,
        ).strip().title()

    if service:
        return f"{service} — {metric_label}"

    return metric_label



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

        c1 = st.columns(1)[0]

        with c1:
            st.metric(
                "AI Confidence",
                f"{max_confidence:.0f}%"
            )

        st.caption(
            f"Primary service investigated: **{affected_service}**"
        )


        # =================================================
        # =================================================
        # =================================================
        # INVESTIGATION TIMELINE
        # =================================================

        st.markdown(
            """
            <style>
            .investigation-timeline {
                position: relative;
                margin: 14px 0 30px 8px;
                padding-left: 34px;
            }

            .investigation-timeline::before {
                content: "";
                position: absolute;
                left: 9px;
                top: 12px;
                bottom: 12px;
                width: 2px;
                background: #d9dee7;
            }

            .timeline-item {
                position: relative;
                margin-bottom: 22px;
                padding-left: 14px;
            }

            .timeline-dot {
                position: absolute;
                left: -33px;
                top: 2px;
                width: 19px;
                height: 19px;
                border-radius: 50%;
                background: #ffffff;
                border: 3px solid #2563eb;
                box-sizing: border-box;
                z-index: 2;
            }

            .timeline-title {
                font-size: 15px;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 3px;
            }

            .timeline-description {
                font-size: 13px;
                color: #667085;
                line-height: 1.5;
            }

            .timeline-count {
                display: inline-block;
                margin-left: 8px;
                padding: 2px 8px;
                border-radius: 12px;
                background: #eef4ff;
                color: #2457c5;
                font-size: 11px;
                font-weight: 650;
            }

            .evidence-card {
                border: 1px solid #e1e5eb;
                border-radius: 10px;
                padding: 17px 19px;
                margin: 10px 0;
                background: #ffffff;
            }

            .evidence-title {
                font-size: 16px;
                font-weight: 700;
                color: #202939;
                margin-bottom: 4px;
            }

            .evidence-subtitle {
                font-size: 13px;
                color: #667085;
                margin-bottom: 14px;
            }

            .evidence-value {
                font-size: 17px;
                font-weight: 700;
                color: #1f2937;
            }

            .evidence-label {
                font-size: 11px;
                color: #667085;
                text-transform: uppercase;
                letter-spacing: .03em;
                margin-bottom: 2px;
            }

            .evidence-description {
                font-size: 13px;
                color: #475467;
                line-height: 1.5;
                margin-top: 12px;
            }

            .impact-badge {
                display: inline-block;
                padding: 3px 9px;
                border-radius: 12px;
                background: #fff4e5;
                color: #b54708;
                font-size: 12px;
                font-weight: 650;
            }

            .normal-badge {
                display: inline-block;
                padding: 3px 9px;
                border-radius: 12px;
                background: #ecfdf3;
                color: #027a48;
                font-size: 12px;
                font-weight: 650;
            }

            .empty-evidence {
                border: 1px dashed #d0d5dd;
                border-radius: 10px;
                padding: 16px;
                color: #667085;
                background: #fafafa;
                font-size: 13px;
            }

            .finding-text {
                margin-top: 10px;
                padding: 9px 12px;
                border-left: 3px solid #2563eb;
                background: #f8faff;
                color: #344054;
                font-size: 13px;
                line-height: 1.5;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # =================================================

        # =========================================================
        # TIMELINE FILTER
        # Chỉ hiển thị evidence thực sự bất thường
        # =========================================================

        def _is_significant_metric(ev):
            try:
                value = pd.to_numeric(
                    ev.get("value", None),
                    errors="coerce",
                )

                baseline = pd.to_numeric(
                    ev.get("baseline", None),
                    errors="coerce",
                )

                if pd.isna(value):
                    return False

                # Cả observed và baseline đều bằng 0
                # => không có bất thường thực sự
                if (
                    pd.notna(baseline)
                    and float(value) == 0
                    and float(baseline) == 0
                ):
                    return False

                # Không có baseline
                if pd.isna(baseline):
                    return float(value) != 0

                baseline = float(baseline)
                value = float(value)

                # Baseline = 0 nhưng observed > 0
                # => bất thường rõ ràng
                if baseline == 0:
                    return value != 0

                deviation = abs(
                    (value - baseline)
                    / abs(baseline)
                ) * 100

                # Chỉ giữ metric lệch >= 20%
                return deviation >= 20

            except Exception:
                return False


        def _is_significant_trace(ev):
            try:
                value = pd.to_numeric(
                    ev.get("latency_ms", ev.get("value", None)),
                    errors="coerce",
                )

                baseline = pd.to_numeric(
                    ev.get(
                        "baseline_ms",
                        ev.get("baseline", None),
                    ),
                    errors="coerce",
                )

                if pd.isna(value):
                    return False

                if pd.isna(baseline):
                    return True

                baseline = float(baseline)
                value = float(value)

                if baseline <= 0:
                    return value > 0

                # Trace phải ít nhất 1.5x baseline
                return (
                    value / baseline
                ) >= 1.5

            except Exception:
                return False


        def _is_significant_log(ev):
            description = str(
                ev.get("description", "")
            ).strip()

            value = ev.get("value", None)

            # Log evidence đã được Log Agent chọn
            # nên chỉ cần có nội dung thực tế.
            return bool(
                description
                or (
                    pd.notna(value)
                    if value is not None
                    else False
                )
            )

        # INCIDENT EVIDENCE TIMELINE
        # =================================================

        st.markdown("### Incident Timeline")

        st.markdown(
            """
            <style>

            .evidence-timeline {
                position: relative;
                margin: 10px 0 30px 0;
                padding: 16px 20px 16px 42px;
                max-height: 520px;
                overflow-y: auto;
                overflow-x: hidden;
                border: 1px solid #e4e7ec;
                border-radius: 10px;
                background: #ffffff;
                box-sizing: border-box;
            }

            .evidence-timeline::-webkit-scrollbar {
                width: 7px;
            }

            .evidence-timeline::-webkit-scrollbar-track {
                background: #f2f4f7;
                border-radius: 10px;
            }

            .evidence-timeline::-webkit-scrollbar-thumb {
                background: #c4c9d1;
                border-radius: 10px;
            }

            .evidence-timeline::-webkit-scrollbar-thumb:hover {
                background: #98a2b3;
            }

            .evidence-timeline::before {
                content: "";
                position: absolute;
                left: 15px;
                top: 8px;
                bottom: 8px;
                width: 2px;
                background: #d9dee7;
            }

            .evidence-event {
                position: relative;
                padding: 4px 0 24px 0;
                margin: 0;
            }

            .evidence-dot {
                position: absolute;
                left: -34px;
                top: 7px;
                width: 15px;
                height: 15px;
                border-radius: 50%;
                background: #ffffff;
                border: 3px solid #2563eb;
                box-sizing: border-box;
                z-index: 2;
            }

            .evidence-time {
                font-size: 12px;
                font-weight: 650;
                color: #667085;
                margin-bottom: 5px;
            }

            .evidence-event-title {
                font-size: 15px;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 3px;
            }

            .evidence-service {
                display: inline-block;
                font-size: 13px;
                font-weight: 650;
                color: #344054;
                margin-right: 8px;
            }

            .evidence-operation {
                display: inline-block;
                font-size: 12px;
                color: #667085;
                margin-bottom: 8px;
            }

            .evidence-metrics {
                display: flex;
                gap: 30px;
                flex-wrap: wrap;
                margin: 5px 0 7px 0;
            }

            .evidence-metric-label {
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: .04em;
                color: #98a2b3;
            }

            .evidence-metric-value {
                font-size: 14px;
                font-weight: 700;
                color: #1f2937;
            }

            .evidence-anomaly {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 4px;
                background: #fff4e5;
                color: #b54708;
                font-size: 11px;
                font-weight: 700;
                margin: 2px 0 6px 0;
            }

            .evidence-event-description {
                font-size: 13px;
                line-height: 1.5;
                color: #667085;
                max-width: 850px;
            }

            .evidence-empty-timeline {
                padding: 18px;
                border: 1px dashed #d0d5dd;
                border-radius: 8px;
                background: #fafafa;
                color: #667085;
                font-size: 13px;
            }

            </style>
            """,
            unsafe_allow_html=True,
        )


        # -------------------------------------------------
        # Build timeline from actual telemetry evidence
        # -------------------------------------------------

        # =================================================
        # INCIDENT DEVELOPMENT EVIDENCE
        #
        # IMPORTANT:
        # Use the complete investigation evidence directly.
        #
        # Do NOT build the timeline from metric_df only.
        # Reasoning Agent / evidence_records contain:
        #   - metric
        #   - log
        #   - trace
        #
        # The timeline should show all three evidence types.
        # =================================================

        timeline_events = []

        if evidence_df is not None and not evidence_df.empty:

            for _, evidence_row in evidence_df.iterrows():

                evidence_type = str(
                    evidence_row.get(
                        "evidence_type",
                        ""
                    )
                    or ""
                ).strip().lower()

                # Only telemetry evidence belongs in the timeline.
                if evidence_type not in {
                    "metric",
                    "log",
                    "trace",
                }:
                    continue

                # Convert pandas NaN -> None
                def _clean_value(value):

                    try:
                        if pd.isna(value):
                            return None
                    except Exception:
                        pass

                    return value

                event = {
                    "id": _clean_value(
                        evidence_row.get("id")
                    ),

                    "type": evidence_type,

                    "evidence_type": evidence_type,

                    "service": _clean_value(
                        evidence_row.get("service")
                    ),

                    "metric_name": _clean_value(
                        evidence_row.get("metric_name")
                    ),

                    "metric": _clean_value(
                        evidence_row.get("metric")
                    ),

                    "operation": _clean_value(
                        evidence_row.get("operation")
                    ),

                    "trace_id": _clean_value(
                        evidence_row.get("trace_id")
                    ),

                    "description": _clean_value(
                        evidence_row.get("description")
                    ),

                    "value": _clean_value(
                        evidence_row.get("value")
                    ),

                    "baseline": _clean_value(
                        evidence_row.get("baseline")
                    ),

                    "timestamp": _clean_value(
                        evidence_row.get("timestamp")
                    ),

                    "score": _clean_value(
                        evidence_row.get("score")
                    ),

                    "confidence": _clean_value(
                        evidence_row.get("confidence")
                    ),

                    "metadata": _clean_value(
                        evidence_row.get("metadata")
                    ),
                }

                timeline_events.append(event)

        # -------------------------------------------------
        # Debug information
        # -------------------------------------------------

        timeline_type_counts = {}

        for event in timeline_events:

            event_type = event.get(
                "evidence_type",
                "unknown"
            )

            timeline_type_counts[event_type] = (
                timeline_type_counts.get(
                    event_type,
                    0
                ) + 1
            )

        print(
            "\nTIMELINE EVIDENCE COUNTS:",
            timeline_type_counts
        )

        print(
            "TOTAL TIMELINE EVIDENCE:",
            len(timeline_events)
        )

        # -------------------------------------------------
        # HOW THE INCIDENT DEVELOPED
        # 15 MINUTES BEFORE + INCIDENT + 15 MINUTES AFTER
        # -------------------------------------------------

        st.markdown("### How the Incident Developed")

        st.markdown(
            """
            <div style="
                color:#667085;
                font-size:13px;
                margin:-4px 0 14px 0;
                line-height:1.5;
            ">
                Showing how the incident developed across a
                <b>30-minute investigation window</b>:
                15 minutes before the incident and
                15 minutes after.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------------------------------------------------
        # Incident reference time
        # -------------------------------------------------

        incident_time = None

        if isinstance(incident, dict):

            for candidate in (
                incident.get("incident_time"),
                incident.get("created_at"),
                incident.get("timestamp"),
            ):

                if candidate:

                    try:
                        incident_time = pd.Timestamp(candidate)
                        break
                    except Exception:
                        pass

        # Fallback: use earliest telemetry event
        if incident_time is None:

            for event in timeline_events:

                ts = event.get("timestamp")

                if ts is None:
                    continue

                try:
                    incident_time = pd.Timestamp(ts)
                    break
                except Exception:
                    continue

        if incident_time is None:
            incident_time = pd.Timestamp.now()

        # -------------------------------------------------
        # 30-minute window
        # -------------------------------------------------

        window_start = (
            incident_time
            - pd.Timedelta(minutes=15)
        )

        window_end = (
            incident_time
            + pd.Timedelta(minutes=15)
        )

        window_events = []

        for event in timeline_events:

            ts = event.get("timestamp")

            if ts is None:
                continue

            try:
                ts = pd.Timestamp(ts)
            except Exception:
                continue

            if window_start <= ts <= window_end:

                event = dict(event)
                event["_parsed_timestamp"] = ts

                window_events.append(event)

        window_events.sort(
            key=lambda e: e["_parsed_timestamp"]
        )

        # -------------------------------------------------
        # Helper: readable service name
        # -------------------------------------------------

        def _timeline_service_name(value):

            name = str(
                value or "Unknown service"
            ).strip()

            name = re.sub(
                r"\s*\d+[-\s]+\d+$",
                "",
                name,
            )

            name = re.sub(
                r"\s+\d+$",
                "",
                name,
            )

            normalized = (
                name.lower()
                .replace("_", "")
                .replace("-", "")
                .replace(" ", "")
            )

            service_map = {

                "productcatalogservice":
                    "Product Catalog Service",

                "productcatalogservice2":
                    "Product Catalog Service",

                "recommendationservice":
                    "Recommendation Service",

                "checkoutservice":
                    "Checkout Service",

                "paymentservice":
                    "Payment Service",

                "cartservice":
                    "Cart Service",

                "currencyservice":
                    "Currency Service",

                "shippingservice":
                    "Shipping Service",

                "emailservice":
                    "Email Service",

                "frontend":
                    "Frontend",
            }

            if normalized in service_map:
                return service_map[normalized]

            name = re.sub(
                r"(?<=[a-z])(?=[A-Z])",
                " ",
                name,
            )

            return (
                name
                .replace("_", " ")
                .replace("-", " ")
                .strip()
                .title()
            )

        # -------------------------------------------------
        # Helper: readable operation
        # -------------------------------------------------

        def _timeline_operation_name(value):

            name = str(value or "").strip()

            if not name:
                return None

            if "/" in name:

                parts = [
                    p.strip()
                    for p in name.split("/")
                    if p.strip()
                ]

                if parts:
                    name = parts[-1]

            name = re.sub(
                r"(?i)^hipstershop[\s_-]*",
                "",
                name,
            )

            normalized = (
                name.lower()
                .replace("_", "")
                .replace("-", "")
                .replace(" ", "")
            )

            operation_map = {

                "getproduct":
                    "Get Product",

                "listrecommendations":
                    "List Recommendations",

                "emptycart":
                    "Empty Cart",

                "charge":
                    "Charge Payment",

                "placeorder":
                    "Place Order",

                "getcurrency":
                    "Get Currency",

                "shiporder":
                    "Ship Order",

                "sendemail":
                    "Send Email",
            }

            if normalized in operation_map:
                return operation_map[normalized]

            name = re.sub(
                r"(?<=[a-z])(?=[A-Z])",
                " ",
                name,
            )

            return (
                name
                .replace("_", " ")
                .replace("-", " ")
                .strip()
                .title()
            )

        # -------------------------------------------------
        # Helper: format values
        # -------------------------------------------------

        def _timeline_value(value):

            if value is None:
                return None

            try:
                return f"{float(value):,.2f}"
            except Exception:
                return str(value)

        # -------------------------------------------------
        # Build timeline
        # -------------------------------------------------

        timeline_html = ""

        for event in window_events:

            event_time = event["_parsed_timestamp"]

            # -------------------------------------------------
            # Safe defaults for timeline rendering
            # -------------------------------------------------

            title = "Performance signal detected"

            description = (
                "The service showed an abnormal performance signal."
            )

            # DEBUG: inspect actual timeline metric fields
            if str(event.get("evidence_type", "")).lower() == "metric":
                print(
                    "\n[TIMELINE METRIC DEBUG]",
                    {
                        "metric_name": event.get("metric_name"),
                        "metric": event.get("metric"),
                        "name": event.get("name"),
                        "operation": event.get("operation"),
                        "title": event.get("title"),
                        "description": event.get("description"),
                        "current": event.get("current"),
                        "value": event.get("value"),
                        "baseline": event.get("baseline"),
                        "normal": event.get("normal"),
                    }
                )

            event_type = str(
                event.get(
                    "evidence_type",
                    event.get(
                        "type",
                        "metric"
                    )
                )
                or "metric"
            ).lower()

            service = _timeline_service_name(
                event.get(
                    "service",
                    "Unknown service"
                )
            )

            # -------------------------------------------------
            # SAFE DEFAULTS
            #
            # Every timeline event gets a title and description
            # before metric/log/trace-specific mapping runs.
            # -------------------------------------------------

            title = "Performance signal detected"

            description = (
                f"{service} showed an abnormal signal "
                f"compared with its normal behavior."
            )


            # -------------------------------------------------
            # Get the real evidence name.
            #
            # Reasoning Agent evidence normally contains:
            #   evidence_type
            #   metric_name
            #   operation
            #   description
            #   value
            #   baseline
            #
            # Some older timeline records use "metric"
            # instead of "metric_name", so support both.
            # -------------------------------------------------

            metric_name = str(
                event.get("metric_name")
                or event.get("metric")
                or event.get("name")
                or event.get("title")
                or ""
            ).strip()

            # If this is a metric but the metric name was not
            # copied into timeline_events, try the metadata object.
            metadata = event.get("metadata")

            if (
                not metric_name
                and isinstance(metadata, dict)
            ):
                metric_name = str(
                    metadata.get("metric")
                    or metadata.get("metric_name")
                    or ""
                ).strip()

            raw_name = metric_name.lower()

            operation = _timeline_operation_name(
                event.get(
                    "operation",
                    ""
                )
            )

            raw_name = metric_name.lower()

            # -------------------------------------------------
            # Phase
            # -------------------------------------------------

            if event_time < incident_time:

                phase = "BEFORE INCIDENT"
                phase_class = "before"

            elif event_time > incident_time:

                phase = "AFTER INCIDENT"
                phase_class = "after"

            else:

                phase = "INCIDENT"
                phase_class = "incident"

            # -------------------------------------------------
            # Human-readable title
            # -------------------------------------------------

            # Read every possible source because evidence records
            # can come from different stages of the pipeline.

            evidence_text = " ".join(
                str(
                    event.get(key, "")
                    or ""
                )
                for key in (
                    "metric_name",
                    "metric",
                    "name",
                    "title",
                    "description",
                )
            ).lower()

            metadata = event.get("metadata")

            if isinstance(metadata, dict):

                evidence_text += " " + " ".join(
                    str(value or "")
                    for value in metadata.values()
                ).lower()

            # -------------------------------------------------
            # METRIC
            # -------------------------------------------------

            elif event_type == "metric":

                # -------------------------------------------------
                # Normalize metric name
                # -------------------------------------------------

                metric_name = str(
                    event.get("metric_name")
                    or event.get("metric")
                    or event.get("name")
                    or metadata.get("metric_name")
                    or metadata.get("metric")
                    or ""
                ).strip()

                raw_name = metric_name.lower()

                normalized_name = re.sub(
                    r"[^a-z0-9_]+",
                    "_",
                    raw_name,
                )

                # -------------------------------------------------
                # Request latency
                # -------------------------------------------------

                if (
                    "request_duration" in normalized_name
                    or "request_latency" in normalized_name
                ):

                    title = (
                        f"{service} — Request latency increased"
                    )

                    description = (
                        f"{service} requests were taking longer "
                        f"than usual."
                    )

                # -------------------------------------------------
                # Response latency
                # -------------------------------------------------

                elif (
                    "response_duration" in normalized_name
                    or "response_latency" in normalized_name
                ):

                    title = (
                        f"{service} — Response latency increased"
                    )

                    description = (
                        f"{service} responses were taking longer "
                        f"than usual."
                    )

                # -------------------------------------------------
                # Request traffic
                # -------------------------------------------------

                elif (
                    "request_bytes" in normalized_name
                    or "request_size" in normalized_name
                ):

                    title = (
                        f"{service} — Request traffic increased"
                    )

                    description = (
                        f"{service} received more request data "
                        f"than usual."
                    )

                # -------------------------------------------------
                # Response traffic
                # -------------------------------------------------

                elif (
                    "response_bytes" in normalized_name
                    or "response_size" in normalized_name
                ):

                    title = (
                        f"{service} — Response traffic increased"
                    )

                    description = (
                        f"{service} returned more response data "
                        f"than usual."
                    )

                # -------------------------------------------------
                # Request volume
                # -------------------------------------------------

                elif (
                    "request_messages" in normalized_name
                    or "request_count" in normalized_name
                    or normalized_name.endswith("_requests")
                    or normalized_name == "requests"
                ):

                    title = (
                        f"{service} — Request volume increased"
                    )

                    description = (
                        f"{service} received more requests "
                        f"than usual."
                    )

                # -------------------------------------------------
                # Response volume
                # -------------------------------------------------

                elif (
                    "response_messages" in normalized_name
                    or "response_count" in normalized_name
                    or normalized_name.endswith("_responses")
                    or normalized_name == "responses"
                ):

                    title = (
                        f"{service} — Response volume increased"
                    )

                    description = (
                        f"{service} produced more responses "
                        f"than usual."
                    )

                # -------------------------------------------------
                # CPU throttling
                # -------------------------------------------------

                elif (
                    "cpu_cfs_throttled" in normalized_name
                    or "cpu_throttled" in normalized_name
                    or "cpu_throttling" in normalized_name
                ):

                    title = (
                        f"{service} — CPU throttling increased"
                    )

                    description = (
                        f"{service} experienced more CPU throttling "
                        f"than usual."
                    )

                # -------------------------------------------------
                # CPU usage
                # -------------------------------------------------

                elif (
                    "cpu_usage" in normalized_name
                    or "cpu_utilization" in normalized_name
                ):

                    title = (
                        f"{service} — CPU usage increased"
                    )

                    description = (
                        f"{service} was using more CPU resources "
                        f"than usual."
                    )

                # -------------------------------------------------
                # Memory
                # -------------------------------------------------

                elif (
                    "memory" in normalized_name
                    or "pgfault" in normalized_name
                    or "page_fault" in normalized_name
                ):

                    title = (
                        f"{service} — Memory usage increased"
                    )

                    description = (
                        f"{service} was using more memory resources "
                        f"than usual."
                    )

                # -------------------------------------------------
                # Network
                # -------------------------------------------------

                elif (
                    "network_receive" in normalized_name
                    or "receive_packets" in normalized_name
                ):

                    title = (
                        f"{service} — Incoming network traffic increased"
                    )

                    description = (
                        f"{service} received more network traffic "
                        f"than usual."
                    )

                elif (
                    "network_transmit" in normalized_name
                    or "transmit_packets" in normalized_name
                ):

                    title = (
                        f"{service} — Outgoing network traffic increased"
                    )

                    description = (
                        f"{service} sent more network traffic "
                        f"than usual."
                    )

                # -------------------------------------------------
                # Generic metric fallback
                # -------------------------------------------------

                else:

                    title = (
                        f"{service} — Performance signal detected"
                    )

                    description = (
                        f"{service} showed an abnormal performance "
                        f"signal compared with its normal behavior."
                    )

            elif event_type == "log":

                title = (
                    f"{service} — "
                    f"Application error detected"
                )

                raw_description = str(
                    event.get("description", "")
                    or ""
                ).strip()

                if raw_description:

                    description = raw_description

                else:

                    description = (
                        f"{service} produced an application "
                        f"log indicating abnormal behavior."
                    )

            # -------------------------------------------------
            # TRACE
            # -------------------------------------------------

            elif event_type == "trace":

                if operation:

                    title = (
                        f"{service} — "
                        f"{operation} became slower"
                    )

                    description = (
                        f"{service} experienced higher latency "
                        f"while running the {operation} operation."
                    )

                else:

                    title = (
                        f"{service} — "
                        f"Application latency increased"
                    )

                    description = (
                        f"{service} experienced higher "
                        f"application latency than usual."
                    )

            # -------------------------------------------------
            # Unknown evidence type
            # -------------------------------------------------

            else:

                title = (
                    f"{service} — "
                    f"Performance signal detected"
                )

                description = (
                    f"{service} showed a measurable change "
                    f"from its normal behavior."
                )

            # -------------------------------------------------
            # Human-readable description
            # -------------------------------------------------

            if event_type == "trace":

                if operation:

                    description = (
                        f"{service} experienced higher latency "
                        f"while running the {operation} operation."
                    )

                else:

                    description = (
                        f"{service} experienced higher "
                        f"application latency than usual."
                    )

            elif "request duration" in raw_name:

                description = (
                    f"{service} requests were taking longer "
                    f"than usual."
                )

            elif "response duration" in raw_name:

                description = (
                    f"{service} responses were taking longer "
                    f"than usual."
                )

            elif "request bytes" in raw_name:

                description = (
                    f"{service} received more request data "
                    f"than usual."
                )

            elif "response bytes" in raw_name:

                description = (
                    f"{service} returned more response data "
                    f"than usual."
                )

            elif (
                "request messages" in raw_name
                or "requests." in raw_name
                or raw_name == "requests"
            ):

                description = (
                    f"{service} received more requests "
                    f"than usual."
                )

            elif "response messages" in raw_name:

                description = (
                    f"{service} produced more response messages "
                    f"than usual."
                )

            elif "cpu cfs throttled" in raw_name:

                description = (
                    f"{service} experienced more CPU throttling "
                    f"than usual."
                )

            elif "cpu usage" in raw_name:

                description = (
                    f"{service} was using more CPU resources "
                    f"than usual."
                )

            elif (
                "memory" in raw_name
                or "pgfault" in raw_name
            ):

                description = (
                    f"{service} showed higher memory pressure "
                    f"than usual."
                )

            elif "network receive" in raw_name:

                description = (
                    f"{service} received more network traffic "
                    f"than usual."
                )

            elif "network transmit" in raw_name:

                description = (
                    f"{service} sent more network traffic "
                    f"than usual."
                )

            else:

                description = (
                    f"{service} showed an abnormal "
                    f"performance signal."
                )

            # -------------------------------------------------
            # Current / baseline
            # -------------------------------------------------

            current = event.get(
                "value",
                event.get(
                    "current"
                )
            )

            baseline = event.get(
                "baseline",
                event.get(
                    "normal"
                )
            )

            current_text = _timeline_value(
                current
            )

            baseline_text = _timeline_value(
                baseline
            )

            values_html = ""

            if current_text is not None:

                values_html += f"""
                    <span>
                        Current:
                        <b>{current_text}</b>
                    </span>
                """

            if baseline_text is not None:

                values_html += f"""
                    <span>
                        Normal:
                        <b>{baseline_text}</b>
                    </span>
                """

            # -------------------------------------------------
            # Deviation
            # -------------------------------------------------

            deviation_text = ""

            try:

                if (
                    current is not None
                    and baseline is not None
                    and float(baseline) != 0
                ):

                    deviation = (
                        (
                            float(current)
                            - float(baseline)
                        )
                        / abs(float(baseline))
                    ) * 100

                    if deviation >= 0:

                        deviation_text = (
                            f"{deviation:.0f}% above normal"
                        )

                    else:

                        deviation_text = (
                            f"{abs(deviation):.0f}% below normal"
                        )

            except Exception:
                pass

            deviation_html = ""

            if deviation_text:

                deviation_html = f"""
                    <span class="development-deviation">
                        {deviation_text}
                    </span>
                """

            icon = {

                "metric": "📈",

                "log": "📋",

                "trace": "🔗",

            }.get(
                event_type,
                "📈"
            )

            # -------------------------------------------------
            # Timeline item
            # -------------------------------------------------

            timeline_html += f"""
            <div class="development-item">

                <div class="development-time">
                    {event_time.strftime("%H:%M:%S")}
                </div>

                <div class="development-marker">

                    <div class="development-dot">
                        {icon}
                    </div>

                    <div class="development-line"></div>

                </div>

                <div class="development-content">

                    <div class="development-meta">

                        <span class="
                            development-phase
                            {phase_class}
                        ">
                            {phase}
                        </span>

                        <span class="development-type">
                            {event_type.upper()}
                        </span>

                    </div>

                    <div class="development-title">
                        {title}
                    </div>

                    <div class="development-description">
                        {description}
                    </div>

                    <div class="development-values">
                        {values_html}
                    </div>

                    {deviation_html}

                </div>

            </div>
            """

        # -------------------------------------------------
        # Render
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="development-summary">
                <b>{len(window_events)}</b>
                abnormal signals detected
                ·
                {window_start.strftime("%H:%M:%S")}
                →
                {window_end.strftime("%H:%M:%S")}
            </div>

            <div class="development-scroll">
                {timeline_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


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
