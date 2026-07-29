from src.jira.jira_client import connect_jira


def test_jira_connection():

    jira = connect_jira()

    print("\nConnected Jira")

    issue_types = jira.issue_types()

    print("\nIssue Types")
    print("----------------")

    for issue in issue_types:
        print(issue.name)



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

    test_create_issue()