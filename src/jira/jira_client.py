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
