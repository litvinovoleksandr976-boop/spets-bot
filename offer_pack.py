"""
SPETS SECURITY — SUBSCRIPTION OFFER PACK (6 pages, dark style, EN / RU / UK)
=====================================================================
  1  What your monthly fee covers
  2  Your system and what it costs   ← equipment + prices of THIS client
  3  Equipment, damage and call-outs
  4  The agreement you will sign     ← name, address, prices of THIS client
  5  What each side promises + signatures
  6  UK standards and compliance

  Тексти всіх сторінок (3 мови) → offer_texts.py
  Дані, яких ще бракує ([X] / £XX) → OFFER_CONFIG нижче (None = "[X]" у PDF)
  Мова = мова, яку клієнт обрав у боті. Для ru/uk в кінець додається англійська
  версія (вона має юридичну силу) — APPEND_ENGLISH.
=====================================================================
"""
import io
import os

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color

import pricing_sub as ps
from offer_texts import T

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 595.5, 842.25

APPEND_ENGLISH = True   # ru/uk PDF + англійська версія в кінці

# ---------------------------------------------------------------------------
# ★ CONFIG — заповнити, коли будуть дані (None → у PDF буде "[X]")
# ---------------------------------------------------------------------------
OFFER_CONFIG = {
    "website": "spetstech.co.uk",
    "phone": "+44 7706 906079",
    "email": "r.brain@spetstech.co.uk",
    "company_address": "1 Oakcroft Road, Chessington, Surrey KT9 1BD",
    "footer_line": "SPETS Security Ltd · 1 Oakcroft Road, Chessington, Surrey KT9 1BD",

    # page 2
    "deposit": None,             # £ депозит за обладнання; None → "None/Немає"
    "camera_monthly": None,      # £/міс за камеру Hikvision; None → "on request"
    "arc_monthly": None,         # £/міс пульт ARC з виїздом; None → "on request"

    # page 3 — платні виїзди (£ без ПДВ)
    "rate_callout": None,        # Standard call-out Mon–Fri 08–18
    "rate_out_of_hours": None,   # Evenings, weekends, bank holidays
    "rate_emergency": None,      # Emergency same-day
    "rate_extra_hour": None,     # Extra labour per hour
    "rate_missed": None,         # Missed appointment < 24h

    # page 4
    "company_no": None,          # Companies House number
    "dd_day": 1,                 # день списання Direct Debit
    "early_exit_pct": None,      # None → платяться залишкові місяці
    "removal_days": 30,
    "price_review_days": 30,
    "late_days": 14,

    # page 5
    "liability_millions": None,  # страховка відповідальності, £ млн (напр. 5)
    "records_years": None,       # скільки років зберігаємо записи
    "images_days": None,         # скільки днів зберігаємо фото тривог (у дизайні було [30])
    "complaint_ack_days": None,  # підтвердження скарги, робочих днів (було [2])
    "complaint_answer_days": None,  # відповідь на скаргу, днів (було [10])
    "complaints_scheme": None,   # напр. "the NSI complaints scheme"

    # page 6 — реквізити
    "vat": "GB 455026800",
    "inspectorate": None,        # "NSI Gold, ref ..." / "SSAIB, ref ..."
    "ico": None,                 # ICO registration number
    "arc_name": None,            # alarm receiving centre (BS EN 50518)
}

PLACEHOLDER_SCHEME = {"en": "[your inspectorate body's complaints scheme]",
                      "ru": "[схему жалоб вашего инспекционного органа]",
                      "uk": "[схему скарг вашого інспекційного органу]"}
MILLION = {"en": "million", "ru": "млн", "uk": "млн"}

# ---------------------------------------------------------------------------
# fonts / colours
# ---------------------------------------------------------------------------
_FONTS = False
FONT_FILES = {"R": "Inter-Regular.ttf", "M": "Inter-Medium.ttf", "SB": "Inter-SemiBold.ttf",
              "B": "Inter-Bold.ttf", "DB": "InterDisplay-Bold.ttf"}


def _fonts():
    global _FONTS
    if not _FONTS:
        for k, f in FONT_FILES.items():
            pdfmetrics.registerFont(TTFont("of" + k, os.path.join(HERE, f)))
        _FONTS = True


def F(k):
    return "of" + k


def C(r, g, b, a=1.0):
    return Color(r / 255, g / 255, b / 255, alpha=a)


WHITE = C(255, 255, 255)
TXT = C(212, 212, 216)
MUTED = C(160, 160, 166)
LABEL = C(203, 203, 208)
DIV = C(52, 52, 56)
RED = C(233, 32, 38)
CARD = C(30, 30, 33, 0.72)
CARD_STROKE = C(62, 62, 68)
RED_CARD = C(70, 12, 15, 0.70)
RED_STROKE = C(150, 28, 34)


def available() -> bool:
    need = ["offer_bg.jpg"] + list(FONT_FILES.values())
    return all(os.path.exists(os.path.join(HERE, f)) for f in need)


# ---------------------------------------------------------------------------
# drawing helpers (top = distance from the top of the page, in pt)
# ---------------------------------------------------------------------------
def Y(top):
    return PH - top


def sw(text, font, size):
    return pdfmetrics.stringWidth(text, F(font), size)


def wrap(text, font, size, width):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if sw(t, font, size) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(c, x, base, s, font, size, color, align="l"):
    c.setFont(F(font), size)
    c.setFillColor(color)
    if align == "r":
        c.drawRightString(x, Y(base), s)
    elif align == "c":
        c.drawCentredString(x, Y(base), s)
    else:
        c.drawString(x, Y(base), s)


def spaced(c, x, base, s, font, size, color, sp=1.6, align="l"):
    w = sw(s, font, size) + sp * (len(s) - 1)
    if align == "r":
        x -= w
    t = c.beginText(x, Y(base))
    t.setFont(F(font), size)
    t.setFillColor(color)
    t.setCharSpace(sp)
    t.textLine(s)
    t.setCharSpace(0)
    c.drawText(t)


def para(c, x, top, width, s, font, size, color, lead=None, draw=True):
    """Draws wrapped text; first baseline = top + size. Returns bottom (top of next line)."""
    lead = lead or size * 1.42
    lines = wrap(s, font, size, width)
    if draw:
        for i, ln in enumerate(lines):
            text(c, x, top + size + i * lead, ln, font, size, color)
    return top + len(lines) * lead + (lead - size) * 0.2


def rich(c, x, top, width, runs, size, lead=None, draw=True):
    """runs = [(text, font, color), ...] — wrapped together. Returns bottom."""
    lead = lead or size * 1.42
    toks = []
    for s, fnt, col in runs:
        for w in s.split():
            toks.append((w, fnt, col))
    lines, cur, curw = [], [], 0.0
    space = sw(" ", "R", size)
    for w, fnt, col in toks:
        ww = sw(w, fnt, size)
        if cur and curw + space + ww > width:
            lines.append(cur)
            cur, curw = [], 0.0
        curw += (space if cur else 0) + ww
        cur.append((w, fnt, col, ww))
    if cur:
        lines.append(cur)
    if draw:
        for i, ln in enumerate(lines):
            xx = x
            for w, fnt, col, ww in ln:
                text(c, xx, top + size + i * lead, w, fnt, size, col)
                xx += ww + space
    return top + len(lines) * lead + (lead - size) * 0.2


def box(c, x, top, w, h, fill=CARD, stroke=CARD_STROKE, r=6, draw=True):
    if draw:
        c.setFillColor(fill)
        c.setStrokeColor(stroke)
        c.setLineWidth(0.7)
        c.roundRect(x, Y(top + h), w, h, r, stroke=1, fill=1)


def check_icon(c, cx, ctop, r=7.5, bg=RED, mark=WHITE, cross=False):
    cy = Y(ctop + r)
    c.setFillColor(bg)
    c.circle(cx + r, cy, r, stroke=0, fill=1)
    c.setStrokeColor(mark)
    c.setLineWidth(1.5)
    c.setLineCap(1)
    if cross:
        d = r * 0.38
        c.line(cx + r - d, cy - d, cx + r + d, cy + d)
        c.line(cx + r - d, cy + d, cx + r + d, cy - d)
    else:
        p = c.beginPath()
        p.moveTo(cx + r * 0.55, cy + r * 0.02)
        p.lineTo(cx + r * 0.88, cy - r * 0.32)
        p.lineTo(cx + r * 1.45, cy + r * 0.36)
        c.drawPath(p, stroke=1, fill=0)
    c.setLineCap(0)


def grad_bar(c, x, top, w, h, a=(244, 244, 244), b=(199, 199, 201), draw=True):
    if not draw:
        return
    n = 40
    for i in range(n):
        f = i / (n - 1)
        c.setFillColor(C(*[a[k] + (b[k] - a[k]) * f for k in range(3)]))
        c.rect(x + w * i / n, Y(top + h), w / n + 0.6, h, stroke=0, fill=1)


def page_frame(c, D, n, footer_left, draw=True):
    """background + header + footer."""
    if not draw:
        return
    c.drawImage(ImageReader(os.path.join(HERE, "offer_bg.jpg")), 0, 0, PW, PH)
    spaced(c, 562, 47.5, D["labels"][n], "B", 8.0, LABEL, 1.8, align="r")
    text(c, 562, 59.5, f"{OFFER_CONFIG['website']} · {OFFER_CONFIG['phone']}", "R", 8.2, MUTED, "r")
    c.setStrokeColor(DIV)
    c.setLineWidth(0.6)
    c.line(33, Y(82), 563, Y(82))
    c.line(33, Y(800), 563, Y(800))
    fl = footer_left if sw(footer_left, "R", 7.8) < 470 else footer_left[:110] + "…"
    text(c, 33, 816, fl, "R", 7.8, MUTED)
    text(c, 562, 816, f"{n} / 6", "B", 8.4, WHITE, "r")


def title_block(c, D, key_t, key_i, s, draw=True, width=500):
    if draw:
        text(c, 33, 124, D[key_t], "DB", 25 * s if sw(D[key_t], "DB", 25 * s) < 530 else 22 * s, WHITE)
    return para(c, 33, 134, width, D[key_i], "R", 10.2 * s, TXT, draw=draw) + 6


def fmt_money(v):
    return f"£{v:,.2f}"


# ---------------------------------------------------------------------------
# values for placeholders
# ---------------------------------------------------------------------------
def values(lang, sub, cust):
    cfg = OFFER_CONFIG
    D = T[lang]
    ph = lambda v, f="{}": f.format(v) if v not in (None, "") else None
    v = {
        "phone": cfg["phone"], "email": cfg["email"],
        "liability": ph(cfg["liability_millions"], "£{} " + MILLION[lang]) or f"£[X] {MILLION[lang]}",
        "records_years": ph(cfg["records_years"]) or "[X]",
        "images_days": ph(cfg["images_days"]) or "[30]",
        "ack_days": ph(cfg["complaint_ack_days"]) or "[2]",
        "answer_days": ph(cfg["complaint_answer_days"]) or "[10]",
        "scheme": cfg["complaints_scheme"] or PLACEHOLDER_SCHEME[lang],
    }
    if sub:
        exit_txt = (D["p4_exit"] if not cfg["early_exit_pct"]
                    else D["p4_exit_pct"].format(pct=cfg["early_exit_pct"]))
        v.update({
            "company_no": cfg["company_no"] or "[XXXXXXXX]",
            "company_address": cfg["company_address"],
            "customer": (cust or {}).get("name") or D["p4_customer_default"],
            "address_part": f", {cust['address']}" if (cust or {}).get("address") else "",
            "monthly": fmt_money(sub["monthly_ex_vat"]), "monthly_inc": fmt_money(sub["monthly_inc_vat"]),
            "dd_day": D["dd_day"](int(cfg["dd_day"])), "setup": fmt_money(sub["install_ex_vat"]),
            "term": sub["min_term"], "notice": sub["notice_days"], "exit": exit_txt,
            "removal_days": cfg["removal_days"], "price_review_days": cfg["price_review_days"],
            "late_days": cfg["late_days"],
        })
    return v


# ---------------------------------------------------------------------------
# PAGE 1
# ---------------------------------------------------------------------------
def p1(c, D, V, ctx, s, draw):
    page_frame(c, D, 1, OFFER_CONFIG["footer_line"], draw)
    y = title_block(c, D, "p1_title", "p1_intro", s, draw) + 10 * s
    gap, cols = 10, 3
    cw = (530 - gap * (cols - 1)) / cols
    pad = 11 * s
    cards = D["p1_cards"]
    for r in range(0, len(cards), cols):
        row = cards[r:r + cols]
        hs = []
        for t, b in row:
            h = pad + 15 * s + 6 * s
            h = para(c, 0, h, cw - 2 * pad, t, "B", 10.6 * s, WHITE, draw=False)
            h = para(c, 0, h + 3 * s, cw - 2 * pad, b, "R", 9.1 * s, TXT, draw=False)
            hs.append(h + pad)
        rh = max(hs)
        for i, (t, b) in enumerate(row):
            x = 33 + i * (cw + gap)
            box(c, x, y, cw, rh, draw=draw)
            if draw:
                check_icon(c, x + pad, y + pad, 7.5 * s)
            yy = para(c, x + pad, y + pad + 15 * s + 6 * s, cw - 2 * pad, t, "B", 10.6 * s, WHITE, draw=draw)
            para(c, x + pad, yy + 3 * s, cw - 2 * pad, b, "R", 9.1 * s, TXT, draw=draw)
        y += rh + gap
    # also included
    runs = [(D["p1_also_lead"], "B", WHITE), (D["p1_also"], "R", TXT)]
    h = rich(c, 0, 0, 530 - 24, runs, 8.8 * s, draw=False) + 20
    y += 4
    box(c, 33, y, 530, h, fill=RED_CARD, stroke=RED_STROKE, draw=draw)
    rich(c, 45, y + 9, 530 - 24, runs, 8.8 * s, draw=draw)
    return y + h


# ---------------------------------------------------------------------------
# PAGE 2 (dynamic)
# ---------------------------------------------------------------------------
def p2(c, D, V, ctx, s, draw):
    sub, cust, ref, date = ctx["sub"], ctx["cust"], ctx["ref"], ctx["date"]
    cfg = OFFER_CONFIG
    page_frame(c, D, 2, D["p2_footer"], draw)
    y = title_block(c, D, "p2_title", "p2_intro", s, draw, width=480) + 4
    # prepared for
    who = " · ".join(x for x in [cust.get("name"), cust.get("address")] if x)
    if draw:
        spaced(c, 33, y + 8, D["p2_prepared"], "B", 7.4, RED, 1.5)
        lw = sw(D["p2_prepared"], "B", 7.4) + 1.5 * len(D["p2_prepared"]) + 8
        text(c, 33 + lw, y + 8, who[:88], "M", 8.6, WHITE)
        text(c, 562, y + 8, f"Ref #{ref} · {date.strftime('%d.%m.%Y')}", "R", 8.0, MUTED, "r")
    top = y + 16
    # table
    rows = []
    for it in sub["items"]:
        name, desc = D["devices"].get(it["key"], (it["key"], ""))
        rows.append((("+ " if it["extra"] else "") + name, str(it["qty"]), desc))
    rows.append((D["p2_app"][0], "—", D["p2_app"][1]))
    head_h = 26
    area = 530 - (top + head_h)
    rh = max(20.0, min(38.0, area / len(rows)))
    ds = 8.5 if rh >= 29 else 7.6
    grad_bar(c, 33, top, 530, head_h, draw=draw)
    if draw:
        dk = C(20, 20, 22)
        spaced(c, 45, top + 17, D["p2_th"][0], "B", 8.2, dk, 0.6)
        tw = sw(D["p2_th"][1], "B", 8.2) + 0.6 * (len(D["p2_th"][1]) - 1)
        spaced(c, 262 - tw / 2, top + 17, D["p2_th"][1], "B", 8.2, dk, 0.6)
        spaced(c, 296, top + 17, D["p2_th"][2], "B", 8.2, dk, 0.6)
    yy = top + head_h
    for i, (name, qty, desc) in enumerate(rows):
        if draw:
            c.setFillColor(C(24, 24, 26, 0.84) if i % 2 == 0 else C(17, 17, 19, 0.84))
            c.rect(33, Y(yy + rh), 530, rh, stroke=0, fill=1)
            c.setStrokeColor(C(42, 42, 46))
            c.setLineWidth(0.5)
            c.line(33, Y(yy + rh), 563, Y(yy + rh))
            mid = yy + rh / 2
            nsz = 9.6 if rh >= 29 else 8.8
            nl = wrap(name, "B", nsz, 200)[:2]
            for j, ln in enumerate(nl):
                text(c, 45, mid + 3.4 + (j - (len(nl) - 1) / 2) * (nsz + 2), ln, "B", nsz, WHITE)
            text(c, 262, mid + 3.8, qty, "B", 10.5, WHITE, "c")
            lines = wrap(desc, "R", ds, 258)[: (2 if rh >= 25 else 1)]
            lh = ds + 3.1
            y0 = mid - (len(lines) * lh) / 2 + ds - 0.6
            for j, ln in enumerate(lines):
                text(c, 296, y0 + j * lh, ln, "R", ds, TXT)
        yy += rh
    # price box
    by, bh = 543, 92
    if draw:
        n = 60
        for i in range(n):
            f = i / (n - 1)
            c.setFillColor(C(233 - 90 * f, 32 - 16 * f, 38 - 17 * f))
            c.rect(33 + 265 * i / n, Y(by + bh), 265 / n + 0.6, bh, stroke=0, fill=1)
        spaced(c, 47, by + 20, D["p2_monthly"], "B", 8.0, C(255, 222, 222), 1.6)
        price = fmt_money(sub["monthly_ex_vat"])
        text(c, 46, by + 53, price, "DB", 29, WHITE)
        text(c, 50 + sw(price, "DB", 29), by + 52, D["p2_per_month"], "B", 9.6, WHITE)
        text(c, 47, by + 68, D["p2_inc1"].format(inc=fmt_money(sub["monthly_inc_vat"])), "R", 8.3, C(255, 226, 226))
        text(c, 47, by + 80, D["p2_inc2"], "R", 8.3, C(255, 226, 226))
        box(c, 313, by, 250, bh, fill=C(16, 16, 18, 0.86), stroke=C(58, 58, 62), r=5)
        dep = cfg["deposit"]
        vals = [f"{fmt_money(sub['install_ex_vat'])} + {D['vat']}", D["p2_months"].format(n=sub["min_term"]),
                D["p2_dd"], fmt_money(dep) if dep else D["p2_none"]]
        for i, (l, v) in enumerate(zip(D["p2_details"], vals)):
            text(c, 327, by + 23 + i * 19, l, "R", 9.0, TXT)
            text(c, 549, by + 23 + i * 19, v, "B", 9.0, WHITE, "r")
        # add-ons
        spaced(c, 33, 660, D["p2_addons_title"], "B", 8.2, LABEL, 1.5)
        E = ps.EXTRAS
        pm = lambda v: f"£{v:.2f} {D['p2_month']}" if v else D["p2_on_request"]
        prices = [pm(E["motioncam"]["monthly"]), pm(E["door"]["monthly"]), pm(E["smoke"]["monthly"]),
                  pm(E["leak"]["monthly"]), pm(cfg["camera_monthly"]), pm(cfg["arc_monthly"])]
        for i, (l, v) in enumerate(zip(D["p2_addons"], prices)):
            col, row = i % 2, i // 2
            x0, x1 = (33, 290) if col == 0 else (305, 562)
            yy = 682 + row * 22
            lab = l if sw(l, "R", 8.4) + sw(v, "B", 8.4) < 248 else wrap(l, "R", 8.4, 248 - sw(v, "B", 8.4))[0] + "…"
            text(c, x0, yy, lab, "R", 8.4, TXT)
            text(c, x1, yy, v, "B", 8.4, WHITE, "r")
            c.setStrokeColor(DIV)
            c.setLineWidth(0.5)
            c.line(x0, Y(yy + 8), x1, Y(yy + 8))
    return 760


# ---------------------------------------------------------------------------
# PAGE 3
# ---------------------------------------------------------------------------
def p3(c, D, V, ctx, s, draw):
    cfg = OFFER_CONFIG
    page_frame(c, D, 3, D["p3_footer"], draw)
    y = title_block(c, D, "p3_title", "p3_intro", s, draw) + 6 * s
    cw = (530 - 10) / 2
    pad = 11 * s
    hh = 24 * s
    fs = 8.6 * s

    def list_h(items, draw_, x, top):
        yy = top
        for it in items:
            yy = para(c, x, yy, cw - 2 * pad, it, "R", fs, TXT, lead=fs * 1.36, draw=draw_) + 5.2 * s
        return yy
    h = max(list_h(D["p3_cov"], False, 0, 0), list_h(D["p3_chg"], False, 0, 0)) + hh + pad + 4
    for i, (tkey, items, red) in enumerate([("p3_cov_title", D["p3_cov"], False),
                                             ("p3_chg_title", D["p3_chg"], True)]):
        x = 33 + i * (cw + 10)
        box(c, x, y, cw, h, fill=RED_CARD if red else CARD, stroke=RED_STROKE if red else CARD_STROKE, draw=draw)
        if draw:
            c.setFillColor(C(120, 20, 24, 0.55) if red else C(48, 48, 52, 0.8))
            c.rect(x + 0.4, Y(y + hh), cw - 0.8, hh - 0.4, stroke=0, fill=1)
            check_icon(c, x + pad, y + hh / 2 - 6.5 * s, 6.5 * s, bg=RED if red else WHITE,
                       mark=WHITE if red else C(20, 20, 22), cross=red)
            text(c, x + pad + 19 * s, y + hh / 2 + 3.4 * s, D[tkey], "B", 9.4 * s, WHITE)
        list_h(items, draw, x + pad, y + hh + pad)
    y += h + 12 * s
    # rates
    th = 24 * s
    grad_bar(c, 33, y, 530, th, draw=draw)
    if draw:
        spaced(c, 45, y + th / 2 + 3.2 * s, D["p3_rates_title"], "B", 8.4 * s, C(20, 20, 22), 0.6)
        spaced(c, 551, y + th / 2 + 3.2 * s, D["p3_rate_col"], "B", 8.4 * s, C(20, 20, 22), 0.6, align="r")
    y += th
    rkeys = ["rate_callout", "rate_out_of_hours", "rate_emergency", "rate_extra_hour", None, "rate_missed"]
    rr = 22 * s
    for i, (lab, k) in enumerate(zip(D["p3_rates"], rkeys)):
        if draw:
            c.setFillColor(C(22, 22, 24, 0.8))
            c.rect(33, Y(y + rr), 530, rr, stroke=0, fill=1)
            c.setStrokeColor(C(42, 42, 46))
            c.setLineWidth(0.5)
            c.line(33, Y(y + rr), 563, Y(y + rr))
            val = D["p3_list_price"] if k is None else (
                f"£{cfg[k]:.2f} + {D['vat']}" if cfg[k] not in (None, "") else f"£XX.00 + {D['vat']}")
            text(c, 45, y + rr / 2 + 3.2 * s, lab, "R", 8.8 * s, TXT)
            text(c, 551, y + rr / 2 + 3.2 * s, val, "B", 8.8 * s, WHITE, "r")
        y += rr
    y += 12 * s
    # ask + owns
    lw = 255
    yl = y
    if draw:
        spaced(c, 33, yl + 8 * s, D["p3_ask_title"], "B", 8.2 * s, LABEL, 1.4)
    yl += 15 * s
    for it in D["p3_ask"]:
        yl = para(c, 33, yl, lw, it, "R", 8.5 * s, TXT, lead=8.5 * s * 1.34, draw=draw) + 3 * s
    ow_h = para(c, 0, 0, 530 - lw - 15 - 2 * pad, D["p3_owns"], "R", 8.5 * s, TXT, draw=False) + 22 * s + pad
    box(c, 33 + lw + 15, y, 530 - lw - 15, ow_h, draw=draw)
    if draw:
        spaced(c, 33 + lw + 15 + pad, y + pad + 7 * s, D["p3_owns_title"], "B", 8.2 * s, LABEL, 1.4)
    para(c, 33 + lw + 15 + pad, y + pad + 14 * s, 530 - lw - 15 - 2 * pad, D["p3_owns"], "R", 8.5 * s, TXT, draw=draw)
    return max(yl, y + ow_h)


# ---------------------------------------------------------------------------
# PAGE 4 (dynamic)
# ---------------------------------------------------------------------------
def p4(c, D, V, ctx, s, draw):
    ref, date = ctx["ref"], ctx["date"]
    page_frame(c, D, 4, f"Ref #{ref} · {date.strftime('%d.%m.%Y')}", draw)
    y = title_block(c, D, "p4_title", "p4_intro", s, draw)
    if D["translation_note"]:
        if draw:
            text(c, 33, y + 7, D["translation_note"], "M", 8.0 * s, RED)
        y += 12
    size, lh = 8.8 * s, 8.8 * s * 1.36
    rows = [(l, wrap(v.format(**V), "R", size, 368)) for l, v in D["p4_rows"]]
    lab_w = 150
    rows = [(wrap(l, "B", 9 * s, lab_w), w) for l, w in rows]
    total = sum(max(len(w), len(l)) * lh for l, w in rows)
    pad = max(8 * s, min(16, (788 - y - total) / len(rows)))
    if draw:
        c.setStrokeColor(DIV)
        c.setLineWidth(0.5)
        c.line(33, Y(y), 563, Y(y))
    for lab, lines in rows:
        if draw:
            for j, ln in enumerate(lab):
                text(c, 33, y + pad / 2 + 9 * s + j * lh, ln, "B", 9 * s, WHITE)
            for j, ln in enumerate(lines):
                text(c, 192, y + pad / 2 + 9 * s + j * lh, ln, "R", size, TXT)
        y += max(len(lines), len(lab)) * lh + pad
        if draw:
            c.line(33, Y(y), 563, Y(y))
    return y


# ---------------------------------------------------------------------------
# PAGE 5
# ---------------------------------------------------------------------------
def p5(c, D, V, ctx, s, draw):
    page_frame(c, D, 5, OFFER_CONFIG["footer_line"], draw)
    if draw:
        text(c, 33, 124, D["p5_title"], "DB", 25 * s, WHITE)
    y = 140
    cw = (530 - 10) / 2
    pad = 11 * s
    fs = 8.5 * s

    def lst(items, x, top, draw_):
        yy = top
        for it in items:
            yy = para(c, x, yy, cw - 2 * pad, it.format(**V), "R", fs, TXT, lead=fs * 1.34, draw=draw_) + 4.5 * s
        return yy
    h = max(lst(D["p5_will"], 0, 0, False), lst(D["p5_cust"], 0, 0, False)) + 22 * s + pad + 2
    for i, (tk, items) in enumerate([("p5_will_title", D["p5_will"]), ("p5_cust_title", D["p5_cust"])]):
        x = 33 + i * (cw + 10)
        box(c, x, y, cw, h, draw=draw)
        if draw:
            spaced(c, x + pad, y + pad + 7 * s, D[tk], "B", 8.4 * s, WHITE, 1.4)
        lst(items, x + pad, y + pad + 15 * s, draw)
    y += h + 13 * s
    if draw:
        spaced(c, 33, y + 8 * s, D["p5_limits_title"], "B", 8.4 * s, WHITE, 1.4)
    y += 14 * s
    for lead_t, body in D["p5_limits"]:
        y = rich(c, 33, y, 530, [(lead_t, "B", WHITE), (body, "R", TXT)], 8.5 * s, lead=8.5 * s * 1.36, draw=draw) + 4 * s
    y += 8 * s
    data_t = D["p5_data"].format(**V)
    wrong_t = D["p5_wrong"].format(**V)
    hb = max(para(c, 0, 0, cw - 2 * pad, data_t, "R", 8.3 * s, TXT, draw=False),
             para(c, 0, 0, cw - 2 * pad, wrong_t, "R", 8.3 * s, TXT, draw=False)) + 22 * s + pad
    for i, (tk, tx) in enumerate([("p5_data_title", data_t), ("p5_wrong_title", wrong_t)]):
        x = 33 + i * (cw + 10)
        box(c, x, y, cw, hb, draw=draw)
        if draw:
            spaced(c, x + pad, y + pad + 7 * s, D[tk], "B", 8.4 * s, WHITE, 1.4)
        para(c, x + pad, y + pad + 14 * s, cw - 2 * pad, tx, "R", 8.3 * s, TXT, draw=draw)
    y += hb + 12 * s
    if D["translation_note"]:
        if draw:
            text(c, 33, y + 4, D["translation_note"], "M", 7.8, RED)
        y += 10
    # signatures
    for i, k in enumerate(["p5_customer", "p5_for_spets"]):
        x = 33 + i * (cw + 10)
        if draw:
            spaced(c, x, y + 9, D[k], "B", 8.2, WHITE, 1.0)
            c.setStrokeColor(C(90, 90, 96))
            c.setLineWidth(0.6)
            c.line(x, Y(y + 40), x + cw - 10, Y(y + 40))
            text(c, x, y + 50, D["p5_sign"], "R", 7.8, MUTED)
    return y + 52


# ---------------------------------------------------------------------------
# PAGE 6
# ---------------------------------------------------------------------------
def p6(c, D, V, ctx, s, draw):
    cfg = OFFER_CONFIG
    page_frame(c, D, 6, OFFER_CONFIG["footer_line"], draw)
    y = title_block(c, D, "p6_title", "p6_intro", s, draw) + 4 * s
    pad = 11 * s
    for t, red, body in D["p6_sections"]:
        h = para(c, 0, 0, 530 - 2 * pad, body, "R", 8.4 * s, TXT, lead=8.4 * s * 1.36, draw=False) + 21 * s + pad
        box(c, 33, y, 530, h, fill=RED_CARD if red else CARD, stroke=RED_STROKE if red else CARD_STROKE, draw=draw)
        if draw:
            text(c, 33 + pad, y + pad + 8 * s, t, "B", 9.2 * s, WHITE)
        para(c, 33 + pad, y + pad + 13 * s, 530 - 2 * pad, body, "R", 8.4 * s, TXT, lead=8.4 * s * 1.36, draw=draw)
        y += h + 8 * s
    cw = (530 - 20) / 3
    hs = max(para(c, 0, 0, cw - 2 * pad, b, "R", 8.2 * s, TXT, draw=False) for _, b in D["p6_small"]) + 21 * s + pad
    for i, (t, b) in enumerate(D["p6_small"]):
        x = 33 + i * (cw + 10)
        box(c, x, y, cw, hs, draw=draw)
        if draw:
            text(c, x + pad, y + pad + 8 * s, t, "B", 9.0 * s, WHITE)
        para(c, x + pad, y + pad + 13 * s, cw - 2 * pad, b, "R", 8.2 * s, TXT, draw=draw)
    y += hs + 8 * s
    ch = 66 * s
    box(c, 33, y, 530, ch, draw=draw)
    if draw:
        spaced(c, 33 + pad, y + pad + 7 * s, D["p6_cred_title"], "B", 8.4 * s, WHITE, 1.4)
        vals = [cfg["company_no"] or "[XXXXXXXX]", cfg["vat"] or "[GB XXX XXXX XX]",
                cfg["inspectorate"] or "[NSI / SSAIB ref]", cfg["ico"] or "[ZAXXXXXX]",
                f"£{cfg['liability_millions']} {MILLION[ctx['lang']]}" if cfg["liability_millions"] else f"[£X {MILLION[ctx['lang']]}]",
                cfg["arc_name"] or "[ARC name, BS EN 50518]"]
        for i, (l, v) in enumerate(zip(D["p6_cred"], vals)):
            col, row = i % 3, i // 3
            x = 33 + pad + col * (530 - 2 * pad) / 3
            yy = y + pad + 22 * s + row * 22 * s
            text(c, x, yy, l, "R", 7.8 * s, MUTED)
            text(c, x, yy + 9.5 * s, v, "B", 8.2 * s, WHITE)
    return y + ch


PAGES = [p1, p2, p3, p4, p5, p6]
LIMIT = {1: 790, 2: 790, 3: 790, 4: 792, 5: 797, 6: 792}


def _render_lang(c, lang, ctx):
    ctx = dict(ctx, lang=lang)
    D = T[lang]
    V = values(lang, ctx["sub"], ctx["cust"])
    for n, fn in enumerate(PAGES, 1):
        scale = 1.0
        for sc in (1.12, 1.09, 1.06, 1.03, 1.0, 0.97, 0.94, 0.91, 0.88, 0.85, 0.82, 0.79, 0.76):
            dummy = canvas.Canvas(io.BytesIO(), pagesize=(PW, PH))
            if fn(dummy, D, V, ctx, sc, False) <= LIMIT[n]:
                scale = sc
                break
            scale = sc
        fn(c, D, V, ctx, scale, True)
        c.showPage()


def build_offer_pdf(sub: dict, customer: dict, ref: str, date, lang: str = "en") -> bytes:
    _fonts()
    lang = lang if lang in T else "en"
    ctx = {"sub": sub, "cust": customer or {}, "ref": ref, "date": date}
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PW, PH))
    c.setTitle(f"SPETS Security — Alarm subscription {ref}")
    _render_lang(c, lang, ctx)
    if lang != "en" and APPEND_ENGLISH:
        _render_lang(c, "en", ctx)
    c.save()
    return buf.getvalue()


if __name__ == "__main__":
    from datetime import datetime
    s = ps.build_subscription("hub2plus", {"motioncam": 1, "smoke": 1, "keypad": 1})
    for lg in ("en", "ru", "uk"):
        pdf = build_offer_pdf(s, {"name": "Олександр Тест", "address": "12 Baker Street, London NW1 6XE"},
                              "250", datetime(2026, 10, 29), lg)
        open(f"/home/claude/offer_{lg}.pdf", "wb").write(pdf)
        print(lg, len(pdf))
