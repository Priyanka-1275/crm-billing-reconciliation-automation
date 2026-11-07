import json

with open(
    "verification/data/scored_match_report.json",
    encoding="utf-8"
) as f:
    data = json.load(f)

target_cities = {
    "kettering",
    "tiffin",
    "marietta",
    "lima",
    "zanesville",
    "batavia",
    "new albany",
    "carlisle",
    "hudson"
}

for item in data:
    address = item.get("website_address", [])

    if len(address) < 2:
        continue

    city = address[1].strip().lower()

    if city not in target_cities:
        continue

    print("\n" + "=" * 60)
    print("WEBSITE:", item.get("website_facility"))
    print("ADDRESS:", item.get("website_address"))
    print("PHONE:", item.get("website_phone"))
    print("CATEGORY:", item.get("category"))

    for c in item.get("candidates", []):
        print("\n  CRM:", c.get("crm_name"))
        print("  ID:", c.get("account_id"))
        print("  Parent:", c.get("parent_name"))
        print("  Score:", c.get("score"))
        print("  Address:", c.get("crm_address"))
        print("  Phone:", c.get("crm_phone"))