import json

import pandas as pd
from psycopg2.extras import execute_values

from src.database.connection import get_connection

# =====================================================
# Helper: Normalize Timestamp For PostgreSQL TIMESTAMP
# =====================================================

def ensure_datetime(df):

    df = df.copy()

    if "timestamp" not in df.columns:
        return df

    if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        return df

    if pd.api.types.is_numeric_dtype(df["timestamp"]):

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            unit="s",
            errors="coerce"
        )

    else:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

    return df


# =====================================================
# INVESTIGATION
# =====================================================

def create_investigation(
    issue_key,
    environment,
    affected_system,
    dataset,
    incident_time,
    window_start,
    window_end,
    incident_description,
    reporter,
    reporter_email
):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO investigations
        (
            issue_key,
            environment,
            affected_system,
            dataset,
            incident_time,
            window_start,
            window_end,
            incident_description,
            reporter,
            reporter_email
        )

        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

        RETURNING id;
    """

    cur.execute(
        sql,
        (
            issue_key,
            environment,
            affected_system,
            dataset,
            incident_time,
            window_start,
            window_end,
            incident_description,
            reporter,
            reporter_email
        )
    )

    investigation_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return investigation_id


# =====================================================
# UPDATE INVESTIGATION STATUS
# =====================================================

def update_investigation_status(
    investigation_id: int,
    status: str
):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        UPDATE investigations
        SET status = %s
        WHERE id = %s;
    """

    cur.execute(
        sql,
        (
            status,
            investigation_id
        )
    )

    conn.commit()

    cur.close()
    conn.close()

# =====================================================
# RAW METRICS
# =====================================================

def insert_metrics(
    investigation_id,
    dataframe
):

    conn = get_connection()
    cur = conn.cursor()

    df = ensure_datetime(
        dataframe
    )

    sql = """
        INSERT INTO investigation_metrics
        (
            investigation_id,
            timestamp,
            cmdb_id,
            kpi_name,
            value
        )

        VALUES %s
    """

    records = []

    for _, row in df.iterrows():

        records.append(
            (
                investigation_id,
                row["timestamp"],
                row["cmdb_id"],
                row["kpi_name"],
                row["value"]
            )
        )

    if records:

        execute_values(
            cur,
            sql,
            records,
            page_size=5000
        )

    conn.commit()

    cur.close()
    conn.close()


# =====================================================
# RAW LOGS
# =====================================================

def insert_logs(
    investigation_id,
    dataframe
):

    conn = get_connection()
    cur = conn.cursor()

    df = ensure_datetime(
        dataframe
    )

    content_col = "content"

    for candidate in [
        "content",
        "log",
        "message",
        "body",
        "text",
        "value",
    ]:

        if candidate in df.columns:

            content_col = candidate
            break

    sql = """
        INSERT INTO investigation_logs
        (
            investigation_id,
            log_id,
            timestamp,
            cmdb_id,
            log_name,
            value
        )

        VALUES %s
    """

    records = []

    for _, row in df.iterrows():

        log_content = ""

        if (
            content_col in df.columns
            and pd.notna(row[content_col])
        ):

            log_content = str(
                row[content_col]
            )

        records.append(
            (
                investigation_id,
                row.get("log_id", ""),
                row["timestamp"],
                row.get("cmdb_id", ""),
                row.get("log_name", ""),
                log_content
            )
        )

    if records:

        execute_values(
            cur,
            sql,
            records,
            page_size=5000
        )

    conn.commit()

    cur.close()
    conn.close()


# =====================================================
# RAW TRACE
# =====================================================

def insert_traces(
    investigation_id,
    dataframe
):

    conn = get_connection()
    cur = conn.cursor()

    df = ensure_datetime(
        dataframe
    )

    sql = """
        INSERT INTO investigation_traces
        (
            investigation_id,
            timestamp,
            cmdb_id,
            span_id,
            trace_id,
            duration,
            type,
            status_code,
            operation_name,
            parent_span
        )

        VALUES %s
    """

    records = []

    for _, row in df.iterrows():

        raw_status = row["status_code"]

        try:

            status_code_val = (
                int(float(raw_status))
                if pd.notna(raw_status)
                else 0
            )

        except (
            ValueError,
            TypeError
        ):

            status_code_val = 0

        records.append(
            (
                investigation_id,
                row["timestamp"],
                row["cmdb_id"],
                row["span_id"],
                row["trace_id"],
                row["duration"],
                row["type"],
                status_code_val,
                row["operation_name"],
                row["parent_span"]
            )
        )

    if records:

        execute_values(
            cur,
            sql,
            records,
            page_size=5000
        )

    conn.commit()

    cur.close()
    conn.close()

# =====================================================
# INVESTIGATION DATA - READ
# =====================================================

def get_investigation_metrics(
    investigation_id,
    service=None
):
    """
    Get preprocessed metrics stored for one investigation.

    If service is provided, only return metrics whose
    cmdb_id contains the logical service name.
    """

    conn = get_connection()

    query = """
        SELECT
            timestamp,
            cmdb_id,
            kpi_name,
            value
        FROM investigation_metrics
        WHERE investigation_id = %s
    """

    params = [investigation_id]

    if service:
        query += """
            AND cmdb_id ILIKE %s
        """
        params.append(
            f"%{service}%"
        )

    query += """
        ORDER BY timestamp;
    """

    df = pd.read_sql(
        query,
        conn,
        params=tuple(params)
    )

    conn.close()

    return df

def get_investigation_logs(
    investigation_id,
    service=None
):
    """
    Get preprocessed logs stored for one investigation.

    If service is provided, only return logs whose
    cmdb_id contains the logical service name.
    """

    conn = get_connection()

    query = """
        SELECT
            log_id,
            timestamp,
            cmdb_id,
            log_name,
            value
        FROM investigation_logs
        WHERE investigation_id = %s
    """

    params = [investigation_id]

    if service:
        query += """
            AND cmdb_id ILIKE %s
        """
        params.append(
            f"%{service}%"
        )

    query += """
        ORDER BY timestamp;
    """

    df = pd.read_sql(
        query,
        conn,
        params=tuple(params)
    )

    conn.close()

    return df

def get_investigation_traces(
    investigation_id,
    service=None
):

    conn = get_connection()

    query = """
        SELECT
            timestamp,
            cmdb_id,
            span_id,
            trace_id,
            duration,
            type,
            status_code,
            operation_name,
            parent_span
        FROM investigation_traces
        WHERE investigation_id = %s
    """

    params = [
        investigation_id
    ]


    if service:

        query += """
            AND cmdb_id ILIKE %s
        """

        params.append(
            f"%{service}%"
        )


    query += """
        ORDER BY timestamp;
    """


    df = pd.read_sql(
        query,
        conn,
        params=tuple(params)
    )


    conn.close()


    return df

def get_investigation_evidence(
    investigation_id,
    service=None
):
    """
    Get evidence generated by agents
    for one investigation.

    If service is provided, only evidence
    belonging to that service is returned.
    """

    conn = get_connection()

    if service is not None:

        query = """
            SELECT
                id,
                service,
                evidence_type,
                metric_name,
                trace_id,
                operation,
                description,
                value,
                baseline,
                timestamp,
                score,
                confidence,
                metadata
            FROM evidence_records
            WHERE investigation_id = %s
              AND service = %s
            ORDER BY id;
        """

        df = pd.read_sql(
            query,
            conn,
            params=(investigation_id, service)
        )

    else:

        query = """
            SELECT
                id,
                service,
                evidence_type,
                metric_name,
                trace_id,
                operation,
                description,
                value,
                baseline,
                timestamp,
                score,
                confidence,
                metadata
            FROM evidence_records
            WHERE investigation_id = %s
            ORDER BY id;
        """

        df = pd.read_sql(
            query,
            conn,
            params=(investigation_id,)
        )

    conn.close()

    return df

# =====================================================
# EVIDENCE
# =====================================================

def insert_evidence(
    investigation_id,
    service,
    evidence_type,
    description,
    score,
    metric_name=None,
    trace_id=None,
    operation=None,
    value=None,
    baseline=None,
    timestamp=None,
    confidence=0.0,
    metadata=None
):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO evidence_records
        (
            investigation_id,
            service,
            evidence_type,
            metric_name,
            trace_id,
            operation,
            description,
            value,
            baseline,
            timestamp,
            score,
            confidence,
            metadata
        )

        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

    cur.execute(
        sql,
        (
            investigation_id,
            service,
            evidence_type,
            metric_name,
            trace_id,
            operation,
            description,
            value,
            baseline,
            timestamp,
            score,
            confidence,
            json.dumps(metadata)
        )
    )

    conn.commit()

    cur.close()
    conn.close()


# =====================================================
# RCA RESULT
# =====================================================

def save_rca_result(
    investigation_id,
    service,
    root_cause,
    confidence,
    explanation
):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO rca_results
        (
            investigation_id,
            service,
            root_cause,
            confidence,
            explanation
        )

        VALUES
        (%s, %s, %s, %s, %s)
    """

    cur.execute(
        sql,
        (
            investigation_id,
            service,
            root_cause,
            confidence,
            explanation
        )
    )

    conn.commit()

    cur.close()
    conn.close()


# =====================================================
# STREAMLIT - MY INCIDENTS
# =====================================================

def get_user_incidents(
    reporter_email
):
    """
    Get all incidents submitted by a user.
    """

    conn = get_connection()

    query = """
        SELECT
            id,
            issue_key,
            environment,
            affected_system,
            created_at,
            incident_time,
            incident_description,
            status
        FROM investigations
        WHERE reporter_email=%s
        ORDER BY created_at DESC;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(reporter_email,)
    )

    conn.close()

    return df


# =====================================================
# STREAMLIT - INCIDENT DETAIL
# =====================================================

def get_incident_detail(
    issue_key
):
    """
    Get one incident detail by Jira ticket.
    """

    conn = get_connection()

    query = """
        SELECT *
        FROM investigations
        WHERE issue_key = %s
        ORDER BY id DESC
        LIMIT 1;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(issue_key,)
    )

    conn.close()

    return df


#
