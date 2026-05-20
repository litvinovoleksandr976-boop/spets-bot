"""
SPETS SECURITY — PDF Quote Generator (multilingual EN/RU/UK)

Cyrillic support: bundled DejaVu Sans fonts in fonts/ folder.
"""
import io
import os
import logging
from datetime import datetime

log = logging.getLogger(__name__)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from translations import t

# Brand colours
NAVY = colors.HexColor("#14213D")
ORANGE = colors.HexColor("#FCA311")
LIGHT_GREY = colors.HexColor("#F0F4F8")
WHITE = colors.white
DARK_TEXT = colors.HexColor("#333333")
MID_GREY = colors.HexColor("#888888")

# Register Cyrillic-capable fonts. Try common Linux paths.
FONT_NAME = "Helvetica"
FONT_NAME_BOLD = "Helvetica-Bold"
CYRILLIC_REGISTERED = False

_FONT_CANDIDATES = [
    # 1. Root of project (works if uploaded to GitHub root)
    (os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSans.ttf"),
     os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSans-Bold.ttf")),
    # 2. Bundled fonts inside fonts/ subfolder
    (os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "DejaVuSans.ttf"),
     os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "DejaVuSans-Bold.ttf")),
    # 3. Path on Debian/Ubuntu (fallback if system has fonts)
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    # 4. Alpine / minimal containers
    ("/usr/share/fonts/TTF/DejaVuSans.ttf",
     "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"),
    # 5. Liberation fonts as alternative
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
]


def _register_cyrillic_font():
    """Try to register a Cyrillic-capable font. Sets globals on success."""
    global FONT_NAME, FONT_NAME_BOLD, CYRILLIC_REGISTERED
    for regular_path, bold_path in _FONT_CANDIDATES:
        if os.path.exists(regular_path):
            try:
                pdfmetrics.registerFont(TTFont("CyrSans", regular_path))
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont("CyrSans-Bold", bold_path))
                    FONT_NAME = "CyrSans"
                    FONT_NAME_BOLD = "CyrSans-Bold"
                else:
                    FONT_NAME = "CyrSans"
                    FONT_NAME_BOLD = "CyrSans"
                CYRILLIC_REGISTERED = True
                log.info(f"Cyrillic font registered from: {regular_path}")
                return
            except Exception as e:
                log.warning(f"Font registration failed for {regular_path}: {e}")
                continue
    log.warning("NO Cyrillic font found — Russian/Ukrainian text will show as squares!")


_register_cyrillic_font()


def _header_footer(canvas_obj: canvas.Canvas, doc):
    """Draw the orange-navy decorative banner."""
    canvas_obj.saveState()
    width, height = A4

    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, height - 50 * mm, 70 * mm, 50 * mm, fill=1, stroke=0)
    p = canvas_obj.beginPath()
    p.moveTo(0, height - 50 * mm)
    p.lineTo(70 * mm, height - 50 * mm)
    p.lineTo(70 * mm, height - 30 * mm)
    p.lineTo(20 * mm, height - 50 * mm)
    p.close()
    canvas_obj.setFillColor(ORANGE)
    canvas_obj.drawPath(p, fill=1, stroke=0)

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
    quote_data must include 'lang' field (en/ru/uk) — defaults to 'en'.
    """
    lang = quote_data.get("lang", "en")

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

    # Custom styles — use registered Cyrillic font
    h_company = ParagraphStyle(
        "company", fontName=FONT_NAME_BOLD, fontSize=12, textColor=NAVY,
        alignment=TA_RIGHT, leading=14,
    )
    s_address = ParagraphStyle(
        "addr", fontName=FONT_NAME, fontSize=9, textColor=DARK_TEXT,
        alignment=TA_RIGHT, leading=12,
    )
    h_brand = ParagraphStyle(
        "brand", fontName=FONT_NAME_BOLD, fontSize=24, textColor=ORANGE,
        alignment=TA_RIGHT, leading=26,
    )
    s_tagline = ParagraphStyle(
        "tagline", fontName=FONT_NAME, fontSize=8, textColor=ORANGE,
        alignment=TA_RIGHT,
    )
    h_invoice_word = ParagraphStyle(
        "inv", fontName=FONT_NAME_BOLD, fontSize=36, textColor=ORANGE,
        alignment=TA_RIGHT, leading=40,
    )
    s_normal = ParagraphStyle(
        "n", fontName=FONT_NAME, fontSize=10, textColor=DARK_TEXT, leading=13,
    )
    s_bold = ParagraphStyle(
        "b", fontName=FONT_NAME_BOLD, fontSize=10, textColor=DARK_TEXT, leading=13,
    )

    # =====================================================
    # TOP: brand + address
    # =====================================================
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
    top_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(top_table)
    story.append(Spacer(1, 8 * mm))

    # =====================================================
    # Invoice block
    # =====================================================
    date_str = (quote_data.get("date") or datetime.now()).strftime("%d %B %Y")
    qn = quote_data["quote_number"]
    cust = quote_data["customer"]

    left_block = [
        [Paragraph(f"<b>{t('pdf_invoice_to', lang)}</b>",
                   ParagraphStyle("bl", fontName=FONT_NAME_BOLD, fontSize=12, leading=14))],
        [Paragraph(cust.get("name", "Client"), s_normal)],
        [Paragraph(cust.get("phone", ""), s_normal)],
        [Paragraph(cust.get("email", ""), s_normal)],
        [Paragraph(cust.get("address", ""), s_normal)],
    ]
    right_block = [
        [Paragraph(f"<b>{t('pdf_invoice_word', lang)}</b>", h_invoice_word)],
        [Spacer(1, 2 * mm)],
        [Paragraph(f"<b>{t('pdf_quote_label', lang)} {qn}</b>",
                   ParagraphStyle("qn", fontName=FONT_NAME_BOLD, fontSize=12, alignment=TA_RIGHT))],
        [Paragraph(f"<b>{t('pdf_date_label', lang)}</b> {date_str}",
                   ParagraphStyle("dt", fontName=FONT_NAME, fontSize=10, alignment=TA_RIGHT))],
    ]

    inv_table = Table(
        [[Table(left_block, colWidths=[90 * mm]), Table(right_block, colWidths=[80 * mm])]],
        colWidths=[90 * mm, 90 * mm],
    )
    inv_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(inv_table)
    story.append(Spacer(1, 8 * mm))

    # =====================================================
    # ITEMS TABLE
    # =====================================================
    header = [
        t("pdf_col_no", lang),
        t("pdf_col_item", lang),
        t("pdf_col_qty", lang),
        t("pdf_col_price", lang),
        t("pdf_col_vat", lang),
        t("pdf_col_total", lang),
    ]
    rows = [header]

    for idx, item in enumerate(quote_data["items"], start=1):
        line_total = (item["base"] + item["vat"]) * item["qty"]
        # Replace English "Installation CCTV" with localized version
        name = item["name"]
        if name == "Installation CCTV":
            name = t("installation_label", lang)
        rows.append([
            str(idx),
            name[:60] + ("..." if len(name) > 60 else ""),
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
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GREY),
        ("TEXTCOLOR", (0, 0), (-1, 0), MID_GREY),
        ("FONTNAME", (0, 0), (-1, 0), FONT_NAME_BOLD),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 1), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK_TEXT),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#FAFAFA")]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8 * mm))

    # =====================================================
    # Payment + Totals
    # =====================================================
    payment_text = (
        f"<b>{t('pdf_payment_details', lang)}</b> Lloyds Bank<br/>"
        f"<b>{t('pdf_account_number', lang)}</b> 48253368<br/>"
        f"<b>{t('pdf_sort_code', lang)}</b> 30-99-50<br/>"
        f"<b>IBAN:</b> GB38LOYD30995048253368<br/>"
        f"<b>BIC:</b> LOYDGB21287<br/>"
        f"<b>VAT:</b> 455026800"
    )
    payment_para = Paragraph(payment_text, s_normal)

    totals_rows = [
        [t("pdf_subtotal", lang), f"£{quote_data['subtotal']:.2f}"],
        [t("pdf_discount", lang), f"£{quote_data.get('discount', 0):.2f}"],
        [t("pdf_total_vat", lang), f"£{quote_data['vat_total']:.2f}"],
        ["", ""],
        [t("pdf_grand_total", lang), f"{quote_data['grand_total']:.2f} GBP"],
    ]
    totals_table = Table(totals_rows, colWidths=[40 * mm, 35 * mm])
    totals_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -2), FONT_NAME_BOLD),
        ("FONTSIZE", (0, 0), (-1, -2), 11),
        ("FONTNAME", (0, -1), (-1, -1), FONT_NAME_BOLD),
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
    bottom_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(bottom_table)
    story.append(Spacer(1, 12 * mm))

    # =====================================================
    # Terms
    # =====================================================
    story.append(Paragraph(f"<b>{t('pdf_terms_title', lang)}</b>",
                           ParagraphStyle("t", fontName=FONT_NAME_BOLD, fontSize=11, leading=14)))
    story.append(Spacer(1, 2 * mm))
    for term_key in ("pdf_term_1", "pdf_term_2", "pdf_term_3"):
        story.append(Paragraph(t(term_key, lang), s_normal))

    story.append(Spacer(1, 10 * mm))

    contact = Paragraph(
        '<font color="#FCA311"><b>📞</b></font> <b>+44 7706 906079</b> &nbsp;&nbsp;&nbsp;'
        '<font color="#FCA311"><b>✉</b></font> <b>r.brain@spetstech.co.uk</b>',
        ParagraphStyle("c", fontName=FONT_NAME, fontSize=11, leading=14)
    )
    story.append(contact)

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)

    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


# =====================================================================
# QUICK TEST
# =====================================================================
if __name__ == "__main__":
    from pricing import build_quote

    for lang in ("en", "ru", "uk"):
        quote = build_quote(camera_count=6, camera_tier="premium", archive_choice="2_weeks")
        quote["quote_number"] = f"TEST-{lang}"
        quote["date"] = datetime.now()
        quote["customer"] = {
            "name": {"en": "John Smith", "ru": "Иван Иванов", "uk": "Іван Іваненко"}[lang],
            "phone": "+44 7700 900123",
            "email": "test@example.com",
            "address": "10 Downing St, London",
        }
        quote["lang"] = lang

        pdf_bytes = generate_quote_pdf(quote)
        with open(f"/tmp/test_quote_{lang}.pdf", "wb") as f:
            f.write(pdf_bytes)
        print(f"PDF {lang}: /tmp/test_quote_{lang}.pdf ({len(pdf_bytes)} bytes)")
