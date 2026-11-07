import json
import html

input_file = "verification/data/website_facilities.json"
output_file = "verification/data/website_facilities_cleaned.json"

# Load original website data
with open(input_file, "r", encoding="utf-8") as file:
    facilities = json.load(file)

# Decode HTML entities in text fields
for facility in facilities:
    for key, value in facility.items():
        if isinstance(value, str):
            facility[key] = html.unescape(value)
        elif isinstance(value, list):
            facility[key] = [
                html.unescape(item) if isinstance(item, str) else item
                for item in value
            ]

# Save cleaned data separately
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(facilities, file, indent=2, ensure_ascii=False)

print("Original records:", len(facilities))
print("Cleaned records:", len(facilities))
print("Cleaned file saved:", output_file)

print("\nChecking duplicate names:")
names = [f["name"].casefold().strip() for f in facilities]

duplicates = set(name for name in names if names.count(name) > 1)

if duplicates:
    for name in sorted(duplicates):
        print("Duplicate:", name)
else:
    print("No duplicate facility names found.")

print("\nRecord 13 after cleaning:")
print(facilities[12]["name"])