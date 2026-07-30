from src.database.connection import get_connection


# =====================================================
# INVESTIGATION
# =====================================================

def create_investigation(
    issue_key,
    environment,
    dataset,
    incident_time,
    window_start,
    window_end,
    incident_description
):

    conn = get_connection()
    cur = conn.cursor()


    sql = """
    INSERT INTO investigations
    (
        issue_key,
        environment,
        dataset,
        incident_time,
        window_start,
        window_end,
        incident_description
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s)

    RETURNING id;
    """


    cur.execute(
        sql,
        (
            issue_key,
            environment,
            dataset,
            incident_time,
            window_start,
            window_end,
            incident_description
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


    sql = """
    INSERT INTO investigation_metrics
    (
        investigation_id,
        timestamp,
        cmdb_id,
        kpi_name,
        value
    )
    VALUES (%s,%s,%s,%s,%s)
    """


    records = []


    for _, row in dataframe.iterrows():

        records.append(
            (
                investigation_id,
                int(row["timestamp"].timestamp() * 1000),
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
    VALUES (%s,%s,%s,%s,%s,%s)
    """


    records = []


    for _, row in dataframe.iterrows():

        records.append(
            (
                investigation_id,
                row["log_id"],
                int(row["timestamp"].timestamp() * 1000),
                row["cmdb_id"],
                row["log_name"],
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
# RAW TRACE
# =====================================================

def insert_traces(
    investigation_id,
    dataframe
):

    conn = get_connection()
    cur = conn.cursor()


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


    for _, row in dataframe.iterrows():

        records.append(
            (
                investigation_id,
                int(row["timestamp"].timestamp() * 1000),
                row["cmdb_id"],
                row["span_id"],
                row["trace_id"],
                row["duration"],
                row["type"],
                str(row["status_code"]),
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
    VALUES (%s,%s,%s,%s,%s)
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
    VALUES (%s,%s,%s,%s)
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