import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.jira.jira_client import connect_jira


# ============================================================
# CONFIG
# ============================================================

PROJECT_KEY = "DEV"

# Existing Epic
EPIC_KEY = "DEV-167"

# Tickets to move into the Epic
TICKET_KEYS = [
    "DEV-112",
    "DEV-113",
    "DEV-114",
    "DEV-115",
    "DEV-116",
    "DEV-117",
    "DEV-119",
    "DEV-120",
    "DEV-121",
    "DEV-122",
    "DEV-123",
    "DEV-124",
    "DEV-125",
    "DEV-126",
    "DEV-127",
    "DEV-128",
    "DEV-129",
    "DEV-130",
    "DEV-131",
    "DEV-132",
    "DEV-133",
    "DEV-134",
    "DEV-135",
    "DEV-136",
    "DEV-137",
    "DEV-138",
    "DEV-139",
    "DEV-140",
    "DEV-141",
    "DEV-142",
    "DEV-143",
    "DEV-144",
    "DEV-145",
    "DEV-146",
    "DEV-147",
    "DEV-148",
    "DEV-149",
    "DEV-150",
    "DEV-151",
    "DEV-152",
    "DEV-153",
    "DEV-154",
    "DEV-155",
    "DEV-156",
    "DEV-157",
    "DEV-158",
    "DEV-159",
    "DEV-160",
    "DEV-161",
    "DEV-162",
    "DEV-163",
    "DEV-164",
    "DEV-165",
    "DEV-166",
    "DEV-168",
    "DEV-175",
    "DEV-176",
    "DEV-177",
    "DEV-178",
    "DEV-179",
    "DEV-180",
    "DEV-181",
]


# ============================================================
# VERIFY EPIC
# ============================================================

def verify_epic(jira):
    print("\nChecking Epic...")

    epic = jira.issue(EPIC_KEY)

    print(f"Epic key     : {epic.key}")
    print(f"Epic summary : {epic.fields.summary}")
    print(f"Issue type   : {epic.fields.issuetype.name}")

    if epic.fields.issuetype.name.lower() != "epic":
        raise ValueError(
            f"{EPIC_KEY} is not an Epic. "
            f"It is {epic.fields.issuetype.name}."
        )

    return epic


# ============================================================
# MOVE TICKET TO EPIC
# ============================================================

def move_ticket_to_epic(jira, ticket_key):
    try:
        issue = jira.issue(ticket_key)

        # Check project
        if issue.fields.project.key != PROJECT_KEY:
            print(
                f"✗ {ticket_key}: wrong project "
                f"({issue.fields.project.key})"
            )
            return False

        # Current parent
        current_parent = getattr(issue.fields, "parent", None)

        if current_parent:
            current_parent_key = current_parent.key
            current_parent_summary = current_parent.fields.summary

            if current_parent_key == EPIC_KEY:
                print(f"✓ {ticket_key}: already in {EPIC_KEY}")
                return True

            print(
                f"  Current parent: "
                f"{current_parent_key} - {current_parent_summary}"
            )
        else:
            print("  Current parent: None")

        # Update parent
        issue.update(
            fields={
                "parent": {
                    "key": EPIC_KEY
                }
            }
        )

        # Verify immediately
        updated_issue = jira.issue(ticket_key)
        updated_parent = getattr(
            updated_issue.fields,
            "parent",
            None
        )

        if updated_parent and updated_parent.key == EPIC_KEY:
            print(f"✓ {ticket_key} → {EPIC_KEY}")
            return True

        print(
            f"✗ {ticket_key}: update sent but verification failed"
        )
        return False

    except Exception as e:
        print(f"✗ {ticket_key}: FAILED")
        print(f"  Error: {e}")
        return False


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("OpenRCA - Move Jira Tickets Into Existing Epic")
    print("=" * 70)

    jira = connect_jira()

    print(
        f"\nConnected to: "
        f"{jira.server_info()['baseUrl']}"
    )

    print(f"Project: {PROJECT_KEY}")
    print(f"Target Epic: {EPIC_KEY}")
    print(f"Tickets: {len(TICKET_KEYS)}")

    # --------------------------------------------------------
    # Verify Epic before changing anything
    # --------------------------------------------------------

    epic = verify_epic(jira)

    print(
        f"\nTarget Epic confirmed:"
        f"\n  {epic.key} | {epic.fields.summary}"
    )

    # --------------------------------------------------------
    # Confirm ticket count
    # --------------------------------------------------------

    print("\nTickets that will be moved:")

    for ticket_key in TICKET_KEYS:
        print(f"  - {ticket_key}")

    print("\nStarting update...")
    print("=" * 70)

    success = []
    failed = []

    # --------------------------------------------------------
    # Move tickets
    # --------------------------------------------------------

    for ticket_key in TICKET_KEYS:
        if move_ticket_to_epic(jira, ticket_key):
            success.append(ticket_key)
        else:
            failed.append(ticket_key)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)

    print(f"Target Epic : {EPIC_KEY}")
    print(f"Total       : {len(TICKET_KEYS)}")
    print(f"Success     : {len(success)}")
    print(f"Failed      : {len(failed)}")

    if failed:
        print("\nFailed tickets:")
        for ticket_key in failed:
            print(f"  ✗ {ticket_key}")

    print("\nSuccessfully moved:")
    for ticket_key in success:
        print(f"  ✓ {ticket_key}")

    print("\nDone.")


if __name__ == "__main__":
    main()