"""
SPETS SECURITY — Ajax Superior quote PDF generator.
Mirrors the CCTV invoice style (black + orange chevrons, serif headings),
reusing shared drawing helpers from quote_generator.py.

Two quote types:
  - ajax_kit    : a ready kit (Budget / Balance / Elite)
  - ajax_custom : build-your-own component list

Each quote: items table + install line (with indicative note) + totals,
then the company presentation is appended (same as CCTV).
"""
import io
import logging
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib.styles import ParagraphStyle

# Reuse all shared styling + helpers from the CCTV generator
from quote_generator import (
    NAVY, BLACK, ORANGE, ORANGE_LIGHT, DARK_TEXT, MUTED_GREY, LIGHT_GREY, SOFT_BG,
    FONT_NAME, FONT_NAME_BOLD, FONT_SERIF, FONT_SERIF_BOLD,
    _draw_top_banner, _draw_bottom_banner, _append_presentation,
)

log = logging.getLogger(__name__)


def _money(v: float) -> str:
    return f"£{v:,.2f}"


def generate_ajax_quote_pdf(quote_data: dict) -> bytes:
    """
    quote_data = {
        "quote": <dict from pricing_ajax.build_kit_quote or build_custom_quote>,
        "quote_number": "210",
        "date": datetime,
        "customer": {"name","phone","email","address"},
        "lang": "en",
        "title": "AJAX ALARM" (optional banner word),
    }
    """
    q = quote_data["quote"]
    customer = quote_data.get("customer", {})
    quote_number = quote_data.get("quote_number", "")
    date = quote_data.get("date", datetime.now())

    buf = io.BytesIO()
    story = []

    # ---------------- Invoice To (left) + AJAX QUOTE (right) ----------------
    left_title = ParagraphStyle("AjTitle", fontName=FONT_SERIF_BOLD, fontSize=15,
                                textColor=BLACK, spaceAfter=3, leading=17)
    left_info = ParagraphStyle("AjInfo", fontName=FONT_NAME, fontSize=10,
                               textColor=DARK_TEXT, leading=14)

    left = [Paragraph("<b>Quote To</b>", left_title)]
    accent = Table([[""]], colWidths=[14 * mm], rowHeights=[1.6])
    accent.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ORANGE),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    left.append(accent)
    left.append(Spacer(1, 3 * mm))
    left.append(Paragraph(customer.get("name", "Client"), left_info))
    if customer.get("phone"):
        left.append(Paragraph(customer["phone"], left_info))
    if customer.get("email"):
        left.append(Paragraph(customer["email"], left_info))
    if customer.get("address"):
        left.append(Paragraph(customer["address"], left_info))

    word_style = ParagraphStyle("AjWord", fontName=FONT_SERIF_BOLD, fontSize=34,
                                textColor=ORANGE, alignment=TA_RIGHT, leading=36)
    meta_style = ParagraphStyle("AjMeta", fontName=FONT_NAME_BOLD, fontSize=10,
                                textColor=DARK_TEXT, alignment=TA_RIGHT, leading=14)
    right = [
        Paragraph("AJAX ALARM", word_style),
        Spacer(1, 2 * mm),
        Paragraph(f"Quote #&nbsp;&nbsp;{quote_number}", meta_style),
        Paragraph(f"Date: {date.strftime('%d %b %Y')}", meta_style),
    ]

    top = Table([[left, right]], colWidths=[95 * mm, 75 * mm])
    top.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(top)
    story.append(Spacer(1, 6 * mm))

    # ---------------- Kit badge (if a ready kit) ----------------
    if q.get("type") == "ajax_kit":
        tier = q.get("tier", "")
        tier_colors = {"Budget": colors.HexColor("#2E7D32"),
                       "Balance": colors.HexColor("#1565C0"),
                       "Elite": ORANGE}
        badge_style = ParagraphStyle("Badge", fontName=FONT_NAME_BOLD, fontSize=11,
                                     textColor=colors.white, alignment=TA_CENTER)
        badge = Table([[Paragraph(f"{tier.upper()} — READY KIT", badge_style)]],
                      colWidths=[70 * mm])
        badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BLACK),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, -1), 2, ORANGE),
            ("LINEABOVE", (0, 0), (-1, -1), 2.5, tier_colors.get(tier, ORANGE)),
        ]))
        story.append(badge)
        story.append(Spacer(1, 5 * mm))

    # ---------------- Items table ----------------
    cell = ParagraphStyle("Cell", fontName=FONT_NAME, fontSize=9.5,
                          textColor=DARK_TEXT, leading=12)
    cell_b = ParagraphStyle("CellB", fontName=FONT_NAME_BOLD, fontSize=9.5,
                            textColor=DARK_TEXT, leading=12)
    cell_c = ParagraphStyle("CellC", fontName=FONT_NAME, fontSize=9.5,
                            textColor=DARK_TEXT, alignment=TA_CENTER, leading=12)
    cell_r = ParagraphStyle("CellR", fontName=FONT_NAME_BOLD, fontSize=9.5,
                            textColor=DARK_TEXT, alignment=TA_RIGHT, leading=12)
    hdr = ParagraphStyle("Hdr", fontName=FONT_NAME_BOLD, fontSize=9,
                         textColor=colors.white, alignment=TA_CENTER)

    rows = [[Paragraph("No", hdr), Paragraph("Device", hdr),
             Paragraph("Qty", hdr), Paragraph("Unit £", hdr), Paragraph("Total £", hdr)]]

    if q.get("type") == "ajax_kit":
        # show kit contents as one block, single price line
        contents = q.get("contents", [])
        lines = "<br/>".join(f"• {n} × {qty}" for n, qty in contents)
        device = Paragraph(f"<b>{q.get('kit_name','Ajax Kit')}</b><br/>{lines}", cell)
        rows.append([Paragraph("1", cell_c), device,
                     Paragraph("1", cell_c),
                     Paragraph(_money(q["equipment_total"]), cell_c),
                     Paragraph(_money(q["equipment_total"]), cell_r)])
    else:
        for i, li in enumerate(q["line_items"], 1):
            device = Paragraph(f"<b>{li['name']}</b><br/>{li['model']}", cell)
            rows.append([Paragraph(str(i), cell_c), device,
                         Paragraph(str(li["qty"]), cell_c),
                         Paragraph(_money(li["unit_price"]), cell_c),
                         Paragraph(_money(li["line_total"]), cell_r)])

    items = Table(rows, colWidths=[12 * mm, 96 * mm, 16 * mm, 22 * mm, 24 * mm], repeatRows=1)
    items.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, 0), BLACK),
        ("TOPPADDING", (0, 0), (-1, 0), 7), ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
        ("LINEBELOW", (0, 0), (-1, 0), 2, ORANGE),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, LIGHT_GREY),
        ("LINEBELOW", (0, -1), (-1, -1), 1.2, BLACK),
    ]))
    story.append(items)
    story.append(Spacer(1, 5 * mm))

    # ---------------- Install line + note ----------------
    if q.get("install", 0):
        inst_lbl = ParagraphStyle("InstL", fontName=FONT_NAME_BOLD, fontSize=10,
                                  textColor=BLACK)
        inst_val = ParagraphStyle("InstV", fontName=FONT_NAME_BOLD, fontSize=10,
                                  textColor=BLACK, alignment=TA_RIGHT)
        inst = Table([[Paragraph("Professional installation", inst_lbl),
                       Paragraph(_money(q["install"]), inst_val)]],
                     colWidths=[146 * mm, 24 * mm])
        inst.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, LIGHT_GREY),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(inst)
        note_style = ParagraphStyle("Note", fontName=FONT_NAME, fontSize=8,
                                    textColor=MUTED_GREY, leading=10)
        story.append(Spacer(1, 1.5 * mm))
        story.append(Paragraph(q.get("install_note", ""), note_style))
        story.append(Spacer(1, 4 * mm))

    # ---------------- Totals ----------------
    tl = ParagraphStyle("TL", fontName=FONT_NAME_BOLD, fontSize=11,
                        textColor=DARK_TEXT, alignment=TA_LEFT, leading=18)
    tv = ParagraphStyle("TV", fontName=FONT_NAME_BOLD, fontSize=11,
                        textColor=DARK_TEXT, alignment=TA_RIGHT, leading=18)
    gl = ParagraphStyle("GL", fontName=FONT_NAME_BOLD, fontSize=11,
                        textColor=colors.white, alignment=TA_LEFT, leading=18)
    gv = ParagraphStyle("GV", fontName=FONT_SERIF_BOLD, fontSize=14,
                        textColor=ORANGE_LIGHT, alignment=TA_RIGHT, leading=17)

    totals = Table([
        [Paragraph("Subtotal", tl), Paragraph(_money(q["subtotal"]), tv)],
        [Paragraph("VAT (20%)", tl), Paragraph(_money(q["vat"]), tv)],
        [Spacer(1, 3 * mm), Spacer(1, 3 * mm)],
        [Paragraph("Grand total", gl), Paragraph(_money(q["grand_total"]), gv)],
    ], colWidths=[32 * mm, 48 * mm])
    totals.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("BACKGROUND", (0, 3), (-1, 3), BLACK),
        ("TOPPADDING", (0, 3), (-1, 3), 7), ("BOTTOMPADDING", (0, 3), (-1, 3), 7),
        ("LEFTPADDING", (0, 3), (0, 3), 8), ("RIGHTPADDING", (-1, 3), (-1, 3), 8),
    ]))

    # bank details on the left, totals on the right (mirror CCTV layout)
    bank_style = ParagraphStyle("Bank", fontName=FONT_NAME, fontSize=8.5,
                                textColor=DARK_TEXT, leading=12)
    bank = Paragraph(
        "Payment details: Lloyds Bank<br/>Account number: 48253368<br/>"
        "Sort code: 30-99-50<br/>IBAN: GB38LOYD30995048253368<br/>"
        "BIC: LOYDGB21287<br/>VAT: 455026800", bank_style)

    bottom = Table([[bank, totals]], colWidths=[90 * mm, 80 * mm])
    bottom.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(bottom)
    story.append(Spacer(1, 8 * mm))

    # ---------------- Terms ----------------
    terms_title = ParagraphStyle("TT", fontName=FONT_SERIF_BOLD, fontSize=12,
                                 textColor=BLACK, spaceAfter=4)
    terms_body = ParagraphStyle("TB", fontName=FONT_NAME, fontSize=9,
                                textColor=DARK_TEXT, leading=13)
    story.append(Paragraph("TERMS &amp; CONDITIONS", terms_title))
    story.append(Paragraph("1. Prices are valid for 1 week", terms_body))
    story.append(Paragraph("2. Equipment delivery time is from 5-7 working days", terms_body))
    story.append(Paragraph("3. Wireless Ajax Superior — installed by certified engineers", terms_body))
    story.append(Paragraph("4. Installation price confirmed after a site survey", terms_body))

    # ---------------- Device descriptions (custom quotes only) ----------------
    if q.get("type") == "ajax_custom" and q.get("line_items"):
        try:
            from pricing_ajax import component_description
        except ImportError:
            component_description = lambda k: ""
        story.append(Spacer(1, 8 * mm))
        story.append(Paragraph("ABOUT YOUR DEVICES", terms_title))
        dev_name = ParagraphStyle("DevN", fontName=FONT_NAME_BOLD, fontSize=10,
                                  textColor=BLACK, leading=13)
        dev_desc = ParagraphStyle("DevD", fontName=FONT_NAME, fontSize=9,
                                  textColor=DARK_TEXT, leading=12)
        for li in q["line_items"]:
            desc = component_description(li.get("key", ""))
            if not desc:
                continue
            story.append(Spacer(1, 2.5 * mm))
            # orange accent tab + device name
            row = Table(
                [[Paragraph(f"{li['name']}", dev_name)]],
                colWidths=[170 * mm])
            row.setStyle(TableStyle([
                ("LINEBEFORE", (0, 0), (0, 0), 2.5, ORANGE),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]))
            story.append(row)
            story.append(Paragraph(desc, dev_desc))

    # ---------------- Build with banners ----------------
    def _first_page(c, doc):
        _draw_top_banner(c)

    def _last_page(c, doc):
        _draw_top_banner(c)
        _draw_bottom_banner(c)

    frame = Frame(20 * mm, 45 * mm, A4[0] - 40 * mm, A4[1] - 130 * mm, id="main")
    # Two-pass: count pages so bottom banner only on last page
    import copy
    count_buf = io.BytesIO()
    count_doc = BaseDocTemplate(count_buf, pagesize=A4,
                                leftMargin=20 * mm, rightMargin=20 * mm,
                                topMargin=85 * mm, bottomMargin=45 * mm)
    count_doc.addPageTemplates([PageTemplate(id="c", frames=[frame], onPage=_first_page)])
    count_doc.build(copy.deepcopy(story))
    total_pages = count_doc.page

    def _draw(c, doc):
        _draw_top_banner(c)
        if doc.page == total_pages:
            _draw_bottom_banner(c)

    doc = BaseDocTemplate(buf, pagesize=A4,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=85 * mm, bottomMargin=45 * mm)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_draw)])
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()

    # append company presentation (same as CCTV)
    pdf_bytes = _append_presentation(pdf_bytes)
    return pdf_bytes


if __name__ == "__main__":
    from pricing_ajax import build_kit_quote, build_custom_quote

    cust = {"name": "John Smith", "phone": "+44 7700 900111",
            "email": "john@example.com", "address": "12 Baker Street, London, NW1 6XE"}

    # Test ready kit
    kq = build_kit_quote("balance")
    pdf = generate_ajax_quote_pdf({
        "quote": kq, "quote_number": "210", "date": datetime(2026, 6, 26),
        "customer": cust, "lang": "en",
    })
    with open("/home/claude/test_ajax_kit.pdf", "wb") as f:
        f.write(pdf)
    print(f"Kit PDF: {len(pdf)} bytes")

    # Test custom
    sel = {"hub2plus": 1, "motion_s": 3, "motioncam_s": 1, "door_s": 2,
           "siren_out_jew": 1, "keypad_s": 1, "keyfob_s": 2}
    cq = build_custom_quote(sel)
    pdf2 = generate_ajax_quote_pdf({
        "quote": cq, "quote_number": "211", "date": datetime(2026, 6, 26),
        "customer": cust, "lang": "en",
    })
    with open("/home/claude/test_ajax_custom.pdf", "wb") as f:
        f.write(pdf2)
    print(f"Custom PDF: {len(pdf2)} bytes")
