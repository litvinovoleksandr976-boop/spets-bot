"""
SPETS SECURITY — Telegram bot for CCTV quote generation
Python 3.10+ | python-telegram-bot 20.7

Conversation flow:
1. /start → welcome
2. Ask: name → phone → email → address → object type
3. Ask: camera count (number)
4. Ask: camera tier (basic/standard/premium/4K)
5. Ask: archive duration (1w / 2w / 1m / 2m)
6. Generate quote → send PDF to email → notify admin → confirm in chat
"""
import os
import re
import logging
import asyncio
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

from pricing import build_quote, CAMERAS
from quote_generator import generate_quote_pdf
from email_sender import send_quote_email, send_admin_notification

# =====================================================================
# CONFIG
# =====================================================================
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")  # Your Telegram chat ID for notifications

# Quote counter — in production this comes from KeyCRM, here just a stub
QUOTE_COUNTER_FILE = "/tmp/spets_quote_counter.txt"

# Conversation states
(NAME, PHONE, EMAIL, ADDRESS, OBJECT_TYPE,
 CAMERA_COUNT, CAMERA_TIER, ARCHIVE, CONFIRM) = range(9)


# =====================================================================
# HELPERS
# =====================================================================
def next_quote_number() -> str:
    """Get next quote number (simple file-based counter)."""
    try:
        with open(QUOTE_COUNTER_FILE, "r") as f:
            n = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        n = 200  # start from 200 since manual invoices go up to ~183
    n += 1
    with open(QUOTE_COUNTER_FILE, "w") as f:
        f.write(str(n))
    return str(n)


def valid_email(s: str) -> bool:
    return bool(re.match(r"^[\w\.\-\+]+@[\w\.\-]+\.\w+$", s))


def valid_phone(s: str) -> bool:
    cleaned = re.sub(r"[\s\-\(\)]", "", s)
    return bool(re.match(r"^\+?\d{7,15}$", cleaned))


# =====================================================================
# COMMAND HANDLERS
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point — greet and ask for name."""
    user = update.effective_user
    context.user_data.clear()
    context.user_data["telegram_user_id"] = user.id
    context.user_data["telegram_username"] = user.username or ""

    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to *Spets Security* — CCTV quote service.\n\n"
        "I'll ask you a few quick questions (about 1 minute) and send you "
        "a personalised PDF quote to your email.\n\n"
        "Let's start. *What is your full name?*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("Please enter a valid name (at least 2 characters).")
        return NAME

    context.user_data["name"] = name
    await update.message.reply_text(
        f"Nice to meet you, {name}!\n\n"
        "📞 What's your *phone number*? (with country code, e.g. +447700900123)",
        parse_mode="Markdown",
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text.strip()
    if not valid_phone(phone):
        await update.message.reply_text(
            "❗ That doesn't look like a valid phone. Try again (e.g. +447700900123)."
        )
        return PHONE

    context.user_data["phone"] = phone
    await update.message.reply_text(
        "📧 What's your *email address*?\n"
        "(We'll send the PDF quote there)",
        parse_mode="Markdown",
    )
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text.strip().lower()
    if not valid_email(email):
        await update.message.reply_text(
            "❗ That doesn't look like a valid email. Try again (e.g. name@example.com)."
        )
        return EMAIL

    context.user_data["email"] = email
    await update.message.reply_text(
        "📍 What's the *installation address*?\n"
        "(Street, city, postcode)",
        parse_mode="Markdown",
    )
    return ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["address"] = update.message.text.strip()

    keyboard = ReplyKeyboardMarkup(
        [["🏠 House", "🏢 Office"], ["🏪 Shop", "🏭 Warehouse"], ["📦 Other"]],
        one_time_keyboard=True, resize_keyboard=True,
    )
    await update.message.reply_text(
        "🏢 What *type of object* needs CCTV?",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    return OBJECT_TYPE


async def get_object_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["object_type"] = update.message.text.strip()
    await update.message.reply_text(
        "📹 How many *cameras* do you need?\n"
        "(Just type a number, e.g. 4)",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CAMERA_COUNT


async def get_camera_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    txt = update.message.text.strip()
    try:
        n = int(txt)
    except ValueError:
        await update.message.reply_text("Please type a number between 1 and 16.")
        return CAMERA_COUNT

    if n < 1 or n > 16:
        await update.message.reply_text(
            "We currently quote 1–16 cameras automatically. "
            "For larger projects, please call us at +44 7706 906079."
        )
        return CAMERA_COUNT

    context.user_data["camera_count"] = n

    # Camera tier choice
    kb = [
        [InlineKeyboardButton("🟢 Basic — HiLook 5MP IR (£50.60)", callback_data="tier:basic")],
        [InlineKeyboardButton("🔵 Standard — HiLook 4MP ColorVu (£60.95)", callback_data="tier:standard")],
        [InlineKeyboardButton("🟠 Premium — Hikvision 4MP ColorVu 3.0 (£141.45)", callback_data="tier:premium")],
        [InlineKeyboardButton("🔴 Premium 4K — Hikvision 8MP 4K (£193.20)", callback_data="tier:premium_4k")],
    ]
    await update.message.reply_text(
        "📸 Which *camera tier* would you like?\n\n"
        "🟢 *Basic* — IR night vision\n"
        "🔵 *Standard* — Colour at night (ColorVu)\n"
        "🟠 *Premium* — ColorVu 3.0 + mic/speaker\n"
        "🔴 *Premium 4K* — 8MP top tier",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return CAMERA_TIER


async def get_camera_tier(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    tier = query.data.replace("tier:", "")
    context.user_data["camera_tier"] = tier

    kb = [
        [InlineKeyboardButton("📅 1 week (1TB HDD)", callback_data="arch:1_week")],
        [InlineKeyboardButton("📅 2 weeks (2TB HDD)", callback_data="arch:2_weeks")],
        [InlineKeyboardButton("📅 1 month (4TB HDD)", callback_data="arch:1_month")],
        [InlineKeyboardButton("📅 2 months (6TB HDD)", callback_data="arch:2_months")],
    ]
    await query.edit_message_text(
        "💾 How long do you want to *keep video archive*?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return ARCHIVE


async def get_archive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    archive = query.data.replace("arch:", "")
    context.user_data["archive"] = archive

    # Build quote
    data = context.user_data
    quote = build_quote(
        camera_count=data["camera_count"],
        camera_tier=data["camera_tier"],
        archive_choice=archive,
    )
    context.user_data["quote"] = quote

    # Summary
    lines = ["📋 *Quote Summary:*\n"]
    for i, item in enumerate(quote["items"], 1):
        line_total = (item["base"] + item["vat"]) * item["qty"]
        lines.append(f"{i}. {item['name'][:45]}")
        lines.append(f"   Qty: {item['qty']} × £{item['base']:.2f} = £{line_total:.2f}")
    lines.append(f"\n💷 *Subtotal:* £{quote['subtotal']:.2f}")
    lines.append(f"💷 *VAT 20%:* £{quote['vat_total']:.2f}")
    lines.append(f"💷 *GRAND TOTAL:* *£{quote['grand_total']:.2f}*")

    kb = [
        [InlineKeyboardButton("✅ Send PDF to my email", callback_data="confirm:yes")],
        [InlineKeyboardButton("❌ Cancel", callback_data="confirm:no")],
    ]
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "confirm:no":
        await query.edit_message_text(
            "❌ Cancelled. Type /start to begin again."
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Generate and send
    await query.edit_message_text("⏳ Generating your quote PDF...")

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
    }

    # Generate PDF
    try:
        pdf_bytes = generate_quote_pdf(quote_for_pdf)
    except Exception as e:
        log.exception("PDF generation failed")
        await query.edit_message_text(
            f"⚠️ Sorry, something went wrong while generating PDF. "
            f"Please call +44 7706 906079.\n\nError: {e}"
        )
        return ConversationHandler.END

    # Send to customer email (via SendGrid)
    email_ok = send_quote_email(
        to_email=data["email"],
        customer_name=data["name"],
        quote_number=quote_number,
        grand_total=quote["grand_total"],
        pdf_bytes=pdf_bytes,
    )

    # Also send PDF directly in Telegram chat (as backup)
    try:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=pdf_bytes,
            filename=f"Spets-Quote-{quote_number}.pdf",
            caption=f"📄 Your quote #{quote_number}",
        )
    except Exception as e:
        log.error(f"Failed to send PDF in chat: {e}")

    # Notify admin
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

    # Final message
    if email_ok:
        msg = (
            f"✅ *Quote #{quote_number} sent!*\n\n"
            f"📧 PDF emailed to: {data['email']}\n"
            f"💷 Total: £{quote['grand_total']:.2f}\n\n"
            "We'll be in touch within 24 hours.\n"
            "Quote is valid for *7 days*."
        )
    else:
        msg = (
            f"⚠️ Quote #{quote_number} generated, but email delivery failed.\n"
            "We have your PDF here in chat. A manager will contact you shortly."
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode="Markdown",
    )

    # TODO Phase 2: POST to KeyCRM via n8n webhook
    # webhook_url = os.getenv("N8N_WEBHOOK_URL")
    # if webhook_url:
    #     requests.post(webhook_url, json={...}, timeout=10)

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ Cancelled. Type /start to begin again.",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *Spets Security Bot — Help*\n\n"
        "/start — Get a CCTV quote\n"
        "/cancel — Cancel current conversation\n"
        "/help — This message\n\n"
        "📞 +44 7706 906079\n"
        "📧 r.brain@spetstech.co.uk",
        parse_mode="Markdown",
    )


# =====================================================================
# MAIN
# =====================================================================
def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN env variable is not set")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
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
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_cmd))

    log.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
