"""
SPETS SECURITY — Pricing module
Single source of truth for CCTV prices (mirrors CCTV_Database_SpetsSecurity_v2.xlsx)
Later we can swap this to read from Google Sheets via API — same data shape.
"""

VAT_RATE = 0.20  # UK Standard VAT

# =====================================================================
# CAMERAS — base prices already include +15% markup over ADK
# =====================================================================
CAMERAS = {
    "CAM-001": {
        "brand": "HiLook",
        "name": "HiLook IP 5MP 30m Turret Dome with Microphone 2.8mm",
        "sku": "HI-IPC-T250H-MU-2.8MM",
        "resolution": "5MP",
        "ir_color": "IR 30m",
        "base": 50.60,
        "tier": "basic",
        "notes": "Budget camera with mic",
    },
    "CAM-002": {
        "brand": "HiLook",
        "name": "HiLook IP Motion 2.0 Smart Hybrid ColorVu 4MP 30m Turret Dome with Mic 2.8mm",
        "sku": "HI-IPC-T249HA-LU-2.8MM",
        "resolution": "4MP",
        "ir_color": "ColorVu 30m",
        "base": 60.95,
        "tier": "standard",
        "notes": "ColorVu colour at night, Motion 2.0",
    },
    "CAM-003": {
        "brand": "Hikvision",
        "name": "Hikvision IP Hybrid ColorVu 3.0 4MP 30m Turret Dome Mic/Speaker/Alarm 2.8mm",
        "sku": "HIK-DS-2CD2347G3-LIS2UY/SL-28",
        "resolution": "4MP",
        "ir_color": "ColorVu 3.0 30m",
        "base": 141.45,
        "tier": "premium",
        "notes": "ColorVu 3.0, mic+speaker, anti-corrosion",
    },
    "CAM-004": {
        "brand": "Hikvision",
        "name": "Hikvision IP Hybrid ColorVu 3.0 4K 8MP 30m Turret Dome Mic/Speaker/Alarm 2.8mm",
        "sku": "HIK-DS-2CD2387G3-LIS2UYSL-28",
        "resolution": "8MP 4K",
        "ir_color": "ColorVu 3.0 30m",
        "base": 193.20,
        "tier": "premium_4k",
        "notes": "4K ColorVu 3.0, NEMA4X, mic+speaker",
    },
}

# =====================================================================
# NVR — auto-picked by camera brand + camera count
# =====================================================================
NVR = {
    "NVR-H04": {"brand": "HiLook", "channels": 4, "name": "HiLook IP 4ch 4K NVR - 4 POE",
                "sku": "HI-NVR-104MH-C/4P", "base": 83.95},
    "NVR-H08": {"brand": "HiLook", "channels": 8, "name": "HiLook IP 8ch 4K NVR - 8 POE",
                "sku": "HI-NVR-108MH-C/8P", "base": 113.85},
    "NVR-H16": {"brand": "HiLook", "channels": 16, "name": "HiLook IP 16ch 4K NVR - 16 POE",
                "sku": "HI-NVR-216MH-C/16P", "base": 188.60},
    "NVR-K04": {"brand": "Hikvision", "channels": 4, "name": "Hikvision AcuSense 4ch 4K NVR - 4 POE",
                "sku": "HIK-DS-7604NXI-K1/4P", "base": 133.40},
    "NVR-K08": {"brand": "Hikvision", "channels": 8, "name": "Hikvision AcuSense 8ch 4K NVR - 8 POE",
                "sku": "HIK-DS-7608NXI-K1/8P", "base": 166.17},
    "NVR-K16": {"brand": "Hikvision", "channels": 16, "name": "Hikvision AcuSense 16ch 4K NVR - 16 POE",
                "sku": "HIK-DS-7616NXI-K2/16P", "base": 290.38},
}

# =====================================================================
# HDD — auto-picked by archive duration
# =====================================================================
HDD = {
    "HDD-1TB": {"name": "Toshiba S300 1TB Surveillance HDD", "sku": "TOS-HDD-1TB",
                "capacity": "1TB", "archive": "~1 week", "base": 74.75},
    "HDD-2TB": {"name": "Toshiba S300 2TB Surveillance HDD", "sku": "TOS-HDD-2TB",
                "capacity": "2TB", "archive": "~2 weeks", "base": 110.40},
    "HDD-4TB": {"name": "Toshiba S300 4TB Surveillance HDD", "sku": "TOS-HDD-4TB",
                "capacity": "4TB", "archive": "~1 month", "base": 156.97},
    "HDD-6TB": {"name": "Toshiba S300 6TB Surveillance HDD", "sku": "TOS-HDD-6TB",
                "capacity": "6TB", "archive": "~2 months", "base": 238.62},
}

# =====================================================================
# DEEP BASE — 1 per camera
# =====================================================================
DEEP_BASE = {
    "name": "Hikvision S Deep Base (DS-1280ZJ-S)",
    "sku": "HIK-DS-1280ZJ-S",
    "base": 18.00,
}

# =====================================================================
# INSTALLATION — by camera count (Min..Max range)
# =====================================================================
INSTALLATION = [
    {"min": 1,  "max": 2,  "desc": "Basic installation (1-2 cameras)",        "base": 200},
    {"min": 3,  "max": 3,  "desc": "Standard installation (3 cameras)",       "base": 220},
    {"min": 4,  "max": 5,  "desc": "Extended installation (4-5 cameras)",     "base": 350},
    {"min": 6,  "max": 6,  "desc": "Full installation (6 cameras)",           "base": 400},
    {"min": 7,  "max": 9,  "desc": "Large site (7-9 cameras)",                "base": 550},
    {"min": 10, "max": 12, "desc": "Commercial (10-12 cameras)",              "base": 800},
    {"min": 13, "max": 16, "desc": "Large commercial (13-16 cameras)",        "base": 1000},
]


# =====================================================================
# AUTO-SELECTION LOGIC
# =====================================================================

def pick_nvr(camera_count: int, brand: str) -> dict:
    """Pick NVR matching camera count and brand."""
    if camera_count <= 4:
        channels = 4
    elif camera_count <= 8:
        channels = 8
    else:
        channels = 16

    prefix = "NVR-K" if brand == "Hikvision" else "NVR-H"
    nvr_id = f"{prefix}{channels:02d}"
    return {"id": nvr_id, **NVR[nvr_id]}


def pick_hdd(archive_choice: str) -> dict:
    """archive_choice: '1_week' | '2_weeks' | '1_month' | '2_months'"""
    mapping = {
        "1_week":   "HDD-1TB",
        "2_weeks":  "HDD-2TB",
        "1_month":  "HDD-4TB",
        "2_months": "HDD-6TB",
    }
    hdd_id = mapping.get(archive_choice, "HDD-2TB")
    return {"id": hdd_id, **HDD[hdd_id]}


def pick_installation(camera_count: int) -> dict:
    """Pick installation tier by camera count range."""
    for tier in INSTALLATION:
        if tier["min"] <= camera_count <= tier["max"]:
            return tier
    # Fallback for >16 (shouldn't happen but be safe)
    return INSTALLATION[-1]


def pick_camera(tier: str) -> dict:
    """tier: 'basic' | 'standard' | 'premium' | 'premium_4k'"""
    for cam_id, cam in CAMERAS.items():
        if cam["tier"] == tier:
            return {"id": cam_id, **cam}
    # Default to standard
    return {"id": "CAM-002", **CAMERAS["CAM-002"]}


# =====================================================================
# QUOTE BUILDER
# =====================================================================

def build_quote(camera_count: int, camera_tier: str, archive_choice: str) -> dict:
    """
    Build full quote with all line items.
    Returns dict with items list + totals.

    Args:
        camera_count: 1-16
        camera_tier: 'basic' | 'standard' | 'premium' | 'premium_4k'
        archive_choice: '1_week' | '2_weeks' | '1_month' | '2_months'
    """
    camera = pick_camera(camera_tier)
    nvr = pick_nvr(camera_count, camera["brand"])
    hdd = pick_hdd(archive_choice)
    installation = pick_installation(camera_count)

    items = []

    # 1. Cameras
    items.append({
        "name": camera["name"],
        "sku": camera["sku"],
        "qty": camera_count,
        "base": camera["base"],
        "vat": round(camera["base"] * VAT_RATE, 2),
        "total": round(camera["base"] * (1 + VAT_RATE), 2),
    })

    # 2. NVR
    items.append({
        "name": nvr["name"],
        "sku": nvr["sku"],
        "qty": 1,
        "base": nvr["base"],
        "vat": round(nvr["base"] * VAT_RATE, 2),
        "total": round(nvr["base"] * (1 + VAT_RATE), 2),
    })

    # 3. HDD
    items.append({
        "name": hdd["name"],
        "sku": hdd["sku"],
        "qty": 1,
        "base": hdd["base"],
        "vat": round(hdd["base"] * VAT_RATE, 2),
        "total": round(hdd["base"] * (1 + VAT_RATE), 2),
    })

    # 4. Deep Base (1 per camera)
    items.append({
        "name": DEEP_BASE["name"],
        "sku": DEEP_BASE["sku"],
        "qty": camera_count,
        "base": DEEP_BASE["base"],
        "vat": round(DEEP_BASE["base"] * VAT_RATE, 2),
        "total": round(DEEP_BASE["base"] * (1 + VAT_RATE), 2),
    })

    # 5. Installation
    items.append({
        "name": "Installation CCTV",
        "sku": "",
        "qty": 1,
        "base": installation["base"],
        "vat": round(installation["base"] * VAT_RATE, 2),
        "total": round(installation["base"] * (1 + VAT_RATE), 2),
        "desc": installation["desc"],
    })

    # Totals
    subtotal_base = sum(item["base"] * item["qty"] for item in items)
    total_vat = sum(item["vat"] * item["qty"] for item in items)
    grand_total = subtotal_base + total_vat

    return {
        "items": items,
        "subtotal": round(subtotal_base, 2),
        "vat_total": round(total_vat, 2),
        "discount": 0.0,
        "grand_total": round(grand_total, 2),
        "currency": "GBP",
    }


# =====================================================================
# QUICK TEST
# =====================================================================
if __name__ == "__main__":
    # Test scenario from earlier conversation: 6 cameras, Hikvision ColorVu 4MP, 2 weeks
    quote = build_quote(camera_count=6, camera_tier="premium", archive_choice="2_weeks")

    print("=== QUOTE TEST: 6 cameras Hikvision premium, 2 weeks archive ===\n")
    for i, item in enumerate(quote["items"], 1):
        print(f"{i}. {item['name'][:55]}")
        print(f"   Qty: {item['qty']}  Base: £{item['base']}  VAT: £{item['vat']}  Line: £{item['base'] * item['qty']:.2f}")
    print()
    print(f"Subtotal: £{quote['subtotal']:.2f}")
    print(f"VAT 20%:  £{quote['vat_total']:.2f}")
    print(f"TOTAL:    £{quote['grand_total']:.2f}")
