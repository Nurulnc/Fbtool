import logging
import pyotp
import random
import httpx
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Configuration ---
TOKEN = "7584347544:AAEaxLzbJs8jgpH3z22mppPk5rQFIoN43rU"
LOGO_URL = "https://ibb.co.com/Ng6M5VG5" 
API_BASE = "https://api.mail.tm"

# --- Data ---
first_names = ["Aarav", "Arjun", "Vihaan", "Aditya", "Ishaan", "Bishal", "Ankit", "Suman", "Prabin", "Roshan", "Ahmad", "Mustafa", "Zubair", "Omar", "Idris", "Alisher", "Bekzod", "Rustam", "Temur", "Azamat", "Mohammed", "Yousef", "Zaid", "Hassan", "Ali"]
last_names = ["Sharma", "Verma", "Gupta", "Singh", "Patel", "Adhikari", "Bista", "Thapa", "Gurung", "Poudel", "Khan", "Ahmadi", "Popal", "Stanikzai", "Wardak", "Abduvokhidov", "Karimov", "Yuldashev", "Sultanov", "Rahmonov", "Al-Farsi", "Mansoor", "Al-Sayed", "Haddad", "Bakir"]

# --- Temp Mail API ---
async def create_temp_mail():
    async with httpx.AsyncClient() as client:
        domains = await client.get(f"{API_BASE}/domains")
        domain = domains.json()['hydra:member'][0]['domain']
        user_id = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
        address = f"{user_id}@{domain}"
        password = "password123"
        await client.post(f"{API_BASE}/accounts", json={"address": address, "password": password})
        token_res = await client.post(f"{API_BASE}/token", json={"address": address, "password": password})
        return address, token_res.json()['token']

# --- Manual Inbox Check Function ---
async def check_inbox_logic(token, chat_id, context):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_BASE}/messages", headers={"Authorization": f"Bearer {token}"})
            messages = res.json().get('hydra:member', [])
            
            if not messages:
                return "📭 **Inbox is Empty!**\nNo messages received yet."
            
            for msg in messages[:3]: # Last 3 messages dekhabe
                details = await client.get(f"{API_BASE}/messages/{msg['id']}", headers={"Authorization": f"Bearer {token}"})
                body = details.json().get('text', 'No content')
                msg_text = (
                    "📩 **New Email!**\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📧 **From:** {}\n"
                    "📝 **Subject:** {}\n\n"
                    "**Content:**\n`{}`".format(msg['from']['address'], msg['subject'], body[:1000])
                )
                await context.bot.send_message(chat_id=chat_id, text=msg_text, parse_mode='Markdown')
            return None
        except Exception as e:
            return "❌ Error checking inbox."

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['🔑 2FA Generator', '👤 Name Generator'], ['📧 Temp Mail', '🛒 Buy Mail/VPN'], ['ℹ️ About']]
    await update.message.reply_photo(
        photo=LOGO_URL,
        caption="✨ **Facebook Tools Pro**\nChoose an option below:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if 'Temp Mail' in text:
        await update.message.reply_text("⏳ Generating mailbox...")
        address, token = await create_temp_mail()
        context.user_data['mail_token'] = token # Token save kora hochhe button-er jonno

        keyboard = [[InlineKeyboardButton("📥 Check Inbox", callback_data="manual_check")]]
        msg = (
            "📧 **Your Temp Mail**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Address: `{}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Click the button below to check for new messages.".format(address)
        )
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif '2FA Generator' in text:
        await update.message.reply_text("📟 Send your Secret Key:")
        context.user_data['state'] = 'AWAITING_2FA'

    elif 'Name Generator' in text:
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        await update.message.reply_text(f"👤 Name: `{name}`", parse_mode='Markdown')

    elif context.user_data.get('state') == 'AWAITING_2FA':
        try:
            totp = pyotp.TOTP(text.replace(" ", "").upper())
            await update.message.reply_text(f"✅ Code: `{totp.now()}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Invalid Key")
        context.user_data['state'] = None

# --- Button Callback Handle ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Checking inbox...") # Button click-er feedback

    if query.data == "manual_check":
        token = context.user_data.get('mail_token')
        if not token:
            await query.message.reply_text("❌ No active mail found. Generate a new one.")
            return
        
        result = await check_inbox_logic(token, query.message.chat_id, context)
        if result:
            await query.message.reply_text(result, parse_mode='Markdown')

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback)) # Button handle-er jonno
    
    print("Bot is running with Manual Check Button...")
    application.run_polling()

if __name__ == '__main__':
    main()
