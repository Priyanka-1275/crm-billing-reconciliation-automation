import json
import re
from collections import Counter

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

    replacements = {
        "w": "west",
        "e": "east",
        "n": "north",
        "s": "south",
        "st": "street",
        "rd": "road",
        "ave": "avenue",
        "blvd": "boulevard",
        "dr": "drive",
        "ln": "lane",
        "pk": "pike",
            "nw": "northwest",
    "ne": "northeast",
    "sw": "southwest",
    "se": "southeast",
    }

    words = value.split()
    words = [replacements.get(word, word) for word in words]

    return " ".join(words)


def get_address(record, website_record=False):

    if website_record:
        street = record["street"]
        city = record["city"]
        state = record["state"]
        zip_code = record["zip"]
    else:
        street = record["billing_street"]
        city = record["billing_city"]
        state = record["billing_state"]
        zip_code = record["billing_zip"]

    return (
        normalize(street),
        normalize(city),
        normalize(state),
        normalize(zip_code)
    )


report = []

for facility in website:

    website_name = normalize(facility["name"])
    website_address = get_address(facility, True)
    website_phone = normalize(facility["phone"])

    candidates = []

    for account in crm:

        crm_name = normalize(account["name"])
        crm_address = get_address(account)
        crm_phone = normalize(account["phone"])

        name_match = website_name == crm_name
        address_match = website_address == crm_address
        phone_match = website_phone == crm_phone

        if name_match or address_match or phone_match:

            candidates.append({
                "account_id": account["account_id"],
                "crm_name": account["name"],
                "parent_name": account["parent_name"],
                "status": account["status"],
                "name_match": name_match,
                "address_match": address_match,
                "phone_match": phone_match,
                "crm_address": account["billing_street"],
                "crm_phone": account["phone"],
                "care_type": account["care_type"]
            })

    if len(candidates) == 0:
        category = "NO_MATCH"

    elif len(candidates) > 1:
        category = "MULTIPLE_CANDIDATES"

    elif candidates[0]["name_match"] and candidates[0]["address_match"]:
        category = "EXACT_NAME_AND_ADDRESS"

    elif candidates[0]["name_match"]:
        category = "NAME_ONLY_MATCH"

    else:
        category = "ADDRESS_ONLY_MATCH"

    report.append({
        "website_facility": facility["name"],
        "website_address": get_address(facility, True),
        "website_phone": facility["phone"],
        "category": category,
        "candidate_count": len(candidates),
        "candidates": candidates
    })


output_file = "verification/data/initial_match_report.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)


print("========== IMPROVED MATCHING SUMMARY ==========")

counts = Counter(x["category"] for x in report)

print("Website facilities:", len(website))

for category, count in sorted(counts.items()):
    print(category, ":", count)

print("\nTotal CRM candidate matches:",
      sum(x["candidate_count"] for x in report))

print("\nReport saved:", output_file)

print("\n========== MULTIPLE CANDIDATE CASES ==========")

for item in report:
    if item["category"] == "MULTIPLE_CANDIDATES":

        print("\nFacility:", item["website_facility"])

        for candidate in item["candidates"]:
            print(
                candidate["account_id"],
                "|",
                candidate["crm_name"],
                "| Parent:",
                candidate["parent_name"],
                "| Name match:",
                candidate["name_match"],
                "| Address match:",
                candidate["address_match"],
                "| Phone match:",
                candidate["phone_match"]
            )