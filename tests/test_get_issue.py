if __name__ != "__main__":
    import pytest

    pytest.skip("manual Jira integration script", allow_module_level=True)

from src.jira.jira_client import get_issue

issue_key = input("Enter Jira Issue Key: ")

issue = get_issue(issue_key)

print("Issue Key :", issue.key)
print("Summary   :", issue.fields.summary)
print("Status    :", issue.fields.status.name)
print("Reporter  :", issue.fields.reporter.displayName)

print("\nDescription:")
print(issue.fields.description)
