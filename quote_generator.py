"""
SPETS SECURITY — PDF Quote Generator v3 (matches KeyCRM invoice design)

Design mirrors the KeyCRM-rendered invoice:
- Top-left diagonal navy+orange banner
- "SPETS / ALWAYS NEAR" logo top-right
- "Invoice To" left, big "INVOICE" right
- Clean items table (No / # / Item / Qty / Price / VAT / Total)
- Payment details bottom-left, totals bottom-right (Grand total in orange)
- Terms & Conditions bottom-left
- Bottom-right diagonal banner (mirrored)
- Cyrillic-capable DejaVu fonts bundled

Coloured package badge (Budget/Balance/Elite) shown in the small "#" column
header so each package is identifiable while keeping the KeyCRM look.
"""
import io
import os
import logging
from datetime import datetime

log = logging.getLogger(__name__)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# =====================================================================
# BRAND COLOURS (from KeyCRM design)
# =====================================================================
NAVY = colors.HexColor("#14213D")      # dark blue diagonal
ORANGE = colors.HexColor("#F58A2C")    # bright orange (logo + grand total + accents)
ORANGE_LIGHT = colors.HexColor("#FCA311")
DARK_TEXT = colors.HexColor("#222222")
MUTED_GREY = colors.HexColor("#9E9E9E")
LIGHT_GREY = colors.HexColor("#E8E8E8")

# Package badge colours (kept for differentiation)
BADGE_COLORS = {
    "Budget":  colors.HexColor("#2E7D32"),
    "Balance": colors.HexColor("#1565C0"),
    "Elite":   colors.HexColor("#C9A227"),
}

# =====================================================================
# FONT REGISTRATION (Cyrillic support)
# =====================================================================
FONT_NAME = "Helvetica"
FONT_NAME_BOLD = "Helvetica-Bold"
CYRILLIC_REGISTERED = False

_FONT_CANDIDATES = [
    (os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSans.ttf"),
     os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSans-Bold.ttf")),
    (os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "DejaVuSans.ttf"),
     os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "DejaVuSans-Bold.ttf")),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/TTF/DejaVuSans.ttf",
     "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"),
]


def _register_cyrillic_font():
    global FONT_NAME, FONT_NAME_BOLD, CYRILLIC_REGISTERED
    for reg, bold in _FONT_CANDIDATES:
        if os.path.exists(reg):
            try:
                pdfmetrics.registerFont(TTFont("CyrSans", reg))
                if os.path.exists(bold):
                    pdfmetrics.registerFont(TTFont("CyrSans-Bold", bold))
                    FONT_NAME = "CyrSans"
                    FONT_NAME_BOLD = "CyrSans-Bold"
                else:
                    FONT_NAME = "CyrSans"
                    FONT_NAME_BOLD = "CyrSans"
                CYRILLIC_REGISTERED = True
                log.info(f"Cyrillic font registered: {reg}")
                return
            except Exception as e:
                log.warning(f"Font registration failed: {e}")
    log.warning("No Cyrillic font found — Cyrillic text will be squares!")


_register_cyrillic_font()


# =====================================================================
# DECORATIVE BANNERS (top-left + bottom-right) — drawn on canvas
# =====================================================================
def _draw_banners(c: canvas.Canvas, doc):
    """Draw the KeyCRM-style diagonal navy+orange banners."""
    width, height = A4
    c.saveState()

    # ---------- TOP-LEFT BANNER ----------
    # A navy rectangle in the corner with orange diagonal stripes overlapping
    # Banner is kept compact (max ~55mm wide) so it doesn't cover "Invoice To" text below
    c.setFillColor(NAVY)
    p = c.beginPath()
    p.moveTo(0, height)
    p.lineTo(55 * mm, height)
    p.lineTo(0, height - 55 * mm)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Orange diagonal stripe 1 (big, in front)
    c.setFillColor(ORANGE)
    p = c.beginPath()
    p.moveTo(22 * mm, height)
    p.lineTo(55 * mm, height)
    p.lineTo(55 * mm, height - 14 * mm)
    p.lineTo(15 * mm, height - 45 * mm)
    p.lineTo(10 * mm, height - 35 * mm)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Orange diagonal stripe 2 (smaller)
    c.setFillColor(ORANGE_LIGHT)
    p = c.beginPath()
    p.moveTo(40 * mm, height - 18 * mm)
    p.lineTo(55 * mm, height - 18 * mm)
    p.lineTo(55 * mm, height - 32 * mm)
    p.lineTo(28 * mm, height - 55 * mm)
    p.lineTo(14 * mm, height - 55 * mm)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # ---------- BOTTOM-RIGHT BANNER (mirrored) ----------
    c.setFillColor(NAVY)
    p = c.beginPath()
    p.moveTo(width, 0)
    p.lineTo(width - 70 * mm, 0)
    p.lineTo(width, 70 * mm)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    c.setFillColor(ORANGE)
    p = c.beginPath()
    p.moveTo(width - 50 * mm, 0)
    p.lineTo(width - 5 * mm, 0)
    p.lineTo(width, 12 * mm)
    p.lineTo(width, 30 * mm)
    p.lineTo(width - 45 * mm, 0)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    c.setFillColor(ORANGE_LIGHT)
    p = c.beginPath()
    p.moveTo(width - 25 * mm, 0)
    p.lineTo(width - 5 * mm, 0)
    p.lineTo(width, 18 * mm)
    p.lineTo(width, 35 * mm)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # ---------- SPETS / ALWAYS NEAR logo top-right ----------
    c.setFillColor(ORANGE)
    c.setFont(FONT_NAME_BOLD, 32)
    logo_y = height - 25 * mm
    c.drawRightString(width - 20 * mm, logo_y, "SPETS")
    c.setFont(FONT_NAME_BOLD, 9)
    c.drawRightString(width - 20 * mm, logo_y - 6 * mm, "ALWAYS NEAR")

    # Company address (below logo, right-aligned)
    c.setFillColor(DARK_TEXT)
    c.setFont(FONT_NAME_BOLD, 9)
    c.drawRightString(width - 20 * mm, logo_y - 14 * mm, "Spets Security LTD")
    c.setFont(FONT_NAME, 8)
    c.drawRightString(width - 20 * mm, logo_y - 19 * mm,
                      "1 Oakcroft Road, Chessington, Surrey,")
    c.drawRightString(width - 20 * mm, logo_y - 23 * mm,
                      "KT9 1BD, United Kingdom")

    # ---------- Phone + Email at bottom-left ----------
    c.setFillColor(DARK_TEXT)
    c.setFont(FONT_NAME_BOLD, 10)
    # Phone icon (orange circle with white phone glyph stylised as ●)
    c.setFillColor(ORANGE)
    c.circle(22 * mm, 25 * mm, 4 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONT_NAME_BOLD, 10)
    c.drawCentredString(22 * mm, 23.5 * mm, "☎")
    c.setFillColor(DARK_TEXT)
    c.setFont(FONT_NAME_BOLD, 11)
    c.drawString(29 * mm, 23.5 * mm, "+44 7706 906079")

    # Email icon
    c.setFillColor(ORANGE)
    c.roundRect(86 * mm, 22 * mm, 8 * mm, 6 * mm, 1, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONT_NAME_BOLD, 7)
    c.drawCentredString(90 * mm, 24 * mm, "✉")
    c.setFillColor(DARK_TEXT)
    c.setFont(FONT_NAME_BOLD, 11)
    c.drawString(97 * mm, 23.5 * mm, "spets.services@gmail.com")

    c.restoreState()


# =====================================================================
# MONEY HELPERS
# =====================================================================
def _gbp(amount: float) -> str:
    """Format as £1,234.50 — but in KeyCRM style £1,234,50 uses comma."""
    return f"£{amount:,.2f}"


def _gbp_keycrm(amount: float) -> str:
    """KeyCRM style: £65,00 (comma instead of dot for decimals)."""
    s = f"{amount:,.2f}"
    # Replace last dot with comma
    if "." in s:
        s = s.rsplit(".", 1)
        return f"£{s[0]},{s[1]}"
    return f"£{s}"


def _format_total(amount: float) -> str:
    """For 'Total' column — KeyCRM shows £780 (no decimals if whole), £70.8 etc."""
    if amount == int(amount):
        return f"£{int(amount)}"
    # 1 decimal if .X0, else 2
    if round(amount * 10) == amount * 10:
        return f"£{amount:.1f}"
    return f"£{amount:.2f}"


def _grand_total_str(amount: float) -> str:
    """Grand total style: '2 394,00 GBP'"""
    whole = int(amount)
    frac = round((amount - whole) * 100)
    # Format whole with space thousand separator
    whole_str = f"{whole:,}".replace(",", " ")
    return f"{whole_str},{frac:02d} GBP"


# =====================================================================
# MAIN: generate_quote_pdf
# =====================================================================
def generate_quote_pdf(quote_data: dict) -> bytes:
    """
    quote_data = {
        "package": "budget"/"balance"/"elite",
        "package_label": "Budget",
        "package_color": "#2E7D32",
        "items": [{name, sku, qty, base, vat, total}],
        "subtotal": ...,
        "vat_total": ...,
        "grand_total": ...,
        "quote_number": "199",
        "date": datetime,
        "customer": {"name", "phone", "email", "address", "object_type"},
        "lang": "en",
    }
    """
    buf = io.BytesIO()
    width, height = A4

    # Frame leaves room for the top banner (85mm) and bottom banner (45mm)
    frame = Frame(
        20 * mm, 45 * mm,
        width - 40 * mm, height - 85 * mm - 45 * mm,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    template = PageTemplate(id="main", frames=[frame], onPage=_draw_banners)

    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=85 * mm, bottomMargin=45 * mm,
    )
    doc.addPageTemplates([template])

    story = []

    # =====================================================================
    # INVOICE TO (left)  + big "INVOICE" (right)
    # =====================================================================
    customer = quote_data.get("customer", {})
    pkg_label = quote_data.get("package_label", "")
    badge_color = BADGE_COLORS.get(pkg_label, NAVY)

    # Left block: "Invoice To" + name + phone + address
    left_style_title = ParagraphStyle(
        "InvTitle", fontName=FONT_NAME_BOLD, fontSize=14, textColor=DARK_TEXT,
        spaceAfter=2, leading=16,
    )
    left_style_info = ParagraphStyle(
        "InvInfo", fontName=FONT_NAME, fontSize=10, textColor=DARK_TEXT,
        leading=14,
    )
    left_para = []
    left_para.append(Paragraph("<b>Invoice To</b>", left_style_title))
    left_para.append(Paragraph(customer.get("name", "Client"), left_style_info))
    if customer.get("phone"):
        left_para.append(Paragraph(customer["phone"], left_style_info))
    if customer.get("email"):
        left_para.append(Paragraph(customer["email"], left_style_info))
    if customer.get("address"):
        left_para.append(Paragraph(customer["address"], left_style_info))

    # Right block: big INVOICE word + # and date
    invoice_word_style = ParagraphStyle(
        "InvWord", fontName=FONT_NAME_BOLD, fontSize=42,
        textColor=ORANGE, alignment=TA_RIGHT, leading=44,
    )
    invoice_meta_style = ParagraphStyle(
        "InvMeta", fontName=FONT_NAME_BOLD, fontSize=11,
        textColor=DARK_TEXT, alignment=TA_RIGHT, leading=14,
    )
    qn = quote_data.get("quote_number", "?")
    dt = quote_data.get("date", datetime.now())
    if isinstance(dt, datetime):
        date_str = dt.strftime("%d %b %Y")
    else:
        date_str = str(dt)

    # Package badge (small coloured chip showing which package)
    badge_style = ParagraphStyle(
        "Badge", fontName=FONT_NAME_BOLD, fontSize=10,
        textColor=colors.white, alignment=TA_CENTER, leading=12,
    )
    badge_tbl = Table(
        [[Paragraph(f"{pkg_label.upper()} PACKAGE", badge_style)]],
        colWidths=[60 * mm],
    )
    badge_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), badge_color),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    right_para = []
    right_para.append(Paragraph("INVOICE", invoice_word_style))
    right_para.append(Spacer(1, 2 * mm))
    # Invoice # box
    inv_num_style = ParagraphStyle(
        "InvNum", fontName=FONT_NAME_BOLD, fontSize=11,
        textColor=DARK_TEXT, alignment=TA_RIGHT,
    )
    right_para.append(Paragraph(
        f'Invoice #&nbsp;&nbsp;<font face="{FONT_NAME_BOLD}"><span backColor="#FFFFFF">'
        f'&nbsp;{qn}&nbsp;</span></font>', inv_num_style))
    right_para.append(Paragraph(f"Date: {date_str}", invoice_meta_style))
    right_para.append(Spacer(1, 3 * mm))
    right_para.append(badge_tbl)

    # Combine left + right
    top_table = Table(
        [[left_para, right_para]],
        colWidths=[85 * mm, 85 * mm],
    )
    top_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(top_table)
    story.append(Spacer(1, 10 * mm))

    # =====================================================================
    # ITEMS TABLE — No / # / Item Description / Qty / Price / VAT / Total
    # =====================================================================
    header_style = ParagraphStyle(
        "Hdr", fontName=FONT_NAME, fontSize=9, textColor=MUTED_GREY,
        alignment=TA_CENTER,
    )
    cell_no_style = ParagraphStyle(
        "CellNo", fontName=FONT_NAME_BOLD, fontSize=11, textColor=DARK_TEXT,
        alignment=TA_CENTER, leading=14,
    )
    cell_name_style = ParagraphStyle(
        "CellName", fontName=FONT_NAME_BOLD, fontSize=10, textColor=DARK_TEXT,
        alignment=TA_CENTER, leading=13,
    )
    cell_num_style = ParagraphStyle(
        "CellNum", fontName=FONT_NAME_BOLD, fontSize=10, textColor=DARK_TEXT,
        alignment=TA_CENTER, leading=13,
    )

    items = quote_data.get("items", [])

    # Header row
    table_rows = [[
        Paragraph("No", header_style),
        Paragraph("#", header_style),
        Paragraph("Item Description", header_style),
        Paragraph("Qty", header_style),
        Paragraph("Price", header_style),
        Paragraph("Vat", header_style),
        Paragraph("Total", header_style),
    ]]

    # Data rows
    for idx, item in enumerate(items, start=1):
        name = item.get("name", "")
        sku = item.get("sku", "")
        # Show name in 2-3 lines max; KeyCRM truncates with "..." — we keep readable
        display_name = name
        if len(display_name) > 70:
            display_name = display_name[:67] + "..."

        qty = item.get("qty", 1)
        base = item.get("base", 0)
        vat = item.get("vat", 0)
        # KeyCRM "Total" = (base + vat) × qty
        line_total = (base + vat) * qty

        table_rows.append([
            Paragraph(str(idx), cell_no_style),
            Paragraph("", cell_no_style),  # # icon column (left blank — no icons)
            Paragraph(display_name, cell_name_style),
            Paragraph(str(qty), cell_num_style),
            Paragraph(_gbp_keycrm(base), cell_num_style),
            Paragraph(_gbp_keycrm(vat), cell_num_style),
            Paragraph(_format_total(line_total), cell_num_style),
        ])

    items_table = Table(
        table_rows,
        colWidths=[12 * mm, 16 * mm, 60 * mm, 14 * mm, 22 * mm, 20 * mm, 26 * mm],
        repeatRows=1,
    )
    items_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        # Header bottom border
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, LIGHT_GREY),
        # Row separators (very light)
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, LIGHT_GREY),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 6 * mm))

    # =====================================================================
    # PAYMENT DETAILS (left) + TOTALS (right)
    # =====================================================================
    pay_label = ParagraphStyle(
        "PayLabel", fontName=FONT_NAME_BOLD, fontSize=9, textColor=DARK_TEXT,
        leading=12,
    )
    pay_value = ParagraphStyle(
        "PayValue", fontName=FONT_NAME, fontSize=9, textColor=DARK_TEXT,
        leading=12,
    )

    payment_block = [
        Paragraph('<b>Payment details:</b> Lloyds Bank', pay_value),
        Paragraph('<b>Account number:</b> 48253368', pay_value),
        Paragraph('<b>Sort code:</b> 30-99-50', pay_value),
        Paragraph('<b>IBAN:</b> GB38LOYD30995048253368', pay_value),
        Paragraph('<b>BIC:</b> LOYDGB21287', pay_value),
        Paragraph('<b>VAT:</b> 455026800', pay_value),
    ]

    totals_label_style = ParagraphStyle(
        "TotLbl", fontName=FONT_NAME_BOLD, fontSize=11, textColor=DARK_TEXT,
        alignment=TA_LEFT, leading=16,
    )
    totals_value_style = ParagraphStyle(
        "TotVal", fontName=FONT_NAME_BOLD, fontSize=11, textColor=DARK_TEXT,
        alignment=TA_RIGHT, leading=16,
    )
    grand_label_style = ParagraphStyle(
        "GrLbl", fontName=FONT_NAME_BOLD, fontSize=11, textColor=MUTED_GREY,
        alignment=TA_LEFT, leading=18,
    )
    grand_value_style = ParagraphStyle(
        "GrVal", fontName=FONT_NAME_BOLD, fontSize=15, textColor=ORANGE,
        alignment=TA_RIGHT, leading=18,
    )

    subtotal = quote_data.get("subtotal", 0)
    vat_total = quote_data.get("vat_total", 0)
    discount = quote_data.get("discount", 0)
    grand = quote_data.get("grand_total", 0)

    totals_tbl = Table(
        [
            [Paragraph("Subtotal", totals_label_style),
             Paragraph(_format_total(subtotal), totals_value_style)],
            [Paragraph("Discount", totals_label_style),
             Paragraph(f"£{discount:.2f}" if discount else "£0.00", totals_value_style)],
            [Paragraph("Total VAT", totals_label_style),
             Paragraph(_format_total(vat_total), totals_value_style)],
            [Spacer(1, 3 * mm), Spacer(1, 3 * mm)],
            [Paragraph("Grand total", grand_label_style),
             Paragraph(_grand_total_str(grand), grand_value_style)],
        ],
        colWidths=[32 * mm, 48 * mm],
    )
    totals_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    bottom_tbl = Table(
        [[payment_block, totals_tbl]],
        colWidths=[90 * mm, 80 * mm],
    )
    bottom_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(bottom_tbl)
    story.append(Spacer(1, 8 * mm))

    # =====================================================================
    # TERMS & CONDITIONS
    # =====================================================================
    terms_title_style = ParagraphStyle(
        "TermsTitle", fontName=FONT_NAME_BOLD, fontSize=11, textColor=DARK_TEXT,
        spaceAfter=4,
    )
    terms_style = ParagraphStyle(
        "Terms", fontName=FONT_NAME, fontSize=9, textColor=DARK_TEXT,
        leading=14,
    )

    story.append(Paragraph("<b>TERMS &amp; CONDITIONS</b>", terms_title_style))
    story.append(Paragraph("1. Prices are valid for 1 week", terms_style))
    story.append(Paragraph("2. Equipment delivery time is from 5-7 working days", terms_style))
    story.append(Paragraph("3. Work completion time is from 3 to 5 days", terms_style))

    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
