import json
from pathlib import Path

BELLHAVEN_PARENT_ID = "0015QAPLGS3FVYEEEM"

DATA_DIR = Path("verification/data")
WEBSITE_FILE = DATA_DIR / "website_facilities_cleaned.json"
CRM_FILE = DATA_DIR / "crm_snapshot.json"
QUEUE_FILE = DATA_DIR / "review_queue.json"

PROPOSALS = [
    {
        "account_id": "001U6RW32TY0WSXZZB",
        "facility": "Bellhaven of Tiffin",
        "action": "CREATE_NEW_ACCOUNT_AND_LINK_CHOW",
        "reason": "Existing account has revenue and outstanding AR. Preserve it and create a new account under Bellhaven if ownership is verified."
    },
    {
        "account_id": "001A34WFSUYHCRBLFT",
        "facility": "Bellhaven of Marietta",
        "action": "CREATE_NEW_ACCOUNT_AND_LINK_CHOW",
        "reason": "Existing account has revenue and outstanding AR. Preserve it and create a new account under Bellhaven if ownership is verified."
    },
    {
        "account_id": "001LGFPBJY4N9MB6KL",
        "facility": "Bellhaven Crossings of Lima",
        "action": "REPARENT_EXISTING_ACCOUNT",
        "reason": "Existing account has revenue but zero outstanding AR. Re-parent it under Bellhaven if ownership is verified."
    }
]


def read_json(path, default=None):
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as file:
        return json.load(file)


website = read_json(WEBSITE_FILE, [])
crm = read_json(CRM_FILE, [])
old_queue = read_json(QUEUE_FILE, [])

old_by_id = {
    item["proposal_id"]: item
    for item in old_queue
    if item.get("proposal_id")
}

website_by_name = {item["name"]: item for item in website}
crm_by_id = {item["account_id"]: item for item in crm}

new_queue = []
preserved_decisions = 0

for proposal in PROPOSALS:
    account = crm_by_id.get(proposal["account_id"])
    facility = website_by_name.get(proposal["facility"])

    if not account or not facility:
        print("Missing data for:", proposal["facility"])
        continue

    proposal_id = "REVIEW-" + account["account_id"]
    previous = old_by_id.get(proposal_id, {})

    item = {
        "proposal_id": proposal_id,
        "facility_name": facility["name"],
        "website_evidence": {
            "address": facility["street"],
            "city": facility["city"],
            "state": facility["state"],
            "zip": facility["zip"],
            "phone": facility["phone"],
            "source_url": facility["source_url"]
        },
        "crm_evidence": {
            "account_id": account["account_id"],
            "name": account["name"],
            "parent_id": account["parent_id"],
            "parent_name": account["parent_name"],
            "status": account["status"],
            "lifetime_revenue": account["lifetime_revenue"],
            "outstanding_ar": account["outstanding_ar"],
            "chow_current_account": account["chow_current_account"],
            "duplicate_of_account": account["duplicate_of_account"]
        },
        "proposed_action": proposal["action"],
        "target_parent_id": BELLHAVEN_PARENT_ID,
        "reason": proposal["reason"],
        "ownership_verified": previous.get("ownership_verified", False),
        "approval_status": previous.get("approval_status", "PENDING"),
        "approved": previous.get("approved", False)
    }

    # Preserve reviewer and decision audit details.
    for field in ("reviewer_name", "decided_at"):
        if field in previous:
            item[field] = previous[field]

    if item["approval_status"] in ("APPROVED", "REJECTED"):
        preserved_decisions += 1

    new_queue.append(item)

# Never discard an already-decided proposal, even if it is
# temporarily absent from the current discovery results.
current_ids = {item["proposal_id"] for item in new_queue}

for previous in old_queue:
    if (
        previous.get("approval_status") in ("APPROVED", "REJECTED")
        and previous.get("proposal_id") not in current_ids
    ):
        new_queue.append(previous)
        preserved_decisions += 1

temporary_file = QUEUE_FILE.with_suffix(".tmp")
with temporary_file.open("w", encoding="utf-8") as file:
    json.dump(new_queue, file, indent=2, ensure_ascii=False)

temporary_file.replace(QUEUE_FILE)

print("Review queue updated successfully.")
print("Total proposals:", len(new_queue))
print("Existing decisions preserved:", preserved_decisions)
print("Pending proposals:", sum(
    item["approval_status"] == "PENDING" for item in new_queue
))
print("CRM writes performed: 0")
print("Output:", QUEUE_FILE)
