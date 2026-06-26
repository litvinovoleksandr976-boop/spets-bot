"""
SPETS SECURITY — Email sender via Gmail SMTP (3 packages)
Sends one email with 3 PDFs attached and a comparison table in body.
No domain needed — uses Gmail App Password.
"""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
from typing import Optional

import requests  # still used for admin Telegram notification

from translations import t

log = logging.getLogger(__name__)

# Gmail SMTP settings
GMAIL_USER = os.getenv("GMAIL_USER", "spets.services@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")  # 16-char app password
FROM_NAME = os.getenv("SENDER_NAME", "Spets Security LTD")
REPLY_TO_EMAIL = os.getenv("REPLY_TO_EMAIL", "spets.services@gmail.com")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_3_packages_email(
    to_email: str,
    customer_name: str,
    quote_number: str,
    quotes: dict,
    pdfs: dict,
    lang: str = "en",
) -> bool:
    """
    Send one email with 3 PDFs (Budget/Balance/Elite) attached via Gmail SMTP.

    quotes = {"budget": {...}, "balance": {...}, "elite": {...}}
    pdfs   = {"budget": b"...", "balance": b"...", "elite": b"..."}
    """
    if not GMAIL_APP_PASSWORD:
        log.error("GMAIL_APP_PASSWORD is not set — cannot send customer email")
        return False

    subject = t("email_subject", lang, n=quote_number)

    # Localized labels
    incl_vat = t("email_incl_vat", lang)
    hello = t("email_hello", lang, name=customer_name)
    intro = t("email_intro", lang)
    valid_7 = t("email_valid_7days", lang)
    next_title = t("email_next_title", lang)
    n1 = t("email_next_1", lang)
    n2 = t("email_next_2", lang)
    n3 = t("email_next_3", lang)
    n4 = t("email_next_4", lang)
    questions = t("email_questions", lang)
    regards = t("email_best_regards", lang)

    budget_total = quotes["budget"]["grand_total"]
    balance_total = quotes["balance"]["grand_total"]
    elite_total = quotes["elite"]["grand_total"]

    if lang == "ru":
        compare_title = "3 пакета на выбор:"
        budget_desc = "Камеры HiLook 4MP ColorVu + HiLook NVR"
        balance_desc = "Камеры Hikvision 4MP ColorVu 3.0 + AcuSense NVR"
        elite_desc = "Камеры Hikvision 4K 8MP + AcuSense NVR"
        attachments_note = "К письму прикреплены 3 PDF — выберите подходящий вам пакет."
    elif lang == "uk":
        compare_title = "3 пакети на вибір:"
        budget_desc = "Камери HiLook 4MP ColorVu + HiLook NVR"
        balance_desc = "Камери Hikvision 4MP ColorVu 3.0 + AcuSense NVR"
        elite_desc = "Камери Hikvision 4K 8MP + AcuSense NVR"
        attachments_note = "До листа додано 3 PDF — оберіть пакет, що вам підходить."
    else:
        compare_title = "Your 3 options:"
        budget_desc = "HiLook 4MP ColorVu cameras + HiLook NVR"
        balance_desc = "Hikvision 4MP ColorVu 3.0 cameras + AcuSense NVR"
        elite_desc = "Hikvision 4K 8MP cameras + AcuSense NVR"
        attachments_note = "3 PDF quotes are attached — choose the package that fits you best."

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; color: #14213D; line-height: 1.6;">
      <div style="max-width: 640px; margin: 0 auto; padding: 20px;">

        <div style="background: #0A0C12; color: #FCA311; padding: 20px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px;">SPETS</h1>
          <p style="margin: 5px 0 0; font-size: 12px; letter-spacing: 2px;">ALWAYS NEAR</p>
        </div>

        <div style="padding: 30px 20px;">
          <p>{hello}</p>
          <p>{intro}</p>

          <h3 style="color: #14213D; margin-top: 30px;">{compare_title}</h3>

          <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
            <tr>
              <td style="padding: 15px; background: #E8F5E9; border-left: 5px solid #2E7D32; border-radius: 4px;">
                <div style="font-size: 18px; font-weight: bold; color: #2E7D32;">🟢 Budget</div>
                <div style="font-size: 13px; color: #555; margin: 5px 0;">{budget_desc}</div>
                <div style="font-size: 22px; font-weight: bold; color: #14213D; margin-top: 8px;">£{budget_total:,.2f} <span style="font-size: 12px; color: #888;">{incl_vat}</span></div>
              </td>
            </tr>
            <tr><td style="height: 10px;"></td></tr>
            <tr>
              <td style="padding: 15px; background: #E3F2FD; border-left: 5px solid #1565C0; border-radius: 4px;">
                <div style="font-size: 18px; font-weight: bold; color: #1565C0;">🔵 Balance</div>
                <div style="font-size: 13px; color: #555; margin: 5px 0;">{balance_desc}</div>
                <div style="font-size: 22px; font-weight: bold; color: #14213D; margin-top: 8px;">£{balance_total:,.2f} <span style="font-size: 12px; color: #888;">{incl_vat}</span></div>
              </td>
            </tr>
            <tr><td style="height: 10px;"></td></tr>
            <tr>
              <td style="padding: 15px; background: #FFF8E1; border-left: 5px solid #F58A2C; border-radius: 4px;">
                <div style="font-size: 18px; font-weight: bold; color: #E07B1E;">🟡 Elite</div>
                <div style="font-size: 13px; color: #555; margin: 5px 0;">{elite_desc}</div>
                <div style="font-size: 22px; font-weight: bold; color: #14213D; margin-top: 8px;">£{elite_total:,.2f} <span style="font-size: 12px; color: #888;">{incl_vat}</span></div>
              </td>
            </tr>
          </table>

          <p style="background: #F0F4F8; padding: 12px; border-left: 4px solid #F58A2C;">
            📎 {attachments_note}
          </p>

          <p>{valid_7}</p>

          <p>{next_title}</p>
          <ul>
            <li>{n1}</li>
            <li>{n2}</li>
            <li>{n3}</li>
            <li>{n4}</li>
          </ul>

          <p>{questions}</p>

          <p style="margin-top: 30px;">
            {regards}<br>
            <strong>Spets Security LTD</strong>
          </p>
        </div>

        <div style="background: #0A0C12; color: white; padding: 15px; text-align: center; font-size: 12px;">
          <p style="margin: 0;">
            📞 +44 7706 906079 &nbsp;|&nbsp; ✉ spets.services@gmail.com<br>
            1 Oakcroft Road, Chessington, Surrey, KT9 1BD, United Kingdom<br>
            VAT: 455026800
          </p>
        </div>
      </div>
    </body>
    </html>
    """

    # Build MIME message
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = formataddr((FROM_NAME, GMAIL_USER))
    msg["To"] = to_email
    msg["Reply-To"] = REPLY_TO_EMAIL

    # HTML part
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)

    # Attach 3 PDFs
    for pkg_id in ("budget", "balance", "elite"):
        part = MIMEApplication(pdfs[pkg_id], _subtype="pdf")
        part.add_header(
            "Content-Disposition", "attachment",
            filename=f"Spets-Quote-{quote_number}-{pkg_id.capitalize()}.pdf",
        )
        msg.attach(part)

    # Send via Gmail SMTP
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, [to_email], msg.as_string())
        log.info(f"3-package email sent to {to_email} (quote #{quote_number}, lang={lang})")
        return True
    except Exception as e:
        log.error(f"Gmail SMTP send failed to {to_email}: {e}")
        return False


def send_admin_notification(
    admin_chat_id: str,
    bot_token: str,
    customer_name: str,
    customer_phone: str,
    customer_email: str,
    quote_number: str,
    grand_total: float,
    keycrm_url: Optional[str] = None,
    all_packages: Optional[dict] = None,
    object_type: str = "",
    camera_count: int = 0,
) -> bool:
    """Notify admin (manager) in Telegram — English, with all 3 prices."""
    text = (
        f"🆕 *New CCTV Quote #{quote_number}*\n\n"
        f"👤 *Client:* {customer_name}\n"
        f"📞 *Phone:* {customer_phone}\n"
        f"📧 *Email:* {customer_email}\n"
        f"🏠 *Type:* {object_type or '?'}\n"
        f"📹 *Cameras:* {camera_count}\n"
    )
    if all_packages:
        text += (
            f"\n💷 *3 packages sent:*\n"
            f"🟢 Budget:  £{all_packages.get('budget', 0):,.2f}\n"
            f"🔵 Balance: £{all_packages.get('balance', 0):,.2f}\n"
            f"🟡 Elite:   £{all_packages.get('elite', 0):,.2f}"
        )
    else:
        text += f"\n💷 *Total:* £{grand_total:,.2f}"

    if keycrm_url:
        text += f"\n\n🔗 [Open in KeyCRM]({keycrm_url})"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": admin_chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        log.error(f"Telegram notify failed: {e}")
        return False
