from src.config import load_config
from src.jira.receive_query import receive_query
from src.input_module.query_parser import parse_query
from src.input_module.telemetry_loader import connect_data_source

issue_key = input("Enter Jira Issue Key: ")

config = load_config()

raw_query = receive_query(issue_key)

parsed_query = parse_query(raw_query)

connect_data_source(
    parsed_query,
    config
)