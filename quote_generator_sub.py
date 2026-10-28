"""
SPETS SECURITY — Alarm SUBSCRIPTION PDF:
  page 1   : Subscription quote (equipment + monthly price + included services)
  page 2   : Subscription Agreement with signature blocks
  page 3+  : Terms & Conditions
Тексти договору/T&C — у contract_texts.py. Ціни — у pricing_sub.py.
Same black/orange style as the CCTV / Ajax invoices.
"""
import io
import copy
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, KeepTogether)
from reportlab.lib.styles import ParagraphStyle

from quote_generator import (
    BLACK, ORANGE, ORANGE_LIGHT, DARK_TEXT, MUTED_GREY, LIGHT_GREY, SOFT_BG,
    FONT_NAME, FONT_NAME_BOLD, FONT_SERIF_BOLD,
    _draw_top_banner, _draw_bottom_banner,
)
import contract_texts as ct

W = A4[0] - 40 * mm  # content width


def _m(v):
    return f"{v:,.2f}"


def _esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# --- styles ---
H_WORD = ParagraphStyle("HW", fontName=FONT_SERIF_BOLD, fontSize=22, textColor=ORANGE,
                        alignment=TA_RIGHT, leading=24)
H_META = ParagraphStyle("HM", fontName=FONT_NAME_BOLD, fontSize=10, textColor=DARK_TEXT,
                        alignment=TA_RIGHT, leading=14)
TITLE = ParagraphStyle("T", fontName=FONT_SERIF_BOLD, fontSize=14, textColor=BLACK,
                       leading=17, spaceAfter=3)
SEC = ParagraphStyle("S", fontName=FONT_SERIF_BOLD, fontSize=12, textColor=BLACK,
                     leading=15, spaceBefore=4, spaceAfter=3)
BODY = ParagraphStyle("B", fontName=FONT_NAME, fontSize=9.5, textColor=DARK_TEXT, leading=13.5)
SMALL = ParagraphStyle("Sm", fontName=FONT_NAME, fontSize=8, textColor=MUTED_GREY, leading=10)
CELL = ParagraphStyle("C", fontName=FONT_NAME, fontSize=9.5, textColor=DARK_TEXT, leading=12)
CELL_C = ParagraphStyle("CC", parent=CELL, alignment=TA_CENTER)
HDR = ParagraphStyle("H", fontName=FONT_NAME_BOLD, fontSize=9, textColor=colors.white,
                     alignment=TA_LEFT)
HDR_C = ParagraphStyle("HC", parent=HDR, alignment=TA_CENTER)
CL_T = ParagraphStyle("CT", fontName=FONT_NAME_BOLD, fontSize=10, textColor=BLACK, leading=13)


def _accent():
    a = Table([[""]], colWidths=[14 * mm], rowHeights=[1.6])
    a.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ORANGE),
                           ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return a


def _header(word, customer, ref, date, loc=None):
    left = [Paragraph("<b>Prepared for</b>", TITLE), _accent(), Spacer(1, 3 * mm)]
    for k in ("name", "phone", "email", "address"):
        if customer.get(k):
            left.append(Paragraph(_esc(customer[k]), BODY))
    if loc and loc.get("url"):
        left.append(Paragraph(f'<link href="{loc["url"]}"><font color="#F58A2C">📍 Map location</font></link>'
                              .replace("📍 ", ""), BODY))
    right = [Paragraph(word, H_WORD), Spacer(1, 2 * mm),
             Paragraph(f"Ref #&nbsp;&nbsp;{_esc(ref)}", H_META),
             Paragraph(f"Date: {date.strftime('%d %b %Y')}", H_META)]
    t = Table([[left, right]], colWidths=[95 * mm, 75 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return t


def _fill(text, v):
    try:
        return text.format(**v)
    except Exception:
        return text


def generate_subscription_pdf(data: dict) -> bytes:
    """
    data = {"sub": <pricing_sub.build_subscription()>, "quote_number": "250",
            "date": datetime, "customer": {...}, "location": {"lat","lon","url"} | None}
    """
    sub = data["sub"]
    cust = data.get("customer", {})
    ref = str(data.get("quote_number", ""))
    date = data.get("date") or datetime.now()
    loc = data.get("location")
    v = {
        "customer": _esc(cust.get("name", "")), "address": _esc(cust.get("address", "")),
        "monthly_ex": _m(sub["monthly_ex_vat"]), "monthly_inc": _m(sub["monthly_inc_vat"]),
        "install_ex": _m(sub["install_ex_vat"]), "install_inc": _m(sub["install_inc_vat"]),
        "term": sub["min_term"], "notice": sub["notice_days"],
        "ref": _esc(ref), "date": date.strftime("%d %B %Y"),
    }

    story = []
    # =================== PAGE 1 — QUOTE ===================
    story.append(_header("SUBSCRIPTION", cust, ref, date, loc))
    story.append(Spacer(1, 4 * mm))

    # Monthly price hero
    big_l = ParagraphStyle("BL", fontName=FONT_NAME_BOLD, fontSize=11, textColor=colors.white, leading=15)
    big_v = ParagraphStyle("BV", fontName=FONT_SERIF_BOLD, fontSize=22, textColor=ORANGE_LIGHT,
                           alignment=TA_RIGHT, leading=25)
    sub_l = ParagraphStyle("SL", fontName=FONT_NAME, fontSize=8.5, textColor=colors.HexColor("#BBBBBB"), leading=11)
    sub_r = ParagraphStyle("SR", parent=sub_l, alignment=TA_RIGHT)
    hero = Table([
        [Paragraph("YOUR MONTHLY SUBSCRIPTION", big_l),
         Paragraph(f"£{_m(sub['monthly_inc_vat'])}<font size=11> /month</font>", big_v)],
        [Paragraph("Everything included — equipment, support, repairs, SIM", sub_l),
         Paragraph(f"£{_m(sub['monthly_ex_vat'])} + VAT £{_m(sub['monthly_vat'])}", sub_r)],
    ], colWidths=[W * 0.55, W * 0.45])
    hero.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLACK),
        ("LINEBELOW", (0, -1), (-1, -1), 2.5, ORANGE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10), ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
    ]))
    story.append(hero)
    story.append(Spacer(1, 3 * mm))

    # Equipment table
    story.append(Paragraph("EQUIPMENT INSTALLED", SEC))
    rows = [[Paragraph("No", HDR_C), Paragraph("Device (Ajax wireless)", HDR), Paragraph("Qty", HDR_C)]]
    for i, (q, name) in enumerate(sub["equipment"], 1):
        rows.append([Paragraph(str(i), CELL_C), Paragraph(_esc(name), CELL), Paragraph(str(q), CELL_C)])
    tbl = Table(rows, colWidths=[12 * mm, W - 32 * mm, 20 * mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLACK), ("LINEBELOW", (0, 0), (-1, 0), 2, ORANGE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT_BG]),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, LIGHT_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 3 * mm))

    # Payments summary
    pl = ParagraphStyle("PL", fontName=FONT_NAME_BOLD, fontSize=10, textColor=DARK_TEXT, leading=14)
    pr = ParagraphStyle("PR", parent=pl, alignment=TA_RIGHT)
    pay = Table([
        [Paragraph("Monthly subscription", pl),
         Paragraph(f"£{_m(sub['monthly_ex_vat'])} + VAT = <b>£{_m(sub['monthly_inc_vat'])}</b>", pr)],
        [Paragraph("Installation — one-off", pl),
         Paragraph(f"£{_m(sub['install_ex_vat'])} + VAT = <b>£{_m(sub['install_inc_vat'])}</b>", pr)],
        [Paragraph("Minimum term", pl), Paragraph(f"{sub['min_term']} months", pr)],
    ], colWidths=[W * 0.5, W * 0.5])
    pay.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, LIGHT_GREY),
        ("BACKGROUND", (0, 0), (-1, 0), SOFT_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(pay)
    story.append(Spacer(1, 3 * mm))

    # Included services (compact)
    inc = "  ·  ".join(_esc(x) for x in sub["included"])
    story.append(KeepTogether([
        Paragraph("WHAT'S INCLUDED EVERY MONTH", SEC),
        Paragraph(f'<font color="#F58A2C"><b>+</b></font> {inc}',
                  ParagraphStyle("Inc", parent=BODY, fontSize=8.8, leading=12)),
        Spacer(1, 2 * mm)]))
    story.append(Paragraph("This quote is valid for 14 days. Equipment remains the property of "
                           "Spets Security Ltd. See the Agreement and Terms &amp; Conditions attached.", SMALL))

    # =================== PAGE 2 — AGREEMENT ===================
    story.append(PageBreak())
    story.append(Paragraph(_esc(ct.AGREEMENT_TITLE), TITLE))
    story.append(_accent())
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(_fill(ct.AGREEMENT_INTRO, v), BODY))
    story.append(Spacer(1, 3 * mm))
    for i, (title, text) in enumerate(ct.AGREEMENT_CLAUSES, 1):
        story.append(KeepTogether([Paragraph(f"{i}. {_esc(title)}", CL_T),
                                   Paragraph(_fill(text, v), BODY), Spacer(1, 2.5 * mm)]))

    # Signature blocks
    story.append(Spacer(1, 6 * mm))
    lab = ParagraphStyle("Lab", fontName=FONT_NAME_BOLD, fontSize=10, textColor=BLACK, leading=13)
    ln = ParagraphStyle("Ln", fontName=FONT_NAME, fontSize=9, textColor=DARK_TEXT, leading=22)

    def sig(who, name):
        return [Paragraph(who, lab), Paragraph(f"Name: {name}", ln),
                Paragraph("Signature: ______________________________", ln),
                Paragraph("Date: ____ / ____ / ________", ln)]
    sigs = Table([[sig("CUSTOMER", _esc(cust.get("name", "")) or "________________________"),
                   sig("FOR SPETS SECURITY LTD", "________________________")]],
                 colWidths=[W / 2, W / 2])
    sigs.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LINEABOVE", (0, 0), (-1, 0), 1.5, ORANGE),
                              ("TOPPADDING", (0, 0), (-1, -1), 6),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(KeepTogether([sigs]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"{ct.COMPANY['name']} · {ct.COMPANY['address']} · {ct.COMPANY['phone']} · "
                           f"{ct.COMPANY['email']} · VAT {ct.COMPANY['vat']}", SMALL))

    # =================== PAGE 3+ — T&C ===================
    story.append(PageBreak())
    story.append(Paragraph(_esc(ct.TERMS_TITLE), TITLE))
    story.append(_accent())
    story.append(Spacer(1, 2.5 * mm))
    tb = ParagraphStyle("TB2", parent=BODY, fontSize=8.6, leading=11.2)
    tt = ParagraphStyle("TT2", parent=CL_T, fontSize=9.2, leading=11.5)
    for title, text in ct.TERMS:
        story.append(KeepTogether([Paragraph(_esc(title), tt),
                                   Paragraph(_fill(text, v), tb), Spacer(1, 1.6 * mm)]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Customer initials: ________", BODY))

    # ---------- build (banner top on every page, bottom on last) ----------
    frame = Frame(20 * mm, 42 * mm, W, A4[1] - 104 * mm, id="main")

    def _build(buf, on_page):
        doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                              topMargin=62 * mm, bottomMargin=42 * mm,
                              title=f"Spets Security — Subscription {ref}")
        doc.addPageTemplates([PageTemplate(id="m", frames=[frame], onPage=on_page)])
        return doc

    cnt = _build(io.BytesIO(), lambda c, d: _draw_top_banner(c))
    cnt.build(copy.deepcopy(story))
    total = cnt.page

    def _draw(c, doc):
        _draw_top_banner(c)
        if doc.page == total:
            _draw_bottom_banner(c)

    buf = io.BytesIO()
    _build(buf, _draw).build(story)
    return buf.getvalue()


if __name__ == "__main__":
    import pricing_sub as ps
    s = ps.build_subscription("hub2plus", {"motion": 2, "door": 1, "smoke": 1, "keypad": 1})
    pdf = generate_subscription_pdf({
        "sub": s, "quote_number": "250", "date": datetime(2026, 10, 28),
        "customer": {"name": "John Smith", "phone": "+44 7700 900111",
                     "email": "john@example.com", "address": "12 Baker Street, London, NW1 6XE"},
        "location": {"lat": 51.5237, "lon": -0.1585, "url": "https://maps.google.com/?q=51.523700,-0.158500"},
    })
    open("/home/claude/test_sub.pdf", "wb").write(pdf)
    print("PDF", len(pdf), "bytes")
