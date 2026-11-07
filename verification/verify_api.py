"""
CRM API Verification Script - READ ONLY
Tests authentication, pagination, and retrieves specific accounts.
Never writes to CRM. Never logs the token.
"""
import os
import sys
import json
import time

try:
    import httpx
except ImportError:
    print("Installing httpx...")
    os.system(f"{sys.executable} -m pip install httpx --quiet")
    import httpx

BASE_URL = "https://analyst-assessment-production.up.railway.app/api/v1"
TOKEN = os.environ.get("CRM_API_TOKEN", "")

if not TOKEN:
    print("ERROR: CRM_API_TOKEN environment variable is not set.")
    sys.exit(1)

print(f"Token loaded: {len(TOKEN)} characters (value hidden)")

headers = {"Authorization": f"Bearer {TOKEN}"}
client = httpx.Client(base_url=BASE_URL, headers=headers, timeout=30.0)

# ── Step 1: Test authentication ──────────────────────────────────
print("\n=== STEP 1: Test /api/v1/me ===")
try:
    r = client.get("/me")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        me_data = r.json()
        # Redact token from output if present
        safe_me = {k: ("***REDACTED***" if "token" in k.lower() else v) for k, v in me_data.items()}
        print(json.dumps(safe_me, indent=2))
    else:
        print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# ── Step 2: Fetch ALL accounts with pagination ───────────────────
print("\n=== STEP 2: Fetch all accounts (paginated) ===")
all_accounts = []
page = 1
page_size = 50

while True:
    time.sleep(0.3)  # Rate limiting
    r = client.get("/accounts", params={"page": page, "page_size": page_size})
    print(f"Page {page}: status={r.status_code}")
    
    if r.status_code != 200:
        print(f"  Error: {r.text[:300]}")
        break
    
    data = r.json()
    
    # Inspect response structure on first page
    if page == 1:
        print(f"  Response type: {type(data).__name__}")
        if isinstance(data, dict):
            print(f"  Top-level keys: {list(data.keys())}")
            for k, v in data.items():
                if isinstance(v, list):
                    print(f"  '{k}' is a list with {len(v)} items")
                    if v:
                        print(f"  First item keys: {list(v[0].keys())}")
                        # Print the FULL first record for schema discovery
                        print(f"\n  === FULL FIRST ACCOUNT RECORD (schema discovery) ===")
                        for fk, fv in v[0].items():
                            print(f"    {fk}: {json.dumps(fv)} ({type(fv).__name__})")
                else:
                    print(f"  '{k}': {v}")
        elif isinstance(data, list):
            print(f"  List with {len(data)} items")
            if data:
                print(f"  First item keys: {list(data[0].keys())}")
                print(f"\n  === FULL FIRST ACCOUNT RECORD (schema discovery) ===")
                for fk, fv in data[0].items():
                    print(f"    {fk}: {json.dumps(fv)} ({type(fv).__name__})")
    
    # Extract accounts from response
    if isinstance(data, dict):
        accounts = data.get("accounts", data.get("items", data.get("results", data.get("data", []))))
        total = data.get("total", data.get("total_count", data.get("count", "unknown")))
        has_more = data.get("has_more", data.get("next", None))
        total_pages = data.get("total_pages", data.get("pages", "unknown"))
        
        if page == 1:
            print(f"  total={total}, total_pages={total_pages}, has_more={has_more}")
        
        if isinstance(accounts, list):
            all_accounts.extend(accounts)
            print(f"  Got {len(accounts)} accounts (running total: {len(all_accounts)})")
            
            if len(accounts) < page_size:
                break
        else:
            print(f"  Could not find accounts list in response")
            break
    elif isinstance(data, list):
        all_accounts.extend(data)
        print(f"  Got {len(data)} accounts (running total: {len(all_accounts)})")
        if len(data) < page_size:
            break
    
    page += 1
    if page > 20:  # Safety limit
        print("  Safety limit reached")
        break

print(f"\nTotal accounts retrieved: {len(all_accounts)}")

# Save full snapshot
os.makedirs("L:/clipboard-project/verification/data", exist_ok=True)
with open("L:/clipboard-project/verification/data/crm_snapshot.json", "w") as f:
    json.dump(all_accounts, f, indent=2)
print("Saved full snapshot to verification/data/crm_snapshot.json")

# ── Step 3: Summary of all accounts ──────────────────────────────
print("\n=== STEP 3: Account summary ===")
parent_accounts = {}
child_accounts = []
status_counts = {}

for acc in all_accounts:
    # Count statuses
    status = acc.get("status", "unknown")
    status_counts[status] = status_counts.get(status, 0) + 1
    
    # Identify parent accounts (those that are parents of others)
    parent_id = acc.get("parent_id") or acc.get("parent_account_id") or acc.get("parent")
    acc_id = acc.get("id") or acc.get("account_id")
    name = acc.get("name") or acc.get("account_name")
    
    if parent_id:
        child_accounts.append(acc)
    
    # Check if this is a parent company type
    acc_type = acc.get("type") or acc.get("account_type")
    if acc_type and "parent" in str(acc_type).lower():
        parent_accounts[acc_id] = name

print(f"Status distribution: {json.dumps(status_counts, indent=2)}")
print(f"Accounts with parent_id: {len(child_accounts)}")

# Find Bellhaven parent
for acc in all_accounts:
    name = acc.get("name") or acc.get("account_name") or ""
    if "bellhaven" in name.lower() and ("senior" in name.lower() or "parent" in name.lower()):
        acc_id = acc.get("id") or acc.get("account_id")
        print(f"\nPotential Bellhaven parent: '{name}' (ID: {acc_id})")
        print(f"  Full record:")
        for k, v in acc.items():
            print(f"    {k}: {json.dumps(v)}")

# ── Step 4: Find all parent company accounts ─────────────────────
print("\n=== STEP 4: All parent company accounts ===")
for acc in all_accounts:
    acc_type = acc.get("type") or acc.get("account_type") or ""
    if "parent" in str(acc_type).lower() or (not acc.get("parent_id") and not acc.get("parent_account_id")):
        name = acc.get("name") or acc.get("account_name") or ""
        acc_id = acc.get("id") or acc.get("account_id")
        # Only show those that actually are parent type or have no parent themselves
        if "parent" in str(acc_type).lower():
            print(f"  Parent account: '{name}' (ID: {acc_id}, type: {acc_type})")

# ── Step 5: Retrieve specific accounts ───────────────────────────
print("\n=== STEP 5: Specific account details ===")

target_names = [
    "bellhaven of marietta",
    "bellhaven crossings of lima",
    "bellhaven of tiffin",
    "bellhaven of owosso",
]

found_targets = []
for acc in all_accounts:
    name = (acc.get("name") or acc.get("account_name") or "").lower()
    for target in target_names:
        if target in name:
            found_targets.append(acc)

print(f"Found {len(found_targets)} matching accounts")

for acc in found_targets:
    acc_id = acc.get("id") or acc.get("account_id")
    print(f"\n--- Fetching individual record: {acc_id} ---")
    time.sleep(0.3)
    r = client.get(f"/accounts/{acc_id}")
    if r.status_code == 200:
        detail = r.json()
        for k, v in detail.items():
            print(f"  {k}: {json.dumps(v)}")
    else:
        print(f"  Error {r.status_code}: {r.text[:200]}")

# ── Step 6: Bellhaven parent account full details ─────────────────
print("\n=== STEP 6: Bellhaven parent account (0015QAPLGS3FVYEEEM) ===")
time.sleep(0.3)
r = client.get("/accounts/0015QAPLGS3FVYEEEM")
if r.status_code == 200:
    detail = r.json()
    for k, v in detail.items():
        print(f"  {k}: {json.dumps(v)}")
else:
    print(f"  Error {r.status_code}: {r.text[:200]}")

# ── Step 7: List all Bellhaven-parented accounts ──────────────────
print("\n=== STEP 7: All accounts under Bellhaven parent ===")
bellhaven_children = []
for acc in all_accounts:
    parent_id = acc.get("parent_id") or acc.get("parent_account_id")
    if parent_id == "0015QAPLGS3FVYEEEM":
        name = acc.get("name") or acc.get("account_name")
        acc_id = acc.get("id") or acc.get("account_id")
        status = acc.get("status", "unknown")
        bellhaven_children.append((name, acc_id, status))
        
print(f"Total accounts under Bellhaven: {len(bellhaven_children)}")
for name, aid, status in sorted(bellhaven_children):
    print(f"  {name} ({aid}) - {status}")

# ── Step 8: Group all accounts by parent ──────────────────────────
print("\n=== STEP 8: Accounts grouped by parent ===")
by_parent = {}
for acc in all_accounts:
    parent_id = acc.get("parent_id") or acc.get("parent_account_id") or "NO_PARENT"
    if parent_id not in by_parent:
        by_parent[parent_id] = []
    name = acc.get("name") or acc.get("account_name") or "unnamed"
    acc_id = acc.get("id") or acc.get("account_id")
    by_parent[parent_id].append((name, acc_id))

for parent_id, children in by_parent.items():
    # Find parent name
    parent_name = parent_id
    for acc in all_accounts:
        if (acc.get("id") or acc.get("account_id")) == parent_id:
            parent_name = acc.get("name") or acc.get("account_name") or parent_id
            break
    print(f"\n  Parent: {parent_name} ({parent_id}) - {len(children)} children")
    for name, aid in sorted(children):
        print(f"    {name} ({aid})")

client.close()
print("\n=== Verification complete ===")
