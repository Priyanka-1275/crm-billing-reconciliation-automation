import json

with open(
    "verification/data/crm_snapshot.json",
    encoding="utf-8"
) as f:
    accounts = json.load(f)

parent_id = "0015QAPLGS3FVYEEEM"

children = [
    a for a in accounts
    if a.get("parent_id") == parent_id
]

print("TOTAL BELLHAVEN CHILD ACCOUNTS:", len(children))

for a in sorted(children, key=lambda x: x.get("name", "")):
    print("\n" + "-" * 50)
    print("Name:", a.get("name"))
    print("Account ID:", a.get("account_id"))
    print("Address:", a.get("billing_street"))
    print("City:", a.get("billing_city"))
    print("State:", a.get("billing_state"))
    print("ZIP:", a.get("billing_zip"))
    print("Phone:", a.get("phone"))
    print("Status:", a.get("status"))
    print("Revenue:", a.get("lifetime_revenue"))
    print("AR:", a.get("outstanding_ar"))