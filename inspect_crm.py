import json

file_path = "verification/data/crm_snapshot.json"

with open(file_path, "r", encoding="utf-8") as file:
    accounts = json.load(file)

print("Total CRM accounts:", len(accounts))

if accounts:
    print("\nAvailable CRM fields:")
    print(list(accounts[0].keys()))

    print("\nFirst 3 CRM records:")

    for account in accounts[:3]:
        print(json.dumps(account, indent=2, ensure_ascii=False))