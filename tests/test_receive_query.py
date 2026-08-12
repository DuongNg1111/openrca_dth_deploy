if __name__ != "__main__":
    import pytest

    pytest.skip("manual Jira integration script", allow_module_level=True)

from src.jira.receive_query import receive_query

issue_key = input("Enter Jira Issue Key: ")

query = receive_query(issue_key)

assert query is not None

print("\n========== RAW QUERY ==========\n")

print(f"Issue Key           : {query.issue_key}")
print(f"Incident_description: {query.incident_description}")
print(f"Reporter            : {query.reporter}")
print(f"Affected System     : {query.affected_system}")
print(f"Incident Time       : {query.incident_time}")
print(f"Status              : {query.status}")
print(f"Created             : {query.created}")


print("\nDescription:")
print("-" * 60)
print(query.incident_description)
print("-" * 60)
