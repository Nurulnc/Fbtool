import logging
import pyotp
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Expanded name list
first_names = [
    "Aarav", "Arjun", "Vihaan", "Aditya", "Ishaan", "Sai", "Aaryan", "Kabir", "Rohan", "Rahul",
    "Bishal", "Ankit", "Suman", "Prabin", "Roshan", "Kiran", "Nabin", "Sagar", "Bibek", "Sandip",
    "Ahmad", "Mustafa", "Zubair", "Omar", "Idris", "Farhad", "Najeeb", "Sami", "Wais", "Zabi",
    "Alisher", "Bekzod", "Rustam", "Temur", "Azamat", "Oybek", "Jasur", "Sardor", "Anvar", "Shokhruth",
    "Mohammed", "Yousef", "Zaid", "Hassan", "Ali", "Ahmed", "Ibrahim", "Khalid", "Faisal", "Tariq"
]

last_names = [
    "Sharma", "Verma", "Gupta", "Singh", "Patel", "Reddy", "Kumar", "Das", "Joshi", "Yadav",
    "Adhikari", "Bista", "Thapa", "Gurung", "Poudel", "Khatri", "Rai", "Magar", "Tamang", "Shrestha",
    "Khan", "Ahmadi", "Popal", "Stanikzai", "Wardak", "Habibi", "Niazi", "Zazi", "Noori", "Barakzai",
    "Abduvokhidov", "Karimov", "Yuldashev", "Sultanov", "Rahmonov", "Usmanov", "Mirzoev", "Tulyaganov", "Tursunov", "Kasimov",
    "Al-Farsi", "Mansoor", "Al-Sayed", "Haddad", "Bakir", "Al-Rashid", "Malik", "Hariri", "Najjar", "Abadi"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['2FA Generator', 'Name Generator']]
    await update.message.reply_text(
        "👋 Welcome! Choice an option below:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == '2FA Generator':
        await update.message.reply_text("Please paste your 2FA Secret Key:")
        context.user_data['state'] = 'AWAITING_2FA'
    
    elif text == 'Name Generator':
        first = random.choice(first_names)
        last = random.choice(last_names)
        full_name = f"{first} {last}"
        
        # Click to copy system (Markdown code block style)
        response = f"👤 **Generated Name:**\n`{full_name}`\n\n_(Click the name to copy)_"
        await update.message.reply_text(response, parse_mode='Markdown')

    elif context.user_data.get('state') == 'AWAITING_2FA':
        clean_key = text.replace(" ", "").upper()
        try:
            totp = pyotp.TOTP(clean_key)
            current_code = totp.now()
            # 2FA code o click to copy kore deya holo
            await update.message.reply_text(f"Your 2FA Code: `{current_code}`\n\n_(Click the code to copy)_", parse_mode='Markdown')
        except Exception:
            await update.message.reply_text("❌ Error: Invalid Secret Key!")
        context.user_data['state'] = None

def main():
    TOKEN = "7584347544:AAEaxLzbJs8jgpH3z22mppPk5rQFIoN43rU"
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
