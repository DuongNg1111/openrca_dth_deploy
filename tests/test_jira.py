import os

import pytest

from src.jira.jira_client import connect_jira

if os.getenv("OPENRCA_RUN_INTEGRATION_TESTS") != "1":
    pytest.skip("requires explicit Jira integration opt-in", allow_module_level=True)


def test_jira_connection():

    jira = connect_jira()

    print("\nConnected Jira")

    issue_types = jira.issue_types()

    print("\nIssue Types")
    print("----------------")

    for issue in issue_types:
        print(issue.name)



@pytest.mark.skipif(
    os.getenv("OPENRCA_RUN_MUTATING_TESTS") != "1",
    reason="creating a Jira issue requires separate mutating-test opt-in",
)
def test_create_issue():

    jira = connect_jira()

    issue = jira.create_issue(
        fields={
            "project": {
                "key": "DEV"
            },
            "summary": "OpenRCA Test Incident",
            "description": (
                "Test incident created from OpenRCA pipeline.\n"
                "Service: Order\n"
                "Severity: High\n"
            ),
            "issuetype": {
                "name": "Task"
            }
        }
    )

    print("\nCreated Issue:")
    print(issue.key)



if __name__ == "__main__":

    test_jira_connection()

    if os.getenv("OPENRCA_RUN_MUTATING_TESTS") == "1":
        test_create_issue()
