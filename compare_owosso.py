import json

with open(
    "verification/data/website_facilities_cleaned.json",
    encoding="utf-8"
) as file:
    website = json.load(file)

with open(
    "verification/data/crm_snapshot.json",
    encoding="utf-8"
) as file:
    crm = json.load(file)

name = "bellhaven of owosso"

website_matches = [
    x for x in website
    if x["name"].strip().casefold() == name
]

crm_matches = [
    x for x in crm
    if x["name"].strip().casefold() == name
]

print("WEBSITE RECORD")

for x in website_matches:
    for key in [
        "name", "street", "city", "state",
        "zip", "phone", "source_url"
    ]:
        print(f"{key}: {x.get(key)}")

print("\nCRM RECORDS")

for x in crm_matches:
    print("\nAccount ID:", x["account_id"])
    print("Street:", x["billing_street"])
    print("City:", x["billing_city"])
    print("State:", x["billing_state"])
    print("ZIP:", x["billing_zip"])
    print("Phone:", x["phone"])