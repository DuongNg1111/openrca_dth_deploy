from src.jira.jira_client import get_issue

issue = get_issue("DEV-110")

for key, value in issue.raw["fields"].items():
    if key.startswith("customfield"):
        print(f"{key}: {value}")