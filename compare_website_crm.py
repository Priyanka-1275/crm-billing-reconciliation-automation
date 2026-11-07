import json

with open("verification/data/website_facilities_cleaned.json", encoding="utf-8") as f:
    website = json.load(f)

with open("verification/data/crm_snapshot.json", encoding="utf-8") as f:
    crm = json.load(f)

parent_id = "0015QAPLGS3FVYEEEM"

children = [
    a for a in crm
    if a.get("parent_id") == parent_id
]

def normalize(value):
    return (value or "").strip().lower()

website_locations = {
    (normalize(w.get("city")), normalize(w.get("state")))
    for w in website
}

crm_locations = {
    (normalize(a.get("billing_city")), normalize(a.get("billing_state")))
    for a in children
}

print("\n========== CRM ACCOUNTS WITHOUT WEBSITE CITY/STATE ==========")

for a in children:
    location = (
        normalize(a.get("billing_city")),
        normalize(a.get("billing_state"))
    )

    if location not in website_locations:
        print(
            a.get("name"),
            "|", a.get("account_id"),
            "|", a.get("billing_city"),
            "|", a.get("billing_state")
        )

print("\n========== WEBSITE FACILITIES WITHOUT CRM CITY/STATE ==========")

for w in website:
    location = (
        normalize(w.get("city")),
        normalize(w.get("state"))
    )

    if location not in crm_locations:
        print(
            w.get("name"),
            "|", w.get("city"),
            "|", w.get("state")
        )

print("\n========== SAME-CITY/STATE RECORDS WITH DIFFERENT NAMES ==========")

for w in website:
    for a in children:
        if (
            normalize(w.get("city")) == normalize(a.get("billing_city"))
            and normalize(w.get("state")) == normalize(a.get("billing_state"))
            and normalize(w.get("name")) != normalize(a.get("name"))
        ):
            print(
                "\nWebsite:", w.get("name"),
                "\nCRM:", a.get("name"),
                "\nAccount ID:", a.get("account_id"),
                "\nAddress:", a.get("billing_street")
            )