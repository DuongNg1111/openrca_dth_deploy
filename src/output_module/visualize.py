"""OUTPUT module — optional charts / text report for the predicted root cause."""
from __future__ import annotations


def plot_component_kpi(telemetry, component, kpi, out_path=None):
    """TODO(DEV 3): plot the KPI time series for `component` and mark the spike.

    matplotlib is imported lazily so the core pipeline never depends on it.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # pragma: no cover
        raise RuntimeError("pip install matplotlib to use plotting") from e

    xs, ys = [], []
    for r in telemetry.get("metric", []):
        if r["component"] == component and r["kpi"] == kpi:
            xs.append(r["timestamp"])
            ys.append(r["value"])
    plt.figure()
    plt.plot(xs, ys, marker="o")
    plt.title(f"{component} / {kpi}")
    if out_path:
        plt.savefig(out_path)
        return out_path
    return plt


def render_report(prediction) -> str:
    """Return a plain-text report (upgrade to markdown/HTML later)."""
    lines = ["# Root Cause Report", ""]
    for k, v in prediction.to_openrca_json().items():
        lines.append(f"## Candidate {k}")
        for name, val in v.items():
            lines.append(f"- **{name}**: {val}")
        lines.append("")
    return "\n".join(lines)
