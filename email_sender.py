"""
SPETS SECURITY — Email sender via Resend
Why Resend: Railway blocks outbound SMTP ports, so we use Resend's HTTPS API.
Free tier: 100 emails/day, 3,000/month — generous and permanent.
Docs: https://resend.com/docs/api-reference/emails/send-email
"""
import os
import base64
import logging
from typing import Optional

import requests

log = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"

# Env config
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
) -> bool:
    """
    Send quote PDF to customer via Resend.
    Returns True on success, False on failure (and logs the reason).
    """
    if not RESEND_API_KEY:
        log.error("RESEND_API_KEY is not set in environment")
        return False

    if pdf_filename is None:
        pdf_filename = f"Quote-{quote_number}.pdf"

    # Resend expects attachments as base64-encoded strings
    pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")

    subject = f"Your CCTV Quote #{quote_number} — Spets Security LTD"

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
          <p>Hello {customer_name},</p>

          <p>Thank you for your interest in Spets Security CCTV solutions.</p>

          <p>Please find your personalised quote <strong>#{quote_number}</strong> attached as a PDF.</p>

          <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
            <tr>
              <td style="padding: 12px; background: #F0F4F8; border-left: 4px solid #FCA311;">
                <strong>Quote Total:</strong> £{grand_total:,.2f} (incl. VAT)
              </td>
            </tr>
          </table>

          <p><strong>Quote is valid for 7 days.</strong></p>

          <p>What happens next:</p>
          <ul>
            <li>Review the quote at your convenience</li>
            <li>Reply to this email or call us with any questions</li>
            <li>Equipment delivery: 5-7 working days from order</li>
            <li>Installation: 3-5 days after equipment arrives</li>
          </ul>

          <p>If you have any questions, just reply to this email or call us directly.</p>

          <p style="margin-top: 30px;">
            Best regards,<br>
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
            log.info(f"Email sent to {to_email} (quote #{quote_number}, resend id={email_id})")
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
    """
    Send Telegram notification to admin (you) when new quote is created.
    Uses Telegram Bot API directly — no email service needed for this.
    """
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
