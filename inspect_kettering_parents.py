import json

with open(
    "verification/data/crm_snapshot.json",
    encoding="utf-8"
) as f:
    accounts = json.load(f)

parent_ids = {
    "001FJZYHR7MLFMNPLL",
    "001FWSQ30SFW6S7604"
}

print("========== KETTERING PARENT ACCOUNTS ==========")

for account in accounts:
    if account["account_id"] in parent_ids:

        print("\nAccount ID:", account["account_id"])
        print("Name:", account["name"])
        print("Parent ID:", account["parent_id"])
        print("Parent Name:", account["parent_name"])
        print("Status:", account["status"])
        print("Created by candidate:",
              account["created_by_candidate"])