import json
import re

with open("verification/data/website_facilities_cleaned.json",
          encoding="utf-8") as f:
    website = json.load(f)

with open("verification/data/crm_snapshot.json",
          encoding="utf-8") as f:
    crm = json.load(f)


def normalize(value):
    if not value:
        return ""

    value = value.casefold().strip()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return " ".join(value.split())


def normalize_address(account, website_record=False):
    if website_record:
        street = account["street"]
        city = account["city"]
        state = account["state"]
        zip_code = account["zip"]
    else:
        street = account["billing_street"]
        city = account["billing_city"]
        state = account["billing_state"]
        zip_code = account["billing_zip"]

    address = f"{street} {city} {state} {zip_code}"

    return normalize(address)


print("========== INITIAL MATCHING REPORT ==========")

matched = 0
unmatched = 0

for facility in website:

    name_key = normalize(facility["name"])
    address_key = normalize_address(facility, True)

    matches = []

    for account in crm:

        crm_name = normalize(account["name"])
        crm_address = normalize_address(account)

        if name_key == crm_name or address_key == crm_address:
            matches.append(account)

    print("\n-----------------------------------")
    print("Website Facility:", facility["name"])

    if matches:
        matched += 1

        print("CRM matches found:", len(matches))

        for account in matches:
            print("Account ID:", account["account_id"])
            print("CRM Name:", account["name"])
            print("CRM Address:", account["billing_street"],
                  account["billing_city"],
                  account["billing_state"],
                  account["billing_zip"])
            print("Parent:", account["parent_name"])
            print("Status:", account["status"])

    else:
        unmatched += 1
        print("NO EXACT NAME OR ADDRESS MATCH FOUND")

print("\n========== SUMMARY ==========")
print("Website facilities:", len(website))
print("Facilities with matches:", matched)
print("Facilities without matches:", unmatched)