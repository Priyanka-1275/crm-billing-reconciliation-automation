
import json
import re
from difflib import SequenceMatcher
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

    value = str(value).casefold().strip()
    value = re.sub(r"[^a-z0-9\s]", " ", value)

    replacements = {
        "w": "west", "e": "east",
        "n": "north", "s": "south",
        "st": "street", "rd": "road",
        "ave": "avenue", "blvd": "boulevard",
        "dr": "drive", "ln": "lane",
        "pk": "pike", "nw": "northwest",
        "ne": "northeast", "sw": "southwest",
        "se": "southeast",
        "rehab": "rehabilitation",
        "centre": "center",
    }

    return " ".join(replacements.get(w, w) for w in value.split())


def similarity(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()


def phone_digits(value):
    return re.sub(r"\D", "", str(value or ""))


def get_address(record, website_record=False):
    if website_record:
        keys = ("street", "city", "state", "zip")
    else:
        keys = ("billing_street", "billing_city",
                "billing_state", "billing_zip")

    return tuple(normalize(record.get(k)) for k in keys)


def score_candidate(facility, account):
    website_address = get_address(facility, True)
    crm_address = get_address(account)

    website_name = normalize(facility.get("name"))
    crm_name = normalize(account.get("name"))

    website_phone = phone_digits(facility.get("phone"))
    crm_phone = phone_digits(account.get("phone"))

    name_similarity = similarity(website_name, crm_name)
    street_similarity = similarity(
        website_address[0], crm_address[0]
    )

    name_score = round(name_similarity * 30)
    street_score = round(street_similarity * 25)

    city_match = bool(
        website_address[1] and
        website_address[1] == crm_address[1]
    )
    state_match = bool(
        website_address[2] and
        website_address[2] == crm_address[2]
    )
    zip_match = bool(
        website_address[3] and
        website_address[3] == crm_address[3]
    )
    phone_match = bool(
        website_phone and
        crm_phone and
        website_phone == crm_phone
    )

    bellhaven_parent = (
        "bellhaven" in normalize(account.get("parent_name"))
    )

    evidence = {
        "name_similarity": round(name_similarity * 100, 1),
        "street_similarity": round(street_similarity * 100, 1),
        "name_score": name_score,
        "street_score": street_score,
        "city_match": city_match,
        "state_match": state_match,
        "zip_match": zip_match,
        "phone_match": phone_match,
        "bellhaven_parent": bellhaven_parent
    }

    score = (
        name_score
        + street_score
        + (10 if city_match else 0)
        + (5 if state_match else 0)
        + (10 if zip_match else 0)
        + (15 if phone_match else 0)
        + (5 if bellhaven_parent else 0)
    )

    # Avoid a misleading high score when key location
    # information is missing.
    if not all(website_address):
        evidence["missing_website_address_fields"] = True

    return min(score, 100), evidence


report = []

for facility in website:
    candidates = []

    for account in crm:
        score, evidence = score_candidate(facility, account)

        # Keep plausible candidates for manual review.
        if score >= 35:
            candidates.append({
                "account_id": account.get("account_id"),
                "crm_name": account.get("name"),
                "parent_id": account.get("parent_id"),
                "parent_name": account.get("parent_name"),
                "status": account.get("status"),
                "crm_address": account.get("billing_street"),
                "crm_city": account.get("billing_city"),
                "crm_state": account.get("billing_state"),
                "crm_zip": account.get("billing_zip"),
                "crm_phone": account.get("phone"),
                "care_type": account.get("care_type"),
                "lifetime_revenue": account.get("lifetime_revenue"),
                "outstanding_ar": account.get("outstanding_ar"),
                "score": score,
                "evidence": evidence
            })

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if not candidates:
        category = "NO_CANDIDATE"

    elif (
        len(candidates) > 1
        and candidates[1]["score"] >= 60
        and candidates[0]["score"] - candidates[1]["score"] <= 15
    ):
        category = "MULTIPLE_CANDIDATES"

    elif candidates[0]["score"] >= 90:
        category = "STRONG_CANDIDATE"

    elif candidates[0]["score"] >= 60:
        category = "REVIEW_CANDIDATE"

    else:
        category = "WEAK_CANDIDATE"

    report.append({
        "website_facility": facility.get("name"),
        "website_slug": facility.get("slug"),
        "website_source_url": facility.get("source_url"),
        "website_address": get_address(facility, True),
        "website_phone": facility.get("phone"),
        "care_offerings": facility.get("care_offerings", []),
        "category": category,
        "candidate_count": len(candidates),
        "candidates": candidates
    })


output_file = "verification/data/scored_match_report.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)


print("========== SCORED MATCHING SUMMARY ==========")
print("Website facilities:", len(website))

for category, count in sorted(
    Counter(x["category"] for x in report).items()
):
    print(category, ":", count)

print("\n========== TOP CANDIDATES ==========")

for item in report:
    print("\nFacility:", item["website_facility"])
    print("Classification:", item["category"])

    for candidate in item["candidates"][:3]:
        print(
            " ",
            candidate["score"],
            "|",
            candidate["crm_name"],
            "|",
            candidate["account_id"]
        )

print("\nScored report saved:", output_file)
