# from jira import JIRA
# from dotenv import load_dotenv
# import os

# load_dotenv()

# JIRA_URL = os.getenv("JIRA_URL")
# JIRA_EMAIL = os.getenv("JIRA_EMAIL")
# JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


# def connect_jira():
#     """
#     Connect to Jira Cloud.
#     """
#     jira = JIRA(
#         server=JIRA_URL,
#         basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
#     )

#     return jira

from jira import JIRA
from dotenv import load_dotenv
import os

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


def connect_jira():
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
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
        "project": {"key": "DEV"},
        "summary": incident_description[:100],
        "description": description,
        "issuetype": {"name": "Task"}
    }

    issue = jira.create_issue(
        fields=issue_dict
    )

    return issue.key
