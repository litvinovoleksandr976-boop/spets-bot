"""
SPETS SECURITY — Ajax Superior pricing module
Wireless-only (Jeweller / S-line Superior).
All ADK prices +15% markup for the client.
Install: £700 base (indicative, varies by job & materials).
"""

MARKUP = 1.15
INSTALL_BASE = 700.00  # indicative, varies by scope/materials

# Note shown under the install line on every Ajax quote
INSTALL_NOTE = (
    "Installation £700 is indicative. The final price depends on the scope of "
    "work, site complexity and materials required, and is confirmed after a "
    "site survey."
)


def _client(adk: float) -> float:
    """ADK price -> client price (+15%), rounded to 2dp."""
    return round(adk * MARKUP, 2)


# ---------------------------------------------------------------------------
# INDIVIDUAL COMPONENTS  (build-your-own)
# key: (name, ADK model/line, ADK price £, category)
# ---------------------------------------------------------------------------
COMPONENTS = {
    # ---- HUBS ----
    "hub2": {
        "name": "Ajax Hub 2",
        "model": "Surveillance Control Panel, dual GSM + Ethernet",
        "adk": 113.00, "category": "hub",
    },
    "hub2plus": {
        "name": "Ajax Hub 2 Plus",
        "model": "Surveillance Control Panel, dual GSM + WiFi + Ethernet",
        "adk": 191.50, "category": "hub",
    },
    "hubg3": {
        "name": "Ajax Superior Hub G3 Jeweller",
        "model": "S-line wireless control panel",
        "adk": 274.50, "category": "hub",
    },

    # ---- MOTION ----
    "motion_s": {
        "name": "Ajax Superior MotionProtect S",
        "model": "Pet-tolerant wireless PIR",
        "adk": 43.50, "category": "motion",
    },
    "combi_s": {
        "name": "Ajax Superior CombiProtect S",
        "model": "PIR + glass-break, wireless",
        "adk": 76.50, "category": "motion",
    },

    # ---- MOTION + CAMERA ----
    "motioncam_s": {
        "name": "Ajax Superior MotionCam S Outdoor",
        "model": "Wireless camera PIR, outdoor",
        "adk": 95.00, "category": "motioncam",
    },

    # ---- DOOR ----
    "door_s": {
        "name": "Ajax Superior DoorProtect S",
        "model": "Wireless door contact",
        "adk": 39.00, "category": "door",
    },
    "door_s_plus": {
        "name": "Ajax Superior DoorProtect S Plus",
        "model": "Shock + tilt + door contact, wireless",
        "adk": 49.50, "category": "door",
    },

    # ---- LEAK ----
    "leak": {
        "name": "Ajax LeaksProtect",
        "model": "Wireless flood detector",
        "adk": 44.00, "category": "leak",
    },

    # ---- SMOKE ----
    "smoke_rb": {
        "name": "Ajax Superior FireProtect 2 RB",
        "model": "Smoke detector, wireless (battery)",
        "adk": 68.50, "category": "smoke",
    },
    "smoke_sb": {
        "name": "Ajax FireProtect 2 SB",
        "model": "Smoke + heat detector, wireless",
        "adk": 78.00, "category": "smoke",
    },
    "smoke_plus": {
        "name": "Ajax FireProtect Plus",
        "model": "CO + smoke + heat detector, wireless",
        "adk": 95.00, "category": "smoke",
    },

    # ---- INDOOR SIREN ----
    "siren_in": {
        "name": "Ajax Superior HomeSiren S",
        "model": "Wireless internal sounder",
        "adk": 53.50, "category": "siren_indoor",
    },

    # ---- OUTDOOR SIREN ----
    "siren_out_dd": {
        "name": "Ajax Superior StreetSiren DoubleDeck S",
        "model": "Wireless outdoor sounder",
        "adk": 78.00, "category": "siren_outdoor",
    },
    "siren_out_jew": {
        "name": "Ajax Superior StreetSiren Jeweller",
        "model": "Wireless external siren",
        "adk": 134.00, "category": "siren_outdoor",
    },

    # ---- KEYPAD ----
    "keypad_s": {
        "name": "Ajax Superior KeyPad Plus S",
        "model": "Wireless prox arming station",
        "adk": 85.50, "category": "keypad",
    },
    "keypad_g3": {
        "name": "Ajax Superior KeyPad Plus G3 Jeweller",
        "model": "Wireless keypad",
        "adk": 94.00, "category": "keypad",
    },

    # ---- KEYFOB ----
    "keyfob_s": {
        "name": "Ajax Superior SpaceControl S",
        "model": "Wireless keyfob",
        "adk": 36.00, "category": "keyfob",
    },
}


# ---------------------------------------------------------------------------
# READY KITS  (Budget / Balance / Elite) — all wireless Ajax Superior
# ---------------------------------------------------------------------------
KITS = {
    "budget": {
        "tier": "Budget",
        "name": "Ajax Superior Wireless Alarm Kit 1 S",
        "adk_ref": "AJA-90763 (White)",
        "adk": 280.00,
        "contents": [
            ("Ajax Hub 2", 1),
            ("Ajax Superior MotionProtect S", 2),
            ("Ajax Superior DoorProtect S", 1),
            ("Ajax SpaceControl Keyfob", 2),
            ("Ajax StreetSiren", 1),
        ],
    },
    "balance": {
        "tier": "Balance",
        "name": "Ajax Superior Wireless Alarm Kit 6 S",
        "adk_ref": "AJA-90773 (White)",
        "adk": 373.50,
        "contents": [
            ("Ajax Hub 2", 1),
            ("Ajax Superior MotionCam S (camera PIR)", 2),
            ("Ajax Superior DoorProtect S", 1),
            ("Ajax SpaceControl Keyfob", 2),
            ("Ajax StreetSiren", 1),
        ],
    },
    "elite": {
        "tier": "Elite",
        "name": "Ajax Superior Hub2 Plus Wireless Alarm Kit 15 S",
        "adk_ref": "AJA-109852 (White)",
        "adk": 466.00,
        "contents": [
            ("Ajax Hub 2 Plus", 1),
            ("Ajax Superior MotionCam S (camera PIR)", 2),
            ("Ajax Superior DoorProtect S", 1),
            ("Ajax Superior KeyPad Plus S", 1),
            ("Ajax StreetSiren", 1),
        ],
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def component_client_price(key: str) -> float:
    return _client(COMPONENTS[key]["adk"])


def kit_client_price(tier: str) -> float:
    return _client(KITS[tier]["adk"])


def components_by_category(category: str) -> dict:
    """All component keys of a given category."""
    return {k: v for k, v in COMPONENTS.items() if v["category"] == category}


def build_custom_quote(selections: dict, with_install: bool = True) -> dict:
    """
    selections = { component_key: qty, ... }
    Returns a quote dict ready for the PDF generator.
    """
    line_items = []
    equipment_total = 0.0
    for key, qty in selections.items():
        if qty <= 0 or key not in COMPONENTS:
            continue
        comp = COMPONENTS[key]
        unit = _client(comp["adk"])
        line_total = round(unit * qty, 2)
        equipment_total += line_total
        line_items.append({
            "key": key,
            "name": comp["name"],
            "model": comp["model"],
            "qty": qty,
            "unit_price": unit,
            "line_total": line_total,
        })

    install = INSTALL_BASE if with_install else 0.0
    subtotal = round(equipment_total + install, 2)
    vat = round(subtotal * 0.20, 2)
    grand = round(subtotal + vat, 2)

    return {
        "type": "ajax_custom",
        "line_items": line_items,
        "equipment_total": round(equipment_total, 2),
        "install": install,
        "install_note": INSTALL_NOTE,
        "subtotal": subtotal,
        "vat": vat,
        "grand_total": grand,
    }


def build_kit_quote(tier: str, with_install: bool = True) -> dict:
    """Ready-kit quote for a tier (budget/balance/elite)."""
    kit = KITS[tier]
    equipment = _client(kit["adk"])
    install = INSTALL_BASE if with_install else 0.0
    subtotal = round(equipment + install, 2)
    vat = round(subtotal * 0.20, 2)
    grand = round(subtotal + vat, 2)

    return {
        "type": "ajax_kit",
        "tier": kit["tier"],
        "kit_name": kit["name"],
        "adk_ref": kit["adk_ref"],
        "contents": kit["contents"],
        "equipment_total": equipment,
        "install": install,
        "install_note": INSTALL_NOTE,
        "subtotal": subtotal,
        "vat": vat,
        "grand_total": grand,
    }


if __name__ == "__main__":
    # quick self-test
    print("=== KITS (client +15%, +£700 install, +20% VAT) ===")
    for t in ("budget", "balance", "elite"):
        q = build_kit_quote(t)
        print(f"{q['tier']:8} equip £{q['equipment_total']:.2f} "
              f"+ install £{q['install']:.0f} + VAT £{q['vat']:.2f} "
              f"= £{q['grand_total']:.2f}")

    print("\n=== CUSTOM example: Hub2 + 3 motion + 1 door + outdoor siren ===")
    sel = {"hub2": 1, "motion_s": 3, "door_s": 1, "siren_out_dd": 1}
    q = build_custom_quote(sel)
    for li in q["line_items"]:
        print(f"  {li['qty']}x {li['name']:42} £{li['unit_price']:.2f} = £{li['line_total']:.2f}")
    print(f"  Equipment £{q['equipment_total']:.2f} + Install £{q['install']:.0f} "
          f"+ VAT £{q['vat']:.2f} = £{q['grand_total']:.2f}")


# ---------------------------------------------------------------------------
# Device descriptions for the quote (EN). Same install pattern for all:
# mounted at ~2 m, two dowel holes, fully wireless, battery once a year.
# ---------------------------------------------------------------------------
BASE_INSTALL_LINE = ("Mounted at ~2 m height with two dowel holes. Fully "
                     "wireless — battery replacement about once a year.")

DESCRIPTIONS = {
    "hub2":        "Control panel — the brain of the system. Connects all wireless devices and communicates via dual GSM + Ethernet.",
    "hub2plus":    "Advanced control panel with dual GSM + Wi-Fi + Ethernet for maximum connection reliability.",
    "hubg3":       "Superior S-line control panel (Jeweller) for larger or more demanding installations.",
    "motion_s":    "Wireless motion detector, pet-immune. " + BASE_INSTALL_LINE,
    "combi_s":     "Wireless combined motion + glass-break detector. " + BASE_INSTALL_LINE,
    "motioncam_s": "Wireless outdoor motion detector with a built-in camera — sends photos on alarm. " + BASE_INSTALL_LINE,
    "door_s":      "Wireless door/window opening detector. " + BASE_INSTALL_LINE,
    "door_s_plus": "Wireless opening detector with shock + tilt sensing. " + BASE_INSTALL_LINE,
    "leak":        "Wireless flood/leak detector — place on the floor where leaks may occur. Battery lasts about a year.",
    "smoke_rb":    "Wireless smoke detector. Mounted on the ceiling. Fully wireless — battery once a year.",
    "smoke_sb":    "Wireless smoke + heat detector. Mounted on the ceiling. Fully wireless — battery once a year.",
    "smoke_plus":  "Wireless CO + smoke + heat detector. Mounted on the ceiling. Fully wireless — battery once a year.",
    "siren_in":    "Wireless indoor siren. Mounted on the wall, two dowel holes. Fully wireless — battery once a year.",
    "siren_out_dd":"Wireless outdoor siren. Mounted on an external wall, two dowel holes. Fully wireless — battery once a year.",
    "siren_out_jew":"Wireless external siren (Jeweller). Mounted on an external wall, two dowel holes. Fully wireless.",
    "keypad_s":    "Wireless keypad with proximity tags to arm/disarm the system. Mounted on the wall, two dowel holes.",
    "keypad_g3":   "Wireless Superior keypad (G3 Jeweller) to arm/disarm the system. Mounted on the wall.",
    "keyfob_s":    "Wireless keyfob to arm/disarm the system from your pocket. No installation required.",
}


def component_description(key: str) -> str:
    return DESCRIPTIONS.get(key, "")
