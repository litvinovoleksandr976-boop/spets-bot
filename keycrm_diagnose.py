"""
SPETS SECURITY — KeyCRM Diagnostic Tool
Run this ONCE to find all IDs needed for integration:
- API key validity
- Managers list (find your ID)
- Sources list (verify Telegram Bot CCTV exists)
- Order statuses
- Pipeline stages
- Custom fields

Usage:
    export KEYCRM_API_KEY='your_key_here'
    python keycrm_diagnose.py

The script is READ-ONLY — it doesn't create or modify anything.
"""
import os
import json
import requests

API_KEY = os.getenv("KEYCRM_API_KEY", "")
BASE_URL = "https://openapi.keycrm.app/v1"

if not API_KEY:
    print("❌ ERROR: KEYCRM_API_KEY environment variable not set")
    print("Run: export KEYCRM_API_KEY='your_key'")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def fetch(endpoint: str, params: dict = None) -> dict:
    """GET request to KeyCRM API. Returns parsed JSON or error dict."""
    url = f"{BASE_URL}{endpoint}"
    try:
        r = requests.get(url, headers=HEADERS, params=params or {}, timeout=15)
        if r.status_code == 200:
            return r.json()
        return {"error": f"HTTP {r.status_code}", "body": r.text[:500]}
    except Exception as e:
        return {"error": str(e)}


def section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


# =====================================================================
# 1. Verify API key
# =====================================================================
section("1. API KEY VERIFICATION")
result = fetch("/order", params={"limit": 1})
if "error" in result:
    print(f"❌ API key FAILED: {result['error']}")
    print(f"   Body: {result.get('body', '')}")
    print(f"   Check that your API key is correct and active.")
    exit(1)
else:
    print(f"✅ API key works")
    total = result.get("total", "?")
    print(f"   Total orders in KeyCRM: {total}")

# =====================================================================
# 2. Sources
# =====================================================================
section("2. SOURCES (we need 'Telegram Bot CCTV' ID = 23)")
result = fetch("/order/source")
if "error" in result:
    print(f"❌ Cannot fetch sources: {result['error']}")
else:
    sources = result.get("data", [])
    print(f"Found {len(sources)} sources:\n")
    for s in sources:
        marker = " 👈 OUR SOURCE!" if s.get("name", "").lower() == "telegram bot cctv" else ""
        print(f"  ID={s.get('id'):>4}  |  {s.get('name', '?')}{marker}")

# =====================================================================
# 3. Managers (find Oleksandr's ID)
# =====================================================================
section("3. MANAGERS (find Oleksandr ID)")
result = fetch("/users")
if "error" in result:
    # Try alternative endpoint name
    result = fetch("/manager")
if "error" in result:
    print(f"⚠️  Cannot fetch managers: {result.get('error')}")
    print(f"   Will try to get manager IDs from existing orders instead...")
    orders = fetch("/order", params={"limit": 5, "include": "manager"})
    if "data" in orders:
        seen = {}
        for o in orders.get("data", []):
            mgr = o.get("manager", {})
            if mgr and mgr.get("id") not in seen:
                seen[mgr.get("id")] = mgr.get("full_name", "?")
        print(f"\nManagers found in recent orders:")
        for mid, mname in seen.items():
            print(f"  ID={mid:>4}  |  {mname}")
else:
    users = result.get("data", [])
    print(f"Found {len(users)} users/managers:\n")
    for u in users:
        print(f"  ID={u.get('id'):>4}  |  {u.get('full_name', u.get('email', '?'))}")

# =====================================================================
# 4. Order statuses
# =====================================================================
section("4. ORDER STATUSES (we need 'Новий' / 'New' ID)")
result = fetch("/order/status")
if "error" in result:
    print(f"⚠️  Cannot fetch statuses: {result.get('error')}")
else:
    statuses = result.get("data", [])
    print(f"Found {len(statuses)} statuses:\n")
    for s in statuses:
        name = s.get("name", "?")
        marker = " 👈 NEW LEAD!" if name.lower() in ("новий", "new", "новый") else ""
        print(f"  ID={s.get('id'):>4}  |  {name}{marker}")

# =====================================================================
# 5. Pipelines
# =====================================================================
section("5. PIPELINES")
result = fetch("/pipelines")
if "error" in result:
    print(f"⚠️  Cannot fetch pipelines: {result.get('error')}")
else:
    pipelines = result.get("data", [])
    print(f"Found {len(pipelines)} pipelines:\n")
    for p in pipelines:
        print(f"  ID={p.get('id'):>4}  |  {p.get('name', '?')}")
        # Get stages for each pipeline
        stages_result = fetch(f"/pipelines/{p.get('id')}/cards")
        if "data" in stages_result:
            print(f"    Stages: (check separately)")

# =====================================================================
# 6. Lead/Pipeline statuses
# =====================================================================
section("6. LEAD STATUSES (pipeline stages)")
result = fetch("/pipelines/statuses")
if "error" in result:
    print(f"⚠️  Cannot fetch lead statuses: {result.get('error')}")
else:
    statuses = result.get("data", [])
    print(f"Found {len(statuses)} lead statuses:\n")
    for s in statuses:
        name = s.get("name", "?")
        pipeline_id = s.get("pipeline_id", "?")
        print(f"  ID={s.get('id'):>4}  |  Pipeline {pipeline_id}  |  {name}")

# =====================================================================
# 7. Test: try to fetch one buyer to see structure
# =====================================================================
section("7. BUYER STRUCTURE (sample)")
result = fetch("/buyer", params={"limit": 1, "include": "custom_fields"})
if "error" in result:
    print(f"⚠️  Cannot fetch buyer: {result.get('error')}")
else:
    buyers = result.get("data", [])
    if buyers:
        print("Sample buyer (first one):\n")
        print(json.dumps(buyers[0], indent=2, ensure_ascii=False)[:2000])
    else:
        print("No buyers in CRM yet.")

print(f"\n{'=' * 60}")
print("  DIAGNOSTIC COMPLETE")
print('=' * 60)
print("\nCopy these IDs for the next step:")
print("  - Source ID (Telegram Bot CCTV): 23")
print("  - Manager ID (Oleksandr): ?")
print("  - Order Status ID (Новий): ?")
print("  - Pipeline ID (main): ?")
