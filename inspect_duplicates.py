import json

with open(
    "verification/data/crm_snapshot.json",
    "r",
    encoding="utf-8"
) as file:
    accounts = json.load(file)

target_name = "bellhaven of owosso"

matches = [
    account for account in accounts
    if account["name"].strip().casefold() == target_name
]

print("Duplicate records found:", len(matches))

for i, account in enumerate(matches, start=1):
    print(f"\n========== RECORD {i} ==========")

    fields = [
        "account_id",
        "name",
        "parent_id",
        "parent_name",
        "billing_street",
        "billing_city",
        "billing_state",
        "billing_zip",
        "care_type",
        "status",
        "phone",
        "lifetime_revenue",
        "outstanding_ar",
        "note",
        "updated_at"
    ]

    for field in fields:
        print(f"{field}: {account.get(field)}")