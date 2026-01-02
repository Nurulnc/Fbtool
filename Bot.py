import logging
import pyotp
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Configuration ---
TOKEN = "7584347544:AAEaxLzbJs8jgpH3z22mppPk5rQFIoN43rU"
LOGO_URL = "https://ibb.co.com/Ng6M5VG5" # Apnar logo-r link ekhane din

# --- Data ---
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

# --- Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['🔑 2FA Generator', '👤 Name Generator'], ['🛒 Buy Mail/VPN', 'ℹ️ About']]
    welcome_text = (
        "✨ **Welcome to Facebook Tools Pro** ✨\n\n"
        "Your all-in-one assistant for fast tools.\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Features:**\n"
        "├ 2FA Code Generation\n"
        "├ Multi-Country Name Generator\n"
        "└ Direct Marketplace Access\n\n"
        "Please choose an option below to start:"
    )
    
    # Send welcome message with a photo for a pro look
    await update.message.reply_photo(
        photo=LOGO_URL,
        caption=welcome_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Shop Button
    if 'Buy Mail/VPN' in text:
        keyboard = [[InlineKeyboardButton("🛍️ Enter Marketplace", url="https://t.me/mailmarketplace_bot")]]
        await update.message.reply_text(
            "💎 **Exclusive Shop Access**\n\n"
            "Get high-quality accounts and VPNs at the best prices.\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    # About Button
    elif 'About' in text:
        about_text = (
            "🤖 **Bot Name:** Facebook Tools Pro\n"
            "🛠 **Version:** 2.0 (Smart Edition)\n"
            "🚀 **Developer:** [Mr.chowdhury]\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Simple. Fast. Reliable."
        )
        await update.message.reply_text(about_text, parse_mode='Markdown')

    # 2FA Logic
    elif '2FA Generator' in text:
        await update.message.reply_text(
            "📟 **2FA Mode Activated**\n"
            "Please send your **Secret Key** below:"
        )
        context.user_data['state'] = 'AWAITING_2FA'
    
    # Name Generator Logic
    elif 'Name Generator' in text:
        first = random.choice(first_names)
        last = random.choice(last_names)
        full_name = f"{first} {last}"
        
        response = (
            "🔰 **New Identity Generated** 🔰\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 **Name:** `{}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👉 _Tap name to copy it instantly._".format(full_name)
        )
        await update.message.reply_text(response, parse_mode='Markdown')

    # 2FA Result Handling
    elif context.user_data.get('state') == 'AWAITING_2FA':
        clean_key = text.replace(" ", "").upper()
        try:
            totp = pyotp.TOTP(clean_key)
            current_code = totp.now()
            await update.message.reply_text(
                "✅ **Verification Code Generated**\n\n"
                "🔑 Code: `{}`\n\n"
                "⚠️ _Expires in 30 seconds_".format(current_code),
                parse_mode='Markdown'
            )
        except Exception:
            await update.message.reply_text("❌ **Invalid Secret Key!** Please check and try again.")
        context.user_data['state'] = None

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running smoothly...")
    application.run_polling()

if __name__ == '__main__':
    main()
