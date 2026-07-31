from src.jira.jira_client import get_issue
from src.schemas import RawQuery


def extract_field(description: str, field_name: str):
    """
    Extract value from Jira description.

    Example:
    Environment:
    Cloud A
    """

    if not description:
        return None

    lines = description.split("\n")

    for i, line in enumerate(lines):

        if line.strip() == field_name:

            if i + 1 < len(lines):
                return lines[i + 1].strip()

    return None



def receive_query(issue_key: str) -> RawQuery:
    """
    Read a Jira issue and convert it into RawQuery.
    """

    issue = get_issue(issue_key)

    description = issue.fields.description or ""


    # =====================================
    # Reporter Information
    # =====================================

    reporter = None

    if getattr(issue.fields, "reporter", None):

        reporter = (
            issue.fields.reporter.displayName
        )


    # Email is stored from Streamlit form
    # because Jira Cloud may hide emailAddress
    reporter_email = extract_field(
        description,
        "Email:"
    )


    # =====================================
    # Environment
    # =====================================

    if getattr(
        issue.fields,
        "customfield_10206",
        None
    ):

        environment = (
            issue.fields.customfield_10206.value
        )

    else:

        environment = extract_field(
            description,
            "Environment:"
        )


    # =====================================
    # Affected System
    # =====================================

    if getattr(
        issue.fields,
        "customfield_10140",
        None
    ):

        affected_system = (
            issue.fields.customfield_10140.value
        )

    else:

        affected_system = extract_field(
            description,
            "Affected System:"
        )


    # =====================================
    # Incident Time
    # =====================================

    if getattr(
        issue.fields,
        "customfield_10173",
        None
    ):

        incident_time = (
            issue.fields.customfield_10173
        )

    else:

        incident_time = extract_field(
            description,
            "Incident Time:"
        )


    # =====================================
    # Build Raw Query
    # =====================================

    return RawQuery(

        issue_key=issue.key,

        incident_description=issue.fields.summary,

        environment=environment,

        affected_system=affected_system,

        incident_time=incident_time,

        reporter=issue.fields.reporter.displayName,

        reporter_email=issue.fields.reporter.emailAddress,

        status=issue.fields.status.name,

        created=issue.fields.created,
    )