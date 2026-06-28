

def send_single_quote_email(
    to_email: str,
    customer_name: str,
    quote_number: str,
    pdf_bytes: bytes,
    subject_label: str = "Quote",
    lang: str = "en",
) -> bool:
    """Send a single PDF quote (used by the Ajax flow) via Gmail SMTP."""
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
