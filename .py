import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": " ",
  "private_key_id": " ",
  "private_key": "-----BEGIN PRIVATE KEY-----\END PRIVATE KEY-----\n",
  "client_email": " ",
  "client_id": " ",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": " ",
  "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred)
db = firestore.client()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "8186852843:AAGxpNGS5D3iyYA80Yw3M6DYzOpFDo4bOc4"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data['step'] = 'awaiting_full_name'
    await update.message.reply_text("به Investia خوش آمدید! لطفاً نام کامل خود را وارد کنید:")


async def handle_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text.strip()
    if any(char.isdigit() for char in full_name):
        await update.message.reply_text("نام کامل نباید شامل عدد باشد. لطفاً مجدداً نام کامل خود را وارد کنید:")
        return

    context.user_data['full_name'] = full_name
    context.user_data['step'] = 'awaiting_phone'
    await update.message.reply_text("با تشکر! لطفاً شماره تلفن 📱 خود را وارد کنید:")


async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not (phone.isdigit() and len(phone) == 11):
        await update.message.reply_text("شماره تلفن باید شامل 11 رقم و فقط شامل عدد باشد. لطفاً مجدداً شماره تلفن خود را وارد کنید:")
        return

    context.user_data['phone'] = phone
    context.user_data['step'] = 'awaiting_email'
    await update.message.reply_text("عالی! لطفاً آدرس ایمیل 📧 خود را وارد کنید:")


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    email_pattern = r'^[A-Za-z0-9._%+-]+@(gmail\.com|[A-Za-z0-9.-]+\.[A-Za-z]{2,})$'
    if not re.fullmatch(email_pattern, email):
        await update.message.reply_text("لطفاً یک ایمیل معتبر وارد کنید (مثلاً example@gmail.com):")
        return

    context.user_data['email'] = email
    context.user_data['step'] = 'awaiting_comment'
    await update.message.reply_text("لطفا انتقاد و پیشنهادات خود را درباره ابنوستیا و برنامه ها بنویسید(اختیاری)")


async def handle_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['comment'] = update.message.text.strip()

    user_data = {
        'full_name': context.user_data.get('full_name'),
        'phone': context.user_data.get('phone'),
        'email': context.user_data.get('email'),
        'comment': context.user_data.get('comment'),
        'timestamp': firestore.SERVER_TIMESTAMP
    }

    try:
        db.collection('users').add(user_data)

        keyboard = [
            [InlineKeyboardButton("فارکس", callback_data='forex')],
            [InlineKeyboardButton("رمزارز", callback_data='crypto')],
            [InlineKeyboardButton("فارکس و رمزارز", callback_data='both')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "اطلاعات شما ذخیره شد! لطفاً یک کانال را انتخاب کنید:",
            reply_markup=reply_markup
        )
        context.user_data['step'] = 'awaiting_channel'
    except Exception as e:
        print(f"Firebase Error: {repr(e)}")
        await update.message.reply_text(f"ذخیره اطلاعات شما با خطا مواجه شد: {str(e)}")


async def handle_channel_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channels = {
        "forex": {"name": "فارکس", "link": "https://t.me/+XALdW4pibdNhMjE8"},
        "crypto": {"name": "رمزارز", "link": "https://t.me/+meSaLIkS7FNmODQ8"},
        "both": {
            "name": "فارکس و رمزارز",
            "link": "https://t.me/+XALdW4pibdNhMjE8\nhttps://t.me/+meSaLIkS7FNmODQ8"
        }
    }

    channel_choice = query.data
    if channel_choice in channels:
        await query.edit_message_text(
            text=f"لینک‌های کانال‌های {channels[channel_choice]['name']}:\n{channels[channel_choice]['link']}"
        )
    else:
        await query.edit_message_text("انتخاب نامعتبر. لطفاً مجدداً تلاش کنید.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')
    handlers = {
        'awaiting_full_name': handle_full_name,
        'awaiting_phone': handle_phone,
        'awaiting_email': handle_email,
        'awaiting_comment': handle_comment
    }

    if step in handlers:
        await handlers[step](update, context)
    else:
        await update.message.reply_text("لطفاً از دستور /start برای شروع استفاده کنید.")


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_channel_choice))

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
