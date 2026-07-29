from src.database.ready_call_db import READY_TO_CALL_DB


def get_case(issue_key: str):

    for case in READY_TO_CALL_DB["cases"]:

        if case.issue_key == issue_key:

            return case

    return None


def get_ready_call_data(issue_key: str):
    """
    Return every InvestigationContext
    belonging to one incident.
    """

    return [

        context

        for context in READY_TO_CALL_DB["services"]

        if context.issue_key == issue_key

    ]