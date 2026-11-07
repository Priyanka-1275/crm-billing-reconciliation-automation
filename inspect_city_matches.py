import json

with open("verification/data/website_facilities_cleaned.json", encoding="utf-8") as f:
    website = json.load(f)

with open("verification/data/crm_snapshot.json", encoding="utf-8") as f:
    crm = json.load(f)

target_cities = {
    "kettering", "tiffin", "marietta", "lima",
    "zanesville", "batavia", "new albany",
    "carlisle", "hudson"
}

for w in website:
    city = (w.get("city") or "").strip().lower()

    if city not in target_cities:
        continue

    print("\n" + "=" * 55)
    print("WEBSITE:", w.get("name"))
    print("ADDRESS:", w.get("street"), w.get("city"), w.get("state"), w.get("zip"))
    print("PHONE:", w.get("phone"))

    matches = [
        a for a in crm
        if (a.get("billing_city") or "").strip().lower() == city
        and (a.get("billing_state") or "").strip().lower()
            == (w.get("state") or "").strip().lower()
    ]

    if not matches:
        print("NO CRM ACCOUNT IN THIS CITY/STATE")
        continue

    for a in matches:
        print("\nCRM:", a.get("name"))
        print("ID:", a.get("account_id"))
        print("Parent:", a.get("parent_name"))
        print("Address:", a.get("billing_street"), a.get("billing_zip"))
        print("Phone:", a.get("phone"))
        print("Revenue:", a.get("lifetime_revenue"))
        print("AR:", a.get("outstanding_ar"))