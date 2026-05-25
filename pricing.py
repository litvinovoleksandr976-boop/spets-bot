"""
SPETS SECURITY — Pricing module (3 packages, May 2026 prices)

Packages:
  Budget  (Green)  — POC analog: Hikvision POC camera + POC DVR (cheapest)
  Balance (Blue)   — HiLook IP: HiLook 4MP ColorVu + HiLook NVR
  Elite   (Gold)   — Hikvision AcuSense IP: 4MP ColorVu 3.0 + AcuSense NVR

Common in all 3 packages:
  HDD (Toshiba S300, chosen by archive duration)
  Deep Base (1 per camera)
  Installation (by camera count)
"""

VAT_RATE = 0.20

# =====================================================================
# CAMERAS (per package)
# =====================================================================
CAMERAS = {
    "budget": {
        # POC analog with audio + coaxial cable
        "name": "Hikvision POC + AoC Hybrid ColorVu 3K 40m Turret Dome with Microphone 2.8mm",
        "sku": "DS-2CE72KF3T-LSYE-2.8MM",
        "brand": "Hikvision POC",
        "resolution": "3K",
        "base": 43.50,
    },
    "balance": {
        # HiLook IP (moved here from old "budget")
        "name": "HiLook IP Motion 2.0 Smart Hybrid ColorVu 4MP 30m Turret Dome with Mic 2.8mm",
        "sku": "HI-IPC-T249HA-LU-2.8MM",
        "brand": "HiLook",
        "resolution": "4MP",
        "base": 60.95,
    },
    "elite": {
        # Hikvision AcuSense IP 4MP (moved here from old "balance")
        "name": "Hikvision IP Hybrid ColorVu 3.0 4MP 30m Turret Dome Mic/Speaker/Alarm 2.8mm",
        "sku": "DS-2CD2347G3-LI2UY-2.8MM",
        "brand": "Hikvision",
        "resolution": "4MP",
        "base": 116.00,  # NEW PRICE (was £141.45)
    },
}

# =====================================================================
# RECORDERS (DVR for Budget POC, NVR for Balance/Elite IP)
# =====================================================================
RECORDERS = {
    # Budget — Hikvision POC DVR (analog, coaxial)
    "budget_4":  {"brand": "Hikvision POC", "channels": 4,  "type": "DVR",
                  "name": "Hikvision POC Acusense Turbo 4ch 4K 8MP DVR",
                  "sku": "IDS-7204HUHI-M1/PXT", "base": 102.00},
    "budget_8":  {"brand": "Hikvision POC", "channels": 8,  "type": "DVR",
                  "name": "Hikvision POC Acusense Turbo 8ch 4K 8MP DVR",
                  "sku": "IDS-7208HUHI-M2/PXT", "base": 206.50},
    "budget_16": {"brand": "Hikvision POC", "channels": 16, "type": "DVR",
                  "name": "Hikvision Acusense POC Turbo 16ch 4K 8MP DVR",
                  "sku": "IDS-7216HUHI-M2/PXT", "base": 329.50},

    # Balance — HiLook IP NVR
    "balance_4":  {"brand": "HiLook", "channels": 4,  "type": "NVR",
                   "name": "HiLook IP 4ch 4K NVR - 4 POE",
                   "sku": "HI-NVR-104MH-C/4P", "base": 83.95},
    "balance_8":  {"brand": "HiLook", "channels": 8,  "type": "NVR",
                   "name": "HiLook IP 8ch 4K NVR - 8 POE",
                   "sku": "HI-NVR-108MH-C/8P", "base": 113.85},
    "balance_16": {"brand": "HiLook", "channels": 16, "type": "NVR",
                   "name": "HiLook IP 16ch 4K 8MP NVR - 16 POE",
                   "sku": "NVR-216MH-C/16P", "base": 164.00},  # NEW PRICE

    # Elite — Hikvision AcuSense NVR
    "elite_4":  {"brand": "Hikvision", "channels": 4,  "type": "NVR",
                 "name": "Hikvision IP AcuSense 4ch 4K 8MP NVR - 4 POE",
                 "sku": "DS-7604NXI-K1/4P", "base": 116.00},   # NEW PRICE
    "elite_8":  {"brand": "Hikvision", "channels": 8,  "type": "NVR",
                 "name": "Hikvision IP AcuSense 8ch 4K 8MP NVR - 8 POE",
                 "sku": "DS-7608NXI-K2/8P", "base": 192.50},   # NEW PRICE
    "elite_16": {"brand": "Hikvision", "channels": 16, "type": "NVR",
                 "name": "Hikvision IP AcuSense 16ch 4K 8MP NVR - 16 POE",
                 "sku": "DS-7616NXI-K2/16P", "base": 252.50},  # NEW PRICE
}

# =====================================================================
# HDD (same in all packages — Toshiba S300 Surveillance, by archive duration)
# =====================================================================
HDD = {
    "1_week":   {"name": "Toshiba S300 1TB Surveillance HDD", "sku": "TOS-HDD-1TB", "capacity": "1TB", "archive": "~1 week",   "base": 74.75},
    "2_weeks":  {"name": "Toshiba S300 2TB Surveillance HDD", "sku": "TOS-HDD-2TB", "capacity": "2TB", "archive": "~2 weeks",  "base": 110.40},
    "1_month":  {"name": "Toshiba S300 4TB Surveillance HDD", "sku": "TOS-HDD-4TB", "capacity": "4TB", "archive": "~1 month",  "base": 156.97},
    "2_months": {"name": "Toshiba S300 6TB Surveillance HDD", "sku": "TOS-HDD-6TB", "capacity": "6TB", "archive": "~2 months", "base": 238.62},
}

# =====================================================================
# DEEP BASE (mounting box, 1 per camera, same in all packages)
# =====================================================================
DEEP_BASE = {
    "name": "Hikvision S Deep Base (DS-1280ZJ-S)",
    "sku":  "DS-1280ZJ-S",
    "base": 18.00,
}

# =====================================================================
# INSTALLATION (by camera count)
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
# PACKAGE METADATA (UI colours and labels)
# =====================================================================
PACKAGE_META = {
    "budget":  {"label": "Budget",  "color": "#2E7D32", "color_name": "green"},
    "balance": {"label": "Balance", "color": "#1565C0", "color_name": "blue"},
    "elite":   {"label": "Elite",   "color": "#C9A227", "color_name": "gold"},
}


# =====================================================================
# HELPERS
# =====================================================================
def _pick_recorder(camera_count: int, package: str) -> dict:
    """Pick DVR/NVR by camera count + package."""
    if camera_count <= 4:
        ch = 4
    elif camera_count <= 8:
        ch = 8
    else:
        ch = 16
    return RECORDERS[f"{package}_{ch}"]


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
    """Build quote for ONE package (budget/balance/elite)."""
    if package not in CAMERAS:
        raise ValueError(f"Unknown package: {package}")

    camera = CAMERAS[package]
    recorder = _pick_recorder(camera_count, package)
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

    # 2. Recorder (DVR or NVR)
    items.append({
        "name": recorder["name"],
        "sku":  recorder["sku"],
        "qty":  1,
        "base": recorder["base"],
        "vat":  _vat(recorder["base"]),
        "total": round(recorder["base"] * (1 + VAT_RATE), 2),
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

    # 4. Deep Base (1 per camera)
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


def build_all_packages(camera_count: int, archive_choice: str) -> dict:
    """Build all 3 quotes (Budget, Balance, Elite) for the same parameters."""
    return {
        "budget":  build_package_quote("budget",  camera_count, archive_choice),
        "balance": build_package_quote("balance", camera_count, archive_choice),
        "elite":   build_package_quote("elite",   camera_count, archive_choice),
    }


# =====================================================================
# QUICK TEST
# =====================================================================
if __name__ == "__main__":
    print("=== TEST: 6 cameras, 2 weeks archive ===\n")
    quotes = build_all_packages(camera_count=6, archive_choice="2_weeks")
    for pkg_id, q in quotes.items():
        print(f"\n{q['package_label']} ({PACKAGE_META[pkg_id]['color_name']}):")
        for it in q["items"]:
            print(f"  {it['qty']:>2}x {it['name'][:55]:<58} £{(it['base'] + it['vat']) * it['qty']:>9,.2f}")
        print(f"  Subtotal: £{q['subtotal']:,.2f}  VAT: £{q['vat_total']:,.2f}  TOTAL: £{q['grand_total']:,.2f}")
