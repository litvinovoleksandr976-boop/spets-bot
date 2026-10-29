# 🗺 КАРТА БОТА — Spets Security (підписка на сигналізацію)

## Як іде клієнт по боту

```
/start → мова → Ім'я → Телефон → Email → Адреса
   └─ Меню послуг
        ├─ 📹 CCTV ............ старий калькулятор (3 пакети, продаж)
        ├─ 🛡 Сигналізація — підписка   ← НОВЕ
        │     1. 📍 Локація (кнопка Telegram) або «Пропустити»
        │     2. Хаб: Hub 2 (в комплекті) / Hub 2 Plus / Hub G3
        │     3. Додаткові пристрої по черзі (0…6 шт), «✅ Готово» — одразу підсумок
        │     4. Підсумок: £/міс + ПДВ, монтаж разово  → [Сформувати] [Змінити] [Скасувати]
        │     5. PDF (пропозиція + договір + T&C) →
        │          • клієнту в Telegram
        │          • клієнту на email (Brevo)
        │          • менеджеру в Telegram: деталі + PDF + 📍 пін на карті
        │          • KeyCRM: замовлення з сумою, адресою і посиланням на Google Maps
        └─ 💬 Менеджер
```

## Формула ціни

```
пристрої  = базовий комплект £38 + доплата за хаб + додаткові пристрої
накладні  = пристрої × 35%           (зв'язок, банкінг, обслуговуюча компанія)
в місяць  = пристрої + накладні       (округлення вгору до £0.50)
+ ПДВ 20% = сума, яку клієнт платить щомісяця
монтаж    = £90 + ПДВ, один раз
```
Приклад: тільки базовий комплект → £38 + £13.30 = **£51.50 + ПДВ = £61.80/міс**, монтаж £108.

## ДЕ ЩО МІНЯТИ

| Що хочу змінити | Файл | Що саме |
|---|---|---|
| Ціна базового комплекту (£38) | `pricing_sub.py` | `BASE_KIT_MONTHLY` |
| Що входить у базовий комплект | `pricing_sub.py` | `BASE_KIT_CONTENTS` |
| Ціна додаткового сенсора в місяць | `pricing_sub.py` | `EXTRAS` → `"monthly"` |
| Які пристрої бот питає і в якому порядку | `pricing_sub.py` | `EXTRA_STEPS` |
| Доплата за хаб | `pricing_sub.py` | `HUBS` |
| Накладні 30–40% | `pricing_sub.py` | `OVERHEAD_PCT` (0.35 = 35%) |
| Монтаж £90 | `pricing_sub.py` | `INSTALL_FEE` |
| ПДВ | `pricing_sub.py` | `VAT_RATE` |
| Мінімальний строк договору | `pricing_sub.py` | `MIN_TERM_MONTHS` |
| Список «що входить щомісяця» | `pricing_sub.py` | `INCLUDED_SERVICES` |
| **Дані в PDF-пакеті (номер компанії, тарифи виїздів, депозит, страховка, ICO…)** | `offer_pack.py` | `OFFER_CONFIG` (None = лишається "[X]") |
| Будь-який текст у PDF (3 мови), опис пристроїв | `offer_texts.py` | `T["en"]`, `T["ru"]`, `T["uk"]` |
| Пункти договору (стор. 4) | `offer_texts.py` | `p4_rows` |
| Старий білий PDF замість пакета | `quote_generator_sub.py` | `USE_OFFER_PACK = False` |
| **Текст договору (старий білий PDF)** | `contract_texts.py` | `AGREEMENT_INTRO`, `AGREEMENT_CLAUSES` |
| **Terms & Conditions** | `contract_texts.py` | `TERMS` |
| Реквізити компанії в договорі | `contract_texts.py` | `COMPANY` |
| Тексти кнопок/питань бота | `sub_flow.py` | словник `TXT` (uk/ru/en) |
| Назва кнопки в меню | `translations.py` | `svc_alarm` |
| Дизайн PDF | `quote_generator_sub.py` | — (краще не чіпати) |

> Після зміни — завантаж файл на GitHub (назва файлу **малими літерами**), Railway сам перезапустить бота.

## Файли проєкту

| Файл | Для чого |
|---|---|
| `bot.py` | головний файл: меню, кроки, відправка PDF/email/KeyCRM |
| `pricing_sub.py` | ⭐ **всі ціни підписки** |
| `contract_texts.py` | ⭐ **договір і T&C** |
| `sub_flow.py` | кроки підписки (локація → хаб → пристрої → підсумок) |
| `offer_pack.py` | ⭐ PDF-пакет 6 сторінок (темний дизайн), мова = мова клієнта в боті; для ru/uk + англійська версія в кінці (`APPEND_ENGLISH`) |
| `offer_texts.py` | ⭐ **усі тексти 6 сторінок PDF — English / Русский / Українська** |
| `offer_bg.jpg` | фон сторінок |
| `Inter-*.ttf`, `InterDisplay-Bold.ttf` | шрифт пакета (з кирилицею) |
| `quote_generator_sub.py` | запускає offer_pack (або старий білий PDF) |
| `pricing.py`, `quote_generator.py` | CCTV (старий продаж) |
| `pricing_ajax.py`, `ajax_flow.py`, `quote_generator_ajax.py` | Ajax разовий продаж (зараз вимкнений, залишений про запас) |
| `email_sender.py` | відправка email через Brevo |
| `keycrm.py` | запис у KeyCRM |
| `translations.py` | тексти бота 3 мовами |

## Змінні в Railway (Variables)
`TELEGRAM_TOKEN`, `ADMIN_CHAT_ID`, `KEYCRM_API_KEY`, `KEYCRM_SOURCE_ID`, `BREVO_API_KEY`, `SENDER_EMAIL`, `SENDER_NAME`, `REPLY_TO_EMAIL`

## Повернути старий Ajax-калькулятор (разовий продаж)
`bot.py` → функція `handle_service` → замінити
`return await sub_flow.enter(update, context, get_lang)` на
`return await ajax_flow.enter_ajax(update, context, t, get_lang)`
