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
            
              /* ==============================
                 Development Timeline
              ============================== */

              .development-summary {
                  margin: 8px 0 14px 0 !important;
                  font-size: 13px !important;
                  color: #667085 !important;
              }

              .development-summary b {
                  color: #1f2937 !important;
                  font-weight: 700 !important;
              }

              .development-scroll {
                  width: 100% !important;
                  max-height: 620px !important;
                  overflow-y: auto !important;
                  overflow-x: hidden !important;
                  padding: 4px 8px 12px 0 !important;
                  box-sizing: border-box !important;
              }

              .development-item {
                  display: grid !important;
                  grid-template-columns: 72px 34px minmax(0, 1fr) !important;
                  column-gap: 10px !important;
                  width: 100% !important;
                  min-width: 0 !important;
                  margin-bottom: 18px !important;
                  box-sizing: border-box !important;
              }

              .development-time {
                  padding-top: 4px !important;
                  color: #667085 !important;
                  font-size: 12px !important;
                  font-weight: 600 !important;
                  white-space: nowrap !important;
                  text-align: right !important;
              }

              .development-marker {
                  position: relative !important;
                  display: flex !important;
                  justify-content: center !important;
                  min-height: 100% !important;
              }

              .development-dot {
                  position: relative !important;
                  z-index: 2 !important;
                  width: 30px !important;
                  height: 30px !important;
                  display: flex !important;
                  align-items: center !important;
                  justify-content: center !important;
                  border: 1px solid #dbe3ef !important;
                  border-radius: 50% !important;
                  background: #ffffff !important;
                  font-size: 14px !important;
                  box-sizing: border-box !important;
              }

              .development-line {
                  position: absolute !important;
                  top: 30px !important;
                  bottom: -18px !important;
                  left: 50% !important;
                  width: 1px !important;
                  transform: translateX(-50%) !important;
                  background: #d9dee8 !important;
              }

              .development-content {
                  min-width: 0 !important;
                  padding: 13px 15px !important;
                  border: 1px solid #e5e7eb !important;
                  border-radius: 9px !important;
                  background: #ffffff !important;
                  box-sizing: border-box !important;
                  overflow: visible !important;
              }

              .development-meta {
                  display: flex !important;
                  align-items: center !important;
                  gap: 7px !important;
                  margin-bottom: 7px !important;
                  flex-wrap: wrap !important;
              }

              .development-phase {
                  display: inline-flex !important;
                  align-items: center !important;
                  padding: 3px 7px !important;
                  border-radius: 5px !important;
                  font-size: 10px !important;
                  line-height: 1.3 !important;
                  font-weight: 700 !important;
                  letter-spacing: .035em !important;
              }

              .development-phase.before {
                  background: #eff6ff !important;
                  color: #1d4ed8 !important;
              }

              .development-phase.during {
                  background: #fff7ed !important;
                  color: #c2410c !important;
              }

              .development-phase.after {
                  background: #f3f4f6 !important;
                  color: #4b5563 !important;
              }

              .development-type {
                  display: inline-flex !important;
                  align-items: center !important;
                  padding: 3px 7px !important;
                  border-radius: 5px !important;
                  background: #f3f4f6 !important;
                  color: #667085 !important;
                  font-size: 10px !important;
                  line-height: 1.3 !important;
                  font-weight: 700 !important;
                  letter-spacing: .035em !important;
              }

              .development-title {
                  margin-bottom: 5px !important;
                  color: #1f2937 !important;
                  font-size: 14px !important;
                  line-height: 1.4 !important;
                  font-weight: 700 !important;
              }

              .development-description {
                  margin-bottom: 0 !important;
                  color: #667085 !important;
                  font-size: 12.5px !important;
                  line-height: 1.5 !important;
              }
                .development-values {
                    display: flex !important;
                    align-items: center !important;
                    flex-wrap: wrap !important;
                    gap: 8px !important;
                    margin-top: 10px !important;
                    margin-bottom: 5px !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    height: auto !important;
                    max-height: none !important;
                    overflow: visible !important;
                    position: relative !important;
                    z-index: 10 !important;
                }

                .development-values span {
                  display: inline-flex !important;
                  align-items: center !important;
                  padding: 5px 9px !important;
                  border: 1px solid #e5e7eb !important;
                  border-radius: 6px !important;
                  background: #f8fafc !important;
                  color: #4b5563 !important;
                  font-size: 12px !important;
                  line-height: 1.4 !important;
                  visibility: visible !important;
                  opacity: 1 !important;
              }

              .development-values b {
                  margin-left: 3px !important;
                  color: #111827 !important;
                  font-weight: 700 !important;
              }

              .development-deviation {
                  display: inline-block !important;
                  margin-top: 2px !important;
                  margin-bottom: 2px !important;
                  color: #b45309 !important;
                  font-size: 12px !important;
                  line-height: 1.4 !important;
                  font-weight: 650 !important;
                  visibility: visible !important;
                  opacity: 1 !important;
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
        # -------------------------------------------------
        # Incident reference time
        # -------------------------------------------------
        # Always use the exact incident timestamp stored
        # in the investigation record.
        # Never infer incident time from telemetry.

        incident_time = None

        try:
            candidate = incident.get("incident_time", None)

            if pd.notna(candidate):
                incident_time = pd.Timestamp(candidate)

        except Exception:
            incident_time = None

        if incident_time is None:
            raise ValueError("Incident record does not contain a valid incident_time.")

        # -------------------------------------------------
        # 30-minute window
        # -------------------------------------------------
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
        # -------------------------------------------------
        # -------------------------------------------------
        # Build human-readable incident story timeline
        # -------------------------------------------------

        timeline_html = ""

        # Group telemetry into fixed incident development phases.
        # Always render all five phases so the user can understand
        # how the incident developed across the full investigation window.

        story_groups = []

        phase_boundaries = [
            (
                incident_time - pd.Timedelta(minutes=15),
                incident_time - pd.Timedelta(minutes=10),
                "Initial signs",
                "before",
            ),
            (
                incident_time - pd.Timedelta(minutes=10),
                incident_time - pd.Timedelta(minutes=5),
                "Degradation increased",
                "before",
            ),
            (
                incident_time - pd.Timedelta(minutes=5),
                incident_time + pd.Timedelta(minutes=5),
                "Incident",
                "during",
            ),
            (
                incident_time + pd.Timedelta(minutes=5),
                incident_time + pd.Timedelta(minutes=10),
                "Impact continued",
                "after",
            ),
            (
                incident_time + pd.Timedelta(minutes=10),
                incident_time + pd.Timedelta(minutes=15),
                "Impact persisted",
                "after",
            ),
        ]

        # Make sure telemetry is ordered by timestamp.
        sorted_window_events = sorted(
            window_events,
            key=lambda event: event["_parsed_timestamp"],
        )

        for (
            phase_start,
            phase_end,
            phase_name,
            phase_class,
        ) in phase_boundaries:

            phase_events = [
                event
                for event in sorted_window_events
                if phase_start
                <= event["_parsed_timestamp"]
                < phase_end
            ]

            # IMPORTANT:
            # Do not skip empty phases.
            # Every phase must appear in the incident story.
            story_groups.append(
                {
                    "first_time": phase_start,
                    "last_time": phase_end,
                    "events": phase_events,
                    "phase": phase_name,
                    "phase_class": phase_class,
                }
            )

        # -------------------------------------------------
        # Build one story card per group
        # -------------------------------------------------

        for group in story_groups:

            # -------------------------------------------------
            # Incident development phase
            # -------------------------------------------------
            # IMPORTANT:
            # Always render every phase, even when there is
            # no telemetry event in that period.
            #
            # This makes the timeline tell the full incident
            # story instead of showing only the phase containing
            # telemetry records.

            events = group["events"]

            event_time = group["first_time"]

            # Use the phase defined above.
            # Do NOT recalculate it from event_time because that
            # would collapse different development phases together.

            phase = group["phase"]
            phase_class = group["phase_class"]

            # -------------------------------------------------
            # Collect evidence
            # -------------------------------------------------

            metric_events = []
            log_events = []
            trace_events = []

            services = []
            operations = []

            has_latency = False
            has_cpu = False
            has_memory = False
            has_network = False
            has_volume = False

            # Keep only useful numeric evidence.
            numeric_details = []

            for event in events:

                event_type = str(
                    event.get(
                        "evidence_type",
                        event.get("type", "metric"),
                    )
                    or "metric"
                ).lower()

                if event_type == "metric":

                    metric_events.append(event)

                elif event_type == "log":

                    log_events.append(event)

                elif event_type == "trace":

                    trace_events.append(event)

                # ---------------------------------------------
                # Service
                # ---------------------------------------------

                service = _timeline_service_name(
                    event.get(
                        "service",
                        "Unknown service",
                    )
                )

                if (
                    service
                    and service != "Unknown service"
                    and service not in services
                ):

                    services.append(service)

                # ---------------------------------------------
                # Metric name
                # ---------------------------------------------

                metric_name = str(
                    event.get(
                        "metric_name",
                        event.get(
                            "metric",
                            event.get(
                                "name",
                                event.get(
                                    "title",
                                    "",
                                ),
                            ),
                        ),
                    )
                    or ""
                ).strip()

                normalized_name = (
                    metric_name
                    .lower()
                    .replace("_", " ")
                    .replace(".", " ")
                    .replace("-", " ")
                )

                # ---------------------------------------------
                # Operation
                # ---------------------------------------------

                operation = _timeline_operation_name(
                    event.get(
                        "operation",
                        "",
                    )
                )

                if (
                    operation
                    and operation not in operations
                ):

                    operations.append(operation)

                # ---------------------------------------------
                # Detect problem category
                # ---------------------------------------------

                if (
                    "request duration" in normalized_name
                    or "request latency" in normalized_name
                    or "response duration" in normalized_name
                    or "response latency" in normalized_name
                    or "duration milliseconds" in normalized_name
                    or "latency" in normalized_name
                ):

                    has_latency = True

                if (
                    "cpu" in normalized_name
                    and (
                        "thrott" in normalized_name
                        or "usage" in normalized_name
                        or "user" in normalized_name
                    )
                ):

                    has_cpu = True

                if (
                    "memory" in normalized_name
                    or "pgfault" in normalized_name
                ):

                    has_memory = True

                if (
                    "network" in normalized_name
                    or "receive packet" in normalized_name
                    or "transmit packet" in normalized_name
                    or "request bytes" in normalized_name
                    or "response bytes" in normalized_name
                ):

                    has_network = True

                if (
                    "request message" in normalized_name
                    or "response message" in normalized_name
                    or normalized_name == "requests"
                    or normalized_name.endswith(" requests")
                ):

                    has_volume = True

                # ---------------------------------------------
                # Useful numeric evidence
                # ---------------------------------------------

                if (
                    event_type != "metric"
                    or not metric_name
                ):

                    continue

                current_value = event.get("current")

                if current_value is None:

                    current_value = event.get("value")

                baseline_value = event.get("baseline")

                if baseline_value is None:

                    baseline_value = event.get("normal")

                if (
                    current_value is None
                    or baseline_value is None
                ):

                    continue

                try:

                    current_num = float(current_value)
                    baseline_num = float(baseline_value)

                except (
                    TypeError,
                    ValueError,
                ):

                    continue

                # Do not show meaningless 0 vs 0 values.

                if (
                    current_num == 0
                    and baseline_num == 0
                ):

                    continue

                deviation = None

                if baseline_num != 0:

                    deviation = (
                        (
                            current_num
                            - baseline_num
                        )
                        / abs(baseline_num)
                    ) * 100

                # Ignore tiny/non-useful changes.

                if (
                    deviation is not None
                    and abs(deviation) < 5
                ):

                    continue

                numeric_details.append(
                    {
                        "name": metric_name,
                        "current": current_num,
                        "baseline": baseline_num,
                        "deviation": deviation,
                    }
                )

            # -------------------------------------------------
            # Human-readable service name
            # -------------------------------------------------

            if services:

                service_text = ", ".join(
                    services[:2]
                )

            else:

                service_text = "Related services"

            # -------------------------------------------------
            # Create story title

            if has_latency and has_cpu:

                title = (
                    f"{service_text} experienced slower requests "
                    f"and CPU pressure"
                )

                description = (
                    "Requests were taking longer to process than normal. "
                    "The service also showed signs of CPU throttling "
                    "or high CPU usage."
                )

            elif has_latency:

                title = (
                    f"{service_text} was processing requests more slowly"
                )

                description = (
                    "Request processing time increased compared with "
                    "the normal baseline, indicating slower service response."
                )

            elif has_cpu:

                title = (
                    f"{service_text} experienced CPU pressure"
                )

                description = (
                    "CPU usage increased or CPU throttling was detected. "
                    "This can cause requests to wait longer for processing."
                )

            elif has_memory:

                title = (
                    f"{service_text} showed abnormal memory activity"
                )

                description = (
                    "Memory activity was higher than the normal baseline."
                )

            elif has_network:

                title = (
                    f"{service_text} showed abnormal network activity"
                )

                description = (
                    "Network traffic changed significantly compared "
                    "with the normal baseline."
                )

            elif has_volume:

                title = (
                    f"{service_text} showed increased request activity"
                )

                description = (
                    "Request or response volume changed compared "
                    "with the normal baseline."
                )

            elif log_events:

                title = (
                    f"{service_text} reported an application error"
                )

                description = (
                    "Application logs reported abnormal activity "
                    "within the service."
                )

            elif trace_events:

                title = (
                    f"{service_text} showed abnormal request behavior"
                )

                description = (
                    "Request traces showed increased latency or "
                    "different request processing behavior."
                )

            else:

                title = (
                    f"{service_text} showed abnormal behavior"
                )

                description = (
                    "Telemetry showed activity that differed "
                    "from the normal baseline."
                )


            # -------------------------------------------------
            # Add operation context
            # -------------------------------------------------

            operation_html = ""

            if operations:

                operation_html = (
                    '<div class="orc-context">'
                    "<b>Affected operations:</b> "
                    + ", ".join(operations[:2])
                    + "</div>"
                )


            # -------------------------------------------------
            # Evidence summary
            # -------------------------------------------------

            evidence_parts = []

            if metric_events:

                evidence_parts.append(
                    f"{len(metric_events)} performance signals"
                )

            if trace_events:

                evidence_parts.append(
                    f"{len(trace_events)} request traces"
                )

            if log_events:

                evidence_parts.append(
                    f"{len(log_events)} application logs"
                )

            evidence_text = " · ".join(
                evidence_parts
            )


            evidence_html = ""

            if evidence_text:

                evidence_html = (
                    '<div class="orc-evidence">'
                    "<b>Evidence:</b> "
                    f"{evidence_text}"
                    "</div>"
                )


            # -------------------------------------------------
            # Numeric details
            # -------------------------------------------------

            values_html = ""

            if numeric_details:

                detail_html = []

                # Show at most two meaningful measurements.
                # Never expose raw telemetry metric names.

                for detail in numeric_details[:2]:

                    name = str(
                        detail["name"]
                    ).lower()

                    if (
                        "request duration" in name
                        or "request latency" in name
                        or "duration milliseconds" in name
                        or "latency" in name
                    ):

                        readable_name = "Request latency"

                    elif (
                        "cpu" in name
                        and "thrott" in name
                    ):

                        readable_name = "CPU throttling"

                    elif "cpu" in name:

                        readable_name = "CPU usage"

                    elif "memory" in name:

                        readable_name = "Memory usage"

                    elif (
                        "request bytes" in name
                        or "response bytes" in name
                        or "network" in name
                    ):

                        readable_name = "Network traffic"

                    elif "request" in name:

                        readable_name = "Request rate"

                    else:

                        readable_name = "Performance metric"


                    deviation_text = ""

                    if detail["deviation"] is not None:

                        if detail["deviation"] > 0:

                            deviation_text = (
                                f" — {abs(detail['deviation']):.0f}% above normal"
                            )

                        elif detail["deviation"] < 0:

                            deviation_text = (
                                f" — {abs(detail['deviation']):.0f}% below normal"
                            )


                    detail_html.append(
                        "<span>"
                        f"<b>{readable_name}</b>: "
                        f"{detail['current']:,.2f} "
                        f"vs. {detail['baseline']:,.2f} baseline"
                        f"{deviation_text}"
                        "</span>"
                    )


                values_html = "".join(
                    detail_html
                )
            # Render one story card
            # -------------------------------------------------

            marker_icon = (
                "🔴"
                if phase == "Incident"
                else "•"
            )

            timeline_html += f"""
            <div class="orc-item">

                <div class="orc-time">
                    {event_time.strftime("%H:%M:%S")}
                </div>

                <div class="orc-marker">

                    <div class="orc-dot">
                        {marker_icon}
                    </div>

                    <div class="orc-line"></div>

                </div>

                <div class="orc-content">

                    <div class="orc-meta">

                        <span class="orc-phase {phase_class}">
                            {phase}
                        </span>

                    </div>

                    <div class="orc-title">
                        {title}
                    </div>

                    <div class="orc-description">
                        {description}
                    </div>

                    {operation_html}

                    {evidence_html}

                    {
                        f'<div class="orc-values">{values_html}</div>'
                        if values_html
                        else ""
                    }

                </div>

            </div>
            """

        # Render timeline
        # -------------------------------------------------

        timeline_css = """
        <style>
        .orc-timeline {
              width: 100%;
              margin-top: 12px;
              box-sizing: border-box;
          }

          .orc-scroll {
              height: 560px;
              max-height: 560px;
              overflow-y: auto;
              overflow-x: hidden;
              padding-right: 12px;
              box-sizing: border-box;
              scroll-behavior: smooth;
          }


        .orc-summary {
            font-size: 13px;
            color: #667085;
            margin-bottom: 18px;
        }

        .orc-summary b {
            color: #1f2937;
        }

        .orc-item {
            display: grid;
            grid-template-columns: 72px 36px minmax(0, 1fr);
            column-gap: 10px;
            width: 100%;
            min-height: 100px;
            box-sizing: border-box;
        }

        .orc-time {
            text-align: right;
            padding-top: 5px;
            padding-right: 4px;
            color: #667085;
            font-size: 12px;
            white-space: nowrap;
        }

        .orc-marker {
            position: relative;
            display: flex;
            justify-content: center;
            min-height: 100%;
        }

        .orc-dot {
            position: relative;
            z-index: 2;
            width: 30px;
            height: 30px;
            border: 1px solid #d0d5dd;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            box-sizing: border-box;
        }

        .orc-line {
            position: absolute;
            top: 30px;
            bottom: 0;
            left: 50%;
            width: 1px;
            background: #e4e7ec;
            transform: translateX(-50%);
        }

        .orc-content {
            min-width: 0;
            padding: 0 0 26px 4px;
            box-sizing: border-box;
        }

        .orc-meta {
            display: flex;
            align-items: center;
            gap: 7px;
            margin-bottom: 7px;
        }

        .orc-phase {
            display: inline-block;
            padding: 4px 7px;
            border-radius: 5px;
            font-size: 10px;
            font-weight: 700;
            line-height: 1;
        }

        .orc-phase.before {
            background: #f2f4f7;
            color: #475467;
        }

        .orc-phase.during {
            background: #fff4e5;
            color: #b54708;
        }

        .orc-phase.after {
            background: #ecfdf3;
            color: #027a48;
        }

        .orc-type {
            font-size: 10px;
            font-weight: 700;
            color: #667085;
        }

        .orc-title {
            font-size: 15px;
            line-height: 1.4;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 5px;
        }

        .orc-description {
            font-size: 13px;
            line-height: 1.5;
            color: #667085;
            margin-bottom: 9px;
        }

        .orc-values {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 8px 0 5px 0;
        }

        .orc-values span {
            display: inline-flex;
            padding: 5px 9px;
            border: 1px solid #e4e7ec;
            border-radius: 6px;
            background: #f8fafc;
            color: #667085;
            font-size: 12px;
        }

        .orc-values b {
            color: #1f2937;
        }

        .orc-deviation {
            display: inline-block;
            margin-top: 2px;
            color: #b54708;
            font-size: 12px;
            font-weight: 700;
        }
        </style>
        """

        timeline_render_html = f"""
        {timeline_css}

        <div class="orc-timeline">

            <div class="orc-summary">
                <b>{len(window_events)}</b>
                abnormal signals detected
                ·
                {window_start.strftime("%H:%M:%S")}
                →
                {window_end.strftime("%H:%M:%S")}
            </div>

            {timeline_html}

        </div>
        """

        st.html(timeline_render_html)

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

            # =================================================
            # SERVICE-SPECIFIC EVIDENCE
            # =================================================
            # Calculate evidence separately for the current RCA service.
            # Related service instances are included automatically.

            service_prefix = service.strip().lower()

            if not evidence_df.empty:
                service_evidence_df = evidence_df[
                    evidence_df["service"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.startswith(service_prefix)
                ].copy()
            else:
                service_evidence_df = pd.DataFrame()

            if not service_evidence_df.empty:
                service_metric_df = service_evidence_df[
                    service_evidence_df["evidence_type"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains("metric", na=False)
                ]

                service_log_df = service_evidence_df[
                    service_evidence_df["evidence_type"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains("log", na=False)
                ]

                service_trace_df = service_evidence_df[
                    service_evidence_df["evidence_type"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains("trace", na=False)
                ]
            else:
                service_metric_df = pd.DataFrame()
                service_log_df = pd.DataFrame()
                service_trace_df = pd.DataFrame()

            metric_count = len(service_metric_df)
            log_count = len(service_log_df)
            trace_count = len(service_trace_df)
            total_service_evidence = len(service_evidence_df)

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

            root_lower = clean_root_cause.lower()

            if (
                "downstream" in root_lower
                or "dependent" in root_lower
                or "dependency" in root_lower
            ):
                why_this_happened = (
                    f"{service} depends on other services or operations. "
                    "When those dependencies became slower, requests "
                    "handled by this service also took longer."
                )

            elif (
                "cpu" in root_lower
                or "resource" in root_lower
                or "throttling" in root_lower
            ):
                why_this_happened = (
                    f"{service} was affected by CPU pressure or limited "
                    "compute resources, which reduced its ability to "
                    "process requests efficiently."
                )

            elif (
                "latency" in root_lower
                or "duration" in root_lower
                or "performance" in root_lower
            ):
                why_this_happened = (
                    f"One or more operations handled by {service} "
                    "became slower than normal, increasing the time "
                    "required to complete requests."
                )

            else:
                why_this_happened = (
                    f"Telemetry shows that {service} was operating "
                    "outside its normal performance baseline."
                )

            st.markdown(
                f'<div class="section-description">'
                f'{why_this_happened}'
                f'</div>',
                unsafe_allow_html=True
            )

            # SUPPORTING EVIDENCE
            # =================================================

            st.markdown("### 🔎 Supporting Evidence")

            st.caption(
                f"Evidence collected specifically for **{service}** "
                "and its related service instances."
            )

            if service_evidence_df.empty:

                st.info(
                    f"No abnormal telemetry evidence was found for {service}."
                )

            else:

                # -------------------------------------------------
                # Evidence summary
                # -------------------------------------------------

                summary_cols = st.columns(3)

                with summary_cols[0]:
                    st.metric(
                        "Metric signals",
                        int(metric_count)
                    )

                with summary_cols[1]:
                    st.metric(
                        "Trace signals",
                        int(trace_count)
                    )

                with summary_cols[2]:
                    st.metric(
                        "Log records",
                        int(log_count)
                    )

                # -------------------------------------------------
                # Build readable evidence table
                # -------------------------------------------------

                evidence_rows = []

                for _, evidence in service_evidence_df.iterrows():

                    evidence_type = str(
                        evidence.get(
                            "evidence_type",
                            ""
                        )
                    ).strip().lower()

                    if evidence_type == "metric":

                        evidence_label = "Metric"

                        metric_name = str(
                            evidence.get(
                                "metric_name",
                                "Unknown metric"
                            )
                        )

                        # Make technical metric names easier to read.
                        metric_name = metric_name.replace(
                            "istio_request_duration_milliseconds",
                            "Request duration"
                        )

                        metric_name = metric_name.replace(
                            "container_cpu_cfs_throttled_periods",
                            "CPU throttling"
                        )

                        description = str(
                            evidence.get(
                                "description",
                                ""
                            )
                        ).strip()

                        observed = evidence.get(
                            "value",
                            None
                        )

                        baseline = evidence.get(
                            "baseline",
                            None
                        )

                        if pd.notna(observed):
                            observed_text = f"{float(observed):.2f}"
                        else:
                            observed_text = "—"

                        if pd.notna(baseline):
                            baseline_text = f"{float(baseline):.2f}"
                        else:
                            baseline_text = "—"

                        detail = description or metric_name

                        context = metric_name

                    elif evidence_type == "trace":

                        evidence_label = "Trace"

                        operation = str(
                            evidence.get(
                                "operation",
                                ""
                            )
                        ).strip()

                        description = str(
                            evidence.get(
                                "description",
                                ""
                            )
                        ).strip()

                        observed = evidence.get(
                            "value",
                            None
                        )

                        baseline = evidence.get(
                            "baseline",
                            None
                        )

                        if pd.notna(observed):
                            observed_text = f"{float(observed):.2f} ms"
                        else:
                            observed_text = "—"

                        if pd.notna(baseline):
                            baseline_text = f"{float(baseline):.2f} ms"
                        else:
                            baseline_text = "—"

                        detail = description or "Abnormal trace latency detected."
                        context = operation or "Unknown operation"

                    elif evidence_type == "log":

                        evidence_label = "Log"

                        detail = str(
                            evidence.get(
                                "description",
                                "Related log activity detected."
                            )
                        ).strip()

                        observed_text = "—"
                        baseline_text = "—"
                        context = str(
                            evidence.get(
                                "operation",
                                "Log record"
                            )
                        ).strip() or "Log record"

                    else:
                        continue

                    evidence_rows.append({
                        "Type": evidence_label,
                        "What was detected": detail,
                        "Observed": observed_text,
                        "Normal": baseline_text,
                        "Operation / Metric": context,
                    })

                if evidence_rows:

                    evidence_display_df = pd.DataFrame(
                        evidence_rows
                    )

                    st.dataframe(
                        evidence_display_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Type": st.column_config.TextColumn(
                                "Evidence type",
                                width="small"
                            ),
                            "What was detected": st.column_config.TextColumn(
                                "What was detected",
                                width="large"
                            ),
                            "Observed": st.column_config.TextColumn(
                                "Observed",
                                width="small"
                            ),
                            "Normal": st.column_config.TextColumn(
                                "Normal",
                                width="small"
                            ),
                            "Operation / Metric": st.column_config.TextColumn(
                                "Operation / Metric",
                                width="medium"
                            ),
                        },
                    )

                else:
                    st.info(
                        "Evidence was found, but no readable evidence details are available."
                    )


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
