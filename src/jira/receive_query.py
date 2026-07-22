from src.jira.jira_client import get_issue
from src.schemas import RawQuery


def receive_query(issue_key: str) -> RawQuery:
    """
    Read a Jira issue and convert it into a RawQuery object.
    """

    issue = get_issue(issue_key)

    return RawQuery(
        issue_key=issue.key,

        summary=issue.fields.summary,
        description=issue.fields.description,

        affected_system=issue.fields.customfield_10140.value,
        incident_time=issue.fields.customfield_10173,

        reporter=issue.fields.reporter.displayName,
        status=issue.fields.status.name,
        created=issue.fields.created,
)