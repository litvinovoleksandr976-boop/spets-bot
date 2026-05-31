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
              "💡 _Tip: type /language anytime to switch to Russian or Ukrainian._\n\n"
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
        "en": "🏠 What *type of object* is this for?",
        "ru": "🏠 *Тип объекта*?",
        "uk": "🏠 *Тип обʼєкта*?",
    },
    "object_home": {"en": "🏠 Home", "ru": "🏠 Дом / квартира", "uk": "🏠 Дім / квартира"},
    "object_business": {"en": "🏢 Business", "ru": "🏢 Бизнес (офис, склад, магазин)", "uk": "🏢 Бізнес (офіс, склад, магазин)"},
    # Legacy keys (kept for backward compat in case any code still uses them)
    "object_house": {"en": "🏠 Home", "ru": "🏠 Дом", "uk": "🏠 Дім"},
    "object_office": {"en": "🏢 Business", "ru": "🏢 Бизнес", "uk": "🏢 Бізнес"},
    "object_shop": {"en": "🏢 Business", "ru": "🏢 Бизнес", "uk": "🏢 Бізнес"},
    "object_warehouse": {"en": "🏢 Business", "ru": "🏢 Бизнес", "uk": "🏢 Бізнес"},
    "object_other": {"en": "🏢 Business", "ru": "🏢 Бизнес", "uk": "🏢 Бізнес"},

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
    # GDPR CONSENT
    # ============================================================
    "gdpr_prompt": {
        "en": "📋 Before I send your quote — by continuing, you agree that "
              "*Spets Security LTD* may process your personal data (name, "
              "phone, email, address) to send this quote and contact you "
              "about CCTV services.\n\n"
              "To delete your data anytime, email: spets.services@gmail.com",
        "ru": "📋 Перед отправкой предложения — продолжая, вы соглашаетесь, "
              "что *Spets Security LTD* может обрабатывать ваши данные "
              "(имя, телефон, email, адрес) для отправки предложения и "
              "связи по услугам CCTV.\n\n"
              "Для удаления данных в любой момент: spets.services@gmail.com",
        "uk": "📋 Перед відправкою пропозиції — продовжуючи, ви погоджуєтесь, "
              "що *Spets Security LTD* може обробляти ваші дані (імʼя, "
              "телефон, email, адреса) для надсилання пропозиції та "
              "звʼязку з вами щодо послуг CCTV.\n\n"
              "Для видалення даних будь-коли: spets.services@gmail.com",
    },
    "gdpr_agree_btn": {
        "en": "✅ I agree",
        "ru": "✅ Я согласен",
        "uk": "✅ Я погоджуюсь",
    },
    "gdpr_decline_btn": {
        "en": "❌ Cancel",
        "ru": "❌ Отмена",
        "uk": "❌ Скасувати",
    },

    # ============================================================
    # QUOTE SUMMARY (3 packages comparison)
    # ============================================================
    "quote_summary_header": {
        "en": "📋 *We've prepared 3 packages for you:*\n",
        "ru": "📋 *Мы подготовили для вас 3 пакета:*\n",
        "uk": "📋 *Ми підготували для вас 3 пакети:*\n",
    },
    "package_budget":  {"en": "🟢 *Budget*",  "ru": "🟢 *Budget*",  "uk": "🟢 *Budget*"},
    "package_balance": {"en": "🔵 *Balance*", "ru": "🔵 *Balance*", "uk": "🔵 *Balance*"},
    "package_elite":   {"en": "🟡 *Elite*",   "ru": "🟡 *Elite*",   "uk": "🟡 *Elite*"},
    "package_budget_desc": {
        "en": "Hikvision POC analog 3K cameras + POC DVR (most affordable)",
        "ru": "Аналоговые камеры Hikvision POC 3K + POC DVR (самый доступный)",
        "uk": "Аналогові камери Hikvision POC 3K + POC DVR (найдоступніший)",
    },
    "package_balance_desc": {
        "en": "HiLook IP 4MP ColorVu cameras + HiLook NVR",
        "ru": "IP-камеры HiLook 4MP ColorVu + HiLook NVR",
        "uk": "IP-камери HiLook 4MP ColorVu + HiLook NVR",
    },
    "package_elite_desc": {
        "en": "Hikvision IP 4MP ColorVu 3.0 + AcuSense NVR (premium)",
        "ru": "Hikvision IP 4MP ColorVu 3.0 + AcuSense NVR (премиум)",
        "uk": "Hikvision IP 4MP ColorVu 3.0 + AcuSense NVR (преміум)",
    },
    "total_label": {
        "en": "Total (incl. VAT)",
        "ru": "Итого (с НДС)",
        "uk": "Разом (з ПДВ)",
    },
    "subtotal": {"en": "💷 *Subtotal:*", "ru": "💷 *Подытог:*", "uk": "💷 *Сума:*"},
    "vat_label": {"en": "💷 *VAT 20%:*", "ru": "💷 *НДС 20%:*", "uk": "💷 *ПДВ 20%:*"},
    "grand_total_label": {
        "en": "💷 *GRAND TOTAL:*",
        "ru": "💷 *ИТОГО:*",
        "uk": "💷 *РАЗОМ:*",
    },
    "send_pdf_btn": {
        "en": "✅ Send PDF quotes to email",
        "ru": "✅ Отправить PDF на email",
        "uk": "✅ Надіслати PDF на пошту",
    },
    "cancel_btn": {"en": "❌ Cancel", "ru": "❌ Отмена", "uk": "❌ Скасувати"},

    # ============================================================
    # CONFIRMATION
    # ============================================================
    "generating_pdf": {
        "en": "⏳ Generating your quote PDFs...",
        "ru": "⏳ Генерирую ваши PDF-предложения...",
        "uk": "⏳ Генерую ваші PDF-пропозиції...",
    },
    "pdf_caption_budget":  {"en": "🟢 Budget package",  "ru": "🟢 Пакет Budget",  "uk": "🟢 Пакет Budget"},
    "pdf_caption_balance": {"en": "🔵 Balance package", "ru": "🔵 Пакет Balance", "uk": "🔵 Пакет Balance"},
    "pdf_caption_elite":   {"en": "🟡 Elite package",   "ru": "🟡 Пакет Elite",   "uk": "🟡 Пакет Elite"},
    "pdf_caption": {
        "en": "📄 Your quote #{n}",
        "ru": "📄 Ваше предложение #{n}",
        "uk": "📄 Ваша пропозиція #{n}",
    },
    "quote_sent_ok": {
        "en": "✅ *Your 3 quote options sent!*\n\n"
              "📧 PDFs emailed to: {email}\n\n"
              "🟢 *Budget:* £{budget:.2f}\n"
              "🔵 *Balance:* £{balance:.2f}\n"
              "🟡 *Elite:* £{elite:.2f}\n\n"
              "Our team will contact you within 24 hours.\n"
              "Quotes are valid for *7 days*.",
        "ru": "✅ *Ваши 3 предложения отправлены!*\n\n"
              "📧 PDF отправлены на: {email}\n\n"
              "🟢 *Budget:* £{budget:.2f}\n"
              "🔵 *Balance:* £{balance:.2f}\n"
              "🟡 *Elite:* £{elite:.2f}\n\n"
              "Наша команда свяжется с вами в течение 24 часов.\n"
              "Предложения действительны *7 дней*.",
        "uk": "✅ *Ваші 3 пропозиції надіслано!*\n\n"
              "📧 PDF надіслано на: {email}\n\n"
              "🟢 *Budget:* £{budget:.2f}\n"
              "🔵 *Balance:* £{balance:.2f}\n"
              "🟡 *Elite:* £{elite:.2f}\n\n"
              "Наша команда звʼяжеться з вами протягом 24 годин.\n"
              "Пропозиції дійсні *7 днів*.",
    },
    "quote_sent_email_failed": {
        "en": "⚠️ Quotes #{n} generated, but email delivery failed.\n"
              "We have your PDFs here in chat. A manager will contact you shortly.",
        "ru": "⚠️ Предложения #{n} созданы, но email не доставлен.\n"
              "PDF выше в чате. Менеджер свяжется с вами в ближайшее время.",
        "uk": "⚠️ Пропозиції #{n} створено, але email не доставлено.\n"
              "PDF вище в чаті. Менеджер звʼяжеться з вами найближчим часом.",
    },
    "cancelled": {
        "en": "❌ Cancelled. Type /start to begin again.",
        "ru": "❌ Отменено. Напишите /start чтобы начать заново.",
        "uk": "❌ Скасовано. Напишіть /start щоб почати знову.",
    },
    "pdf_error": {
        "en": "⚠️ Sorry, something went wrong while generating PDFs. Please call +44 7706 906079.",
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

    # ============================================================
    # NEW: SERVICE MENU (CCTV / Alarm / Contact)
    # ============================================================
    "ask_service": {
        "en": "What service are you interested in?",
        "ru": "Какая услуга вас интересует?",
        "uk": "Яка послуга вас цікавить?",
    },
    "svc_cctv":    {"en": "🎥 CCTV Cameras",   "ru": "🎥 Камеры CCTV",   "uk": "🎥 Камери CCTV"},
    "svc_alarm":   {"en": "🚨 Alarm System",   "ru": "🚨 Сигнализация",  "uk": "🚨 Сигналізація"},
    "svc_contact": {"en": "💬 Contact Manager","ru": "💬 Связаться с менеджером","uk": "💬 Звʼязатися з менеджером"},

    "alarm_coming_soon": {
        "en": "🚧 *Alarm System* calculator is coming soon!\n\n"
              "Our manager will contact you shortly to discuss your alarm needs.\n"
              "You can also call us directly: +44 7706 906079",
        "ru": "🚧 Калькулятор *сигнализации* появится скоро!\n\n"
              "Наш менеджер свяжется с вами в ближайшее время.\n"
              "Можете также позвонить: +44 7706 906079",
        "uk": "🚧 Калькулятор *сигналізації* зʼявиться скоро!\n\n"
              "Наш менеджер звʼяжеться з вами найближчим часом.\n"
              "Можете також зателефонувати: +44 7706 906079",
    },

    "contact_prompt": {
        "en": "💬 Tap the button below to chat with our manager directly.\n"
              "We'll reply as soon as possible!",
        "ru": "💬 Нажмите кнопку ниже, чтобы написать менеджеру напрямую.\n"
              "Мы ответим как можно скорее!",
        "uk": "💬 Натисніть кнопку нижче, щоб написати менеджеру напряму.\n"
              "Ми відповімо якнайшвидше!",
    },
    "message_sent": {
        "en": "✅ Thank you! Your message has been sent to our manager.\n"
              "We will reply within 24 hours.",
        "ru": "✅ Спасибо! Ваше сообщение отправлено менеджеру.\n"
              "Мы ответим в течение 24 часов.",
        "uk": "✅ Дякуємо! Ваше повідомлення надіслано менеджеру.\n"
              "Ми відповімо протягом 24 годин.",
    },

    # ============================================================
    # NEW: OBJECT TYPE (Residential / Business)
    # ============================================================
    "ask_object_type": {
        "en": "🏠 What type of object?",
        "ru": "🏠 Тип объекта?",
        "uk": "🏠 Тип обʼєкта?",
    },
    "obj_residential": {"en": "🏠 Residential (Home / Flat)", "ru": "🏠 Жилое (Дом / Квартира)", "uk": "🏠 Житло (Дім / Квартира)"},
    "obj_business":    {"en": "🏢 Business", "ru": "🏢 Бизнес", "uk": "🏢 Бізнес"},

    # ============================================================
    # NEW: BUSINESS TYPE
    # ============================================================
    "ask_business_type": {
        "en": "🏢 What type of business?",
        "ru": "🏢 Какой тип бизнеса?",
        "uk": "🏢 Який тип бізнесу?",
    },
    "biz_cafe":         {"en": "🍽️ Cafe / Restaurant / Beauty Salon",
                         "ru": "🍽️ Кафе / Ресторан / Салон красоты",
                         "uk": "🍽️ Кафе / Ресторан / Салон краси"},
    "biz_office":       {"en": "🏢 Office / Warehouse / School",
                         "ru": "🏢 Офис / Склад / Школа",
                         "uk": "🏢 Офіс / Склад / Школа"},
    "biz_construction": {"en": "🏗️ Construction Site",
                         "ru": "🏗️ Строительный объект",
                         "uk": "🏗️ Будівельний обʼєкт"},

    # ============================================================
    # NEW: CAMERA COUNT (inline buttons)
    # ============================================================
    "ask_camera_count_buttons": {
        "en": "📹 *How many cameras do you need?*",
        "ru": "📹 *Сколько камер вам нужно?*",
        "uk": "📹 *Скільки камер вам потрібно?*",
    },
    "cam_17plus": {
        "en": "17+ — Talk to manager",
        "ru": "17+ — Связаться с менеджером",
        "uk": "17+ — Звʼязатися з менеджером",
    },
    "big_project_msg": {
        "en": "📋 For large projects (*17+ cameras*) our manager will contact you "
              "directly to discuss the details and prepare a custom quote.\n\n"
              "We have all your contact info — expect a call within 24 hours.\n"
              "Direct line: +44 7706 906079",
        "ru": "📋 Для крупных проектов (*17+ камер*) наш менеджер свяжется с вами "
              "напрямую, чтобы обсудить детали и подготовить персональное предложение.\n\n"
              "У нас есть все ваши контакты — ждите звонок в течение 24 часов.\n"
              "Прямая линия: +44 7706 906079",
        "uk": "📋 Для великих проектів (*17+ камер*) наш менеджер звʼяжеться з вами "
              "напряму, щоб обговорити деталі та підготувати персональну пропозицію.\n\n"
              "У нас є всі ваші контакти — чекайте дзвінок протягом 24 годин.\n"
              "Пряма лінія: +44 7706 906079",
    },

    # ============================================================
    # NEW: AFTER QUOTE menu
    # ============================================================
    "after_quote_prompt": {
        "en": "What would you like to do next?",
        "ru": "Что хотите сделать дальше?",
        "uk": "Що бажаєте зробити далі?",
    },
    "btn_msg_manager": {
        "en": "💬 Message Manager",
        "ru": "💬 Написать менеджеру",
        "uk": "💬 Написати менеджеру",
    },
    "btn_back_main": {
        "en": "🏠 Back to Main Menu",
        "ru": "🏠 На главное меню",
        "uk": "🏠 На головне меню",
    },

    # ============================================================
    # NEW: PACKAGE DESCRIPTIONS (updated for POC Budget)
    # ============================================================
    # Override old package_budget_desc with POC info
    "package_budget_desc_v2": {
        "en": "Hikvision POC analog cameras + POC DVR (most affordable)",
        "ru": "Аналоговые камеры Hikvision POC + POC DVR (самый доступный)",
        "uk": "Аналогові камери Hikvision POC + POC DVR (найдоступніший)",
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
