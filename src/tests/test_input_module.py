# # from datetime import datetime
# # from types import SimpleNamespace

# # from src.input_module.telemetry_loader import load

# # window = SimpleNamespace(
# #     start=datetime(2022, 3, 20, 0, 0, 0),
# #     end=datetime(2022, 3, 20, 0, 5, 0),
# # )

# # result = load(
# #     system="cloudbed-1",
# #     window=window,
# #     data_root="/mnt/d/Market",
# # )

# from src.input_module.query_parser import parse_query


# query = "Payment creation failed at 2022-03-20 10:00"


# window, components = parse_query(query)


# print("Start time:")
# print(window.start)

# print("End time:")
# print(window.end)

# print("Components:")
# print(components)

from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import load


query = "Payment creation failed at 2022-03-20 10:00"


window, _ = parse_query(query)


print("Window:")
print(window.start)
print(window.end)


result = load(
    system="cloudbed-1",
    window=window,
    data_root="/mnt/d/Market"
)


import pandas as pd

# Chuyển về DataFrame để xuất CSV
metric_df = pd.DataFrame(result["metric"])
log_df = pd.DataFrame(result["log"])
trace_df = pd.DataFrame(result["trace"])

# Chỉ lấy 5 dòng đầu
metric_df.head(5).to_csv("metric_sample.csv", index=False)
log_df.head(5).to_csv("log_sample.csv", index=False)
trace_df.head(5).to_csv("trace_sample.csv", index=False)

print("Sample CSV files created successfully!")