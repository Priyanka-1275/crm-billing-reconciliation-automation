"""
Scrape all 34 website community detail pages. READ ONLY.
Extract: name, address (street, city, state, zip), care offerings, administrator, phone, source URL.
"""
from pathlib import Path
import os, sys, json, time, re

try:
    import httpx
except ImportError:
    os.system(f"{sys.executable} -m pip install httpx --quiet")
    import httpx

BASE = "https://analyst-assessment-production.up.railway.app"
client = httpx.Client(timeout=30.0)

# Step 1: Get all community slugs from directory pages
print("=== Scraping community directory pages ===")
all_slugs = []
page = 1
total_pages = None

while True:
    url = f"{BASE}/communities?page={page}" if page > 1 else f"{BASE}/communities"
    time.sleep(0.5)
    r = client.get(url)
    html = r.text
    
    # Parse "Page X of Y . N communities listed"
    page_match = re.search(r'Page\s+(\d+)\s+of\s+(\d+)\s*[·.]\s*(\d+)\s+communities listed', html)
    if page_match:
        current_page = int(page_match.group(1))
        total_pages = int(page_match.group(2))
        total_communities = int(page_match.group(3))
        print(f"  Page {current_page} of {total_pages} ({total_communities} total communities)")
    
    # Extract all community links
    links = re.findall(r'href="(/communities/[^"]+)"', html)
    # Filter out just the back link and page links
    detail_links = [l for l in links if '?' not in l and l != '/communities']
    # Deduplicate while preserving order
    seen = set()
    for l in detail_links:
        if l not in seen:
            seen.add(l)
            all_slugs.append(l)
    
    print(f"  Found {len(detail_links)} unique links on page {page}")
    
    if total_pages and page >= total_pages:
        break
    if not re.search(r'href="/communities\?page=', html):
        break
    page += 1

print(f"\nTotal unique community URLs found: {len(all_slugs)}")

# Step 2: Visit each detail page
print("\n=== Scraping detail pages ===")
facilities = []
errors = []

for i, slug in enumerate(all_slugs):
    time.sleep(0.4)
    url = f"{BASE}{slug}"
    try:
        r = client.get(url)
        if r.status_code != 200:
            errors.append({"slug": slug, "status": r.status_code})
            print(f"  [{i+1}/{len(all_slugs)}] ERROR {r.status_code}: {slug}")
            continue
        
        html = r.text
        
        # Extract facility name from <h1>
        name_match = re.search(r'<h1>(.*?)</h1>', html)
        name = name_match.group(1).strip() if name_match else ""
        
        # Extract address from <dt>Address</dt><dd>...</dd>
        addr_match = re.search(r'<dt>Address</dt>\s*<dd>(.*?)</dd>', html, re.DOTALL)
        street = city = state = zip_code = ""
        if addr_match:
            addr_raw = addr_match.group(1).strip()
            # Address format: "Street<br>City, ST ZIP"
            parts = re.split(r'<br\s*/?>', addr_raw)
            if len(parts) >= 2:
                street = parts[0].strip()
                city_state_zip = parts[1].strip()
                csz_match = re.match(r'(.+?),\s*(\w{2})\s+(\d{5}(?:-\d{4})?)', city_state_zip)
                if csz_match:
                    city = csz_match.group(1).strip()
                    state = csz_match.group(2).strip()
                    zip_code = csz_match.group(3).strip()
                else:
                    city = city_state_zip
            elif len(parts) == 1:
                street = parts[0].strip()
        
        # Extract care offerings
        care_offerings = re.findall(r'<span class="badge">(.*?)</span>', html)
        # Decode HTML entities
        care_offerings = [c.replace('&amp;', '&') for c in care_offerings]
        
        # Extract administrator
        admin_match = re.search(r'<dt>Administrator</dt>\s*<dd>(.*?)</dd>', html, re.DOTALL)
        administrator = admin_match.group(1).strip() if admin_match else ""
        
        # Extract phone
        phone_match = re.search(r'<dt>Phone</dt>\s*<dd>(.*?)</dd>', html, re.DOTALL)
        phone = phone_match.group(1).strip() if phone_match else ""
        
        facility = {
            "name": name,
            "slug": slug,
            "source_url": url,
            "street": street,
            "city": city,
            "state": state,
            "zip": zip_code,
            "care_offerings": care_offerings,
            "administrator": administrator,
            "phone": phone
        }
        facilities.append(facility)
        print(f"  [{i+1}/{len(all_slugs)}] {name} | {street}, {city}, {state} {zip_code} | {care_offerings}")
        
    except Exception as e:
        errors.append({"slug": slug, "error": str(e)})
        print(f"  [{i+1}/{len(all_slugs)}] EXCEPTION: {slug} - {e}")

print(f"\nTotal facilities scraped: {len(facilities)}")
print(f"Errors: {len(errors)}")

# Step 3: Check the homepage mention of Findlay
print("\n=== Checking homepage Bellhaven Meadows of Findlay ===")
r = client.get(f"{BASE}/")
if "bellhaven-meadows-of-findlay" in r.text:
    print("  Findlay IS linked on the homepage (announcement)")
    # Check if it's also in our scraped list
    findlay_in_directory = any(f["slug"] == "/communities/bellhaven-meadows-of-findlay" for f in facilities)
    print(f"  Findlay IS in directory: {findlay_in_directory}")
else:
    print("  Findlay NOT found on homepage")

# Save results
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

with (DATA_DIR / "website_facilities.json").open("w", encoding="utf-8") as f:
    json.dump(facilities, f, indent=2, ensure_ascii=False)
    

# Summary
print("\n=== ALL FACILITIES SUMMARY ===")
for f in facilities:
    missing = []
    if not f["street"]: missing.append("street")
    if not f["city"]: missing.append("city")
    if not f["state"]: missing.append("state")
    if not f["zip"]: missing.append("zip")
    if not f["care_offerings"]: missing.append("care_offerings")
    missing_str = f" [MISSING: {', '.join(missing)}]" if missing else ""
    print(f"  {f['name']} | {f['city']}, {f['state']} {f['zip']}{missing_str}")

if errors:
    print(f"\n=== ERRORS ===")
    for e in errors:
        print(f"  {e}")

client.close()
print("\n=== Website scrape complete ===")
