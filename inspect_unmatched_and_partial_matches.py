
import json
import re
from pathlib import Path
from difflib import SequenceMatcher

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

CRM_FILE = BASE_DIR / "verification" / "data" / "crm_snapshot.json"

# Update this path if your cleaned website file has a different name.
WEBSITE_FILE = BASE_DIR / "verification" / "data" / "website_facilities_cleaned.json"


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def normalize(value):
    if isinstance(value, list):
        value = " ".join(str(x) for x in value)

    if not value:
        return ""

    value = str(value).lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def similarity(a, b):
    a = normalize(a)
    b = normalize(b)

    if not a or not b:
        return 0

    return round(SequenceMatcher(None, a, b).ratio() * 100, 2)


def get_address(record):
    street = (
        record.get("street")
        or record.get("billing_street")
        or ""
    )

    city = (
        record.get("city")
        or record.get("billing_city")
        or ""
    )

    state = (
        record.get("state")
        or record.get("billing_state")
        or ""
    )

    zip_code = (
        record.get("zip")
        or record.get("billing_zip")
        or ""
    )

    return " ".join([street, city, state, zip_code])


def get_name(record):
    return (
        record.get("name")
        or record.get("facility_name")
        or record.get("website_name")
        or ""
    )


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

with open(CRM_FILE, "r", encoding="utf-8") as f:
    crm_data = json.load(f)

with open(WEBSITE_FILE, "r", encoding="utf-8") as f:
    website_data = json.load(f)


print("\n========== UNMATCHED AND PARTIAL MATCH INVESTIGATION ==========\n")

print("Total CRM records:", len(crm_data))
print("Total Website records:", len(website_data))


# --------------------------------------------------
# MATCHING ANALYSIS
# --------------------------------------------------

for website in website_data:

    website_name = get_name(website)
    website_address = get_address(website)

    website_name_norm = normalize(website_name)
    website_address_norm = normalize(website_address)

    candidates = []

    for crm in crm_data:

        crm_name = get_name(crm)
        crm_address = get_address(crm)

        name_score = similarity(website_name, crm_name)
        address_score = similarity(website_address, crm_address)

        # Consider possible matches based on either field.
        if name_score >= 65 or address_score >= 65:

            candidates.append({
                "crm": crm,
                "name_score": name_score,
                "address_score": address_score,
                "combined_score": round(
                    (name_score + address_score) / 2, 2
                )
            })

    candidates.sort(
        key=lambda x: x["combined_score"],
        reverse=True
    )

    # --------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------

    print("\n--------------------------------------------------")
    print("WEBSITE FACILITY:", website_name)
    print("WEBSITE ADDRESS:", website_address)

    if not candidates:
        print("\nSTATUS: NO POSSIBLE CRM MATCH FOUND")
        continue

    print("\nPOSSIBLE CRM MATCHES:")

    for index, candidate in enumerate(candidates[:5], start=1):

        crm = candidate["crm"]

        print(f"\nCandidate {index}")
        print("CRM ID:", crm.get("account_id", "N/A"))
        print("CRM Name:", get_name(crm))
        print("CRM Address:", get_address(crm))
        print("Parent ID:", crm.get("parent_id", "N/A"))
        print("Parent Name:", crm.get("parent_name", "N/A"))

        print("Name Similarity:",
              candidate["name_score"], "%")

        print("Address Similarity:",
              candidate["address_score"], "%")

        print("Combined Similarity:",
              candidate["combined_score"], "%")

        if (
            candidate["name_score"] >= 85
            and candidate["address_score"] >= 85
        ):
            print("Assessment: STRONG POSSIBLE MATCH")

        elif candidate["name_score"] >= 85:
            print("Assessment: NAME-BASED POSSIBLE MATCH")

        elif candidate["address_score"] >= 85:
            print("Assessment: ADDRESS-BASED POSSIBLE MATCH")

        else:
            print("Assessment: WEAK POSSIBLE MATCH")


print("\n========== INVESTIGATION COMPLETED ==========\n")
