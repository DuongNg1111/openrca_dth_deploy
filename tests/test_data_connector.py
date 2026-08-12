if __name__ != "__main__":
    import pytest

    pytest.skip("manual Jira/dataset integration script", allow_module_level=True)

from src.config import load_config
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source
from src.jira.receive_query import receive_query

issue_key = input("Enter Jira Issue Key: ")

config = load_config()

raw_query = receive_query(issue_key)

parsed_query = parse_query(raw_query)

connect_data_source(
    parsed_query,
    config
)
