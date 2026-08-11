"""OUTPUT module — visualization utilities for RCA results."""

from __future__ import annotations

from typing import Any


def plot_component_kpi(
    telemetry,
    component,
    kpi,
    out_path=None,
):
    """
    Plot KPI time series for a component.

    Parameters
    ----------
    telemetry : dict
        Telemetry dictionary.
    component : str
        Target component.
    kpi : str
        KPI name.
    out_path : str | None
        Save figure if specified.

    Returns
    -------
    matplotlib.pyplot | str
    """

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

    except Exception as e:
        raise RuntimeError(
            "pip install matplotlib to use plotting"
        ) from e

    xs = []
    ys = []

    for r in telemetry.get("metric", []):

        if (
            r.get("component") == component
            and r.get("kpi") == kpi
        ):

            xs.append(r.get("timestamp"))
            ys.append(r.get("value"))

    plt.figure(figsize=(8, 4))
    plt.plot(xs, ys, marker="o")

    plt.title(f"{component} - {kpi}")
    plt.xlabel("Timestamp")
    plt.ylabel(kpi)

    plt.grid(True)

    if out_path:

        plt.savefig(
            out_path,
            bbox_inches="tight",
        )

        plt.close()

        return out_path

    return plt


def build_dashboard_data(prediction) -> dict[str, Any]:
    """
    Convert Prediction into Streamlit-ready data.
    """

    rows = []

    for c in prediction.candidates:

        rows.append(
            {
                "Component": c.component,
                "Root Cause": c.reason,
                "Confidence": round(
                    c.confidence * 100,
                    2,
                ),
                "Occurrence Time": c.occurrence_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "Metric Count": len(
                    c.evidence.get("metrics", [])
                ),
                "Log Count": len(
                    c.evidence.get("logs", [])
                ),
                "Trace Count": len(
                    c.evidence.get("traces", [])
                ),
            }
        )

    return {
        "total_candidates": len(rows),
        "table": rows,
    }


def render_report(prediction) -> str:
    """
    Generate a human-readable RCA report.
    """

    report = []

    report.append("=" * 60)
    report.append("ROOT CAUSE ANALYSIS REPORT")
    report.append("=" * 60)
    report.append("")

    # --------------------------------------------------
    # Overall Summary
    # --------------------------------------------------

    total_candidates = len(prediction.candidates)

    if total_candidates > 0:

        best = max(
            prediction.candidates,
            key=lambda x: x.confidence,
        )

        report.append("OVERALL SUMMARY")
        report.append("-" * 60)

        report.append(f"Total Candidates   : {total_candidates}")
        report.append(f"Top Component      : {best.component}")
        report.append(f"Top Root Cause     : {best.reason}")
        report.append(f"Highest Confidence : {best.confidence:.2%}")

    else:

        report.append("OVERALL SUMMARY")
        report.append("-" * 60)
        report.append("No root cause candidates found.")

    report.append("")
    report.append("=" * 60)
    report.append("")

    # --------------------------------------------------
    # Candidate Details
    # --------------------------------------------------

    for i, c in enumerate(prediction.candidates, start=1):
        report.append("")
        report.append(f"Candidate #{i}")
        report.append("-" * 60)

        report.append(f"Component          : {c.component}")
        report.append(f"Root Cause         : {c.reason}")
        explanation = c.evidence.get("explanation")

        if explanation:

            report.append("")
            report.append("Explanation")
            report.append("-"*60)
            report.append(explanation)
            report.append("")
        report.append(f"Confidence         : {c.confidence:.2%}")
        report.append(
            f"Occurrence Time    : "
            f"{c.occurrence_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        report.append("")
        report.append("Evidence Summary")
        report.append(
            f"Evidence Status : "
            f"{c.evidence.get('status', 'UNKNOWN')}"
        )
        missing = c.evidence.get("missing", [])

        if missing:

            report.append(
                f"Missing Evidence : {', '.join(missing)}"
            )

        report.append("")
        report.append("")
        report.append(
            f"  Metrics : {len(c.evidence.get('metrics', []))}"
        )
        report.append(
            f"  Logs    : {len(c.evidence.get('logs', []))}"
        )

        report.append(
            f"  Traces  : {len(c.evidence.get('traces', []))}"
        )

        report.append("")
        report.append("=" * 60)
        report.append("")

    return "\n".join(report)