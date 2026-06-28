"""
SPETS SECURITY — Email sender via Gmail SMTP.
Functions:
  send_3_packages_email   - CCTV: 3 PDFs (Budget/Balance/Elite) in one email
  send_single_quote_email - Ajax: one PDF quote
  send_admin_notification - Telegram notify to the manager
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

import requests  # for admin Telegram notification

from translations import t

log = logging.getLogger(__name__)

GMAIL_USER = os.getenv("GMAIL_USER", "spets.services@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
FROM_NAME = os.getenv("SENDER_NAME", "Spets Security LTD")
REPLY_TO_EMAIL = os.getenv("REPLY_TO_EMAIL", "spets.services@gmail.com")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_3_packages_email(to_email, customer_name, quote_number, quotes, pdfs, lang="en") -> bool:
    """CCTV: send one email with 3 PDFs (Budget/Balance/Elite) attached."""
    if not GMAIL_APP_PASSWORD:
        log.error("GMAIL_APP_PASSWORD is not set — cannot send customer email")
        return False

    try:
        subject = t("email_subject", lang, n=quote_number)
        if subject.startswith("[missing"):
            subject = f"Spets Security — Quote #{quote_number}"
    except Exception:
        subject = f"Spets Security — Quote #{quote_number}"

    budget_total = quotes["budget"]["grand_total"]
    balance_total = quotes["balance"]["grand_total"]
    elite_total = quotes["elite"]["grand_total"]

    if lang == "ru":
        hello = f"Здравствуйте, {customer_name}!"
        intro = "Спасибо за ваш запрос! Во вложении 3 варианта системы видеонаблюдения."
        compare = "3 пакета на выбор:"
        bd, bl, el = "Бюджетный", "Баланс", "Премиум"
        incl = "вкл. НДС"
        att = "Во вложении 3 PDF — выберите подходящий пакет."
        regards = "С уважением,"
    elif lang == "uk":
        hello = f"Вітаємо, {customer_name}!"
        intro = "Дякуємо за ваш запит! У вкладенні 3 варіанти системи відеоспостереження."
        compare = "3 пакети на вибір:"
        bd, bl, el = "Бюджетний", "Баланс", "Преміум"
        incl = "вкл. ПДВ"
        att = "У вкладенні 3 PDF — оберіть пакет, що вам підходить."
        regards = "З повагою,"
    else:
        hello = f"Hello {customer_name},"
        intro = "Thank you for your enquiry! Attached are 3 CCTV system options."
        compare = "Your 3 options:"
        bd, bl, el = "Budget", "Balance", "Elite"
        incl = "incl. VAT"
        att = "3 PDF quotes are attached — choose the package that fits you best."
        regards = "Best regards,"

    html_body = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; color: #14213D; line-height: 1.6;">
      <div style="max-width: 640px; margin: 0 auto; padding: 20px;">
        <div style="background: #0A0C12; color: #FCA311; padding: 20px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px;">SPETS</h1>
          <p style="margin: 5px 0 0; font-size: 12px; letter-spacing: 2px;">ALWAYS NEAR</p>
        </div>
        <div style="padding: 30px 20px;">
          <p>{hello}</p>
          <p>{intro}</p>
          <h3 style="color:#14213D; margin-top:30px;">{compare}</h3>
          <table style="width:100%; margin:20px 0; border-collapse:collapse;">
            <tr><td style="padding:15px; background:#E8F5E9; border-left:5px solid #2E7D32; border-radius:4px;">
              <div style="font-size:18px; font-weight:bold; color:#2E7D32;">🟢 {bd}</div>
              <div style="font-size:22px; font-weight:bold; color:#14213D; margin-top:8px;">£{budget_total:,.2f} <span style="font-size:12px; color:#888;">{incl}</span></div>
            </td></tr><tr><td style="height:10px;"></td></tr>
            <tr><td style="padding:15px; background:#E3F2FD; border-left:5px solid #1565C0; border-radius:4px;">
              <div style="font-size:18px; font-weight:bold; color:#1565C0;">🔵 {bl}</div>
              <div style="font-size:22px; font-weight:bold; color:#14213D; margin-top:8px;">£{balance_total:,.2f} <span style="font-size:12px; color:#888;">{incl}</span></div>
            </td></tr><tr><td style="height:10px;"></td></tr>
            <tr><td style="padding:15px; background:#FFF8E1; border-left:5px solid #F58A2C; border-radius:4px;">
              <div style="font-size:18px; font-weight:bold; color:#E07B1E;">🟡 {el}</div>
              <div style="font-size:22px; font-weight:bold; color:#14213D; margin-top:8px;">£{elite_total:,.2f} <span style="font-size:12px; color:#888;">{incl}</span></div>
            </td></tr>
          </table>
          <p style="background:#F0F4F8; padding:12px; border-left:4px solid #F58A2C;">📎 {att}</p>
          <p style="margin-top:30px;">{regards}<br><strong>Spets Security LTD</strong></p>
        </div>
        <div style="background:#0A0C12; color:white; padding:15px; text-align:center; font-size:12px;">
          <p style="margin:0;">📞 +44 7706 906079 &nbsp;|&nbsp; ✉ spets.services@gmail.com<br>
          1 Oakcroft Road, Chessington, Surrey, KT9 1BD, United Kingdom<br>VAT: 455026800</p>
        </div>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = formataddr((FROM_NAME, GMAIL_USER))
    msg["To"] = to_email
    msg["Reply-To"] = REPLY_TO_EMAIL
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)
    for pkg_id in ("budget", "balance", "elite"):
        part = MIMEApplication(pdfs[pkg_id], _subtype="pdf")
        part.add_header("Content-Disposition", "attachment",
                        filename=f"Spets-Quote-{quote_number}-{pkg_id.capitalize()}.pdf")
        msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, [to_email], msg.as_string())
        log.info(f"3-package email sent to {to_email} (#{quote_number})")
        return True
    except Exception as e:
        log.error(f"Gmail SMTP send failed to {to_email}: {e}")
        return False


def send_single_quote_email(to_email, customer_name, quote_number, pdf_bytes,
                            subject_label="Quote", lang="en") -> bool:
    """Ajax: send a single PDF quote via Gmail SMTP."""
    if not GMAIL_APP_PASSWORD:
        log.error("GMAIL_APP_PASSWORD not set — cannot send Ajax email")
        return False

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

    html_body = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; color: #14213D; line-height: 1.6;">
      <div style="max-width: 640px; margin: 0 auto; padding: 20px;">
        <div style="background: #0A0C12; color: #FCA311; padding: 20px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px;">SPETS</h1>
          <p style="margin: 5px 0 0; font-size: 12px; letter-spacing: 2px;">ALWAYS NEAR</p>
        </div>
        <div style="padding: 30px 20px;">
          <p>{hello}</p>
          <p>{intro}</p>
          <p style="background: #F0F4F8; padding: 12px; border-left: 4px solid #F58A2C;">📎 {note}</p>
          <p style="margin-top: 30px;">{regards}<br><strong>Spets Security LTD</strong></p>
        </div>
        <div style="background: #0A0C12; color: white; padding: 15px; text-align: center; font-size: 12px;">
          <p style="margin: 0;">📞 +44 7706 906079 &nbsp;|&nbsp; ✉ spets.services@gmail.com<br>
          1 Oakcroft Road, Chessington, Surrey, KT9 1BD, United Kingdom<br>VAT: 455026800</p>
        </div>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = formataddr((FROM_NAME, GMAIL_USER))
    msg["To"] = to_email
    msg["Reply-To"] = REPLY_TO_EMAIL
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)
    part = MIMEApplication(pdf_bytes, _subtype="pdf")
    part.add_header("Content-Disposition", "attachment",
                    filename=f"Spets-Ajax-Quote-{quote_number}.pdf")
    msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, [to_email], msg.as_string())
        log.info(f"Ajax quote email sent to {to_email} (#{quote_number})")
        return True
    except Exception as e:
        log.error(f"Ajax email failed to {to_email}: {e}")
        return False


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
