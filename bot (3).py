"""
SPETS SECURITY — Telegram bot (3-package quote)

Flow:
  /start → English by default (use /language to switch)
  Name → Phone → Email → Address → Type (Home/Business) →
  Cameras → Archive → GDPR consent → Send 3 PDFs (Budget/Balance/Elite)
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

from pricing import build_all_packages, PACKAGE_META
from quote_generator import generate_quote_pdf
from email_sender import send_admin_notification
from translations import t
from keycrm import push_quote_to_keycrm, get_next_quote_number

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

# States
(LANGUAGE, NAME, PHONE, EMAIL, ADDRESS, OBJECT_TYPE,
 CAMERA_COUNT, ARCHIVE, GDPR) = range(9)


# =====================================================================
# HELPERS
# =====================================================================
def next_quote_number() -> str:
    """
    Last-resort local file counter. Used only if KeyCRM is completely unreachable.
    Starts at 195 (last known KeyCRM order at time of writing).
    """
    try:
        with open(QUOTE_COUNTER_FILE, "r") as f:
            n = int(f.read().strip())
        # Sanity check: if cached number is older than known baseline, reset
        if n < 195:
            n = 195
    except (FileNotFoundError, ValueError):
        n = 195
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
# HANDLERS
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry — English by default, no language picker at start."""
    user = update.effective_user
    context.user_data.clear()
    context.user_data["telegram_user_id"] = user.id
    context.user_data["telegram_username"] = user.username or ""
    context.user_data["first_name"] = user.first_name or ""
    context.user_data["lang"] = "en"  # default

    await update.message.reply_text(
        t("welcome", "en", name=user.first_name or "there"),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def change_language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/language — switch language anytime."""
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


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process language pick from /language command."""
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang:", "")
    context.user_data["lang"] = lang

    await query.edit_message_text(t("language_set", lang))

    # If conversation just started (no name yet) — go to NAME, else stay
    if not context.user_data.get("name"):
        first_name = context.user_data.get("first_name", "")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("welcome", lang, name=first_name),
            parse_mode="Markdown",
        )
        return NAME

    # If mid-flow, just confirm and end (user can /start again)
    return ConversationHandler.END


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
        [[t("object_home", lang)], [t("object_business", lang)]],
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
    text = update.message.text.strip()
    # Normalize: if user typed something containing "home" or matches translation
    if text == t("object_home", lang) or "home" in text.lower() or "дом" in text.lower() or "дім" in text.lower() or "квартир" in text.lower():
        obj_type = "Home"
    else:
        obj_type = "Business"
    context.user_data["object_type"] = obj_type

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
        [InlineKeyboardButton(t("arch_1week", lang), callback_data="arch:1_week")],
        [InlineKeyboardButton(t("arch_2weeks", lang), callback_data="arch:2_weeks")],
        [InlineKeyboardButton(t("arch_1month", lang), callback_data="arch:1_month")],
        [InlineKeyboardButton(t("arch_2months", lang), callback_data="arch:2_months")],
    ]
    await update.message.reply_text(
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

    # Build all 3 packages
    quotes = build_all_packages(
        camera_count=context.user_data["camera_count"],
        archive_choice=archive,
    )
    context.user_data["quotes"] = quotes

    # Comparison summary
    lines = [t("quote_summary_header", lang)]
    lines.append(f"\n{t('package_budget', lang)} — {t('package_budget_desc', lang)}")
    lines.append(f"   *£{quotes['budget']['grand_total']:.2f}*")
    lines.append(f"\n{t('package_balance', lang)} — {t('package_balance_desc', lang)}")
    lines.append(f"   *£{quotes['balance']['grand_total']:.2f}*")
    lines.append(f"\n{t('package_elite', lang)} — {t('package_elite_desc', lang)}")
    lines.append(f"   *£{quotes['elite']['grand_total']:.2f}*")
    lines.append("")
    lines.append(t("gdpr_prompt", lang))

    kb = [
        [InlineKeyboardButton(t("gdpr_agree_btn", lang), callback_data="gdpr:yes")],
        [InlineKeyboardButton(t("gdpr_decline_btn", lang), callback_data="gdpr:no")],
    ]
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return GDPR


async def gdpr_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()

    if query.data == "gdpr:no":
        await query.edit_message_text(t("cancelled", lang))
        context.user_data.clear()
        return ConversationHandler.END

    # User agreed → generate and send
    await query.edit_message_text(t("generating_pdf", lang))

    data = context.user_data
    quotes = data["quotes"]

    customer = {
        "name": data["name"],
        "phone": data["phone"],
        "email": data["email"],
        "address": data.get("address", ""),
        "object_type": data.get("object_type", ""),
    }

    # =================================================================
    # STEP 1: Create 3 orders in KeyCRM (Budget, Balance, Elite) FIRST
    # → get real order_ids. First order's id becomes the quote number.
    # =================================================================
    keycrm_url = None
    quote_number = None
    order_ids = {}
    try:
        keycrm_data = {
            "customer": customer,
            "quote_number": "pending",  # placeholder, real ids come back
            "lang": lang,
            "packages": {
                "budget": {
                    "label": "Budget",
                    "items": quotes["budget"]["items"],
                    "grand_total": quotes["budget"]["grand_total"],
                },
                "balance": {
                    "label": "Balance",
                    "items": quotes["balance"]["items"],
                    "grand_total": quotes["balance"]["grand_total"],
                },
                "elite": {
                    "label": "Elite",
                    "items": quotes["elite"]["items"],
                    "grand_total": quotes["elite"]["grand_total"],
                },
            },
        }
        crm_result = push_quote_to_keycrm(keycrm_data)
        if crm_result.get("ok"):
            keycrm_url = crm_result.get("url")
            order_ids = crm_result.get("order_ids", {})
            # Use first (Budget) order id as the quote number
            quote_number = str(crm_result.get("main_order_id"))
            log.info(f"KeyCRM push OK: order_ids={order_ids}")
        else:
            log.error(f"KeyCRM push failed: {crm_result.get('error')}")
    except Exception as e:
        log.exception(f"KeyCRM push exception: {e}")

    # Fallback: if KeyCRM order creation failed, try to get latest order_id
    # from KeyCRM and use +1, so we still align with KeyCRM numbering.
    # Local file counter is the very last resort.
    if not quote_number:
        try:
            n = get_next_quote_number()
            if n is not None:
                quote_number = str(n)
                log.warning(f"Order creation failed but got next number from KeyCRM: {quote_number}")
        except Exception:
            pass
    if not quote_number:
        quote_number = next_quote_number()
        log.warning(f"Using local file fallback quote number: {quote_number}")

    # =================================================================
    # STEP 2: Generate 3 PDFs with the real quote_number
    # =================================================================
    try:
        pdfs = {}
        for pkg_id in ("budget", "balance", "elite"):
            quote_for_pdf = {
                **quotes[pkg_id],
                "quote_number": quote_number,
                "date": datetime.now(),
                "customer": customer,
                "lang": lang,
            }
            pdfs[pkg_id] = generate_quote_pdf(quote_for_pdf)
    except Exception as e:
        log.exception("PDF generation failed")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("pdf_error", lang),
        )
        context.user_data.clear()
        return ConversationHandler.END

    # =================================================================
    # STEP 3: Email is handled by KeyCRM automation trigger
    # (when order is created in "Новий" status with source "Telegram Bot CCTV",
    #  KeyCRM auto-sends email via sales@spetstech.co.uk).
    # We no longer use Resend.
    # =================================================================
    # If KeyCRM was unreachable, customer still has PDFs in Telegram chat.
    email_will_be_sent = bool(keycrm_url)  # True if order was created in KeyCRM

    # Send all 3 PDFs in Telegram chat
    for pkg_id, pdf_bytes in pdfs.items():
        try:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=pdf_bytes,
                filename=f"Spets-Quote-{quote_number}-{pkg_id.capitalize()}.pdf",
                caption=t(f"pdf_caption_{pkg_id}", lang),
            )
        except Exception as e:
            log.error(f"Failed to send PDF {pkg_id} in chat: {e}")

    # Notify admin
    if ADMIN_CHAT_ID:
        send_admin_notification(
            admin_chat_id=ADMIN_CHAT_ID,
            bot_token=TELEGRAM_TOKEN,
            customer_name=data["name"],
            customer_phone=data["phone"],
            customer_email=data["email"],
            quote_number=quote_number,
            grand_total=quotes["balance"]["grand_total"],
            keycrm_url=keycrm_url,
            all_packages={
                "budget":  quotes["budget"]["grand_total"],
                "balance": quotes["balance"]["grand_total"],
                "elite":   quotes["elite"]["grand_total"],
            },
            object_type=customer.get("object_type", ""),
            camera_count=data.get("camera_count", 0),
        )

    # Final message — always positive (KeyCRM will email or PDFs are in chat)
    msg = t(
        "quote_sent_ok", lang,
        n=quote_number,
        email=data["email"],
        budget=quotes["budget"]["grand_total"],
        balance=quotes["balance"]["grand_total"],
        elite=quotes["elite"]["grand_total"],
    )

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
            LANGUAGE:     [CallbackQueryHandler(set_language, pattern="^lang:")],
            NAME:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            EMAIL:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            ADDRESS:      [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            OBJECT_TYPE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_object_type)],
            CAMERA_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_camera_count)],
            ARCHIVE:      [CallbackQueryHandler(get_archive, pattern="^arch:")],
            GDPR:         [CallbackQueryHandler(gdpr_response, pattern="^gdpr:")],
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
