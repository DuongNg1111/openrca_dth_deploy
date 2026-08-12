if __name__ != "__main__":
    import pytest

    pytest.skip("manual Jira integration script", allow_module_level=True)

from src.jira.jira_client import connect_jira

jira = connect_jira()

me = jira.myself()

print("Account ID :", me["accountId"])
print("Display Name :", me["displayName"])
print("Email :", me.get("emailAddress", "Hidden"))
