"""
Database schemas for OpenRCA investigation workflow.

Stores only investigation-related data:
- raw telemetry snapshot
- processed telemetry
- evidence
- RCA result
"""


TABLE_SCHEMAS = {


    # =====================================================
    # INVESTIGATION / TICKET
    # =====================================================

    "investigations": {

        "columns": {

            "id": "SERIAL PRIMARY KEY",

            "issue_key": "TEXT",

            "environment": "TEXT",

            "dataset": "TEXT",

            "incident_time": "TIMESTAMP",

            "window_start": "TIMESTAMP",

            "window_end": "TIMESTAMP",

            "incident_description": "TEXT"

        }
    },


    # =====================================================
    # RAW METRIC SNAPSHOT
    # =====================================================

    "investigation_metrics": {

        "columns": {

            "id": "SERIAL PRIMARY KEY",

            "investigation_id": "INTEGER",

            "timestamp": "BIGINT",

            "cmdb_id": "TEXT",

            "kpi_name": "TEXT",

            "value": "DOUBLE PRECISION"

        }
    },


    # =====================================================
    # RAW LOG SNAPSHOT
    # =====================================================

    "investigation_logs": {

        "columns": {

            "id": "SERIAL PRIMARY KEY",

            "investigation_id": "INTEGER",

            "log_id": "TEXT",

            "timestamp": "BIGINT",

            "cmdb_id": "TEXT",

            "log_name": "TEXT",

            "value": "TEXT"

        }
    },


    # =====================================================
    # RAW TRACE SNAPSHOT
    # =====================================================

    "investigation_traces": {

        "columns": {

            "id": "SERIAL PRIMARY KEY",

            "investigation_id": "INTEGER",

            "timestamp": "BIGINT",

            "cmdb_id": "TEXT",

            "span_id": "TEXT",

            "trace_id": "TEXT",

            "duration": "INTEGER",

            "type": "TEXT",

            "status_code": "INTEGER",

            "operation_name": "TEXT",

            "parent_span": "TEXT"

        }
    },


    # =====================================================
    # PROCESSED METRIC
    # =====================================================

    "processed_metrics": {

        "columns": {

            "id": "SERIAL PRIMARY KEY",

            "investigation_id": "INTEGER",

            "cmdb_id": "TEXT",

            "kpi_name": "TEXT",

            "feature_name": "TEXT",

            "feature_value": "DOUBLE PRECISION",

            "is_anomaly": "BOOLEAN"

        }
    },


    # =====================================================
    # PROCESSED LOG
    # =====================================================

    "processed_logs": {

        "columns": {

            "id": "SERIAL PRIMARY KEY",

            "investigation_id": "INTEGER",

            "cmdb_id": "TEXT",

            "log_pattern": "TEXT",

            "severity": "TEXT"

        }
    },


    # =====================================================
    # PROCESSED TRACE
    # =====================================================

    "processed_traces": {

        "columns": {

            "id": "SERIAL PRIMARY KEY",

            "investigation_id": "INTEGER",

            "parent_service": "TEXT",

            "child_service": "TEXT",

            "latency": "DOUBLE PRECISION"

        }
    },


    # =====================================================
    # EVIDENCE
    # =====================================================

    "evidence_records": {

        "columns": {

            "id": "SERIAL PRIMARY KEY",

            "investigation_id": "INTEGER",

            "service": "TEXT",

            "evidence_type": "TEXT",

            "description": "TEXT",

            "score": "DOUBLE PRECISION"

        }
    },


    # =====================================================
    # RCA RESULT
    # =====================================================

    "rca_results": {

        "columns": {

            "id": "SERIAL PRIMARY KEY",

            "investigation_id": "INTEGER",

            "root_cause": "TEXT",

            "confidence": "DOUBLE PRECISION",

            "explanation": "TEXT"

        }
    }

}