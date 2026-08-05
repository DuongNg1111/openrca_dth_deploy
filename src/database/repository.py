from src.database.connection import get_connection
import pandas as pd


# =====================================================
# Helper: Normalize Timestamp For PostgreSQL TIMESTAMP
# =====================================================

def ensure_datetime(df):

    df = df.copy()

    if "timestamp" in df.columns:

        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):

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

    VALUES
    (%s,%s,%s,%s,%s)
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


    cur.executemany(
        sql,
        records
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
        "text"
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

    VALUES
    (%s,%s,%s,%s,%s,%s)
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
                row.get("log_id",""),
                row["timestamp"],
                row.get("cmdb_id",""),
                row.get("log_name",""),
                log_content
            )
        )

    cur.executemany(
        sql,
        records
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

    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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


    cur.executemany(
        sql,
        records
    )


    conn.commit()

    cur.close()
    conn.close()



# =====================================================
# EVIDENCE
# =====================================================

def insert_evidence(
    investigation_id,
    service,
    evidence_type,
    description,
    score
):

    conn = get_connection()
    cur = conn.cursor()


    sql = """
    INSERT INTO evidence_records
    (
        investigation_id,
        service,
        evidence_type,
        description,
        score
    )

    VALUES
    (%s,%s,%s,%s,%s)
    """


    cur.execute(
        sql,
        (
            investigation_id,
            service,
            evidence_type,
            description,
            score
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
        root_cause,
        confidence,
        explanation
    )

    VALUES
    (%s,%s,%s,%s)
    """


    cur.execute(
        sql,
        (
            investigation_id,
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
        WHERE issue_key = %s;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(issue_key,)
    )

    conn.close()

    return df