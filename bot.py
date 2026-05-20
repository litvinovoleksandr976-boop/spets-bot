"""
SPETS SECURITY — Telegram bot for CCTV quote generation (multilingual EN/RU/UK)
Python 3.10+ | python-telegram-bot 20.7

Flow:
1. /start → language selection
2. Welcome → 8 questions
3. Build quote → confirm → generate PDF → email → notify admin
"""
import os
import re
import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

from pricing import build_quote
from quote_generator import generate_quote_pdf
from email_sender import send_quote_email, send_admin_notification
from translations import t

# =====================================================================
# CONFIG
# =====================================================================
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

QUOTE_COUNTER_FILE = "/tmp/spets_quote_counter.txt"

# Conversation states
(LANGUAGE, NAME, PHONE, EMAIL, ADDRESS, OBJECT_TYPE,
 CAMERA_COUNT, CAMERA_TIER, ARCHIVE, CONFIRM) = range(10)


# =====================================================================
# HELPERS
# =====================================================================
def next_quote_number() -> str:
    try:
        with open(QUOTE_COUNTER_FILE, "r") as f:
            n = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        n = 200
    n += 1
    with open(QUOTE_COUNTER_FILE, "w") as f:
        f.write(str(n))
    return str(n)


def valid_email(s: str) -> bool:
    return bool(re.match(r"^[\w\.\-\+]+@[\w\.\-]+\.\w+$", s))


def valid_phone(s: str) -> bool:
    cleaned = re.sub(r"[\s\-\(\)]", "", s)
    return bool(re.match(r"^\+?\d{7,15}$", cleaned))


def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "en")


# =====================================================================
# COMMAND HANDLERS
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point — first ask language."""
    user = update.effective_user
    context.user_data.clear()
    context.user_data["telegram_user_id"] = user.id
    context.user_data["telegram_username"] = user.username or ""
    context.user_data["first_name"] = user.first_name or ""

    kb = [
        [InlineKeyboardButton("English", callback_data="lang:en")],
        [InlineKeyboardButton("Русский", callback_data="lang:ru")],
        [InlineKeyboardButton("Українська", callback_data="lang:uk")],
    ]
    await update.message.reply_text(
        t("language_prompt", "en"),
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return LANGUAGE


async def change_language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/language command — change language anytime."""
    kb = [
        [InlineKeyboardButton("English", callback_data="lang:en")],
        [InlineKeyboardButton("Русский", callback_data="lang:ru")],
        [InlineKeyboardButton("Українська", callback_data="lang:uk")],
    ]
    await update.message.reply_text(
        t("language_prompt", "en"),
        reply_markup=InlineKeyboardMarkup(kb),
    )
    # If user was mid-conversation, restart it
    return LANGUAGE


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process language selection."""
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang:", "")
    context.user_data["lang"] = lang

    first_name = context.user_data.get("first_name", "")

    await query.edit_message_text(
        t("language_set", lang)
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=t("welcome", lang, name=first_name),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text(t("ask_name_invalid", lang))
        return NAME

    context.user_data["name"] = name
    await update.message.reply_text(
        t("ask_phone", lang, name=name),
        parse_mode="Markdown",
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    phone = update.message.text.strip()
    if not valid_phone(phone):
        await update.message.reply_text(t("ask_phone_invalid", lang))
        return PHONE

    context.user_data["phone"] = phone
    await update.message.reply_text(t("ask_email", lang), parse_mode="Markdown")
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    email = update.message.text.strip().lower()
    if not valid_email(email):
        await update.message.reply_text(t("ask_email_invalid", lang))
        return EMAIL

    context.user_data["email"] = email
    await update.message.reply_text(t("ask_address", lang), parse_mode="Markdown")
    return ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    context.user_data["address"] = update.message.text.strip()

    keyboard = ReplyKeyboardMarkup(
        [
            [t("object_house", lang), t("object_office", lang)],
            [t("object_shop", lang), t("object_warehouse", lang)],
            [t("object_other", lang)],
        ],
        one_time_keyboard=True, resize_keyboard=True,
    )
    await update.message.reply_text(
        t("ask_object_type", lang),
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    return OBJECT_TYPE


async def get_object_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    context.user_data["object_type"] = update.message.text.strip()
    await update.message.reply_text(
        t("ask_camera_count", lang),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CAMERA_COUNT


async def get_camera_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    txt = update.message.text.strip()
    try:
        n = int(txt)
    except ValueError:
        await update.message.reply_text(t("ask_camera_count_invalid", lang))
        return CAMERA_COUNT

    if n < 1 or n > 16:
        await update.message.reply_text(t("ask_camera_count_too_big", lang))
        return CAMERA_COUNT

    context.user_data["camera_count"] = n

    kb = [
        [InlineKeyboardButton(t("tier_basic_btn", lang), callback_data="tier:basic")],
        [InlineKeyboardButton(t("tier_standard_btn", lang), callback_data="tier:standard")],
        [InlineKeyboardButton(t("tier_premium_btn", lang), callback_data="tier:premium")],
        [InlineKeyboardButton(t("tier_4k_btn", lang), callback_data="tier:premium_4k")],
    ]
    await update.message.reply_text(
        t("ask_camera_tier", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return CAMERA_TIER


async def get_camera_tier(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()
    tier = query.data.replace("tier:", "")
    context.user_data["camera_tier"] = tier

    kb = [
        [InlineKeyboardButton(t("arch_1week", lang), callback_data="arch:1_week")],
        [InlineKeyboardButton(t("arch_2weeks", lang), callback_data="arch:2_weeks")],
        [InlineKeyboardButton(t("arch_1month", lang), callback_data="arch:1_month")],
        [InlineKeyboardButton(t("arch_2months", lang), callback_data="arch:2_months")],
    ]
    await query.edit_message_text(
        t("ask_archive", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return ARCHIVE


async def get_archive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()
    archive = query.data.replace("arch:", "")
    context.user_data["archive"] = archive

    data = context.user_data
    quote = build_quote(
        camera_count=data["camera_count"],
        camera_tier=data["camera_tier"],
        archive_choice=archive,
    )
    context.user_data["quote"] = quote

    # Summary
    lines = [t("quote_summary_header", lang)]
    for i, item in enumerate(quote["items"], 1):
        line_total = (item["base"] + item["vat"]) * item["qty"]
        lines.append(f"{i}. {item['name'][:45]}")
        lines.append(f"   Qty: {item['qty']} × £{item['base']:.2f} = £{line_total:.2f}")
    lines.append(f"\n{t('subtotal', lang)} £{quote['subtotal']:.2f}")
    lines.append(f"{t('vat_label', lang)} £{quote['vat_total']:.2f}")
    lines.append(f"{t('grand_total_label', lang)} *£{quote['grand_total']:.2f}*")

    kb = [
        [InlineKeyboardButton(t("send_pdf_btn", lang), callback_data="confirm:yes")],
        [InlineKeyboardButton(t("cancel_btn", lang), callback_data="confirm:no")],
    ]
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()

    if query.data == "confirm:no":
        await query.edit_message_text(t("cancelled", lang))
        context.user_data.clear()
        return ConversationHandler.END

    await query.edit_message_text(t("generating_pdf", lang))

    data = context.user_data
    quote = data["quote"]

    quote_number = next_quote_number()
    quote_for_pdf = {
        **quote,
        "quote_number": quote_number,
        "date": datetime.now(),
        "customer": {
            "name": data["name"],
            "phone": data["phone"],
            "email": data["email"],
            "address": data.get("address", ""),
        },
        "lang": lang,
    }

    # Generate PDF
    try:
        pdf_bytes = generate_quote_pdf(quote_for_pdf)
    except Exception as e:
        log.exception("PDF generation failed")
        await query.edit_message_text(t("pdf_error", lang))
        return ConversationHandler.END

    # Send to customer email (via Resend)
    email_ok = send_quote_email(
        to_email=data["email"],
        customer_name=data["name"],
        quote_number=quote_number,
        grand_total=quote["grand_total"],
        pdf_bytes=pdf_bytes,
        lang=lang,
    )

    # Also send PDF in chat
    try:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=pdf_bytes,
            filename=f"Spets-Quote-{quote_number}.pdf",
            caption=t("pdf_caption", lang, n=quote_number),
        )
    except Exception as e:
        log.error(f"Failed to send PDF in chat: {e}")

    # Notify admin (always in English so manager understands regardless of client lang)
    if ADMIN_CHAT_ID:
        send_admin_notification(
            admin_chat_id=ADMIN_CHAT_ID,
            bot_token=TELEGRAM_TOKEN,
            customer_name=data["name"],
            customer_phone=data["phone"],
            customer_email=data["email"],
            quote_number=quote_number,
            grand_total=quote["grand_total"],
        )

    # Final message to customer
    if email_ok:
        msg = t("quote_sent_ok", lang, n=quote_number, email=data["email"], total=quote["grand_total"])
    else:
        msg = t("quote_sent_email_failed", lang, n=quote_number)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode="Markdown",
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    await update.message.reply_text(
        t("cancelled", lang),
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(t("help", lang), parse_mode="Markdown")


# =====================================================================
# MAIN
# =====================================================================
def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN env variable is not set")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("language", change_language_cmd),
        ],
        states={
            LANGUAGE:      [CallbackQueryHandler(set_language, pattern="^lang:")],
            NAME:          [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            EMAIL:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            ADDRESS:       [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            OBJECT_TYPE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, get_object_type)],
            CAMERA_COUNT:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_camera_count)],
            CAMERA_TIER:   [CallbackQueryHandler(get_camera_tier, pattern="^tier:")],
            ARCHIVE:       [CallbackQueryHandler(get_archive, pattern="^arch:")],
            CONFIRM:       [CallbackQueryHandler(confirm, pattern="^confirm:")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True,
        per_user=True,
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_cmd))

    log.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
