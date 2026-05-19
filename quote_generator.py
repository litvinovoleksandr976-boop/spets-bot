"""
SPETS SECURITY — PDF Quote Generator
Generates branded PDF quotes in the style of invoice #183.
Uses ReportLab (already in requirements).
"""
import io
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.pdfgen import canvas

# Brand colours (from invoice #183)
NAVY = colors.HexColor("#14213D")
ORANGE = colors.HexColor("#FCA311")
LIGHT_GREY = colors.HexColor("#F0F4F8")
WHITE = colors.white
DARK_TEXT = colors.HexColor("#333333")
MID_GREY = colors.HexColor("#888888")


def _header_footer(canvas_obj: canvas.Canvas, doc):
    """Draw the orange-navy decorative banner top-left and bottom-right."""
    canvas_obj.saveState()
    width, height = A4

    # Top-left navy block
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, height - 50 * mm, 70 * mm, 50 * mm, fill=1, stroke=0)
    # Orange diagonal accent (top-left)
    p = canvas_obj.beginPath()
    p.moveTo(0, height - 50 * mm)
    p.lineTo(70 * mm, height - 50 * mm)
    p.lineTo(70 * mm, height - 30 * mm)
    p.lineTo(20 * mm, height - 50 * mm)
    p.close()
    canvas_obj.setFillColor(ORANGE)
    canvas_obj.drawPath(p, fill=1, stroke=0)

    # Bottom-right accent (mirror)
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(width - 70 * mm, 0, 70 * mm, 50 * mm, fill=1, stroke=0)
    p2 = canvas_obj.beginPath()
    p2.moveTo(width - 70 * mm, 50 * mm)
    p2.lineTo(width - 70 * mm, 30 * mm)
    p2.lineTo(width - 20 * mm, 50 * mm)
    p2.close()
    canvas_obj.setFillColor(ORANGE)
    canvas_obj.drawPath(p2, fill=1, stroke=0)

    canvas_obj.restoreState()


def generate_quote_pdf(quote_data: dict) -> bytes:
    """
    Generate PDF and return bytes.

    quote_data structure:
    {
        "quote_number": "184",
        "date": datetime (or None — auto-set),
        "customer": {
            "name": "John Smith",
            "phone": "+44...",
            "email": "...",
            "address": "..." (optional),
        },
        "items": [
            {"name": "...", "sku": "...", "qty": 4, "base": 101.00, "vat": 20.20, "total": 121.20},
            ...
        ],
        "subtotal": 1082.00,
        "vat_total": 216.40,
        "discount": 0.00,
        "grand_total": 1298.40,
    }
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Quote #{quote_data['quote_number']} — Spets Security",
        author="Spets Security LTD",
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    h_company = ParagraphStyle(
        "company", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=12, textColor=NAVY,
        alignment=TA_RIGHT, leading=14,
    )
    s_address = ParagraphStyle(
        "addr", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9, textColor=DARK_TEXT,
        alignment=TA_RIGHT, leading=12,
    )
    h_brand = ParagraphStyle(
        "brand", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=24, textColor=ORANGE,
        alignment=TA_RIGHT, leading=26,
    )
    s_tagline = ParagraphStyle(
        "tagline", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8, textColor=ORANGE,
        alignment=TA_RIGHT,
    )
    h_invoice_word = ParagraphStyle(
        "inv", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=36, textColor=ORANGE,
        alignment=TA_RIGHT, leading=40,
    )
    s_normal = ParagraphStyle(
        "n", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10, textColor=DARK_TEXT, leading=13,
    )
    s_bold = ParagraphStyle(
        "b", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10, textColor=DARK_TEXT, leading=13,
    )
    s_small = ParagraphStyle(
        "sm", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8, textColor=MID_GREY, leading=10,
    )

    # =================================================================
    # TOP: Brand + Address right side (top-left is left for the navy/orange banner from page func)
    # =================================================================
    # Spacer to push content below the banner
    story.append(Spacer(1, 5 * mm))

    top_right = [
        [Paragraph("<b>SPETS</b>", h_brand)],
        [Paragraph("ALWAYS NEAR", s_tagline)],
        [Spacer(1, 4 * mm)],
        [Paragraph("<b>Spets Security LTD</b>", h_company)],
        [Paragraph("1 Oakcroft Road, Chessington, Surrey,<br/>KT9 1BD, United Kingdom", s_address)],
    ]
    top_table = Table(
        [[Spacer(1, 1), Table(top_right, colWidths=[80 * mm])]],
        colWidths=[100 * mm, 80 * mm],
    )
    top_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(top_table)
    story.append(Spacer(1, 8 * mm))

    # =================================================================
    # Invoice block: "Invoice To" (left) | "INVOICE #" (right)
    # =================================================================
    date_str = (quote_data.get("date") or datetime.now()).strftime("%d %B %Y")
    qn = quote_data["quote_number"]
    cust = quote_data["customer"]

    left_block = [
        [Paragraph("<b>Invoice To</b>", ParagraphStyle("bl", parent=s_bold, fontSize=12, leading=14))],
        [Paragraph(cust.get("name", "Client"), s_normal)],
        [Paragraph(cust.get("phone", ""), s_normal)],
        [Paragraph(cust.get("email", ""), s_normal)],
        [Paragraph(cust.get("address", ""), s_normal)],
    ]
    right_block = [
        [Paragraph("<b>INVOICE</b>", h_invoice_word)],
        [Spacer(1, 2 * mm)],
        [Paragraph(f"<b>Quote # {qn}</b>", ParagraphStyle("qn", parent=s_bold, fontSize=12, alignment=TA_RIGHT))],
        [Paragraph(f"<b>Date:</b> {date_str}", ParagraphStyle("dt", parent=s_normal, alignment=TA_RIGHT))],
    ]

    inv_table = Table(
        [[Table(left_block, colWidths=[90 * mm]), Table(right_block, colWidths=[80 * mm])]],
        colWidths=[90 * mm, 90 * mm],
    )
    inv_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(inv_table)
    story.append(Spacer(1, 8 * mm))

    # =================================================================
    # ITEMS TABLE
    # =================================================================
    header = ["No", "Item Description", "Qty", "Price", "VAT", "Total"]
    rows = [header]

    for idx, item in enumerate(quote_data["items"], start=1):
        line_total = (item["base"] + item["vat"]) * item["qty"]
        rows.append([
            str(idx),
            item["name"][:60] + ("..." if len(item["name"]) > 60 else ""),
            str(item["qty"]),
            f"£{item['base']:.2f}",
            f"£{item['vat']:.2f}",
            f"£{line_total:.2f}",
        ])

    items_table = Table(
        rows,
        colWidths=[12 * mm, 85 * mm, 15 * mm, 25 * mm, 22 * mm, 25 * mm],
    )
    items_table.setStyle(TableStyle([
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GREY),
        ("TEXTCOLOR", (0, 0), (-1, 0), MID_GREY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        # Body rows
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK_TEXT),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),       # No column
        ("ALIGN", (2, 1), (2, -1), "CENTER"),        # Qty
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),        # Money columns
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#FAFAFA")]),
        # Padding
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8 * mm))

    # =================================================================
    # PAYMENT INFO + TOTALS (two columns)
    # =================================================================
    payment_text = (
        "<b>Payment details:</b> Lloyds Bank<br/>"
        "<b>Account number:</b> 48253368<br/>"
        "<b>Sort code:</b> 30-99-50<br/>"
        "<b>IBAN:</b> GB38LOYD30995048253368<br/>"
        "<b>BIC:</b> LOYDGB21287<br/>"
        "<b>VAT:</b> 455026800"
    )
    payment_para = Paragraph(payment_text, s_normal)

    totals_rows = [
        ["Subtotal", f"£{quote_data['subtotal']:.2f}"],
        ["Discount", f"£{quote_data.get('discount', 0):.2f}"],
        ["Total VAT", f"£{quote_data['vat_total']:.2f}"],
        ["", ""],
        ["Grand total", f"{quote_data['grand_total']:.2f} GBP"],
    ]
    totals_table = Table(totals_rows, colWidths=[40 * mm, 35 * mm])
    totals_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -2), 11),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 12),
        ("TEXTCOLOR", (0, -1), (-1, -1), MID_GREY),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (-1, -2), DARK_TEXT),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEABOVE", (0, -1), (-1, -1), 1, MID_GREY),
    ]))

    bottom_table = Table(
        [[payment_para, totals_table]],
        colWidths=[100 * mm, 75 * mm],
    )
    bottom_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(bottom_table)
    story.append(Spacer(1, 12 * mm))

    # =================================================================
    # TERMS & CONDITIONS
    # =================================================================
    story.append(Paragraph("<b>TERMS &amp; CONDITIONS</b>",
                           ParagraphStyle("t", parent=s_bold, fontSize=11, leading=14)))
    story.append(Spacer(1, 2 * mm))
    terms = [
        "1. Prices are valid for 1 week",
        "2. Equipment delivery time is from 5-7 working days",
        "3. Work completion time is from 3 to 5 days",
    ]
    for t in terms:
        story.append(Paragraph(t, s_normal))

    story.append(Spacer(1, 10 * mm))

    # Contact line
    contact = Paragraph(
        '<font color="#FCA311"><b>📞</b></font> <b>+44 7706 906079</b> &nbsp;&nbsp;&nbsp;'
        '<font color="#FCA311"><b>✉</b></font> <b>r.brain@spetstech.co.uk</b>',
        ParagraphStyle("c", parent=s_normal, fontSize=11, leading=14)
    )
    story.append(contact)

    # Build PDF
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)

    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


# =====================================================================
# QUICK TEST
# =====================================================================
if __name__ == "__main__":
    from pricing import build_quote

    quote = build_quote(camera_count=6, camera_tier="premium", archive_choice="2_weeks")
    quote["quote_number"] = "TEST-001"
    quote["date"] = datetime.now()
    quote["customer"] = {
        "name": "John Smith",
        "phone": "+44 7700 900123",
        "email": "john.smith@example.com",
        "address": "10 Downing St, London, SW1A 2AA",
    }

    pdf_bytes = generate_quote_pdf(quote)
    with open("/tmp/test_quote.pdf", "wb") as f:
        f.write(pdf_bytes)
    print(f"PDF generated: /tmp/test_quote.pdf ({len(pdf_bytes)} bytes)")
