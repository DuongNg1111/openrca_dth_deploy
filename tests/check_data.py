from datetime import datetime

from src.input_module.telemetry_loader import load
from src.schemas import TimeWindow


window = TimeWindow(
    start=datetime(2022, 3, 20, 17, 0, 0),
    end=datetime(2022, 3, 20, 18, 0, 0)
)

result = load(
    system="cloudbed-1",
    window=window,
    data_root="data/Market"
)

print(result)