from src.jira.receive_query import receive_query
from src.input_module.validate_query import validate_query
from src.schemas import RawQuery

# ----------------------------
# Test with a real Jira ticket
# ----------------------------
issue_key = input("Enter Jira Issue Key: ")

query = receive_query(issue_key)

result = validate_query(query)

print("=" * 40)
print("VALIDATION RESULT")
print("=" * 40)

print("Valid :", result.is_valid)
print("Errors:", result.errors)


# ----------------------------
# Test with an invalid query
# ----------------------------
invalid_query = RawQuery(
    issue_key="TEST-001",
    incident_description="abc",
    additional_information="",
    affected_system="Order",
    incident_time="2020-03-20T10:00:00",
    reporter="Tester",
    status="Open",
    created="2026-07-22"
)

result = validate_query(invalid_query)

print("\nINVALID TEST")
print("Valid :", result.is_valid)
print("Errors:", result.errors)