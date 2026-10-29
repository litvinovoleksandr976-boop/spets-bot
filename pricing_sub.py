"""
SPETS SECURITY — Alarm SUBSCRIPTION pricing (rental model)
=====================================================================
  ★★★  ВСІ ЦІНИ ПІДПИСКИ — ТІЛЬКИ ТУТ. Міняєш цифру → бот рахує по-новому. ★★★
=====================================================================

Model:
  • Equipment stays the property of Spets Security.
  • Client pays a FIXED MONTHLY fee (service, support, repairs included).
  • One-off installation fee is paid once, at installation.

Monthly formula:
    devices  = BASE_KIT_MONTHLY + hub upgrade + sum(extra devices)
    overhead = devices × OVERHEAD_PCT        (SIM/mobile data, banking, monitoring co.)
    monthly  = devices + overhead            (ex VAT)
    VAT      = monthly × VAT_RATE
    monthly inc VAT = monthly + VAT

One-off:
    install inc VAT = INSTALL_FEE × (1 + VAT_RATE)
"""

# ---------------------------------------------------------------------------
# 1) GLOBAL SETTINGS  — міняти тут
# ---------------------------------------------------------------------------
VAT_RATE = 0.20          # 20% VAT
OVERHEAD_PCT = 0.35      # +35% зверху (зв'язок, банкінг, обслуговуюча компанія). 0.30–0.40
INSTALL_FEE = 90.00      # разова оплата за монтаж (ex VAT)
MIN_TERM_MONTHS = 36     # мінімальний строк договору (місяців) — УТОЧНИТИ з директором
NOTICE_DAYS = 30         # за скільки днів попереджати про розірвання
PRICE_ROUND = 0.50       # округлення місячної суми вгору до £0.50 (0 = без округлення)

# ---------------------------------------------------------------------------
# 2) BASE KIT  — входить за замовчуванням
# ---------------------------------------------------------------------------
BASE_KIT_VALUE = 380.00                 # вартість комплекту (для довідки/договору)
BASE_KIT_MONTHLY = 38.00                # = 380 / 10  (фіксовано, ex VAT)
BASE_KIT_CONTENTS = [                   # (кількість, назва) — показується в PDF і договорі
    (1, "Ajax Hub 2 (control panel, dual SIM + Ethernet)"),
    (2, "Ajax MotionProtect S (motion detector)"),
    (1, "Ajax DoorProtect S (door/window opening detector)"),
    (1, "Ajax StreetSiren DoubleDeck S (outdoor siren)"),
    (1, "Ajax HomeSiren S (indoor siren)"),
    (2, "Ajax SpaceControl S (keyfob)"),
]

# Ключі пристроїв базового комплекту (той самий порядок, що й BASE_KIT_CONTENTS) —
# потрібні для таблиці "Your system and what it costs" в PDF (offer_pack.py → DEVICE_INFO)
BASE_KIT_KEYS = [("hub2", 1), ("motion", 2), ("door", 1), ("siren_out", 1),
                 ("siren_in", 1), ("keyfob", 2)]

# ---------------------------------------------------------------------------
# 3) HUB OPTIONS  — доплата в місяць за апгрейд хаба (ex VAT)
#    Hub 2 вже в базовому комплекті → 0
# ---------------------------------------------------------------------------
HUBS = {
    "hub2":     {"name": "Ajax Hub 2 (included)",          "monthly": 0.00},
    "hub2plus": {"name": "Ajax Hub 2 Plus (Wi-Fi + 2 SIM)", "monthly": 9.00},
    "hubg3":    {"name": "Ajax Superior Hub G3 Jeweller",   "monthly": 18.50},
}

# ---------------------------------------------------------------------------
# 4) EXTRA DEVICES  — фіксована ціна В МІСЯЦЬ за 1 шт (ex VAT)
#    Правило: ціна пристрою ÷ 10, округлено. Міняти прямо тут.
# ---------------------------------------------------------------------------
EXTRAS = {
    "motion":    {"name": "Ajax MotionProtect S (motion detector)",        "monthly": 5.00},
    "combi":     {"name": "Ajax CombiProtect S (motion + glass break)",    "monthly": 9.00},
    "motioncam": {"name": "Ajax MotionCam S (motion detector with camera)", "monthly": 11.00},
    "door":      {"name": "Ajax DoorProtect S (door/window detector)",     "monthly": 4.50},
    "door_plus": {"name": "Ajax DoorProtect S Plus (door + shock + tilt)", "monthly": 5.50},
    "leak":      {"name": "Ajax LeaksProtect (water leak detector)",       "monthly": 5.00},
    "smoke":     {"name": "Ajax FireProtect 2 (smoke + heat detector)",    "monthly": 8.00},
    "smoke_co":  {"name": "Ajax FireProtect Plus (smoke + heat + CO)",     "monthly": 11.00},
    "siren_in":  {"name": "Ajax HomeSiren S (indoor siren)",               "monthly": 6.00},
    "siren_out": {"name": "Ajax StreetSiren DoubleDeck S (outdoor siren)", "monthly": 9.00},
    "keypad":    {"name": "Ajax KeyPad Plus S (wall keypad)",              "monthly": 10.00},
    "keyfob":    {"name": "Ajax SpaceControl S (keyfob)",                  "monthly": 4.00},
}

# Порядок кроків у боті (ключі з EXTRAS). Прибрав рядок → бот не питає.
EXTRA_STEPS = ["motion", "motioncam", "door", "leak", "smoke", "siren_in",
               "siren_out", "keypad", "keyfob"]

# Що входить у підписку (показується в PDF / договорі)
INCLUDED_SERVICES = [
    "All Ajax equipment listed (remains property of Spets Security Ltd)",
    "Professional installation and configuration",
    "SIM card / mobile data for the alarm hub",
    "Ajax app setup for the client's phones",
    "Remote support and system health monitoring",
    "Repair or replacement of faulty equipment at no extra cost",
    "Battery replacement",
    "Annual maintenance visit",
]


# ---------------------------------------------------------------------------
# CALCULATION  — зазвичай тут нічого міняти не треба
# ---------------------------------------------------------------------------
def _round_up(v: float) -> float:
    if not PRICE_ROUND:
        return round(v, 2)
    import math
    return round(math.ceil(v / PRICE_ROUND - 1e-9) * PRICE_ROUND, 2)


def build_subscription(hub: str = "hub2", extras: dict = None) -> dict:
    """
    hub    : key from HUBS
    extras : {extra_key: qty}
    Returns a dict used by the bot review screen, the PDF and KeyCRM.
    """
    extras = {k: int(v) for k, v in (extras or {}).items() if int(v) > 0 and k in EXTRAS}
    hub = hub if hub in HUBS else "hub2"

    lines = []  # monthly breakdown lines
    lines.append({"name": "Base alarm kit", "qty": 1,
                  "unit": BASE_KIT_MONTHLY, "total": BASE_KIT_MONTHLY})
    if HUBS[hub]["monthly"]:
        lines.append({"name": f"Hub upgrade — {HUBS[hub]['name']}", "qty": 1,
                      "unit": HUBS[hub]["monthly"], "total": HUBS[hub]["monthly"]})
    for key in EXTRAS:  # stable order
        if key in extras:
            u = EXTRAS[key]["monthly"]
            q = extras[key]
            lines.append({"name": EXTRAS[key]["name"], "qty": q,
                          "unit": u, "total": round(u * q, 2)})

    devices = round(sum(l["total"] for l in lines), 2)
    overhead = round(devices * OVERHEAD_PCT, 2)
    monthly_ex = _round_up(devices + overhead)
    monthly_vat = round(monthly_ex * VAT_RATE, 2)
    monthly_inc = round(monthly_ex + monthly_vat, 2)

    install_vat = round(INSTALL_FEE * VAT_RATE, 2)
    install_inc = round(INSTALL_FEE + install_vat, 2)

    # Full equipment list (base kit + hub swap + extras) for PDF/contract
    equipment = [list(x) for x in BASE_KIT_CONTENTS]
    if hub != "hub2":
        equipment[0] = [1, HUBS[hub]["name"]]
    for key in EXTRAS:
        if key in extras:
            equipment.append([extras[key], EXTRAS[key]["name"] + " — additional"])

    # Same list with device keys (for the offer-pack table)
    items = [{"key": k, "qty": q, "extra": False} for k, q in BASE_KIT_KEYS]
    if hub != "hub2":
        items[0] = {"key": hub, "qty": 1, "extra": False}
    for key in EXTRAS:
        if key in extras:
            items.append({"key": key, "qty": extras[key], "extra": True})

    return {
        "type": "subscription",
        "items": items,
        "hub": hub,
        "extras": extras,
        "lines": lines,
        "equipment": equipment,
        "devices_monthly": devices,
        "overhead": overhead,
        "monthly_ex_vat": monthly_ex,
        "monthly_vat": monthly_vat,
        "monthly_inc_vat": monthly_inc,
        "install_ex_vat": INSTALL_FEE,
        "install_vat": install_vat,
        "install_inc_vat": install_inc,
        "min_term": MIN_TERM_MONTHS,
        "notice_days": NOTICE_DAYS,
        "included": INCLUDED_SERVICES,
        # for admin/CRM (not shown to client)
        "grand_total": monthly_inc,
    }


if __name__ == "__main__":
    for hub, ex in [("hub2", {}), ("hub2", {"motion": 2, "door": 2}),
                    ("hubg3", {"motioncam": 2, "smoke": 1, "keypad": 1})]:
        s = build_subscription(hub, ex)
        print(hub, ex, "→ devices £%.2f + overhead £%.2f = £%.2f ex VAT | £%.2f inc VAT /mo | install £%.2f inc"
              % (s["devices_monthly"], s["overhead"], s["monthly_ex_vat"],
                 s["monthly_inc_vat"], s["install_inc_vat"]))
