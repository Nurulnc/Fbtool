import logging
import pyotp
import random
import httpx  # Temp Mail API call er jonno lagbe (pip install httpx)
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Configuration ---
TOKEN = "7584347544:AAEaxLzbJs8jgpH3z22mppPk5rQFIoN43rU"
LOGO_URL = "https://ibb.co.com/Ng6M5VG5" # Apnar Logo Link
API_BASE = "https://api.mail.tm"

# --- Name Data ---
first_names = ["Aarav", "Arjun", "Vihaan", "Aditya", "Ishaan", "Bishal", "Ankit", "Suman", "Prabin", "Roshan", "Ahmad", "Mustafa", "Zubair", "Omar", "Idris", "Alisher", "Bekzod", "Rustam", "Temur", "Azamat", "Mohammed", "Yousef", "Zaid", "Hassan", "Ali"]
last_names = ["Sharma", "Verma", "Gupta", "Singh", "Patel", "Adhikari", "Bista", "Thapa", "Gurung", "Poudel", "Khan", "Ahmadi", "Popal", "Stanikzai", "Wardak", "Abduvokhidov", "Karimov", "Yuldashev", "Sultanov", "Rahmonov", "Al-Farsi", "Mansoor", "Al-Sayed", "Haddad", "Bakir"]

# --- Temp Mail Logic ---
async def create_temp_mail():
    async with httpx.AsyncClient() as client:
        # Get Domain
        domains = await client.get(f"{API_BASE}/domains")
        domain = domains.json()['hydra:member'][0]['domain']
        
        # Create Credentials
        user_id = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
        address = f"{user_id}@{domain}"
        password = "password123"
        
        # Create Account
        await client.post(f"{API_BASE}/accounts", json={"address": address, "password": password})
        
        # Get Token
        token_res = await client.post(f"{API_BASE}/token", json={"address": address, "password": password})
        token = token_res.json()['token']
        
        return address, token

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ['🔑 2FA Generator', '👤 Name Generator'],
        ['📧 Temp Mail', '🛒 Buy Mail/VPN'],
        ['ℹ️ About']
    ]
    welcome_text = (
        "✨ **Welcome to Facebook Tools Pro** ✨\n\n"
        "Your premium assistant for automation tools.\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Temp Mail Integrated!**\n"
        "Now generate & check inbox directly.\n\n"
        "Please choose an option below:"
    )
    await update.message.reply_photo(
        photo=LOGO_URL,
        caption=welcome_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # 📧 Temp Mail Logic
    if 'Temp Mail' in text:
        await update.message.reply_text("⏳ Generating your private mailbox...")
        try:
            address, token = await create_temp_mail()
            context.user_data['mail_address'] = address
            context.user_data['mail_token'] = token
            
            keyboard = [[InlineKeyboardButton("📥 Check Inbox", callback_data="check_inbox")]]
            msg = (
                "📧 **Your Temporary Email**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "Address: `{}`\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👉 _Copy the address and use it anywhere. Then click the button below to see messages._".format(address)
            )
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text("❌ Failed to generate mail. Try again.")

    # 👤 Name Generator
    elif 'Name Generator' in text:
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        await update.message.reply_text(f"🔰 **New Identity**\n━━━━━━━━━━━━\nName: `{full_name}`\n━━━━━━━━━━━━\n_Tap to copy_", parse_mode='Markdown')

    # 🛒 Shop Button
    elif 'Buy Mail/VPN' in text:
        keyboard = [[InlineKeyboardButton("🛍️ Open Marketplace", url="https://t.me/mailmarketplace_bot")]]
        await update.message.reply_text("🚀 **Mail Marketplace Bot**\nClick below to buy accounts:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # 🔑 2FA Generator
    elif '2FA Generator' in text:
        await update.message.reply_text("📟 **2FA Mode**\nPlease send your Secret Key:")
        context.user_data['state'] = 'AWAITING_2FA'

    # ℹ️ About
    elif 'About' in text:
        await update.message.reply_text("🤖 **Facebook Tools Pro**\nVersion: 3.0 (Cloud)\nStatus: Online ✅", parse_mode='Markdown')

    # 2FA Result Handling
    elif context.user_data.get('state') == 'AWAITING_2FA':
        try:
            totp = pyotp.TOTP(text.replace(" ", "").upper())
            await update.message.reply_text(f"✅ **Code:** `{totp.now()}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Invalid Key!")
        context.user_data['state'] = None

# --- Callback for Inbox ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_inbox":
        token = context.user_data.get('mail_token')
        if not token:
            await query.edit_message_text("❌ No active session found. Please generate a new mail.")
            return
            
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{API_BASE}/messages", headers={"Authorization": f"Bearer {token}"})
            messages = res.json()['hydra:member']
            
            if not messages:
                await query.message.reply_text("📭 **Inbox is Empty!**\n(Auto-refreshing is not active, click Check Inbox again)")
            else:
                for msg in messages[:3]: # Last 3 messages dekhabe
                    details = await client.get(f"{API_BASE}/messages/{msg['id']}", headers={"Authorization": f"Bearer {token}"})
                    body = details.json().get('text', 'No content')
                    await query.message.reply_text(f"📩 **From:** {msg['from']['address']}\n📝 **Subject:** {msg['subject']}\n\n**Content:**\n`{body[:500]}`", parse_mode='Markdown')

def main():
    application = Application.builder().token(TOKEN).build()
    from telegram.ext import CallbackQueryHandler
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot is Live with Temp Mail!")
    application.run_polling()

if __name__ == '__main__':
    main()
