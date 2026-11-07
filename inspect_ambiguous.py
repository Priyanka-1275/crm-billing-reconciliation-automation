import json

file_path = "verification/data/scored_match_report.json"

with open(file_path, encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if item.get("category") == "MULTIPLE_CANDIDATES":

        print("\n" + "=" * 60)
        print("FACILITY:", item.get("website_facility"))
        print("WEBSITE ADDRESS:", item.get("website_address"))
        print("WEBSITE PHONE:", item.get("website_phone"))

        for candidate in item.get("candidates", []):
            print("\nCRM CANDIDATE")
            print("Score:", candidate.get("score"))
            print("Name:", candidate.get("crm_name"))
            print("Account ID:", candidate.get("account_id"))
            print("Parent:", candidate.get("parent_name"))
            print("Address:", candidate.get("crm_address"))
            print("Phone:", candidate.get("crm_phone"))
            print("Revenue:", candidate.get("lifetime_revenue"))
            print("Outstanding AR:", candidate.get("outstanding_ar"))