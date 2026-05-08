import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from quote_generator import generate_quote_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8688325915:AAGF9wA942VvdfuHO8h8OyJlGl-s-Kc05Vk"

# Email налаштування
EMAIL_FROM    = "litvinovoleksandr976@gmail.com"
EMAIL_PASSWORD = "ovml wxvb rhpp ytpb"

# Стани розмови
TYPE, PROP, SIZE, BUDGET, NAME, EMAIL_STATE = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("📷 Камери відеоспостереження", callback_data="cctv")],
        [InlineKeyboardButton("🔒 Сигналізація Ajax", callback_data="alarm")],
        [InlineKeyboardButton("🛡️ Обидві системи", callback_data="both")],
        [InlineKeyboardButton("🤔 Ще не визначився", callback_data="unsure")],
    ]
    await update.message.reply_text(
        "👋 Вітаємо у *Spets Security*!\n\n"
        "Я допоможу вам отримати безкоштовну квотацію на систему безпеки.\n\n"
        "*Питання 1 з 5:*\nЯка система безпеки вам потрібна?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return TYPE

async def get_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["type"] = query.data
    keyboard = [
        [InlineKeyboardButton("🏠 Будинок / Квартира", callback_data="house")],
        [InlineKeyboardButton("🏢 Офіс / Бізнес", callback_data="office")],
        [InlineKeyboardButton("🏪 Магазин / Торгівля", callback_data="shop")],
        [InlineKeyboardButton("🏭 Склад / Майданчик", callback_data="warehouse")],
    ]
    await query.edit_message_text(
        "*Питання 2 з 5:*\nЯкий тип об'єкта?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return PROP

async def get_prop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["prop"] = query.data
    keyboard = [
        [InlineKeyboardButton("1️⃣ 1–4 камери / малий об'єкт", callback_data="small")],
        [InlineKeyboardButton("4️⃣ 4–8 камер / середній", callback_data="medium")],
        [InlineKeyboardButton("8️⃣ 8+ камер / великий", callback_data="large")],
        [InlineKeyboardButton("❓ Не впевнений", callback_data="unsure")],
    ]
    await query.edit_message_text(
        "*Питання 3 з 5:*\nСкільки камер / зон приблизно потрібно?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return SIZE

async def get_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["size"] = query.data
    keyboard = [
        [InlineKeyboardButton("💚 До £1,000", callback_data="low")],
        [InlineKeyboardButton("💛 £1,000 – £1,500", callback_data="mid")],
        [InlineKeyboardButton("💎 £1,500+", callback_data="high")],
        [InlineKeyboardButton("🔓 Гнучкий / відкритий", callback_data="open")],
    ]
    await query.edit_message_text(
        "*Питання 4 з 5:*\nЯкий приблизний бюджет?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return BUDGET

async def get_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["budget"] = query.data
    await query.edit_message_text(
        "*Питання 5 з 5:*\nВведіть ваше ім'я для квотації:",
        parse_mode="Markdown"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    context.user_data["name"] = name
    await update.message.reply_text(
        f"✅ Дякуємо, *{name}*!\n\n"
        "📧 Бажаєте отримати квотацію також на *email*?\n\n"
        "Введіть вашу email адресу або натисніть /skip щоб пропустити:",
        parse_mode="Markdown"
    )
    return EMAIL_STATE

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Пропустити email
    if text == "/skip":
        context.user_data["email"] = None
    else:
        context.user_data["email"] = text

    await send_quote(update, context)
    return ConversationHandler.END

async def send_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name  = context.user_data.get("name", "Клієнт")
    email = context.user_data.get("email")

    await update.message.reply_text("⏳ Формуємо вашу квотацію...\nЦе займе декілька секунд.")

    try:
        pdf_path = generate_quote_pdf(context.user_data)

        # Надсилаємо PDF в Telegram
        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename=f"Spets_Security_Quotation_{name}.pdf",
                caption=(
                    f"✅ *Квотація готова, {name}!*\n\n"
                    "📋 Ваша персональна пропозиція від Spets Security.\n\n"
                    "📞 Для замовлення або питань:\n"
                    "+447706906079\n"
                    "r.brain@spetstech.co.uk"
                ),
                parse_mode="Markdown"
            )

        # Надсилаємо PDF на email якщо вказано
        if email:
            await update.message.reply_text(f"📧 Надсилаємо квотацію на *{email}*...", parse_mode="Markdown")
            success = send_email(email, name, pdf_path)
            if success:
                await update.message.reply_text(f"✅ Квотацію надіслано на *{email}*!", parse_mode="Markdown")
            else:
                await update.message.reply_text("⚠️ Не вдалося надіслати на email. Перевірте адресу.")

        os.remove(pdf_path)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            f"✅ Дякуємо, {name}!\n\n"
            "Наш менеджер зв'яжеться з вами найближчим часом.\n\n"
            "📞 +447706906079\n"
            "✉️ r.brain@spetstech.co.uk"
        )

def send_email(to_email: str, client_name: str, pdf_path: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_FROM
        msg["To"]      = to_email
        msg["Subject"] = f"Spets Security — Квотація для {client_name}"

        body = f"""Доброго дня, {client_name}!

Дякуємо за звернення до Spets Security.

У додатку ви знайдете персональну квотацію на систему безпеки для вашого об'єкта.

Якщо у вас є питання або ви готові замовити — зв'яжіться з нами:
📞 +447706906079
✉️ r.brain@spetstech.co.uk
🌐 spetstech.co.uk

З повагою,
Команда Spets Security
Always Near"""

        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Додаємо PDF
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename=Spets_Security_Quotation_{client_name}.pdf"
            )
            msg.attach(part)

        # Надсилаємо через Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Email error: {e}")
        return False

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано. Напишіть /start щоб почати знову.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TYPE:        [CallbackQueryHandler(get_type)],
            PROP:        [CallbackQueryHandler(get_prop)],
            SIZE:        [CallbackQueryHandler(get_size)],
            BUDGET:      [CallbackQueryHandler(get_budget)],
            NAME:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            EMAIL_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_email),
                CommandHandler("skip", get_email),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    logger.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
