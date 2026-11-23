"""
SPETS SECURITY — Alarm SUBSCRIPTION flow (Telegram).

Ціни — у pricing_sub.py. Тексти кнопок/питань — у словнику TXT нижче.

Flow (after Name → Phone → Email → Address → service "alarm"):
  SUB_LOC    : 📍 send location  |  ⏭ skip
  SUB_HUB    : Hub 2 (included) | Hub 2 Plus | Hub G3
  SUB_EXTRA  : extra devices one by one (qty 0..N), "✅ Done" jumps to review
  SUB_REVIEW : shows monthly price → [Generate quote + contract] [Cancel]
"""
import logging
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

import pricing_sub as ps

log = logging.getLogger(__name__)
S = {}  # state ids, filled by bot.py via init_states()


def init_states(state_ids: dict):
    S.update(state_ids)


# ---------------------------------------------------------------------------
# TEXTS (uk / ru / en)
# ---------------------------------------------------------------------------
TXT = {
    "ask_loc": {
        "uk": ("📍 *Локація об'єкта*\n\n"
               "• На телефоні — кнопка «Надіслати локацію» нижче\n"
               "• Або 📎 → Геопозиція → оберіть точку на карті\n"
               "• Або вставте посилання Google Maps чи поштовий індекс\n\n"
               "Якщо не потрібно — «Пропустити»."),
        "ru": ("📍 *Локация объекта*\n\n"
               "• На телефоне — кнопка «Отправить локацию» ниже\n"
               "• Или 📎 → Геопозиция → выберите точку на карте\n"
               "• Или вставьте ссылку Google Maps или почтовый индекс\n\n"
               "Если не нужно — «Пропустить»."),
        "en": ("📍 *Property location*\n\n"
               "• On a phone — tap «Send location» below\n"
               "• Or 📎 → Location → pick the spot on the map\n"
               "• Or paste a Google Maps link or the postcode\n\n"
               "Not needed — tap «Skip»."),
    },
    "btn_loc": {"uk": "📍 Надіслати локацію", "ru": "📍 Отправить локацию", "en": "📍 Send location"},
    "btn_skip": {"uk": "⏭ Пропустити", "ru": "⏭ Пропустить", "en": "⏭ Skip"},
    "loc_ok": {"uk": "✅ Локацію збережено", "ru": "✅ Локация сохранена", "en": "✅ Location saved"},
    "loc_skip": {"uk": "Ок, без локації", "ru": "Ок, без локации", "en": "OK, no location"},
    "ask_hub": {
        "uk": "🛡 *Підписка на сигналізацію Ajax*\n\n*Базовий комплект* (включено):\n{base}\n\n*£{base_m:.2f}/міс* (без ПДВ, до накладних)\n\nКрок 1 — оберіть *хаб*:",
        "ru": "🛡 *Подписка на сигнализацию Ajax*\n\n*Базовый комплект* (включено):\n{base}\n\n*£{base_m:.2f}/мес* (без НДС, до накладных)\n\nШаг 1 — выберите *хаб*:",
        "en": "🛡 *Ajax alarm subscription*\n\n*Base kit* (included):\n{base}\n\n*£{base_m:.2f}/month* (ex VAT, before overheads)\n\nStep 1 — choose the *hub*:",
    },
    "ask_extra": {
        "uk": "➕ *Додатково:* {name}\n_+£{m:.2f}/міс за 1 шт_\n\nСкільки додати? (крок {i}/{n})",
        "ru": "➕ *Дополнительно:* {name}\n_+£{m:.2f}/мес за 1 шт_\n\nСколько добавить? (шаг {i}/{n})",
        "en": "➕ *Extra:* {name}\n_+£{m:.2f}/month each_\n\nHow many to add? (step {i}/{n})",
    },
    "btn_done": {"uk": "✅ Готово → підсумок", "ru": "✅ Готово → итог", "en": "✅ Done → summary"},
    "review": {
        "uk": ("✅ *Підсумок підписки*\n\n{lines}\n\n"
               "Пристрої: £{dev:.2f}\nНакладні ({oh_pct}%): £{oh:.2f}\n"
               "*Щомісяця: £{mex:.2f} + ПДВ = £{minc:.2f}*\n\n"
               "Монтаж (разово): £{iex:.2f} + ПДВ = £{iinc:.2f}\n"
               "Мін. строк: {term} міс.\n\nСформувати пропозицію + договір?"),
        "ru": ("✅ *Итог подписки*\n\n{lines}\n\n"
               "Устройства: £{dev:.2f}\nНакладные ({oh_pct}%): £{oh:.2f}\n"
               "*Ежемесячно: £{mex:.2f} + НДС = £{minc:.2f}*\n\n"
               "Монтаж (разово): £{iex:.2f} + НДС = £{iinc:.2f}\n"
               "Мин. срок: {term} мес.\n\nСформировать предложение + договор?"),
        "en": ("✅ *Subscription summary*\n\n{lines}\n\n"
               "Devices: £{dev:.2f}\nOverheads ({oh_pct}%): £{oh:.2f}\n"
               "*Monthly: £{mex:.2f} + VAT = £{minc:.2f}*\n\n"
               "Installation (one-off): £{iex:.2f} + VAT = £{iinc:.2f}\n"
               "Minimum term: {term} months\n\nGenerate quote + agreement?"),
    },
    "btn_yes": {"uk": "📄 Сформувати", "ru": "📄 Сформировать", "en": "📄 Generate"},
    "btn_restart": {"uk": "🔁 Змінити", "ru": "🔁 Изменить", "en": "🔁 Change"},
    "btn_no": {"uk": "✖️ Скасувати", "ru": "✖️ Отмена", "en": "✖️ Cancel"},
    "caption": {"uk": "🛡 Пропозиція + договір підписки", "ru": "🛡 Предложение + договор подписки",
                "en": "🛡 Your alarm subscription quote + agreement"},
}


def tx(key, lang, **kw):
    d = TXT.get(key, {})
    s = d.get(lang) or d.get("en") or key
    return s.format(**kw) if kw else s


# ---------------------------------------------------------------------------
# 1) ENTRY → ask location
# ---------------------------------------------------------------------------
async def enter(update, context, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    if q:
        await q.answer()
    context.user_data["sub_hub"] = "hub2"
    context.user_data["sub_extras"] = {}
    context.user_data["sub_step"] = 0
    context.user_data.pop("location", None)
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(tx("btn_loc", lang), request_location=True)],
         [KeyboardButton(tx("btn_skip", lang))]],
        resize_keyboard=True, one_time_keyboard=True)
    await context.bot.send_message(update.effective_chat.id, tx("ask_loc", lang),
                                   parse_mode="Markdown", reply_markup=kb)
    return S["SUB_LOC"]


async def handle_location(update, context, get_lang):
    """Accepts: shared location / venue (phone or 📎 → Location),
    a Google Maps link, "lat, lon" coordinates or a postcode/address as text, or Skip."""
    import re
    from urllib.parse import quote_plus
    lang = get_lang(context)
    msg = update.message or update.edited_message
    if msg is None:
        return S["SUB_LOC"]
    loc = msg.location or (msg.venue.location if getattr(msg, "venue", None) else None)
    text = (msg.text or "").strip()
    skip_words = {tx("btn_skip", l) for l in ("uk", "ru", "en")} | {"skip", "пропустити", "пропустить", "-"}

    if loc:
        lat, lon = loc.latitude, loc.longitude
        context.user_data["location"] = {"lat": lat, "lon": lon,
                                         "url": f"https://maps.google.com/?q={lat:.6f},{lon:.6f}"}
        note = tx("loc_ok", lang)
    elif text and text.lower() not in {w.lower() for w in skip_words}:
        m = re.search(r"(-?\d{1,2}\.\d{3,})\s*,\s*(-?\d{1,3}\.\d{3,})", text)
        if m:
            lat, lon = float(m.group(1)), float(m.group(2))
            context.user_data["location"] = {"lat": lat, "lon": lon,
                                             "url": f"https://maps.google.com/?q={lat:.6f},{lon:.6f}"}
        elif re.search(r"https?://\S+", text):
            context.user_data["location"] = {"url": re.search(r"https?://\S+", text).group(0)}
        else:
            context.user_data["location"] = {"url": "https://maps.google.com/?q=" + quote_plus(text),
                                             "text": text}
        note = tx("loc_ok", lang)
    else:
        note = tx("loc_skip", lang)
    await msg.reply_text(note, reply_markup=ReplyKeyboardRemove())
    return await _ask_hub(update, context, lang)


# ---------------------------------------------------------------------------
# 2) HUB
# ---------------------------------------------------------------------------
async def _ask_hub(update, context, lang):
    base = "\n".join(f"• {q}× {n}" for q, n in ps.BASE_KIT_CONTENTS)
    kb = []
    for key, h in ps.HUBS.items():
        label = h["name"] + (f"  +£{h['monthly']:.2f}/mo" if h["monthly"] else "")
        kb.append([InlineKeyboardButton(label, callback_data=f"subhub:{key}")])
    await context.bot.send_message(
        update.effective_chat.id,
        tx("ask_hub", lang, base=base, base_m=ps.BASE_KIT_MONTHLY),
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return S["SUB_HUB"]


async def handle_hub(update, context, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    context.user_data["sub_hub"] = q.data.split(":")[1]
    context.user_data["sub_step"] = 0
    return await _ask_extra(q, context, lang)


# ---------------------------------------------------------------------------
# 3) EXTRAS (one state, loops through ps.EXTRA_STEPS)
# ---------------------------------------------------------------------------
def _qty_kb(max_n=6):
    btns = [InlineKeyboardButton(str(n), callback_data=f"subx:{n}") for n in range(0, max_n + 1)]
    return [btns[i:i + 4] for i in range(0, len(btns), 4)]


async def _ask_extra(q, context, lang):
    i = context.user_data.get("sub_step", 0)
    steps = ps.EXTRA_STEPS
    if i >= len(steps):
        return await _show_review(q, context, lang)
    key = steps[i]
    item = ps.EXTRAS[key]
    rows = _qty_kb(3 if key in ("siren_in", "siren_out", "keypad") else 6)
    rows.append([InlineKeyboardButton(tx("btn_done", lang), callback_data="subx:done")])
    await q.edit_message_text(
        tx("ask_extra", lang, name=item["name"], m=item["monthly"], i=i + 1, n=len(steps)),
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))
    return S["SUB_EXTRA"]


async def handle_extra(update, context, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    val = q.data.split(":")[1]
    if val == "done":
        return await _show_review(q, context, lang)
    i = context.user_data.get("sub_step", 0)
    key = ps.EXTRA_STEPS[i]
    n = int(val)
    if n:
        context.user_data["sub_extras"][key] = n
    else:
        context.user_data["sub_extras"].pop(key, None)
    context.user_data["sub_step"] = i + 1
    return await _ask_extra(q, context, lang)


# ---------------------------------------------------------------------------
# 4) REVIEW
# ---------------------------------------------------------------------------
async def _show_review(q, context, lang):
    sub = ps.build_subscription(context.user_data.get("sub_hub", "hub2"),
                                context.user_data.get("sub_extras", {}))
    context.user_data["sub_quote"] = sub
    lines = "\n".join(
        f"• {l['qty']}× {l['name']} — £{l['total']:.2f}" for l in sub["lines"])
    kb = [
        [InlineKeyboardButton(tx("btn_yes", lang), callback_data="subok:yes")],
        [InlineKeyboardButton(tx("btn_restart", lang), callback_data="subok:restart"),
         InlineKeyboardButton(tx("btn_no", lang), callback_data="subok:cancel")],
    ]
    await q.edit_message_text(
        tx("review", lang, lines=lines, dev=sub["devices_monthly"],
           oh_pct=int(round(ps.OVERHEAD_PCT * 100)), oh=sub["overhead"],
           mex=sub["monthly_ex_vat"], minc=sub["monthly_inc_vat"],
           iex=sub["install_ex_vat"], iinc=sub["install_inc_vat"], term=sub["min_term"]),
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return S["SUB_REVIEW"]


async def restart_selection(update, context, get_lang):
    """'Change' button on review → back to hub step."""
    lang = get_lang(context)
    context.user_data["sub_extras"] = {}
    context.user_data["sub_step"] = 0
    return await _ask_hub(update, context, lang)
