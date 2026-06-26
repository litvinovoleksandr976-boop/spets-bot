"""
SPETS SECURITY — Telegram bot (v3, full menu)

Flow:
  /start → Name → Phone → Email → Address     (LIKE BEFORE — director approved)
  → Service: [CCTV] [Alarm System] [Contact Manager]    (NEW)
  → CCTV → Type: [Residential] [Business]               (NEW)
  → Business → [Cafe/Restaurant] [Office/Warehouse] [Construction]  (NEW)
  → Cameras: 4×4 inline buttons (1-16) + [17+ — Manager]            (NEW)
  → Archive duration → GDPR → 3 PDFs + KeyCRM
  → After quote: [Message Manager] [Back to Main Menu]              (NEW)
"""
import os
import re
import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

from pricing import build_all_packages, PACKAGE_META
from quote_generator import generate_quote_pdf
from email_sender import send_admin_notification, send_3_packages_email
from translations import t
from keycrm import push_quote_to_keycrm, get_next_quote_number, create_inquiry

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

# Support bot (connected to KeyCRM as a chat channel).
# Customers tap "Message Manager" → open this bot → write → appears in KeyCRM chat.
SUPPORT_BOT_URL = os.getenv("SUPPORT_BOT_URL", "https://t.me/SpetsSupport_bot")

# States
(LANGUAGE, NAME, PHONE, EMAIL, ADDRESS,
 SERVICE, OBJECT_TYPE, BUSINESS_TYPE,
 CAMERA_COUNT, ARCHIVE, GDPR,
 BIG_PROJECT_CONFIRM, MESSAGE_MANAGER, AFTER_QUOTE) = range(14)


# =====================================================================
# HELPERS
# =====================================================================
def next_quote_number() -> str:
    """Last-resort local counter. Starts at 195."""
    try:
        with open(QUOTE_COUNTER_FILE, "r") as f:
            n = int(f.read().strip())
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
# /start
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    context.user_data.clear()
    context.user_data["telegram_user_id"] = user.id
    context.user_data["telegram_chat_id"] = update.effective_chat.id
    context.user_data["telegram_username"] = user.username or ""
    context.user_data["first_name"] = user.first_name or ""
    context.user_data["lang"] = "en"

    await update.message.reply_text(
        t("welcome", "en", name=user.first_name or "there"),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


# =====================================================================
# /language
# =====================================================================
async def change_language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang:", "")
    context.user_data["lang"] = lang
    await query.edit_message_text(t("language_set", lang))

    if not context.user_data.get("name"):
        first_name = context.user_data.get("first_name", "")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("welcome", lang, name=first_name),
            parse_mode="Markdown",
        )
        return NAME

    return ConversationHandler.END


# =====================================================================
# NAME → PHONE → EMAIL → ADDRESS  (DIRECTOR APPROVED — DO NOT CHANGE)
# =====================================================================
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
    # → Show service menu (NEW)
    return await show_service_menu(update, context)


# =====================================================================
# SERVICE MENU (NEW)
# =====================================================================
async def show_service_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    kb = [
        [InlineKeyboardButton(t("svc_cctv", lang), callback_data="svc:cctv")],
        [InlineKeyboardButton(t("svc_alarm", lang), callback_data="svc:alarm")],
        [InlineKeyboardButton(t("svc_contact", lang), callback_data="svc:contact")],
    ]
    text = t("ask_service", lang)
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown",
                                        reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.callback_query.message.reply_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb)
        )
    return SERVICE


async def handle_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()
    choice = query.data.replace("svc:", "")
    context.user_data["service"] = choice

    if choice == "cctv":
        # → ask object type (Residential / Business)
        kb = [
            [InlineKeyboardButton(t("obj_residential", lang), callback_data="obj:residential")],
            [InlineKeyboardButton(t("obj_business", lang), callback_data="obj:business")],
        ]
        await query.edit_message_text(
            t("ask_object_type", lang),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb),
        )
        return OBJECT_TYPE

    elif choice == "alarm":
        # Alarm — placeholder, create inquiry in KeyCRM
        await query.edit_message_text(t("alarm_coming_soon", lang), parse_mode="Markdown")
        await _create_inquiry_in_keycrm(update, context, inquiry_type="Alarm System Inquiry")
        await _show_after_quote_menu(update, context)
        return AFTER_QUOTE

    else:  # contact
        kb = [[InlineKeyboardButton(t("btn_msg_manager", lang), url=SUPPORT_BOT_URL)]]
        await query.edit_message_text(
            t("contact_prompt", lang),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb),
        )
        return ConversationHandler.END


# =====================================================================
# OBJECT TYPE (Residential / Business)
# =====================================================================
async def handle_object_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()
    obj = query.data.replace("obj:", "")
    context.user_data["object_type"] = obj.capitalize()

    if obj == "residential":
        # Skip business subtype — go straight to cameras
        return await ask_cameras(update, context)

    # Business → ask subtype
    kb = [
        [InlineKeyboardButton(t("biz_cafe", lang), callback_data="biz:cafe")],
        [InlineKeyboardButton(t("biz_office", lang), callback_data="biz:office")],
        [InlineKeyboardButton(t("biz_construction", lang), callback_data="biz:construction")],
    ]
    await query.edit_message_text(
        t("ask_business_type", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return BUSINESS_TYPE


async def handle_business_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()
    biz = query.data.replace("biz:", "")
    biz_label = {
        "cafe": "Cafe / Restaurant / Beauty Salon",
        "office": "Office / Warehouse / School",
        "construction": "Construction Site",
    }[biz]
    context.user_data["business_type"] = biz_label
    context.user_data["object_type"] = f"Business: {biz_label}"

    return await ask_cameras(update, context)


# =====================================================================
# CAMERA COUNT (inline 4×4 grid + 17+)
# =====================================================================
async def ask_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    # Build 4×4 grid of buttons 1-16 + 17+ row
    grid = []
    for row_start in range(1, 17, 4):
        row = [
            InlineKeyboardButton(str(n), callback_data=f"cam:{n}")
            for n in range(row_start, row_start + 4)
        ]
        grid.append(row)
    grid.append([InlineKeyboardButton(t("cam_17plus", lang), callback_data="cam:17plus")])

    text = t("ask_camera_count_buttons", lang)
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(grid)
        )
    else:
        await update.message.reply_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(grid)
        )
    return CAMERA_COUNT


async def handle_camera_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()
    choice = query.data.replace("cam:", "")

    if choice == "17plus":
        # Big project — create inquiry in KeyCRM, no quote
        context.user_data["camera_count"] = "17+"
        await query.edit_message_text(t("big_project_msg", lang), parse_mode="Markdown")
        await _create_inquiry_in_keycrm(update, context, inquiry_type="Big Project (17+ cameras)")
        await _show_after_quote_menu(update, context)
        return AFTER_QUOTE

    n = int(choice)
    context.user_data["camera_count"] = n

    # → archive
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


# =====================================================================
# ARCHIVE → quotes preview + GDPR
# =====================================================================
async def get_archive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()
    archive = query.data.replace("arch:", "")
    context.user_data["archive"] = archive

    quotes = build_all_packages(
        camera_count=context.user_data["camera_count"],
        archive_choice=archive,
    )
    context.user_data["quotes"] = quotes

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


# =====================================================================
# GDPR → generate PDFs + KeyCRM + email
# =====================================================================
async def gdpr_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()

    if query.data == "gdpr:no":
        await query.edit_message_text(t("cancelled", lang))
        context.user_data.clear()
        return ConversationHandler.END

    await query.edit_message_text(t("generating_pdf", lang))

    data = context.user_data
    quotes = data["quotes"]

    customer = {
        "name": data["name"],
        "phone": data["phone"],
        "email": data["email"],
        "address": data.get("address", ""),
        "object_type": data.get("object_type", ""),
        "telegram_chat_id": data.get("telegram_chat_id", ""),
        "telegram_username": data.get("telegram_username", ""),
    }

    # STEP 1: Create 3 orders in KeyCRM
    keycrm_url = None
    quote_number = None
    try:
        keycrm_data = {
            "customer": customer,
            "quote_number": "pending",
            "lang": lang,
            "packages": {
                "budget":  {"label": "Budget",  "items": quotes["budget"]["items"],
                            "grand_total": quotes["budget"]["grand_total"]},
                "balance": {"label": "Balance", "items": quotes["balance"]["items"],
                            "grand_total": quotes["balance"]["grand_total"]},
                "elite":   {"label": "Elite",   "items": quotes["elite"]["items"],
                            "grand_total": quotes["elite"]["grand_total"]},
            },
        }
        crm_result = push_quote_to_keycrm(keycrm_data)
        if crm_result.get("ok"):
            keycrm_url = crm_result.get("url")
            quote_number = str(crm_result.get("main_order_id"))
            log.info(f"KeyCRM push OK: {crm_result.get('order_ids')}")
        else:
            log.error(f"KeyCRM push failed: {crm_result.get('error')}")
    except Exception as e:
        log.exception(f"KeyCRM push exception: {e}")

    # Fallback
    if not quote_number:
        try:
            n = get_next_quote_number()
            if n is not None:
                quote_number = str(n)
        except Exception:
            pass
    if not quote_number:
        quote_number = next_quote_number()

    # STEP 2: Generate 3 PDFs
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
    except Exception:
        log.exception("PDF generation failed")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("pdf_error", lang),
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Send PDFs in Telegram chat
    for pkg_id, pdf_bytes in pdfs.items():
        try:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=pdf_bytes,
                filename=f"Spets-Quote-{quote_number}-{pkg_id.capitalize()}.pdf",
                caption=t(f"pdf_caption_{pkg_id}", lang),
            )
        except Exception as e:
            log.error(f"Failed to send PDF {pkg_id}: {e}")

    # Email the 3 quotes to the customer
    email_sent = False
    customer_email = data.get("email", "")
    if customer_email:
        try:
            email_sent = send_3_packages_email(
                to_email=customer_email,
                customer_name=data["name"],
                quote_number=quote_number,
                quotes=quotes,
                pdfs=pdfs,
                lang=lang,
            )
            if email_sent:
                log.info(f"Quote email sent to {customer_email} (#{quote_number})")
            else:
                log.error(f"Quote email NOT sent to {customer_email} (#{quote_number})")
        except Exception as e:
            log.exception(f"Quote email exception for {customer_email}: {e}")

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

    # Success message
    if email_sent:
        msg = t(
            "quote_sent_ok", lang,
            n=quote_number,
            email=data["email"],
            budget=quotes["budget"]["grand_total"],
            balance=quotes["balance"]["grand_total"],
            elite=quotes["elite"]["grand_total"],
        )
    else:
        # Email failed or no email — don't promise an email that won't arrive
        msg = t(
            "quote_sent_ok", lang,
            n=quote_number,
            email=data.get("email", ""),
            budget=quotes["budget"]["grand_total"],
            balance=quotes["balance"]["grand_total"],
            elite=quotes["elite"]["grand_total"],
        )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode="Markdown",
    )

    # Show after-quote menu
    await _show_after_quote_menu(update, context)
    return AFTER_QUOTE


# =====================================================================
# AFTER QUOTE menu
# =====================================================================
async def _show_after_quote_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    kb = [
        [InlineKeyboardButton(t("btn_msg_manager", lang), url=SUPPORT_BOT_URL)],
        [InlineKeyboardButton(t("btn_back_main", lang), callback_data="after:main")],
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=t("after_quote_prompt", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )


async def handle_after_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    query = update.callback_query
    await query.answer()
    choice = query.data.replace("after:", "")

    # "msg" no longer used (button is now a direct URL to support bot)
    # back to main → service menu (keep contacts)
    return await show_service_menu(update, context)


# =====================================================================
# MESSAGE MANAGER — collect free-form message
# =====================================================================
async def get_manager_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    msg_text = update.message.text.strip()
    context.user_data["customer_message"] = msg_text

    # Notify admin in Telegram
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    f"💬 *Message from {context.user_data.get('name', '?')}*\n\n"
                    f"📞 {context.user_data.get('phone', '?')}\n"
                    f"📧 {context.user_data.get('email', '?')}\n\n"
                    f"_Message:_\n{msg_text}"
                ),
                parse_mode="Markdown",
            )
        except Exception as e:
            log.error(f"Failed to notify admin about message: {e}")

    # Save in KeyCRM as inquiry
    await _create_inquiry_in_keycrm(update, context, inquiry_type=f"Customer message: {msg_text[:60]}")

    await update.message.reply_text(t("message_sent", lang), parse_mode="Markdown")
    await _show_after_quote_menu(update, context)
    return AFTER_QUOTE


# =====================================================================
# CREATE INQUIRY in KeyCRM (used for alarm / big project / messages)
# =====================================================================
async def _create_inquiry_in_keycrm(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    inquiry_type: str):
    """Push a non-quote inquiry to KeyCRM."""
    data = context.user_data
    customer = {
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "email": data.get("email", ""),
        "address": data.get("address", ""),
        "object_type": data.get("object_type", inquiry_type),
        "telegram_chat_id": data.get("telegram_chat_id", ""),
        "telegram_username": data.get("telegram_username", ""),
    }
    try:
        result = create_inquiry(
            customer=customer,
            inquiry_type=inquiry_type,
            details=data.get("customer_message", "") or inquiry_type,
            extra_info={
                "service": data.get("service", ""),
                "camera_count": data.get("camera_count", ""),
                "business_type": data.get("business_type", ""),
            },
        )
        if result.get("ok"):
            log.info(f"Inquiry created in KeyCRM: order_id={result.get('order_id')}")
    except Exception as e:
        log.exception(f"Failed to create KeyCRM inquiry: {e}")


# =====================================================================
# CANCEL & HELP
# =====================================================================
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
            LANGUAGE:        [CallbackQueryHandler(set_language, pattern="^lang:")],
            NAME:            [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE:           [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            EMAIL:           [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            ADDRESS:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            SERVICE:         [CallbackQueryHandler(handle_service, pattern="^svc:")],
            OBJECT_TYPE:     [CallbackQueryHandler(handle_object_type, pattern="^obj:")],
            BUSINESS_TYPE:   [CallbackQueryHandler(handle_business_type, pattern="^biz:")],
            CAMERA_COUNT:    [CallbackQueryHandler(handle_camera_count, pattern="^cam:")],
            ARCHIVE:         [CallbackQueryHandler(get_archive, pattern="^arch:")],
            GDPR:            [CallbackQueryHandler(gdpr_response, pattern="^gdpr:")],
            AFTER_QUOTE:     [CallbackQueryHandler(handle_after_quote, pattern="^after:")],
            MESSAGE_MANAGER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_manager_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
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
