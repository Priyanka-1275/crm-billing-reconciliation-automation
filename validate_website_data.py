import json
from collections import Counter

file_path = "verification/data/website_facilities_cleaned.json"

with open(file_path, "r", encoding="utf-8") as file:
    facilities = json.load(file)

# Check duplicate URLs
urls = [x["source_url"].strip().lower() for x in facilities]
duplicate_urls = [
    url for url, count in Counter(urls).items()
    if count > 1
]

# Check duplicate addresses
addresses = [
    " ".join(
        f'{x["street"]}, {x["city"]}, {x["state"]}, {x["zip"]}'
        .casefold().split()
    )
    for x in facilities
]

duplicate_addresses = [
    address for address, count in Counter(addresses).items()
    if count > 1
]

# Check missing values
missing_records = []

for i, facility in enumerate(facilities, start=1):
    missing = [
        key for key, value in facility.items()
        if value is None or value == "" or value == []
    ]

    if missing:
        missing_records.append((i, facility["name"], missing))

print("Total facilities:", len(facilities))

print("\nDuplicate URLs:")
print(duplicate_urls if duplicate_urls else "None")

print("\nDuplicate addresses:")
print(duplicate_addresses if duplicate_addresses else "None")

print("\nRecords with missing values:")
print(missing_records if missing_records else "None")