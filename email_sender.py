"""
SPETS SECURITY — Email sender via Resend (multilingual)
"""
import os
import base64
import logging
from typing import Optional

import requests

from translations import t

log = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"

FROM_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")
FROM_NAME = os.getenv("SENDER_NAME", "Spets Security LTD")
REPLY_TO_EMAIL = os.getenv("REPLY_TO_EMAIL", "r.brain@spetstech.co.uk")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")


def send_quote_email(
    to_email: str,
    customer_name: str,
    quote_number: str,
    grand_total: float,
    pdf_bytes: bytes,
    pdf_filename: Optional[str] = None,
    lang: str = "en",
) -> bool:
    """Send quote PDF to customer via Resend, in the chosen language."""
    if not RESEND_API_KEY:
        log.error("RESEND_API_KEY is not set in environment")
        return False

    if pdf_filename is None:
        pdf_filename = f"Quote-{quote_number}.pdf"

    pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")

    subject = t("email_subject", lang, n=quote_number)

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; color: #14213D; line-height: 1.6;">
      <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #14213D; color: #FCA311; padding: 20px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px;">SPETS</h1>
          <p style="margin: 5px 0 0; font-size: 12px; letter-spacing: 2px;">ALWAYS NEAR</p>
        </div>

        <div style="padding: 30px 20px;">
          <p>{t("email_hello", lang, name=customer_name)}</p>

          <p>{t("email_intro", lang)}</p>

          <p>{t("email_find_pdf", lang, n=quote_number)}</p>

          <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
            <tr>
              <td style="padding: 12px; background: #F0F4F8; border-left: 4px solid #FCA311;">
                <strong>{t("email_total_label", lang)}</strong> £{grand_total:,.2f} {t("email_incl_vat", lang)}
              </td>
            </tr>
          </table>

          <p>{t("email_valid_7days", lang)}</p>

          <p>{t("email_next_title", lang)}</p>
          <ul>
            <li>{t("email_next_1", lang)}</li>
            <li>{t("email_next_2", lang)}</li>
            <li>{t("email_next_3", lang)}</li>
            <li>{t("email_next_4", lang)}</li>
          </ul>

          <p>{t("email_questions", lang)}</p>

          <p style="margin-top: 30px;">
            {t("email_best_regards", lang)}<br>
            <strong>Spets Security LTD</strong>
          </p>
        </div>

        <div style="background: #14213D; color: white; padding: 15px; text-align: center; font-size: 12px;">
          <p style="margin: 0;">
            📞 +44 7706 906079 &nbsp;|&nbsp; ✉ r.brain@spetstech.co.uk<br>
            1 Oakcroft Road, Chessington, Surrey, KT9 1BD, United Kingdom<br>
            VAT: 455026800
          </p>
        </div>
      </div>
    </body>
    </html>
    """

    payload = {
        "from": f"{FROM_NAME} <{FROM_EMAIL}>",
        "to": [to_email],
        "reply_to": REPLY_TO_EMAIL,
        "subject": subject,
        "html": html_body,
        "attachments": [{
            "filename": pdf_filename,
            "content": pdf_b64,
        }],
    }

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=30)
        if 200 <= response.status_code < 300:
            email_id = response.json().get("id", "?")
            log.info(f"Email sent to {to_email} (quote #{quote_number}, lang={lang}, resend id={email_id})")
            return True
        else:
            log.error(f"Resend error {response.status_code}: {response.text}")
            return False
    except requests.RequestException as e:
        log.error(f"Resend request failed: {e}")
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
) -> bool:
    """Notify admin in Telegram — always in English so manager understands."""
    text = (
        f"🆕 *New CCTV Quote #{quote_number}*\n\n"
        f"👤 *Client:* {customer_name}\n"
        f"📞 *Phone:* {customer_phone}\n"
        f"📧 *Email:* {customer_email}\n\n"
        f"💷 *Total:* £{grand_total:,.2f}"
    )
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
