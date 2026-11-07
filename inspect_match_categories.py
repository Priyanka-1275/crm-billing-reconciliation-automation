import json

with open(
    "verification/data/initial_match_report.json",
    encoding="utf-8"
) as f:
    report = json.load(f)

# 1. Facilities with no matches
print("========== NO MATCHES ==========")

for item in report:
    if item["category"] == "NO_MATCH":
        print("\nFacility:", item["website_facility"])
        print("Website address:", item["website_address"])
        print("Website phone:", item["website_phone"])

# 2. Name-only matches
print("\n========== NAME-ONLY MATCHES ==========")

for item in report:
    if item["category"] == "NAME_ONLY_MATCH":
        print("\nFacility:", item["website_facility"])

        for candidate in item["candidates"]:
            print("CRM ID:", candidate["account_id"])
            print("CRM name:", candidate["crm_name"])
            print("CRM address:", candidate["crm_address"])
            print("Parent:", candidate["parent_name"])

# 3. Address-only matches
print("\n========== ADDRESS-ONLY MATCHES ==========")

for item in report:
    if item["category"] == "ADDRESS_ONLY_MATCH":
        print("\nFacility:", item["website_facility"])

        for candidate in item["candidates"]:
            print("CRM ID:", candidate["account_id"])
            print("CRM name:", candidate["crm_name"])
            print("CRM address:", candidate["crm_address"])
            print("Parent:", candidate["parent_name"])