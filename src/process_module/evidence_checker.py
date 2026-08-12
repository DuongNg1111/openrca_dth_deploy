"""Deterministic pre-flight validation for RCA evidence."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from math import isfinite
from typing import Any

from src.process_module.schemas import ValidationResult


def _value(source: Any, *names: str) -> Any:
    if source is None:
        return None
    for name in names:
        value = None
        if isinstance(source, Mapping) and name in source:
            value = source[name]
        elif hasattr(source, name):
            value = getattr(source, name)
        if value is not None:
            return value
    return None


def _has_records(value: Any) -> bool:
    if value is None:
        return False

    empty = getattr(value, "empty", None)
    if empty is not None:
        return not bool(empty)

    for count_name in ("total_files", "count"):
        count = getattr(value, count_name, None)
        if count is not None and not callable(count):
            try:
                return int(count) > 0
            except (TypeError, ValueError):
                return False

    if isinstance(value, Mapping):
        return any(_has_records(nested) for nested in value.values())

    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_has_records(nested) for nested in value)

    try:
        return len(value) > 0
    except TypeError:
        return bool(value)


def _dataframes(value: Any):
    if isinstance(value, Mapping):
        for nested in value.values():
            yield from _dataframes(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for nested in value:
            yield from _dataframes(nested)
    elif hasattr(value, "columns") and hasattr(value, "empty"):
        yield value


def _has_usable_rows(frame: Any, required: set[str], content_columns: set[str] | None) -> bool:
    """Return whether a frame has a row populated for every required field."""
    populated = frame.dropna(subset=sorted(required))
    if populated.empty:
        return False
    if not content_columns:
        return True

    available = sorted(content_columns.intersection(frame.columns))
    if not available:
        return False
    return bool(populated[available].notna().any(axis=1).any())


def _is_finite_metric_value(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError):
        return False
    return isfinite(numeric)


def _is_postgres_trace_duration(value: Any) -> bool:
    """Whether a duration can be persisted in PostgreSQL INTEGER losslessly."""
    if isinstance(value, bool):
        return False
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError):
        return False
    return (
        isfinite(numeric)
        and numeric.is_integer()
        and 0 <= numeric <= 2_147_483_647
    )


def _schema_issues(telemetry: Any) -> list[str]:
    requirements = {
        "metric": {"timestamp", "cmdb_id", "kpi_name", "value"},
        "log": {"timestamp", "cmdb_id"},
        "trace": {
            "timestamp",
            "cmdb_id",
            "span_id",
            "trace_id",
            "duration",
            "type",
            "status_code",
            "operation_name",
            "parent_span",
        },
    }
    issues = []
    for singular, plural in (("metric", "metrics"), ("log", "logs"), ("trace", "traces")):
        for frame in _dataframes(_value(telemetry, singular, plural)):
            if frame.empty:
                continue
            columns = {str(column) for column in frame.columns}
            missing = sorted(requirements[singular] - columns)
            content_columns = (
                {"content", "log", "message", "body", "text", "value"}
                if singular == "log"
                else None
            )
            if missing:
                issues.append(f"{singular} schema missing columns: {', '.join(missing)}")
            if content_columns and not columns.intersection(content_columns):
                issues.append("log schema missing a content column")
            if not missing and _has_usable_rows(
                frame,
                requirements[singular],
                content_columns,
            ) is False:
                issues.append(f"{singular} schema has no usable populated rows")
            if singular == "metric" and not missing:
                invalid_values = sum(
                    not _is_finite_metric_value(value)
                    for value in frame["value"]
                )
                if invalid_values:
                    issues.append(
                        "metric schema contains "
                        f"{invalid_values} non-numeric or non-finite value(s)"
                    )
            if singular == "trace" and not missing:
                invalid_durations = sum(
                    not _is_postgres_trace_duration(value)
                    for value in frame["duration"]
                )
                if invalid_durations:
                    issues.append(
                        "trace schema contains "
                        f"{invalid_durations} duration value(s) outside the "
                        "non-negative PostgreSQL INTEGER contract"
                    )
    return issues


def validate(
    query: Any,
    telemetry: Any,
    metadata: Any = None,
    *,
    required_modalities: Iterable[str] | None = None,
) -> ValidationResult:
    """Check critical context and telemetry without making an LLM/network call.

    ``query`` and ``telemetry`` may be dictionaries or project dataclasses.
    With no explicit policy, at least one telemetry modality is required for
    backward-compatible lightweight checks. A caller that depends on specific
    evidence must pass ``required_modalities``; the full agent pipeline requires
    metric, log, and trace evidence. Metadata is checked against the same policy.
    """
    modality_aliases = {
        "metric": "metrics",
        "log": "logs",
        "trace": "traces",
    }
    required = None
    if required_modalities is not None:
        required = tuple(dict.fromkeys(required_modalities))
        unsupported = sorted(set(required) - set(modality_aliases))
        if unsupported:
            raise ValueError(f"Unsupported required modalities: {', '.join(unsupported)}")

    checks = {
        "incident timestamp": bool(_value(query, "incident_time", "time_window")),
        "target component": bool(_value(query, "affected_system", "system", "service")),
        "incident symptom": bool(
            _value(query, "incident_description", "raw_query", "description")
        ),
    }

    if required is None:
        checks["telemetry records"] = any(
            _has_records(_value(telemetry, singular, plural))
            for singular, plural in modality_aliases.items()
        )
    else:
        for singular in required:
            plural = modality_aliases[singular]
            checks[f"{singular} telemetry records"] = _has_records(
                _value(telemetry, singular, plural)
            )

    for schema_issue in _schema_issues(telemetry):
        checks[schema_issue] = False

    if metadata is not None:
        if required is None:
            checks["telemetry metadata"] = _has_records(metadata)
        else:
            for singular in required:
                checks[f"{singular} telemetry metadata"] = _has_records(
                    _value(metadata, singular, modality_aliases[singular])
                )

    missing = [name for name, passed in checks.items() if not passed]
    confidence = round((len(checks) - len(missing)) / len(checks), 2)

    if not missing:
        return ValidationResult(
            status="COMPLETE",
            confidence=confidence,
            reason="Incident context and telemetry are sufficient for reasoning.",
            ready_for_reasoning=True,
        )

    return ValidationResult(
        status="INCOMPLETE",
        confidence=confidence,
        reason="Critical incident context or telemetry is missing.",
        missing_evidence=missing,
        next_actions=[f"Collect or provide {item}." for item in missing],
        ready_for_reasoning=False,
    )
