from src.jira.receive_query import receive_query

query = receive_query("DEV-110")   # đổi thành Issue Key của bạn

print("\n========== RAW QUERY ==========\n")

print(f"Issue Key           : {query.issue_key}")
print(f"Summary             : {query.summary}")
print(f"Reporter            : {query.reporter}")
print(f"Affected System     : {query.affected_system}")
print(f"Incident Time       : {query.incident_time}")
print(f"Status              : {query.status}")
print(f"Created             : {query.created}")



print("\nDescription:")
print("-" * 60)
print(query.description)
print("-" * 60)
