import json
from collections import Counter

file_path = "verification/data/crm_snapshot.json"

with open(file_path, "r", encoding="utf-8") as file:
    accounts = json.load(file)

print("========== CRM ANALYSIS ==========")

print("\nTotal accounts:", len(accounts))

# Account status
print("\nAccount Status:")
for status, count in Counter(
    x.get("status") for x in accounts
).items():
    print(status, ":", count)

# Parent account relationships
with_parent = [x for x in accounts if x.get("parent_id")]
without_parent = [x for x in accounts if not x.get("parent_id")]

print("\nParent Relationships:")
print("Accounts with parent:", len(with_parent))
print("Accounts without parent:", len(without_parent))

# Duplicate account names
names = [
    x["name"].strip().casefold()
    for x in accounts if x.get("name")
]

print("\nDuplicate Account Names:")
duplicates = [
    name for name, count in Counter(names).items()
    if count > 1
]

print(duplicates if duplicates else "None")

# Duplicate references
duplicate_accounts = [
    x for x in accounts if x.get("duplicate_of_account")
]

print("\nAccounts marked as duplicates:",
      len(duplicate_accounts))

for x in duplicate_accounts:
    print(x["name"], "->", x["duplicate_of_account"])

# Change of ownership
chow_accounts = [
    x for x in accounts if x.get("chow_current_account")
]

print("\nAccounts with CHOW indicators:",
      len(chow_accounts))

for x in chow_accounts:
    print(x["name"], "->", x["chow_current_account"])

# Candidate-created accounts
candidate_accounts = [
    x for x in accounts if x.get("created_by_candidate") is True
]

print("\nAccounts created by candidate:",
      len(candidate_accounts))

for x in candidate_accounts:
    print(x["name"], "|", x["account_id"])

print("\n========== ANALYSIS COMPLETE ==========")