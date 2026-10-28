"""
SPETS SECURITY — тексти ДОГОВОРУ та TERMS & CONDITIONS для підписки.
=====================================================================
  ★ Сюди вставляється ваш готовий контракт. Просто заміни текст пунктів. ★
=====================================================================

• Кожен пункт — це рядок у списку. Порядок = порядок у PDF.
• Можна використовувати змінні в {фігурних дужках} — бот підставить сам:
    {customer}   ім'я клієнта            {address}  адреса об'єкта
    {monthly_ex} £/міс без ПДВ           {monthly_inc} £/міс з ПДВ
    {install_ex} монтаж без ПДВ          {install_inc} монтаж з ПДВ
    {term}       мін. строк (міс)        {notice}   днів попередження
    {ref}        номер пропозиції        {date}     дата
• Жирний текст: <b>...</b>

ЧЕРНЕТКА: перед використанням договір має перевірити юрист.
"""

COMPANY = {
    "name": "Spets Security Ltd",
    "address": "1 Oakcroft Road, Chessington, Surrey, KT9 1BD, United Kingdom",
    "phone": "+44 7706 906079",
    "email": "sales@spetstech.co.uk",
    "vat": "455026800",
}

# ---------------------------------------------------------------------------
# SUBSCRIPTION AGREEMENT  (сторінка з підписами)
# ---------------------------------------------------------------------------
AGREEMENT_TITLE = "ALARM SYSTEM SUBSCRIPTION AGREEMENT"

AGREEMENT_INTRO = (
    "This Agreement (ref. <b>{ref}</b>, dated <b>{date}</b>) is made between "
    "<b>Spets Security Ltd</b> (the \"Company\") and <b>{customer}</b> (the \"Customer\") "
    "for the supply, installation and ongoing service of an Ajax wireless alarm system "
    "at the property: <b>{address}</b>."
)

AGREEMENT_CLAUSES = [
    ("The Offer",
     "The Company will install the alarm system listed in the attached Quote and keep it "
     "working for the Customer for a fixed monthly fee. The equipment is provided on a "
     "rental basis and remains the property of the Company at all times."),
    ("Monthly fee",
     "The Customer will pay <b>£{monthly_ex} + VAT (£{monthly_inc} per month)</b>. "
     "The monthly fee includes equipment rental, SIM / mobile data, remote support, "
     "repairs, replacement of faulty devices, batteries and an annual maintenance visit."),
    ("Installation",
     "A one-off installation fee of <b>£{install_ex} + VAT (£{install_inc})</b> is payable "
     "on the day of installation."),
    ("Payment",
     "The monthly fee is collected in advance by Direct Debit / standing order on the same "
     "date each month, starting from the installation date."),
    ("Term",
     "The minimum term is <b>{term} months</b> from the installation date. After that the "
     "Agreement continues month to month until either party gives <b>{notice} days'</b> "
     "written notice."),
    ("Acceptance",
     "By signing below, both parties agree to this Agreement and to the Terms &amp; "
     "Conditions on the following pages."),
]

# ---------------------------------------------------------------------------
# TERMS & CONDITIONS  (окремі сторінки)
# ---------------------------------------------------------------------------
TERMS_TITLE = "TERMS & CONDITIONS — ALARM SUBSCRIPTION"

TERMS = [
    ("1. Ownership of equipment",
     "All equipment installed under this Agreement remains the property of Spets Security Ltd. "
     "The Customer must not sell, move, modify, or allow third parties to alter the equipment."),
    ("2. Company obligations",
     "The Company will install and configure the system, set up the Ajax app for the Customer, "
     "provide remote support, and repair or replace faulty equipment at no extra cost, normally "
     "within 3 working days of the fault being reported."),
    ("3. Customer obligations",
     "The Customer will keep the equipment in good condition, use it as instructed, report any "
     "fault promptly, and give the Company reasonable access to the property for installation, "
     "maintenance and repairs."),
    ("4. Damage and loss",
     "Damage caused by misuse, negligence, deliberate acts, or loss/theft of equipment is not "
     "covered by the monthly fee and may be charged at the current replacement price."),
    ("5. Payments",
     "If a payment is missed, the Company will contact the Customer. If payment is not made within "
     "14 days, the Company may suspend remote services until the account is up to date."),
    ("6. Early termination",
     "If the Customer ends the Agreement before the minimum term, the remaining monthly fees up to "
     "the end of the minimum term become payable, unless agreed otherwise in writing."),
    ("7. End of agreement",
     "When the Agreement ends, the Customer must allow the Company to collect the equipment within "
     "14 days. Equipment not returned may be charged at the current replacement price."),
    ("8. Price review",
     "The Company may review the monthly fee once every 12 months, with at least 30 days' written "
     "notice. Prices will not change during the first 12 months."),
    ("9. Monitoring and response",
     "The system sends alerts to the Customer's phones via the Ajax app. Unless a separate "
     "monitoring/keyholding service is agreed in writing, the Company does not provide police or "
     "guard response."),
    ("10. Liability",
     "An alarm system reduces risk but cannot guarantee that a break-in, fire or leak will be "
     "prevented. The Company is not liable for indirect loss. Nothing limits liability that cannot "
     "be limited by law."),
    ("11. Data protection",
     "Customer data is used only to provide this service and is processed in line with UK GDPR. "
     "Camera/photo verification images remain the Customer's data."),
    ("12. Governing law",
     "This Agreement is governed by the laws of England and Wales."),
]
