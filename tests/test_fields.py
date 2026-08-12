if __name__ != "__main__":
    import pytest

    pytest.skip("manual Jira integration script", allow_module_level=True)

from src.jira.jira_client import get_issue

issue = get_issue("DEV-112")

for key, value in issue.raw["fields"].items():
    if key.startswith("customfield"):
        print(f"{key}: {value}")
