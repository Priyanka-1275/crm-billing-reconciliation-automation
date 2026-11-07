import json

with open(
    "verification/data/scored_match_report.json",
    encoding="utf-8"
) as f:
    data = json.load(f)

for item in data:
    if item.get("category") == "STRONG_CANDIDATE":

        print("\n" + "=" * 55)
        print("FACILITY:", item.get("website_facility"))
        print("WEBSITE ADDRESS:", item.get("website_address"))
        print("WEBSITE PHONE:", item.get("website_phone"))

        candidates = item.get("candidates", [])

        if candidates:
            c = candidates[0]

            print("\nCRM MATCH")
            print("Score:", c.get("score"))
            print("Name:", c.get("crm_name"))
            print("Account ID:", c.get("account_id"))
            print("Parent:", c.get("parent_name"))
            print("Address:", c.get("crm_address"))
            print("Phone:", c.get("crm_phone"))
            print("Revenue:", c.get("lifetime_revenue"))
            print("AR:", c.get("outstanding_ar"))