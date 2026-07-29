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
    additional_details=""
):
    """
    Create a new Jira issue and return its issue key.
    """

    jira = connect_jira()

    description = f"""
Environment:
{environment}

Incident Time:
{incident_time}

Affected System:
{affected_system}

Incident Description:
{incident_description}
"""

    if additional_details.strip():
        description += f"""

Additional Details:
{additional_details}
"""

    issue_dict = {
        "project": {"key": "DEV"},          # <-- đổi thành project key của nhóm nếu khác
        "summary": incident_description[:100],
        "description": description,
        "issuetype": {"name": "Task"}       # <-- hoặc "Bug" tùy project Jira
    }

    issue = jira.create_issue(fields=issue_dict)

    return issue.key
