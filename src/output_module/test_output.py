from datetime import datetime

from src.output_module.formatter import (
    build_output,
    build_dashboard_data,
    build_summary,
    save_prediction,
)

from src.output_module.visualize import (
    render_report,
)
# --------------------------------------------------
# Mock reasoning results (simulate Process Module)
# --------------------------------------------------

mock_candidates = [

    {
        "component": "shippingservice",
        "reason": "Database timeout",
        "occurrence_time": datetime(2022,3,21,9,28),
        "confidence":0.92,

        "metrics":[
            {"kpi":"CPU","value":95},
            {"kpi":"Memory","value":88}
        ],

        "logs":[
            {"level":"ERROR","message":"Database timeout"}
        ],

        "traces":[
            {"span":"shipping-db"}
        ],
    },

    {
        "component":"checkoutservice",

        "reason":"CPU overload",

        "occurrence_time":datetime(2022,3,21,9,29),

        "confidence":0.81,

        "metrics":[
            {"kpi":"CPU","value":91}
        ],

        "logs":[
            {"level":"WARN","message":"CPU overload"}
        ],

        "traces":[
            {"span":"checkout-api"}
        ],
    }

]


# --------------------------------------------------
# Build Prediction
# --------------------------------------------------

prediction = build_output(mock_candidates)


# --------------------------------------------------
# Dashboard Data
# --------------------------------------------------

dashboard = build_dashboard_data(prediction)

print("=" * 60)
print("Dashboard")
print("=" * 60)

print(f"Total Candidates : {dashboard['total_candidates']}")
print()

for i, c in enumerate(dashboard["candidates"], start=1):

    print(f"Candidate {i}")

    print(f"Component  : {c['component']}")

    print(f"Reason     : {c['reason']}")

    print(f"Confidence : {c['confidence']:.2f}")

    print(f"Metrics    : {c['metrics']}")

    print(f"Logs       : {c['logs']}")

    print(f"Traces     : {c['traces']}")

    print("-" * 50)


# --------------------------------------------------
# Summary
# --------------------------------------------------

summary = build_summary(prediction)

print("="*60)
print("Summary")
print("="*60)

print(f"Total Candidates   : {summary['total_candidates']}")
print(f"Top Component      : {summary['top_component']}")
print(f"Top Root Cause     : {summary['top_reason']}")
print(f"Highest Confidence : {summary['highest_confidence']:.2%}")

# --------------------------------------------------
# Markdown Report
# --------------------------------------------------

report = render_report(prediction)

print("=" * 60)
print("Report")
print("=" * 60)

print(report)


# --------------------------------------------------
# Export JSON
# --------------------------------------------------

save_prediction(
    prediction,
    "prediction.json",
)

print("=" * 60)
print("Prediction saved to prediction.json")
