from src.database.connection import get_connection
import pandas as pd

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
        dataset,
        incident_time,
        window_start,
        window_end,
        incident_description,
        reporter,
        reporter_email
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s)

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

    # Ép kiểu toàn bộ cột timestamp trong dataframe thành epoch milliseconds (kiểu int)
    df = dataframe.copy()
    if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = df["timestamp"].astype('int64') // 10**6
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"]).astype('int64') // 10**6


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

    for _, row in df.iterrows():
        records.append(
            (
                investigation_id,
                int(row["timestamp"]),  # Đảm bảo chắc chắn là kiểu int
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

    df = dataframe.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Ép kiểu toàn bộ cột timestamp thành int64 milliseconds một lần duy nhất
    df["timestamp"] = df["timestamp"].astype('int64') // 10**6
    # Tự động tìm tên cột nội dung log nếu không có sẵn cột 'content'
    content_col = "content"
    for candidate in ["content", "log", "message", "body", "text"]:
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
        content
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    records = []
    for _, row in df.iterrows():
        # Lấy nội dung an toàn, nếu không tìm thấy cột nào thì gán chuỗi rỗng
        log_content = str(row[content_col]) if content_col in df.columns and pd.notna(row[content_col]) else ""

        records.append(
            (
                investigation_id,
                row.get("log_id",""),
                int(row["timestamp"]),  # Đã là kiểu int được chuẩn hóa từ trước
                row.get("cmdb_id",""),
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
  # Ép kiểu toàn bộ cột timestamp trong dataframe thành epoch milliseconds (kiểu int)
    df = dataframe.copy()
    if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = df["timestamp"].astype('int64') // 10**6
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"]).astype('int64') // 10**6

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

        # Xử lý an toàn cho status_code để tránh lỗi nếu dữ liệu trống hoặc không phải số
        raw_status = row["status_code"]
        try:
            status_code_val = int(float(raw_status)) if pd.notna(raw_status) else 0
        except (ValueError, TypeError):
            status_code_val = 0

        records.append(
            (
                investigation_id,
                int(row["timestamp"]),
                row["cmdb_id"],
                row["span_id"],
                row["trace_id"],
                row["duration"],
                row["type"],
                status_code_val,  # Sử dụng giá trị đã ép kiểu integer an toàn
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