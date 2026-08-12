if __name__ != "__main__":
    import pytest

    pytest.skip("manual Jira integration script", allow_module_level=True)

from src.input_module.query_parser import parse_query
from src.jira.receive_query import receive_query

issue_key = input("Enter Jira Issue Key: ")

query = receive_query(issue_key)

parsed = parse_query(query)

print("=" * 40)
print("PARSED QUERY")
print("=" * 40)

print("Issue Key            :", parsed.issue_key)
print("Incident Description :", parsed.incident_description)
print("Environment          :", parsed.environment)
print("Affected System      :", parsed.affected_system)
print("Incident Time        :", parsed.incident_time)
print("Additional Info      :", parsed.additional_information)
print("Keywords             :", parsed.keywords)
