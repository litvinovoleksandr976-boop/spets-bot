"""
SPETS SECURITY — Pricing module (3 packages)

Packages:
  Budget  (Green)  — HiLook 4MP ColorVu + HiLook NVR
  Balance (Blue)   — Hikvision 4MP ColorVu 3.0 + Hikvision AcuSense NVR
  Elite   (Gold)   — Hikvision 4K 8MP + Hikvision AcuSense NVR

Common (same in all 3 packages):
  HDD (chosen by archive duration)
  Deep Base (1 per camera)
  Installation (by camera count)
"""

VAT_RATE = 0.20

# =====================================================================
# CAMERAS (per package)
# =====================================================================
CAMERAS = {
    "budget": {
        "name": "HiLook IP Motion 2.0 Smart Hybrid ColorVu 4MP 30m Turret Dome with Mic 2.8mm",
        "sku": "HI-IPC-T249HA-LU-2.8MM",
        "brand": "HiLook",
        "resolution": "4MP",
        "base": 60.95,
    },
    "balance": {
        "name": "Hikvision IP Hybrid ColorVu 3.0 4MP 30m Turret Dome Mic/Speaker/Alarm 2.8mm",
        "sku": "HIK-DS-2CD2347G3-LIS2UY/SL-28",
        "brand": "Hikvision",
        "resolution": "4MP",
        "base": 141.45,
    },
    "elite": {
        "name": "Hikvision IP Hybrid ColorVu 3.0 4K 8MP 30m Turret Dome Mic/Speaker/Alarm 2.8mm",
        "sku": "HIK-DS-2CD2387G3-LIS2UYSL-28",
        "brand": "Hikvision",
        "resolution": "8MP 4K",
        "base": 193.20,
    },
}

# =====================================================================
# NVR (per package + per channels)
# Budget → HiLook NVR | Balance & Elite → Hikvision AcuSense NVR
# =====================================================================
NVR = {
    # HiLook (Budget)
    "budget_4":  {"brand": "HiLook",    "channels": 4,  "name": "HiLook IP 4ch 4K NVR - 4 POE",          "sku": "HI-NVR-104MH-C/4P",     "base": 83.95},
    "budget_8":  {"brand": "HiLook",    "channels": 8,  "name": "HiLook IP 8ch 4K NVR - 8 POE",          "sku": "HI-NVR-108MH-C/8P",     "base": 113.85},
    "budget_16": {"brand": "HiLook",    "channels": 16, "name": "HiLook IP 16ch 4K NVR - 16 POE",        "sku": "HI-NVR-216MH-C/16P",    "base": 188.60},
    # Hikvision AcuSense (Balance + Elite)
    "hik_4":     {"brand": "Hikvision", "channels": 4,  "name": "Hikvision AcuSense 4ch 4K NVR - 4 POE",  "sku": "HIK-DS-7604NXI-K1/4P",  "base": 133.40},
    "hik_8":     {"brand": "Hikvision", "channels": 8,  "name": "Hikvision AcuSense 8ch 4K NVR - 8 POE",  "sku": "HIK-DS-7608NXI-K1/8P",  "base": 166.17},
    "hik_16":    {"brand": "Hikvision", "channels": 16, "name": "Hikvision AcuSense 16ch 4K NVR - 16 POE","sku": "HIK-DS-7616NXI-K2/16P", "base": 290.38},
}

# =====================================================================
# HDD (same in all packages, depends on archive duration)
# =====================================================================
HDD = {
    "1_week":   {"name": "Toshiba S300 1TB Surveillance HDD", "sku": "TOS-HDD-1TB", "capacity": "1TB", "archive": "~1 week",   "base": 74.75},
    "2_weeks":  {"name": "Toshiba S300 2TB Surveillance HDD", "sku": "TOS-HDD-2TB", "capacity": "2TB", "archive": "~2 weeks",  "base": 110.40},
    "1_month":  {"name": "Toshiba S300 4TB Surveillance HDD", "sku": "TOS-HDD-4TB", "capacity": "4TB", "archive": "~1 month",  "base": 156.97},
    "2_months": {"name": "Toshiba S300 6TB Surveillance HDD", "sku": "TOS-HDD-6TB", "capacity": "6TB", "archive": "~2 months", "base": 238.62},
}

# =====================================================================
# DEEP BASE (same in all packages, 1 per camera)
# =====================================================================
DEEP_BASE = {
    "name": "Hikvision S Deep Base (DS-1280ZJ-S)",
    "sku":  "HIK-DS-1280ZJ-S",
    "base": 18.00,
}

# =====================================================================
# INSTALLATION (same in all packages, by camera count range)
# =====================================================================
INSTALLATION = [
    {"min": 1,  "max": 2,  "desc": "Basic installation (1-2 cameras)",       "base": 200},
    {"min": 3,  "max": 3,  "desc": "Standard installation (3 cameras)",      "base": 220},
    {"min": 4,  "max": 5,  "desc": "Extended installation (4-5 cameras)",    "base": 350},
    {"min": 6,  "max": 6,  "desc": "Full installation (6 cameras)",          "base": 400},
    {"min": 7,  "max": 9,  "desc": "Large site (7-9 cameras)",               "base": 550},
    {"min": 10, "max": 12, "desc": "Commercial (10-12 cameras)",             "base": 800},
    {"min": 13, "max": 16, "desc": "Large commercial (13-16 cameras)",       "base": 1000},
]

# =====================================================================
# PACKAGE METADATA (for UI / PDF colours / labels)
# =====================================================================
PACKAGE_META = {
    "budget":  {"label": "Budget",  "color": "#2E7D32", "color_name": "green"},   # Green
    "balance": {"label": "Balance", "color": "#1565C0", "color_name": "blue"},    # Blue
    "elite":   {"label": "Elite",   "color": "#C9A227", "color_name": "gold"},    # Gold
}


# =====================================================================
# HELPERS
# =====================================================================
def _pick_nvr(camera_count: int, package: str) -> dict:
    """Pick NVR by camera count + package (Budget → HiLook, Balance/Elite → Hikvision)."""
    if camera_count <= 4:
        ch = 4
    elif camera_count <= 8:
        ch = 8
    else:
        ch = 16

    if package == "budget":
        return NVR[f"budget_{ch}"]
    else:
        return NVR[f"hik_{ch}"]


def _pick_installation(camera_count: int) -> dict:
    for tier in INSTALLATION:
        if tier["min"] <= camera_count <= tier["max"]:
            return tier
    return INSTALLATION[-1]


def _vat(amount: float) -> float:
    return round(amount * VAT_RATE, 2)


# =====================================================================
# SINGLE PACKAGE QUOTE
# =====================================================================
def build_package_quote(package: str, camera_count: int, archive_choice: str) -> dict:
    """
    Build quote for ONE package (budget/balance/elite).
    Returns dict with items + totals.
    """
    if package not in CAMERAS:
        raise ValueError(f"Unknown package: {package}")

    camera = CAMERAS[package]
    nvr = _pick_nvr(camera_count, package)
    hdd = HDD.get(archive_choice, HDD["2_weeks"])
    installation = _pick_installation(camera_count)

    items = []

    # 1. Cameras
    items.append({
        "name": camera["name"],
        "sku":  camera["sku"],
        "qty":  camera_count,
        "base": camera["base"],
        "vat":  _vat(camera["base"]),
        "total": round(camera["base"] * (1 + VAT_RATE), 2),
    })

    # 2. NVR
    items.append({
        "name": nvr["name"],
        "sku":  nvr["sku"],
        "qty":  1,
        "base": nvr["base"],
        "vat":  _vat(nvr["base"]),
        "total": round(nvr["base"] * (1 + VAT_RATE), 2),
    })

    # 3. HDD
    items.append({
        "name": hdd["name"],
        "sku":  hdd["sku"],
        "qty":  1,
        "base": hdd["base"],
        "vat":  _vat(hdd["base"]),
        "total": round(hdd["base"] * (1 + VAT_RATE), 2),
    })

    # 4. Deep Base
    items.append({
        "name": DEEP_BASE["name"],
        "sku":  DEEP_BASE["sku"],
        "qty":  camera_count,
        "base": DEEP_BASE["base"],
        "vat":  _vat(DEEP_BASE["base"]),
        "total": round(DEEP_BASE["base"] * (1 + VAT_RATE), 2),
    })

    # 5. Installation
    items.append({
        "name": "Installation CCTV",
        "sku":  "",
        "qty":  1,
        "base": installation["base"],
        "vat":  _vat(installation["base"]),
        "total": round(installation["base"] * (1 + VAT_RATE), 2),
        "desc": installation["desc"],
    })

    subtotal_base = sum(it["base"] * it["qty"] for it in items)
    total_vat = sum(it["vat"] * it["qty"] for it in items)
    grand_total = subtotal_base + total_vat

    return {
        "package": package,
        "package_label": PACKAGE_META[package]["label"],
        "package_color": PACKAGE_META[package]["color"],
        "items": items,
        "subtotal": round(subtotal_base, 2),
        "vat_total": round(total_vat, 2),
        "discount": 0.0,
        "grand_total": round(grand_total, 2),
        "currency": "GBP",
    }


# =====================================================================
# ALL 3 PACKAGES AT ONCE
# =====================================================================
def build_all_packages(camera_count: int, archive_choice: str) -> dict:
    """
    Build all 3 quotes (Budget, Balance, Elite) for the same parameters.
    Returns dict with all 3 packages.
    """
    return {
        "budget":  build_package_quote("budget",  camera_count, archive_choice),
        "balance": build_package_quote("balance", camera_count, archive_choice),
        "elite":   build_package_quote("elite",   camera_count, archive_choice),
    }


# =====================================================================
# QUICK TEST
# =====================================================================
if __name__ == "__main__":
    quotes = build_all_packages(camera_count=6, archive_choice="2_weeks")
    print("=== 3 PACKAGES — 6 cameras, 2 weeks archive ===\n")
    for pkg_id, q in quotes.items():
        print(f"\n{q['package_label']} ({PACKAGE_META[pkg_id]['color_name']}):")
        for it in q["items"]:
            line = (it["base"] + it["vat"]) * it["qty"]
            print(f"  {it['qty']}x {it['name'][:50]:<55} £{line:.2f}")
        print(f"  → Subtotal: £{q['subtotal']:.2f}  VAT: £{q['vat_total']:.2f}  TOTAL: £{q['grand_total']:.2f}")
