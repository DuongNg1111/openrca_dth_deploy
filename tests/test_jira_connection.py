if __name__ != "__main__":
    import pytest

    pytest.skip("manual Jira integration script", allow_module_level=True)

from src.jira.jira_client import connect_jira

jira = connect_jira()

print("✅ Connected successfully!\n")

print("Projects:")

for project in jira.projects():
    print(f"- {project.key} : {project.name}")
