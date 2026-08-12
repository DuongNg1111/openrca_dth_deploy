import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.jira.jira_client import connect_jira


def main():
    jira = connect_jira()

    project = jira.project("DEV")

    print(f"Project: {project.key} | {project.name}")
    print("\n=== EPIC / PARENT FIELDS ===")

    fields = jira.fields()

    for field in fields:
        field_id = field.get("id", "")
        field_name = field.get("name", "")
        schema = field.get("schema", {})

        name_lower = field_name.lower()

        if "epic" in name_lower or "parent" in name_lower:
            print(
                f"ID     : {field_id}\n"
                f"Name   : {field_name}\n"
                f"Type   : {schema.get('type', '')}\n"
                f"Custom : {schema.get('custom', '')}\n"
                f"---"
            )


if __name__ == "__main__":
    main()