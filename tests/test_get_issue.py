from src.jira.jira_client import get_issue

ISSUE_KEY = "DEV-105" #name of key issue on Jira

issue = get_issue(ISSUE_KEY)

print("Issue Key :", issue.key)
print("Summary   :", issue.fields.summary)
print("Status    :", issue.fields.status.name)
print("Reporter  :", issue.fields.reporter.displayName)

print("\nDescription:")
print(issue.fields.description)