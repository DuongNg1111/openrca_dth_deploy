from jira import JIRA

from src.config import load_config


config = load_config()

jira_cfg = config["jira"]

JIRA_URL = jira_cfg["url"]
JIRA_EMAIL = jira_cfg["email"]
JIRA_API_TOKEN = jira_cfg["token"]


def connect_jira():

    return JIRA(
        server=JIRA_URL,
        basic_auth=(
            JIRA_EMAIL,
            JIRA_API_TOKEN
        )
    )


def get_issue(issue_key: str):
    """
    Get a Jira Issue by its key.
    """

    jira = connect_jira()

    return jira.issue(issue_key)


def create_issue(
    incident_description,
    environment,
    affected_system,
    incident_time,
    reporter_name="",
    reporter_email=""
):
    """
    Create a new Jira issue and return its issue key.
    """

    jira = connect_jira()

    description = f"""
Reporter:
{reporter_name}

Email:
{reporter_email}

Environment:
{environment}

Incident Time:
{incident_time}

Affected System:
{affected_system}

Incident Description:
{incident_description}
"""

    issue_dict = {
        "project": {
            "key": jira_cfg["project_key"]
        },
        "summary": (
            incident_description[:100]
            if incident_description.strip()
            else f"Incident Report - {incident_time}"
        ),
        "description": description,
        "issuetype": {
            "name": "Task"
        }
    }

    issue = jira.create_issue(
        fields=issue_dict
    )

    return issue.key