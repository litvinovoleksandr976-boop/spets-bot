# 🗺 СХЕМА БОТА — Spets Security (підписка на сигналізацію) · v8

## 1. Шлях клієнта

```
/start → мова (UK / RU / EN)
  → Ім'я → Телефон → Email → Адреса
  → 📍 Локація: кнопка (тільки телефон) / індекс / посилання Google Maps / «Пропустити»
  → 🛡 Хаб: Hub 2 (в комплекті) / Hub 2 Plus / Hub G3
  → ➕ Додаткові пристрої по черзі (0…6 шт), «✅ Готово» — одразу на підсумок
  → 🧾 Підсумок: £/міс + ПДВ, монтаж разово
        [Сформувати]  [Змінити]  [Скасувати]
  → 📄 PDF-пропозиція (6 темних сторінок; UK/RU = 6 своєю мовою + 6 англійською)
        • клієнту в Telegram
        • клієнту на email (Brevo)
        • менеджеру в Telegram: деталі + PDF + 📍 пін
        • KeyCRM: заявка з сумою, адресою, Google Maps
  → кнопка «Новий розрахунок» → знову з кроку Локація
```

## 2. Блоки (файли) і як вони зв'язані

```
                 ┌────────────── bot.py ──────────────┐
                 │ меню, кроки (стани), збирає все    │
                 └──┬────────┬─────────┬────────┬─────┘
                    │        │         │        │
          translations.py  sub_flow.py │   keycrm.py → KeyCRM
          (тексти меню)    (кроки      │   email_sender.py → Brevo → email
                            підписки)  │
                               │       │
                         pricing_sub.py│  ← ⭐ ВСІ ЦІНИ
                               │       │
                     quote_generator_sub.py  (вибирає, який PDF робити)
                               │
                         offer_pack.py   ← ⭐ PDF (дизайн, реквізити OFFER_CONFIG)
                         offer_texts.py  ← ⭐ тексти PDF 3 мовами
                         offer_bg.jpg + шрифти Inter*.ttf
                               │ (якщо помилка)
                         запасний білий PDF ← contract_texts.py
```

## 3. Де що зберігається

| Що | Де | Нюанс |
|---|---|---|
| Дані клієнта під час розмови (ім'я, телефон, вибір, розрахунок) | пам'ять бота `context.user_data` | бази немає: при перезапуску Railway незавершена розмова злітає, клієнт тисне /start |
| Готова заявка | **KeyCRM** | головне постійне сховище |
| PDF | Telegram клієнта і менеджера, email клієнта | на сервері не зберігається |
| Ціни, тексти, реквізити | файли `.py` на GitHub | змінив файл → Railway перезапускає бота |
| Ключі та паролі | Railway → Variables | у код не писати |

## 4. Формула ціни (`pricing_sub.py`)

```
пристрої  = базовий комплект £38 + доплата за хаб + додаткові пристрої
накладні  = пристрої × 35%                    (OVERHEAD_PCT)
в місяць  = пристрої + накладні, вгору до £0.50
+ ПДВ 20% = клієнт платить щомісяця
монтаж    = £90 + ПДВ, один раз               (INSTALL_FEE)
```
Приклад: базовий комплект → £51.50 + ПДВ = **£61.80/міс**, монтаж £108.

## 5. Де що міняти

| Що змінити | Файл | Що саме |
|---|---|---|
| Ціна базового комплекту | `pricing_sub.py` | `BASE_KIT_MONTHLY` |
| Склад базового комплекту | `pricing_sub.py` | `BASE_KIT_CONTENTS`, `BASE_KIT_KEYS` |
| Ціни додаткових пристроїв | `pricing_sub.py` | `EXTRAS` |
| Які пристрої питає і в якому порядку | `pricing_sub.py` | `EXTRA_STEPS` |
| Доплата за хаб | `pricing_sub.py` | `HUBS` |
| Накладні / монтаж / ПДВ / строк | `pricing_sub.py` | `OVERHEAD_PCT`, `INSTALL_FEE`, `VAT_RATE`, `MIN_TERM_MONTHS`, `NOTICE_DAYS` |
| Тексти питань і кнопок підписки | `sub_flow.py` | словник `TXT` |
| Привітання, меню | `translations.py` | — |
| Цифри в PDF: депозит, тарифи виїздів, страховка, ICO, ARC, № компанії | `offer_pack.py` | `OFFER_CONFIG` (None = друкує «[X]») |
| Телефон, email, адреса в PDF | `offer_pack.py` | `OFFER_CONFIG` |
| Тексти сторінок PDF | `offer_texts.py` | `T["uk"/"ru"/"en"]` |
| Чи додавати англійську копію до UK/RU | `offer_pack.py` | `APPEND_ENGLISH` |
| Лист клієнту | `email_sender.py` | — |
| Що летить у KeyCRM | `bot.py` → `sb_review` + `keycrm.py` | — |

> Після зміни: завантаж файл на GitHub (назва **малими літерами**, без «[1]») → дочекайся **Active** у Railway → перевір у Telegram.

## 6. Змінні Railway
`TELEGRAM_TOKEN`, `ADMIN_CHAT_ID`, `KEY_API_KEY`, `KEYCRM_SOURCE_ID`, `BREVO_API_KEY`, `SENDER_EMAIL`, `SENDER_NAME`, `REPLY_TO_EMAIL`

## 7. Резервні / старі файли
`pricing.py`, `quote_generator.py` — CCTV (старий продаж) · `pricing_ajax.py`, `ajax_flow.py`, `quote_generator_ajax.py` — Ajax разовий продаж (вимкнений) · `contract_texts.py` — тільки запасний білий PDF.
