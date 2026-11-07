import json

with open("verification/data/website_facilities_cleaned.json",
          encoding="utf-8") as f:
    website = json.load(f)

with open("verification/data/crm_snapshot.json",
          encoding="utf-8") as f:
    crm = json.load(f)

facility = next(
    x for x in website
    if x["name"].casefold() == "bellhaven of kettering"
)

print("========== WEBSITE RECORD ==========")
print(json.dumps(facility, indent=2))

print("\n========== CRM RECORDS AT SAME ADDRESS ==========")

for account in crm:
    if (
        account["billing_city"].casefold() == facility["city"].casefold()
        and account["billing_state"].casefold() == facility["state"].casefold()
        and account["billing_zip"] == facility["zip"]
    ):
        print("\n", json.dumps(account, indent=2))