"""
SPETS SECURITY — Translations module
Supports: English (en), Русский (ru), Українська (uk)

Usage:
    from translations import t
    text = t("welcome", "uk", name="Олександр")
"""

TRANSLATIONS = {
    # ============================================================
    # WELCOME / LANGUAGE SELECTION
    # ============================================================
    "language_prompt": {
        "en": "🌍 Choose language / Выберите язык / Виберіть мову:",
        "ru": "🌍 Choose language / Выберите язык / Виберіть мову:",
        "uk": "🌍 Choose language / Выберите язык / Виберіть мову:",
    },
    "language_set": {
        "en": "✅ Language set to English",
        "ru": "✅ Язык переключён на Русский",
        "uk": "✅ Мову встановлено на Українську",
    },
    "welcome": {
        "en": "👋 Hello {name}!\n\nWelcome to *Spets Security* — CCTV quote service.\n\n"
              "I'll ask you a few quick questions (about 1 minute) and send you "
              "a personalised PDF quote to your email.\n\n"
              "Let's start. *What is your full name?*",
        "ru": "👋 Здравствуйте, {name}!\n\nДобро пожаловать в *Spets Security* — сервис расчёта CCTV.\n\n"
              "Я задам вам несколько быстрых вопросов (около 1 минуты) и отправлю "
              "персональное PDF-предложение на ваш email.\n\n"
              "Давайте начнём. *Как вас полностью зовут?*",
        "uk": "👋 Вітаю, {name}!\n\nЛаскаво просимо в *Spets Security* — сервіс розрахунку CCTV.\n\n"
              "Я поставлю вам декілька швидких запитань (близько 1 хвилини) і надішлю "
              "персональну PDF-пропозицію на вашу пошту.\n\n"
              "Почнімо. *Як вас повністю звати?*",
    },

    # ============================================================
    # QUESTIONS
    # ============================================================
    "ask_name_invalid": {
        "en": "Please enter a valid name (at least 2 characters).",
        "ru": "Пожалуйста, введите корректное имя (минимум 2 символа).",
        "uk": "Будь ласка, введіть коректне імʼя (мінімум 2 символи).",
    },
    "ask_phone": {
        "en": "Nice to meet you, {name}!\n\n📞 What's your *phone number*?\n(with country code, e.g. +447700900123)",
        "ru": "Приятно познакомиться, {name}!\n\n📞 Ваш *номер телефона*?\n(с кодом страны, например +447700900123)",
        "uk": "Приємно познайомитись, {name}!\n\n📞 Ваш *номер телефону*?\n(з кодом країни, наприклад +447700900123)",
    },
    "ask_phone_invalid": {
        "en": "❗ That doesn't look like a valid phone. Try again (e.g. +447700900123).",
        "ru": "❗ Это не похоже на корректный телефон. Попробуйте ещё раз (например +447700900123).",
        "uk": "❗ Це не схоже на коректний телефон. Спробуйте ще раз (наприклад +447700900123).",
    },
    "ask_email": {
        "en": "📧 What's your *email address*?\n(We'll send the PDF quote there)",
        "ru": "📧 Ваш *email*?\n(Мы отправим PDF-предложение туда)",
        "uk": "📧 Ваша *електронна пошта*?\n(Ми надішлемо PDF-пропозицію туди)",
    },
    "ask_email_invalid": {
        "en": "❗ That doesn't look like a valid email. Try again (e.g. name@example.com).",
        "ru": "❗ Это не похоже на корректный email. Попробуйте ещё раз (например name@example.com).",
        "uk": "❗ Це не схоже на коректну пошту. Спробуйте ще раз (наприклад name@example.com).",
    },
    "ask_address": {
        "en": "📍 What's the *installation address*?\n(Street, city, postcode)",
        "ru": "📍 *Адрес установки*?\n(Улица, город, индекс)",
        "uk": "📍 *Адреса встановлення*?\n(Вулиця, місто, індекс)",
    },
    "ask_object_type": {
        "en": "🏢 What *type of object* needs CCTV?",
        "ru": "🏢 Какой *тип объекта* нуждается в CCTV?",
        "uk": "🏢 Який *тип обʼєкта* потребує CCTV?",
    },
    "object_house": {"en": "🏠 House", "ru": "🏠 Дом", "uk": "🏠 Будинок"},
    "object_office": {"en": "🏢 Office", "ru": "🏢 Офис", "uk": "🏢 Офіс"},
    "object_shop": {"en": "🏪 Shop", "ru": "🏪 Магазин", "uk": "🏪 Магазин"},
    "object_warehouse": {"en": "🏭 Warehouse", "ru": "🏭 Склад", "uk": "🏭 Склад"},
    "object_other": {"en": "📦 Other", "ru": "📦 Другое", "uk": "📦 Інше"},

    "ask_camera_count": {
        "en": "📹 How many *cameras* do you need?\n(Just type a number, e.g. 4)",
        "ru": "📹 Сколько *камер* вам нужно?\n(Просто введите число, например 4)",
        "uk": "📹 Скільки *камер* вам потрібно?\n(Просто введіть число, наприклад 4)",
    },
    "ask_camera_count_invalid": {
        "en": "Please type a number between 1 and 16.",
        "ru": "Пожалуйста, введите число от 1 до 16.",
        "uk": "Будь ласка, введіть число від 1 до 16.",
    },
    "ask_camera_count_too_big": {
        "en": "We currently quote 1–16 cameras automatically. "
              "For larger projects, please call us at +44 7706 906079.",
        "ru": "Сейчас автоматически рассчитываем 1–16 камер. "
              "Для бо́льших проектов звоните +44 7706 906079.",
        "uk": "Зараз автоматично розраховуємо 1–16 камер. "
              "Для більших проектів телефонуйте +44 7706 906079.",
    },
    "ask_camera_tier": {
        "en": "📸 Which *camera tier* would you like?\n\n"
              "🟢 *Basic* — IR night vision\n"
              "🔵 *Standard* — Colour at night (ColorVu)\n"
              "🟠 *Premium* — ColorVu 3.0 + mic/speaker\n"
              "🔴 *Premium 4K* — 8MP top tier",
        "ru": "📸 Какой *уровень камер* вы хотите?\n\n"
              "🟢 *Базовый* — Ночное видение (IR)\n"
              "🔵 *Стандарт* — Цветное ночью (ColorVu)\n"
              "🟠 *Премиум* — ColorVu 3.0 + микрофон/динамик\n"
              "🔴 *Премиум 4K* — 8MP топовый",
        "uk": "📸 Який *рівень камер* ви бажаєте?\n\n"
              "🟢 *Базовий* — Нічне бачення (IR)\n"
              "🔵 *Стандарт* — Кольорове вночі (ColorVu)\n"
              "🟠 *Преміум* — ColorVu 3.0 + мікрофон/динамік\n"
              "🔴 *Преміум 4K* — 8MP топовий",
    },
    "tier_basic_btn": {
        "en": "🟢 Basic — HiLook 5MP IR (£50.60)",
        "ru": "🟢 Базовый — HiLook 5MP IR (£50.60)",
        "uk": "🟢 Базовий — HiLook 5MP IR (£50.60)",
    },
    "tier_standard_btn": {
        "en": "🔵 Standard — HiLook 4MP ColorVu (£60.95)",
        "ru": "🔵 Стандарт — HiLook 4MP ColorVu (£60.95)",
        "uk": "🔵 Стандарт — HiLook 4MP ColorVu (£60.95)",
    },
    "tier_premium_btn": {
        "en": "🟠 Premium — Hikvision 4MP ColorVu 3.0 (£141.45)",
        "ru": "🟠 Премиум — Hikvision 4MP ColorVu 3.0 (£141.45)",
        "uk": "🟠 Преміум — Hikvision 4MP ColorVu 3.0 (£141.45)",
    },
    "tier_4k_btn": {
        "en": "🔴 Premium 4K — Hikvision 8MP 4K (£193.20)",
        "ru": "🔴 Премиум 4K — Hikvision 8MP 4K (£193.20)",
        "uk": "🔴 Преміум 4K — Hikvision 8MP 4K (£193.20)",
    },
    "ask_archive": {
        "en": "💾 How long do you want to *keep video archive*?",
        "ru": "💾 Сколько хранить *видеоархив*?",
        "uk": "💾 Скільки зберігати *відеоархів*?",
    },
    "arch_1week": {
        "en": "📅 1 week (1TB HDD)",
        "ru": "📅 1 неделя (1TB HDD)",
        "uk": "📅 1 тиждень (1TB HDD)",
    },
    "arch_2weeks": {
        "en": "📅 2 weeks (2TB HDD)",
        "ru": "📅 2 недели (2TB HDD)",
        "uk": "📅 2 тижні (2TB HDD)",
    },
    "arch_1month": {
        "en": "📅 1 month (4TB HDD)",
        "ru": "📅 1 месяц (4TB HDD)",
        "uk": "📅 1 місяць (4TB HDD)",
    },
    "arch_2months": {
        "en": "📅 2 months (6TB HDD)",
        "ru": "📅 2 месяца (6TB HDD)",
        "uk": "📅 2 місяці (6TB HDD)",
    },

    # ============================================================
    # QUOTE SUMMARY
    # ============================================================
    "quote_summary_header": {
        "en": "📋 *Quote Summary:*\n",
        "ru": "📋 *Сводка предложения:*\n",
        "uk": "📋 *Підсумок пропозиції:*\n",
    },
    "subtotal": {"en": "💷 *Subtotal:*", "ru": "💷 *Подытог:*", "uk": "💷 *Сума:*"},
    "vat_label": {"en": "💷 *VAT 20%:*", "ru": "💷 *НДС 20%:*", "uk": "💷 *ПДВ 20%:*"},
    "grand_total_label": {
        "en": "💷 *GRAND TOTAL:*",
        "ru": "💷 *ИТОГО:*",
        "uk": "💷 *РАЗОМ:*",
    },
    "send_pdf_btn": {
        "en": "✅ Send PDF to my email",
        "ru": "✅ Отправить PDF на мой email",
        "uk": "✅ Надіслати PDF на мою пошту",
    },
    "cancel_btn": {"en": "❌ Cancel", "ru": "❌ Отмена", "uk": "❌ Скасувати"},

    # ============================================================
    # CONFIRMATION
    # ============================================================
    "generating_pdf": {
        "en": "⏳ Generating your quote PDF...",
        "ru": "⏳ Генерирую ваше PDF-предложение...",
        "uk": "⏳ Генерую вашу PDF-пропозицію...",
    },
    "pdf_caption": {
        "en": "📄 Your quote #{n}",
        "ru": "📄 Ваше предложение #{n}",
        "uk": "📄 Ваша пропозиція #{n}",
    },
    "quote_sent_ok": {
        "en": "✅ *Quote #{n} sent!*\n\n"
              "📧 PDF emailed to: {email}\n"
              "💷 Total: £{total:.2f}\n\n"
              "We'll be in touch within 24 hours.\n"
              "Quote is valid for *7 days*.",
        "ru": "✅ *Предложение #{n} отправлено!*\n\n"
              "📧 PDF отправлен на: {email}\n"
              "💷 Итого: £{total:.2f}\n\n"
              "Мы свяжемся с вами в течение 24 часов.\n"
              "Предложение действительно *7 дней*.",
        "uk": "✅ *Пропозицію #{n} надіслано!*\n\n"
              "📧 PDF надіслано на: {email}\n"
              "💷 Разом: £{total:.2f}\n\n"
              "Ми звʼяжемося з вами протягом 24 годин.\n"
              "Пропозиція дійсна *7 днів*.",
    },
    "quote_sent_email_failed": {
        "en": "⚠️ Quote #{n} generated, but email delivery failed.\n"
              "We have your PDF here in chat. A manager will contact you shortly.",
        "ru": "⚠️ Предложение #{n} создано, но email не доставлен.\n"
              "PDF выше в чате. Менеджер свяжется с вами в ближайшее время.",
        "uk": "⚠️ Пропозицію #{n} створено, але email не доставлено.\n"
              "PDF вище в чаті. Менеджер звʼяжеться з вами найближчим часом.",
    },
    "cancelled": {
        "en": "❌ Cancelled. Type /start to begin again.",
        "ru": "❌ Отменено. Напишите /start чтобы начать заново.",
        "uk": "❌ Скасовано. Напишіть /start щоб почати знову.",
    },
    "pdf_error": {
        "en": "⚠️ Sorry, something went wrong while generating PDF. Please call +44 7706 906079.",
        "ru": "⚠️ Извините, ошибка при создании PDF. Звоните +44 7706 906079.",
        "uk": "⚠️ Вибачте, помилка при створенні PDF. Телефонуйте +44 7706 906079.",
    },

    # ============================================================
    # HELP
    # ============================================================
    "help": {
        "en": "🆘 *Spets Security Bot — Help*\n\n"
              "/start — Get a CCTV quote\n"
              "/language — Change language\n"
              "/cancel — Cancel current conversation\n"
              "/help — This message\n\n"
              "📞 +44 7706 906079\n"
              "📧 r.brain@spetstech.co.uk",
        "ru": "🆘 *Spets Security Bot — Помощь*\n\n"
              "/start — Получить предложение CCTV\n"
              "/language — Сменить язык\n"
              "/cancel — Отменить текущий диалог\n"
              "/help — Это сообщение\n\n"
              "📞 +44 7706 906079\n"
              "📧 r.brain@spetstech.co.uk",
        "uk": "🆘 *Spets Security Bot — Допомога*\n\n"
              "/start — Отримати пропозицію CCTV\n"
              "/language — Змінити мову\n"
              "/cancel — Скасувати поточний діалог\n"
              "/help — Це повідомлення\n\n"
              "📞 +44 7706 906079\n"
              "📧 r.brain@spetstech.co.uk",
    },

    # ============================================================
    # PDF DOCUMENT LABELS
    # ============================================================
    "pdf_invoice_to": {"en": "Invoice To", "ru": "Кому", "uk": "Кому"},
    "pdf_invoice_word": {"en": "INVOICE", "ru": "СЧЁТ", "uk": "РАХУНОК"},
    "pdf_quote_label": {"en": "Quote #", "ru": "Предложение №", "uk": "Пропозиція №"},
    "pdf_date_label": {"en": "Date:", "ru": "Дата:", "uk": "Дата:"},
    "pdf_col_no": {"en": "No", "ru": "№", "uk": "№"},
    "pdf_col_item": {"en": "Item Description", "ru": "Описание", "uk": "Опис"},
    "pdf_col_qty": {"en": "Qty", "ru": "Кол-во", "uk": "К-сть"},
    "pdf_col_price": {"en": "Price", "ru": "Цена", "uk": "Ціна"},
    "pdf_col_vat": {"en": "VAT", "ru": "НДС", "uk": "ПДВ"},
    "pdf_col_total": {"en": "Total", "ru": "Итого", "uk": "Разом"},
    "pdf_payment_details": {
        "en": "Payment details:", "ru": "Реквизиты:", "uk": "Реквізити:",
    },
    "pdf_account_number": {"en": "Account number:", "ru": "Номер счёта:", "uk": "Номер рахунку:"},
    "pdf_sort_code": {"en": "Sort code:", "ru": "Sort code:", "uk": "Sort code:"},
    "pdf_subtotal": {"en": "Subtotal", "ru": "Подытог", "uk": "Сума"},
    "pdf_discount": {"en": "Discount", "ru": "Скидка", "uk": "Знижка"},
    "pdf_total_vat": {"en": "Total VAT", "ru": "Итого НДС", "uk": "Разом ПДВ"},
    "pdf_grand_total": {"en": "Grand total", "ru": "К оплате", "uk": "До сплати"},
    "pdf_terms_title": {"en": "TERMS &amp; CONDITIONS", "ru": "УСЛОВИЯ", "uk": "УМОВИ"},
    "pdf_term_1": {
        "en": "1. Prices are valid for 1 week",
        "ru": "1. Цены действительны 1 неделю",
        "uk": "1. Ціни дійсні 1 тиждень",
    },
    "pdf_term_2": {
        "en": "2. Equipment delivery time is from 5-7 working days",
        "ru": "2. Срок поставки оборудования 5-7 рабочих дней",
        "uk": "2. Термін постачання обладнання 5-7 робочих днів",
    },
    "pdf_term_3": {
        "en": "3. Work completion time is from 3 to 5 days",
        "ru": "3. Срок выполнения работ от 3 до 5 дней",
        "uk": "3. Термін виконання робіт від 3 до 5 днів",
    },
    "installation_label": {
        "en": "Installation CCTV",
        "ru": "Монтаж CCTV",
        "uk": "Монтаж CCTV",
    },

    # ============================================================
    # EMAIL BODY
    # ============================================================
    "email_subject": {
        "en": "Your CCTV Quote #{n} — Spets Security LTD",
        "ru": "Ваше предложение CCTV #{n} — Spets Security LTD",
        "uk": "Ваша пропозиція CCTV #{n} — Spets Security LTD",
    },
    "email_hello": {"en": "Hello {name},", "ru": "Здравствуйте, {name},", "uk": "Вітаємо, {name},"},
    "email_intro": {
        "en": "Thank you for your interest in Spets Security CCTV solutions.",
        "ru": "Благодарим вас за интерес к решениям CCTV от Spets Security.",
        "uk": "Дякуємо за інтерес до рішень CCTV від Spets Security.",
    },
    "email_find_pdf": {
        "en": "Please find your personalised quote <strong>#{n}</strong> attached as a PDF.",
        "ru": "Ваше персональное предложение <strong>#{n}</strong> прилагается в PDF.",
        "uk": "Ваша персональна пропозиція <strong>#{n}</strong> додається у PDF.",
    },
    "email_total_label": {
        "en": "Quote Total:",
        "ru": "Сумма предложения:",
        "uk": "Сума пропозиції:",
    },
    "email_incl_vat": {
        "en": "(incl. VAT)",
        "ru": "(вкл. НДС)",
        "uk": "(вкл. ПДВ)",
    },
    "email_valid_7days": {
        "en": "<strong>Quote is valid for 7 days.</strong>",
        "ru": "<strong>Предложение действительно 7 дней.</strong>",
        "uk": "<strong>Пропозиція дійсна 7 днів.</strong>",
    },
    "email_next_title": {
        "en": "What happens next:",
        "ru": "Что дальше:",
        "uk": "Що далі:",
    },
    "email_next_1": {
        "en": "Review the quote at your convenience",
        "ru": "Изучите предложение в удобное время",
        "uk": "Перегляньте пропозицію у зручний час",
    },
    "email_next_2": {
        "en": "Reply to this email or call us with any questions",
        "ru": "Ответьте на это письмо или позвоните нам с любыми вопросами",
        "uk": "Дайте відповідь на цей лист або зателефонуйте з будь-якими питаннями",
    },
    "email_next_3": {
        "en": "Equipment delivery: 5-7 working days from order",
        "ru": "Доставка оборудования: 5-7 рабочих дней с момента заказа",
        "uk": "Доставка обладнання: 5-7 робочих днів від замовлення",
    },
    "email_next_4": {
        "en": "Installation: 3-5 days after equipment arrives",
        "ru": "Монтаж: 3-5 дней после поступления оборудования",
        "uk": "Монтаж: 3-5 днів після надходження обладнання",
    },
    "email_questions": {
        "en": "If you have any questions, just reply to this email or call us directly.",
        "ru": "Если есть вопросы — отвечайте на это письмо или звоните напрямую.",
        "uk": "Якщо є питання — відповідайте на цей лист або телефонуйте напряму.",
    },
    "email_best_regards": {
        "en": "Best regards,",
        "ru": "С уважением,",
        "uk": "З повагою,",
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """
    Get translation by key for given language.
    Falls back to English if lang not found.
    Supports {placeholder} formatting via kwargs.

    Example:
        t("welcome", "uk", name="Олександр")
    """
    if lang not in ("en", "ru", "uk"):
        lang = "en"

    entry = TRANSLATIONS.get(key)
    if not entry:
        return f"[missing: {key}]"

    text = entry.get(lang) or entry.get("en") or f"[missing translation: {key}/{lang}]"

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass

    return text
