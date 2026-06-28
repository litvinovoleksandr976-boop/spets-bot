"""
SPETS SECURITY — Ajax Superior conversation flow (Telegram).

Self-contained module: exposes ajax states + a dict of handlers that bot.py
registers into its ConversationHandler. Keeps the CCTV flow untouched.

Flow:
  SERVICE -> (user picks "alarm")
    AJAX_MODE         : Ready kit  |  Build your own
      kit  -> AJAX_KIT        : Budget / Balance / Elite -> confirm -> quote
      own  -> AJAX_HUB        : Hub 2 / Hub 2 Plus / Superior G3
              AJAX_MOTION     : qty of MotionProtect S
              AJAX_MOTIONCAM  : qty of MotionCam S
              AJAX_DOOR       : qty of DoorProtect S
              AJAX_EXTRA      : multi-select (leak / smoke / combi) -> qty each
              AJAX_SIREN      : indoor / outdoor / both
              AJAX_KEYPAD     : yes (which) / no
              AJAX_KEYFOB     : qty (0..n)
              -> review -> quote
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import pricing_ajax as pa

log = logging.getLogger(__name__)

# State IDs are assigned by bot.py (passed in via init). We store them here.
S = {}  # filled by init_states()


def init_states(state_ids: dict):
    """bot.py calls this with the integer state ids it allocated."""
    S.update(state_ids)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _qty_keyboard(prefix: str, max_n: int = 8, allow_zero: bool = True):
    """Build a 0..max_n quantity keyboard (rows of 4)."""
    start = 0 if allow_zero else 1
    btns = [InlineKeyboardButton(str(n), callback_data=f"{prefix}:{n}")
            for n in range(start, max_n + 1)]
    rows = [btns[i:i + 4] for i in range(0, len(btns), 4)]
    return InlineKeyboardMarkup(rows)


def _t(translations_t, key, lang, **kw):
    """Wrapper around bot's t(); falls back to the key text if missing."""
    try:
        val = translations_t(key, lang, **kw)
        if val.startswith("[missing"):
            return _FALLBACK.get(key, {}).get(lang) or _FALLBACK.get(key, {}).get("en") or key
        return val
    except Exception:
        return _FALLBACK.get(key, {}).get(lang) or key


# Inline fallback texts (so it works before translations.py is updated)
_FALLBACK = {
    "ajax_choose_mode": {
        "en": "🛡️ *Ajax Wireless Alarm*\n\nHow would you like to proceed?",
        "ru": "🛡️ *Беспроводная сигнализация Ajax*\n\nКак продолжим?",
        "uk": "🛡️ *Бездротова сигналізація Ajax*\n\nЯк продовжимо?",
    },
    "ajax_mode_kit": {"en": "📦 Ready kit", "ru": "📦 Готовый комплект", "uk": "📦 Готовий комплект"},
    "ajax_mode_custom": {"en": "🔧 Build my own", "ru": "🔧 Собрать свою", "uk": "🔧 Зібрати свою"},
    "ajax_choose_kit": {
        "en": "Choose a ready kit:", "ru": "Выберите готовый комплект:", "uk": "Оберіть готовий комплект:"},
    "ajax_kit_budget": {"en": "🟢 Budget", "ru": "🟢 Budget", "uk": "🟢 Budget"},
    "ajax_kit_balance": {"en": "🔵 Balance", "ru": "🔵 Balance", "uk": "🔵 Balance"},
    "ajax_kit_elite": {"en": "🟡 Elite", "ru": "🟡 Elite", "uk": "🟡 Elite"},
    "ajax_choose_hub": {
        "en": "Step 1 — choose the hub (control panel):",
        "ru": "Шаг 1 — выберите хаб (контрольную панель):",
        "uk": "Крок 1 — оберіть хаб (контрольну панель):"},
    "ajax_ask_motion": {
        "en": "Step 2 — how many *motion detectors* (MotionProtect S)?",
        "ru": "Шаг 2 — сколько *датчиков движения* (MotionProtect S)?",
        "uk": "Крок 2 — скільки *датчиків руху* (MotionProtect S)?"},
    "ajax_ask_motioncam": {
        "en": "Step 3 — how many *motion detectors with camera* (MotionCam S)?",
        "ru": "Шаг 3 — сколько *датчиков движения с камерой* (MotionCam S)?",
        "uk": "Крок 3 — скільки *датчиків руху з камерою* (MotionCam S)?"},
    "ajax_ask_door": {
        "en": "Step 4 — how many *door/window detectors* (DoorProtect S)?",
        "ru": "Шаг 4 — сколько *датчиков открытия* (DoorProtect S)?",
        "uk": "Крок 4 — скільки *датчиків відкриття* (DoorProtect S)?"},
    "ajax_ask_leak": {
        "en": "How many *leak detectors* (LeaksProtect)?",
        "ru": "Сколько *датчиков протечки* (LeaksProtect)?",
        "uk": "Скільки *датчиків протікання* (LeaksProtect)?"},
    "ajax_ask_smoke": {
        "en": "How many *smoke detectors* (FireProtect 2)?",
        "ru": "Сколько *датчиков дыма* (FireProtect 2)?",
        "uk": "Скільки *датчиків диму* (FireProtect 2)?"},
    "ajax_ask_siren": {
        "en": "Step 5 — which *siren* do you need?",
        "ru": "Шаг 5 — какая *сирена* нужна?",
        "uk": "Крок 5 — яка *сирена* потрібна?"},
    "ajax_siren_in": {"en": "🔔 Indoor", "ru": "🔔 Внутренняя", "uk": "🔔 Внутрішня"},
    "ajax_siren_out": {"en": "📢 Outdoor", "ru": "📢 Наружная", "uk": "📢 Зовнішня"},
    "ajax_siren_both": {"en": "🔔📢 Both", "ru": "🔔📢 Обе", "uk": "🔔📢 Обидві"},
    "ajax_siren_none": {"en": "➖ None", "ru": "➖ Не нужна", "uk": "➖ Не потрібна"},
    "ajax_ask_keypad": {
        "en": "Step 6 — add a *keypad* (arm/disarm on the wall)?",
        "ru": "Шаг 6 — добавить *клавиатуру* (постановка на стене)?",
        "uk": "Крок 6 — додати *клавіатуру* (керування на стіні)?"},
    "ajax_keypad_s": {"en": "KeyPad Plus S", "ru": "KeyPad Plus S", "uk": "KeyPad Plus S"},
    "ajax_keypad_g3": {"en": "KeyPad Plus G3", "ru": "KeyPad Plus G3", "uk": "KeyPad Plus G3"},
    "ajax_keypad_no": {"en": "➖ No keypad", "ru": "➖ Без клавиатуры", "uk": "➖ Без клавіатури"},
    "ajax_ask_keyfob": {
        "en": "Step 7 — how many *keyfobs* (SpaceControl S)?",
        "ru": "Шаг 7 — сколько *брелоков* (SpaceControl S)?",
        "uk": "Крок 7 — скільки *брелоків* (SpaceControl S)?"},
    "ajax_review": {
        "en": "✅ *Your Ajax system:*\n\n{summary}\n\n*Total (incl. install &amp; VAT): £{total:,.2f}*\n\nGenerate the quote?",
        "ru": "✅ *Ваша система Ajax:*\n\n{summary}\n\n*Итого (с монтажом и НДС): £{total:,.2f}*\n\nСформировать предложение?",
        "uk": "✅ *Ваша система Ajax:*\n\n{summary}\n\n*Разом (з монтажем та ПДВ): £{total:,.2f}*\n\nСформувати пропозицію?"},
    "ajax_kit_review": {
        "en": "✅ *{name}*\n\n{contents}\n\n*Total (incl. install &amp; VAT): £{total:,.2f}*\n\nGenerate the quote?",
        "ru": "✅ *{name}*\n\n{contents}\n\n*Итого (с монтажом и НДС): £{total:,.2f}*\n\nСформировать предложение?",
        "uk": "✅ *{name}*\n\n{contents}\n\n*Разом (з монтажем та ПДВ): £{total:,.2f}*\n\nСформувати пропозицію?"},
    "ajax_confirm_yes": {"en": "✅ Generate quote", "ru": "✅ Сформировать", "uk": "✅ Сформувати"},
    "ajax_confirm_no": {"en": "✖️ Cancel", "ru": "✖️ Отмена", "uk": "✖️ Скасувати"},
    "ajax_empty": {
        "en": "You haven't selected any devices. Let's start again — /start",
        "ru": "Вы не выбрали устройства. Начнём заново — /start",
        "uk": "Ви не обрали жодного пристрою. Почнімо заново — /start"},
}


# ---------------------------------------------------------------------------
# Entry: user picked "alarm" in SERVICE  →  choose mode
# ---------------------------------------------------------------------------
async def enter_ajax(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    context.user_data["service"] = "ajax"
    context.user_data["ajax_sel"] = {}  # component_key -> qty
    kb = [
        [InlineKeyboardButton(_t(t, "ajax_mode_kit", lang), callback_data="ajmode:kit")],
        [InlineKeyboardButton(_t(t, "ajax_mode_custom", lang), callback_data="ajmode:custom")],
    ]
    await q.edit_message_text(_t(t, "ajax_choose_mode", lang),
                              parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return S["AJAX_MODE"]


async def handle_mode(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    mode = q.data.split(":")[1]
    if mode == "kit":
        kb = [
            [InlineKeyboardButton(_t(t, "ajax_kit_budget", lang) + "  £%.0f" %
                                  pa.build_kit_quote("budget")["grand_total"], callback_data="ajkit:budget")],
            [InlineKeyboardButton(_t(t, "ajax_kit_balance", lang) + "  £%.0f" %
                                  pa.build_kit_quote("balance")["grand_total"], callback_data="ajkit:balance")],
            [InlineKeyboardButton(_t(t, "ajax_kit_elite", lang) + "  £%.0f" %
                                  pa.build_kit_quote("elite")["grand_total"], callback_data="ajkit:elite")],
        ]
        await q.edit_message_text(_t(t, "ajax_choose_kit", lang),
                                  parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        return S["AJAX_KIT"]
    else:
        # build your own — hub first
        kb = [
            [InlineKeyboardButton("Ajax Hub 2  £%.0f" % pa.component_client_price("hub2"),
                                  callback_data="ajhub:hub2")],
            [InlineKeyboardButton("Ajax Hub 2 Plus  £%.0f" % pa.component_client_price("hub2plus"),
                                  callback_data="ajhub:hub2plus")],
            [InlineKeyboardButton("Ajax Superior Hub G3  £%.0f" % pa.component_client_price("hubg3"),
                                  callback_data="ajhub:hubg3")],
        ]
        await q.edit_message_text(_t(t, "ajax_choose_hub", lang),
                                  parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        return S["AJAX_HUB"]


# ---------------------------------------------------------------------------
# Ready kit chosen → review
# ---------------------------------------------------------------------------
async def handle_kit(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    tier = q.data.split(":")[1]
    context.user_data["ajax_kit_tier"] = tier
    quote = pa.build_kit_quote(tier)
    contents = "\n".join(f"• {n} × {qty}" for n, qty in quote["contents"])
    kb = [
        [InlineKeyboardButton(_t(t, "ajax_confirm_yes", lang), callback_data="ajok:kit")],
        [InlineKeyboardButton(_t(t, "ajax_confirm_no", lang), callback_data="ajok:cancel")],
    ]
    await q.edit_message_text(
        _t(t, "ajax_kit_review", lang, name=quote["kit_name"],
           contents=contents, total=quote["grand_total"]),
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return S["AJAX_REVIEW"]


# ---------------------------------------------------------------------------
# Build your own — step by step
# ---------------------------------------------------------------------------
async def handle_hub(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    hub = q.data.split(":")[1]
    context.user_data["ajax_sel"][hub] = 1
    await q.edit_message_text(_t(t, "ajax_ask_motion", lang),
                              parse_mode="Markdown",
                              reply_markup=_qty_keyboard("ajmot"))
    return S["AJAX_MOTION"]


async def handle_motion(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    n = int(q.data.split(":")[1])
    if n:
        context.user_data["ajax_sel"]["motion_s"] = n
    await q.edit_message_text(_t(t, "ajax_ask_motioncam", lang),
                              parse_mode="Markdown",
                              reply_markup=_qty_keyboard("ajmcam"))
    return S["AJAX_MOTIONCAM"]


async def handle_motioncam(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    n = int(q.data.split(":")[1])
    if n:
        context.user_data["ajax_sel"]["motioncam_s"] = n
    await q.edit_message_text(_t(t, "ajax_ask_door", lang),
                              parse_mode="Markdown",
                              reply_markup=_qty_keyboard("ajdoor"))
    return S["AJAX_DOOR"]


async def handle_door(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    n = int(q.data.split(":")[1])
    if n:
        context.user_data["ajax_sel"]["door_s"] = n
    # extra sensors: leak
    await q.edit_message_text(_t(t, "ajax_ask_leak", lang),
                              parse_mode="Markdown",
                              reply_markup=_qty_keyboard("ajleak"))
    return S["AJAX_LEAK"]


async def handle_leak(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    n = int(q.data.split(":")[1])
    if n:
        context.user_data["ajax_sel"]["leak"] = n
    await q.edit_message_text(_t(t, "ajax_ask_smoke", lang),
                              parse_mode="Markdown",
                              reply_markup=_qty_keyboard("ajsmoke"))
    return S["AJAX_SMOKE"]


async def handle_smoke(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    n = int(q.data.split(":")[1])
    if n:
        context.user_data["ajax_sel"]["smoke_rb"] = n
    # siren choice
    kb = [
        [InlineKeyboardButton(_t(t, "ajax_siren_in", lang), callback_data="ajsir:in")],
        [InlineKeyboardButton(_t(t, "ajax_siren_out", lang), callback_data="ajsir:out")],
        [InlineKeyboardButton(_t(t, "ajax_siren_both", lang), callback_data="ajsir:both")],
        [InlineKeyboardButton(_t(t, "ajax_siren_none", lang), callback_data="ajsir:none")],
    ]
    await q.edit_message_text(_t(t, "ajax_ask_siren", lang),
                              parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return S["AJAX_SIREN"]


async def handle_siren(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    choice = q.data.split(":")[1]
    sel = context.user_data["ajax_sel"]
    if choice in ("in", "both"):
        sel["siren_in"] = 1
    if choice in ("out", "both"):
        sel["siren_out_dd"] = 1
    # keypad
    kb = [
        [InlineKeyboardButton(_t(t, "ajax_keypad_s", lang) + "  £%.0f" %
                              pa.component_client_price("keypad_s"), callback_data="ajkp:keypad_s")],
        [InlineKeyboardButton(_t(t, "ajax_keypad_g3", lang) + "  £%.0f" %
                              pa.component_client_price("keypad_g3"), callback_data="ajkp:keypad_g3")],
        [InlineKeyboardButton(_t(t, "ajax_keypad_no", lang), callback_data="ajkp:no")],
    ]
    await q.edit_message_text(_t(t, "ajax_ask_keypad", lang),
                              parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return S["AJAX_KEYPAD"]


async def handle_keypad(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    choice = q.data.split(":")[1]
    if choice != "no":
        context.user_data["ajax_sel"][choice] = 1
    await q.edit_message_text(_t(t, "ajax_ask_keyfob", lang),
                              parse_mode="Markdown",
                              reply_markup=_qty_keyboard("ajkf"))
    return S["AJAX_KEYFOB"]


async def handle_keyfob(update, context, t, get_lang):
    lang = get_lang(context)
    q = update.callback_query
    await q.answer()
    n = int(q.data.split(":")[1])
    if n:
        context.user_data["ajax_sel"]["keyfob_s"] = n

    sel = context.user_data["ajax_sel"]
    if not sel:
        await q.edit_message_text(_t(t, "ajax_empty", lang))
        return -1  # ConversationHandler.END (bot.py maps)

    quote = pa.build_custom_quote(sel)
    # summary
    lines = []
    for li in quote["line_items"]:
        lines.append(f"• {li['qty']} × {li['name']} — £{li['line_total']:,.2f}")
    lines.append(f"• Installation — £{quote['install']:,.0f}")
    summary = "\n".join(lines)
    kb = [
        [InlineKeyboardButton(_t(t, "ajax_confirm_yes", lang), callback_data="ajok:custom")],
        [InlineKeyboardButton(_t(t, "ajax_confirm_no", lang), callback_data="ajok:cancel")],
    ]
    await q.edit_message_text(
        _t(t, "ajax_review", lang, summary=summary, total=quote["grand_total"]),
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return S["AJAX_REVIEW"]
