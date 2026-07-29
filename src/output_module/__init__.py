"""
Public APIs for the Output Module.
"""

from .formatter import (
    aggregate_evidence,
    build_output,
    build_dashboard_data,
    build_summary,
    save_prediction,
)

from .visualize import (
    plot_component_kpi,
    render_report,
)

__all__ = [
    "aggregate_evidence",
    "build_output",
    "build_dashboard_data",
    "build_summary",
    "save_prediction",
    "plot_component_kpi",
    "render_report",
]