import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.jira.jira_client import connect_jira

EPIC_KEY = "DEV-167"

TICKET_KEYS = [
    "DEV-175",
    "DEV-178",
]


def remove_ticket_from_epic(jira, ticket_key):
    try:
        issue = jira.issue(ticket_key)

        current_parent = getattr(
            issue.fields,
            "parent",
            None,
        )

        if not current_parent:
            print(f"✓ {ticket_key}: already has no parent")
            return True

        print(
            f"{ticket_key}: "
            f"current parent = {current_parent.key}"
        )

        if current_parent.key != EPIC_KEY:
            print(
                f"⚠ {ticket_key}: "
                f"not in {EPIC_KEY}, skipping"
            )
            return True

        issue.update(
            fields={
                "parent": None
            }
        )

        updated_issue = jira.issue(ticket_key)
        updated_parent = getattr(
            updated_issue.fields,
            "parent",
            None,
        )

        if updated_parent is None:
            print(f"✓ {ticket_key}: removed from {EPIC_KEY}")
            return True

        print(
            f"✗ {ticket_key}: "
            "remove verification failed"
        )
        return False

    except Exception as e:
        print(f"✗ {ticket_key}: FAILED")
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 70)
    print("OpenRCA - Remove Jira Tickets From Epic")
    print("=" * 70)

    jira = connect_jira()

    print(f"\nTarget Epic: {EPIC_KEY}")

    success = []
    failed = []

    for ticket_key in TICKET_KEYS:
        if remove_ticket_from_epic(jira, ticket_key):
            success.append(ticket_key)
        else:
            failed.append(ticket_key)

    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)

    print(f"Total   : {len(TICKET_KEYS)}")
    print(f"Success : {len(success)}")
    print(f"Failed  : {len(failed)}")

    if failed:
        print("\nFailed:")
        for ticket_key in failed:
            print(f"  ✗ {ticket_key}")

    print("\nDone.")


if __name__ == "__main__":
    main()