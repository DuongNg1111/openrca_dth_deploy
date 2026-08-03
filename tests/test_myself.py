from src.jira.jira_client import connect_jira

jira = connect_jira()

me = jira.myself()

print("Account ID :", me["accountId"])
print("Display Name :", me["displayName"])
print("Email :", me.get("emailAddress", "Hidden"))
