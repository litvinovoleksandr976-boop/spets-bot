"""
SPETS SECURITY — Email sender via Brevo HTTP API.
Works on Railway (HTTPS/443 — no blocked SMTP ports).
Free forever: 300 emails/day.

Functions (signatures unchanged):
  send_3_packages_email   - CCTV: 3 PDFs in one email
  send_single_quote_email - Ajax: one PDF quote
  send_admin_notification - Telegram notify to the manager
"""
import os
import base64
import logging

import requests

from translations import t

log = logging.getLogger(__name__)

BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "spets.services@gmail.com")
SENDER_NAME = os.getenv("SENDER_NAME", "Spets Security LTD")
REPLY_TO_EMAIL = os.getenv("REPLY_TO_EMAIL", "spets.services@gmail.com")

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def _send_via_brevo(to_email, subject, html, attachments):
    """attachments = [(filename, bytes), ...]. Returns True/False."""
    if not BREVO_API_KEY:
        log.error("BREVO_API_KEY is not set — cannot send email")
        return False

    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email}],
        "replyTo": {"email": REPLY_TO_EMAIL},
        "subject": subject,
        "htmlContent": html,
    }
    if attachments:
        payload["attachment"] = [
            {"name": fname, "content": base64.b64encode(data).decode("ascii")}
            for fname, data in attachments
        ]

    try:
        r = requests.post(
            BREVO_URL,
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            json=payload,
            timeout=30,
        )
        if r.status_code in (200, 201, 202):
            log.info(f"Brevo email sent to {to_email}")
            return True
        log.error(f"Brevo send failed ({r.status_code}) to {to_email}: {r.text[:300]}")
        return False
    except requests.RequestException as e:
        log.error(f"Brevo request error to {to_email}: {e}")
        return False


def send_3_packages_email(to_email, customer_name, quote_number, quotes, pdfs, lang="en") -> bool:
    """CCTV: one email with 3 PDFs (Budget/Balance/Elite)."""
    try:
        subject = t("email_subject", lang, n=quote_number)
        if subject.startswith("[missing"):
            subject = f"Spets Security — Quote #{quote_number}"
    except Exception:
        subject = f"Spets Security — Quote #{quote_number}"

    bt = quotes["budget"]["grand_total"]
    bl = quotes["balance"]["grand_total"]
    el = quotes["elite"]["grand_total"]

    if lang == "ru":
        hello = f"Здравствуйте, {customer_name}!"
        intro = "Спасибо за ваш запрос! Во вложении 3 варианта системы видеонаблюдения."
        compare = "3 пакета на выбор:"
        bd_l, bl_l, el_l = "Бюджетный", "Баланс", "Премиум"
        incl = "вкл. НДС"; att = "Во вложении 3 PDF — выберите подходящий пакет."
        regards = "С уважением,"
    elif lang == "uk":
        hello = f"Вітаємо, {customer_name}!"
        intro = "Дякуємо за ваш запит! У вкладенні 3 варіанти системи відеоспостереження."
        compare = "3 пакети на вибір:"
        bd_l, bl_l, el_l = "Бюджетний", "Баланс", "Преміум"
        incl = "вкл. ПДВ"; att = "У вкладенні 3 PDF — оберіть пакет, що вам підходить."
        regards = "З повагою,"
    else:
        hello = f"Hello {customer_name},"
        intro = "Thank you for your enquiry! Attached are 3 CCTV system options."
        compare = "Your 3 options:"
        bd_l, bl_l, el_l = "Budget", "Balance", "Elite"
        incl = "incl. VAT"; att = "3 PDF quotes are attached — choose the package that fits you best."
        regards = "Best regards,"

    html = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"></head>
    <body style="font-family:Arial,sans-serif;color:#14213D;line-height:1.6;">
      <div style="max-width:640px;margin:0 auto;padding:20px;">
        <div style="background:#0A0C12;color:#FCA311;padding:20px;text-align:center;">
          <h1 style="margin:0;font-size:28px;">SPETS</h1>
          <p style="margin:5px 0 0;font-size:12px;letter-spacing:2px;">ALWAYS NEAR</p>
        </div>
        <div style="padding:30px 20px;">
          <p>{hello}</p><p>{intro}</p>
          <h3 style="color:#14213D;margin-top:30px;">{compare}</h3>
          <table style="width:100%;margin:20px 0;border-collapse:collapse;">
            <tr><td style="padding:15px;background:#E8F5E9;border-left:5px solid #2E7D32;border-radius:4px;">
              <div style="font-size:18px;font-weight:bold;color:#2E7D32;">🟢 {bd_l}</div>
              <div style="font-size:22px;font-weight:bold;color:#14213D;margin-top:8px;">£{bt:,.2f} <span style="font-size:12px;color:#888;">{incl}</span></div>
            </td></tr><tr><td style="height:10px;"></td></tr>
            <tr><td style="padding:15px;background:#E3F2FD;border-left:5px solid #1565C0;border-radius:4px;">
              <div style="font-size:18px;font-weight:bold;color:#1565C0;">🔵 {bl_l}</div>
              <div style="font-size:22px;font-weight:bold;color:#14213D;margin-top:8px;">£{bl:,.2f} <span style="font-size:12px;color:#888;">{incl}</span></div>
            </td></tr><tr><td style="height:10px;"></td></tr>
            <tr><td style="padding:15px;background:#FFF8E1;border-left:5px solid #F58A2C;border-radius:4px;">
              <div style="font-size:18px;font-weight:bold;color:#E07B1E;">🟡 {el_l}</div>
              <div style="font-size:22px;font-weight:bold;color:#14213D;margin-top:8px;">£{el:,.2f} <span style="font-size:12px;color:#888;">{incl}</span></div>
            </td></tr>
          </table>
          <p style="background:#F0F4F8;padding:12px;border-left:4px solid #F58A2C;">📎 {att}</p>
          <p style="margin-top:30px;">{regards}<br><strong>Spets Security LTD</strong></p>
        </div>
        <div style="background:#0A0C12;color:white;padding:15px;text-align:center;font-size:12px;">
          <p style="margin:0;">📞 +44 7706 906079 &nbsp;|&nbsp; ✉ spets.services@gmail.com<br>
          1 Oakcroft Road, Chessington, Surrey, KT9 1BD, United Kingdom<br>VAT: 455026800</p>
        </div>
      </div>
    </body></html>
    """

    attachments = []
    for pkg_id in ("budget", "balance", "elite"):
        attachments.append((f"Spets-Quote-{quote_number}-{pkg_id.capitalize()}.pdf", pdfs[pkg_id]))

    return _send_via_brevo(to_email, subject, html, attachments)


def send_single_quote_email(to_email, customer_name, quote_number, pdf_bytes,
                            subject_label="Quote", lang="en") -> bool:
    """Ajax: one PDF quote."""
    if lang == "ru":
        subject = f"Spets Security — предложение #{quote_number} ({subject_label})"
        hello = f"Здравствуйте, {customer_name}!"
        intro = "Во вложении ваше индивидуальное предложение по беспроводной сигнализации Ajax."
        note = "Цена монтажа уточняется после осмотра объекта."
        regards = "С уважением,"
    elif lang == "uk":
        subject = f"Spets Security — пропозиція #{quote_number} ({subject_label})"
        hello = f"Вітаємо, {customer_name}!"
        intro = "У вкладенні ваша індивідуальна пропозиція щодо бездротової сигналізації Ajax."
        note = "Ціна монтажу уточнюється після огляду об'єкта."
        regards = "З повагою,"
    else:
        subject = f"Spets Security — Quote #{quote_number} ({subject_label})"
        hello = f"Hello {customer_name},"
        intro = "Please find attached your personalised Ajax wireless alarm quote."
        note = "Installation price is confirmed after a site survey."
        regards = "Best regards,"

    html = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"></head>
    <body style="font-family:Arial,sans-serif;color:#14213D;line-height:1.6;">
      <div style="max-width:640px;margin:0 auto;padding:20px;">
        <div style="background:#0A0C12;color:#FCA311;padding:20px;text-align:center;">
          <h1 style="margin:0;font-size:28px;">SPETS</h1>
          <p style="margin:5px 0 0;font-size:12px;letter-spacing:2px;">ALWAYS NEAR</p>
        </div>
        <div style="padding:30px 20px;">
          <p>{hello}</p><p>{intro}</p>
          <p style="background:#F0F4F8;padding:12px;border-left:4px solid #F58A2C;">📎 {note}</p>
          <p style="margin-top:30px;">{regards}<br><strong>Spets Security LTD</strong></p>
        </div>
        <div style="background:#0A0C12;color:white;padding:15px;text-align:center;font-size:12px;">
          <p style="margin:0;">📞 +44 7706 906079 &nbsp;|&nbsp; ✉ spets.services@gmail.com<br>
          1 Oakcroft Road, Chessington, Surrey, KT9 1BD, United Kingdom<br>VAT: 455026800</p>
        </div>
      </div>
    </body></html>
    """

    return _send_via_brevo(
        to_email, subject, html,
        [(f"Spets-Ajax-Quote-{quote_number}.pdf", pdf_bytes)],
    )


def send_admin_notification(admin_chat_id, bot_token, customer_name, customer_phone,
                            customer_email, quote_number, grand_total,
                            keycrm_url=None, all_packages=None,
                            object_type="", camera_count=0) -> bool:
    """Notify the manager in Telegram (English)."""
    text = (
        f"🆕 *New Quote #{quote_number}*\n\n"
        f"👤 *Client:* {customer_name}\n"
        f"📞 *Phone:* {customer_phone}\n"
        f"📧 *Email:* {customer_email}\n"
        f"🏠 *Type:* {object_type or '?'}\n"
    )
    if camera_count:
        text += f"📹 *Cameras:* {camera_count}\n"
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
        r = requests.post(url, json={
            "chat_id": admin_chat_id, "text": text,
            "parse_mode": "Markdown", "disable_web_page_preview": True,
        }, timeout=10)
        return r.status_code == 200
    except requests.RequestException as e:
        log.error(f"Telegram notify failed: {e}")
        return False
