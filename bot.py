import logging
import threading
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from config import Config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global Bot Mode
GLOBAL_BOT_MODE = "REDIRECT"  # Can be "REDIRECT" (video+channel) or "REVERSE" (tools)

# Your Video File ID
VIDEO_FILE_ID = "BAACAgQAAxkBAAOqalhoF0J6aDBYMwqetdkzy7p5gMAAAgUfAALKX8LSBkXisCadrWY9BA"

# Welcome message for REDIRECT mode
REDIRECT_MESSAGE = (
    "🏅📊 <b>Welcome to Prime Analysis!</b>\n\n"
    "Your ultimate source for real-time sports betting insights. "
    "Get expert predictions, stats and tips to sharpen your betting game. "
    "Join us for updates and discussions as we keep you ahead of the curve 📊"
)

# Welcome message for REVERSE mode (normal tools)
REVERSE_MESSAGE = (
    "🔐 <b>Welcome to RandomPass Bot!</b>\n\n"
    "I can help you generate:\n"
    "🔐 Strong passwords with uppercase, numbers & symbols\n"
    "🎲 Random numbers with customizable ranges\n\n"
    "Choose an option below to get started!"
)

# Password generation function
def generate_password(length=12, use_uppercase=True, use_numbers=True, use_symbols=True):
    import random
    import string
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase if use_uppercase else ''
    numbers = string.digits if use_numbers else ''
    symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?' if use_symbols else ''
    all_chars = lowercase + uppercase + numbers + symbols
    if not all_chars:
        all_chars = lowercase
    password_parts = []
    if use_uppercase and uppercase:
        password_parts.append(random.choice(uppercase))
    if use_numbers and numbers:
        password_parts.append(random.choice(numbers))
    if use_symbols and symbols:
        password_parts.append(random.choice(symbols))
    password_parts.append(random.choice(lowercase))
    remaining = length - len(password_parts)
    if remaining > 0:
        password_parts.extend(random.choice(all_chars) for _ in range(remaining))
    random.shuffle(password_parts)
    return ''.join(password_parts)

# --- START COMMAND ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    
    if GLOBAL_BOT_MODE == "REDIRECT":
        # REDIRECT MODE: Show video + channel buttons
        keyboard = [
            [
                InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss'),
                InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await update.message.reply_video(
                video=VIDEO_FILE_ID,
                caption=REDIRECT_MESSAGE,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            logger.info("✅ Redirect mode - Video sent successfully!")
            return
        except Exception as e:
            logger.error(f"Failed to send video: {e}")
            await update.message.reply_text(
                REDIRECT_MESSAGE,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            return
    
    else:
        # REVERSE MODE: Show normal tools
        keyboard = [
            [
                InlineKeyboardButton("🔐 Generate Password", callback_data='password'),
                InlineKeyboardButton("🎲 Generate Number", callback_data='number')
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            REVERSE_MESSAGE,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# --- TEXT HANDLER (Intercepts REDIRECT/REVERSE commands) ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    
    text = (update.message.text or "").strip()
    
    # Intercept SECRET ADMIN commands
    if text == "REDIRECT":
        GLOBAL_BOT_MODE = "REDIRECT"
        await update.message.reply_text(
            "✅ <b>Redirect mode activated!</b>\n\n"
            "The bot will now show the video and channel buttons.",
            parse_mode='HTML'
        )
        return
    
    elif text == "REVERSE":
        GLOBAL_BOT_MODE = "REVERSE"
        await update.message.reply_text(
            "✅ <b>Normal mode activated!</b>\n\n"
            "The bot will now show the password and number generator tools.",
            parse_mode='HTML'
        )
        return
    
    # If in REDIRECT mode, ignore all other text messages
    if GLOBAL_BOT_MODE == "REDIRECT":
        return

# --- PASSWORD MENU ---
async def password_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("8 chars", callback_data='pwd_8'),
            InlineKeyboardButton("12 chars", callback_data='pwd_12'),
            InlineKeyboardButton("16 chars", callback_data='pwd_16')
        ],
        [
            InlineKeyboardButton("20 chars", callback_data='pwd_20'),
            InlineKeyboardButton("24 chars", callback_data='pwd_24'),
            InlineKeyboardButton("32 chars", callback_data='pwd_32')
        ],
        [
            InlineKeyboardButton("⚙️ Custom Settings", callback_data='pwd_settings')
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data='main_menu')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔐 *Password Generator*\n\n"
        "Choose password length:\n"
        "(Default: uppercase, numbers & symbols included)",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# --- GENERATE PASSWORD ---
async def generate_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    query = update.callback_query
    await query.answer()
    
    length = int(query.data.split('_')[1])
    
    settings = context.user_data.get('pwd_settings', {
        'uppercase': True,
        'numbers': True,
        'symbols': True
    })
    
    password = generate_password(
        length=length,
        use_uppercase=settings['uppercase'],
        use_numbers=settings['numbers'],
        use_symbols=settings['symbols']
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy", callback_data=f'copy_{password}')],
        [InlineKeyboardButton("🔄 Generate Another", callback_data='password')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔐 *Your Generated Password*\n\n"
        f"`{password}`\n\n"
        f"Length: {length} characters\n"
        f"Uppercase: {'✅' if settings['uppercase'] else '❌'}\n"
        f"Numbers: {'✅' if settings['numbers'] else '❌'}\n"
        f"Symbols: {'✅' if settings['symbols'] else '❌'}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# --- NUMBER MENU ---
async def number_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("1-6", callback_data='num_1_6'),
            InlineKeyboardButton("1-10", callback_data='num_1_10')
        ],
        [
            InlineKeyboardButton("1-20", callback_data='num_1_20'),
            InlineKeyboardButton("1-100", callback_data='num_1_100')
        ],
        [
            InlineKeyboardButton("1-1000", callback_data='num_1_1000'),
            InlineKeyboardButton("🎯 Custom Range", callback_data='num_custom')
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data='main_menu')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎲 *Number Generator*\n\n"
        "Select a preset range or choose custom:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# --- GENERATE NUMBER ---
async def generate_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    import random
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split('_')
    
    if data_parts[1] == 'custom':
        context.user_data['waiting_for_range'] = True
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data='number')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎯 *Custom Range*\n\n"
            "Please enter your range in the format:\n"
            "`min max` (e.g., `1 50` or `10 100`)",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    min_val = int(data_parts[1])
    max_val = int(data_parts[2])
    
    random_num = random.randint(min_val, max_val)
    
    keyboard = [
        [InlineKeyboardButton("🔄 Generate Another", callback_data='number')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎲 *Random Number*\n\n"
        f"**{random_num}**\n\n"
        f"Range: {min_val} - {max_val}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# --- HANDLE CUSTOM RANGE ---
async def handle_custom_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    if not context.user_data.get('waiting_for_range'):
        return
    
    import random
    try:
        parts = update.message.text.split()
        if len(parts) != 2:
            await update.message.reply_text(
                "❌ Please enter two numbers separated by space.\n"
                "Example: `1 50`",
                parse_mode='Markdown'
            )
            return
        
        min_val = int(parts[0])
        max_val = int(parts[1])
        
        if min_val >= max_val:
            await update.message.reply_text(
                "❌ Minimum must be less than maximum!"
            )
            return
        
        random_num = random.randint(min_val, max_val)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Generate Another", callback_data='number')],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🎲 *Random Number*\n\n"
            f"**{random_num}**\n\n"
            f"Range: {min_val} - {max_val}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        context.user_data['waiting_for_range'] = False
        
    except ValueError:
        await update.message.reply_text(
            "❌ Please enter valid numbers!\n"
            "Example: `1 50`",
            parse_mode='Markdown'
        )

# --- COPY HANDLER ---
async def copy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    query = update.callback_query
    await query.answer()
    
    password = query.data.split('_', 1)[1]
    
    await query.message.reply_text(
        f"📋 *Password copied to clipboard!*\n\n"
        f"`{password}`\n\n"
        f"*Note:* Please select and copy the password manually.",
        parse_mode='Markdown'
    )

# --- PASSWORD SETTINGS ---
async def password_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    query = update.callback_query
    await query.answer()
    
    settings = context.user_data.get('pwd_settings', {
        'uppercase': True,
        'numbers': True,
        'symbols': True
    })
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if settings['uppercase'] else '❌'} Uppercase",
                callback_data='toggle_uppercase'
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if settings['numbers'] else '❌'} Numbers",
                callback_data='toggle_numbers'
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if settings['symbols'] else '❌'} Symbols",
                callback_data='toggle_symbols'
            )
        ],
        [
            InlineKeyboardButton("🔙 Back to Password Menu", callback_data='password')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ *Password Settings*\n\n"
        "Toggle which character types to include:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# --- TOGGLE SETTINGS ---
async def toggle_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    query = update.callback_query
    await query.answer()
    
    setting = query.data.split('_')[1]
    settings = context.user_data.get('pwd_settings', {
        'uppercase': True,
        'numbers': True,
        'symbols': True
    })
    
    settings[setting] = not settings[setting]
    context.user_data['pwd_settings'] = settings
    
    await password_settings(update, context)

# --- HELP ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    query = update.callback_query
    if query:
        await query.answer()
    
    help_text = (
        "🤖 *Help & Commands*\n\n"
        "*Main Features:*\n"
        "🔐 Generate strong passwords with custom settings\n"
        "🎲 Generate random numbers with preset or custom ranges\n\n"
        "*Commands:*\n"
        "/start - Show main menu\n"
        "/help - Show this help message\n"
        "/password - Generate a password\n"
        "/number - Generate a number"
    )
    
    if query:
        await query.edit_message_text(help_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown')

# --- MAIN MENU ---
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    query = update.callback_query
    await query.answer()
    await start_command(update, context)

# --- BUTTON HANDLER ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    
    query = update.callback_query
    data = query.data
    
    if data == 'main_menu':
        await main_menu(update, context)
    elif data == 'password':
        await password_menu(update, context)
    elif data == 'number':
        await number_menu(update, context)
    elif data.startswith('pwd_'):
        await generate_password_handler(update, context)
    elif data.startswith('num_'):
        await generate_number_handler(update, context)
    elif data == 'pwd_settings':
        await password_settings(update, context)
    elif data.startswith('toggle_'):
        await toggle_setting(update, context)
    elif data == 'help':
        await help_command(update, context)
    elif data.startswith('copy_'):
        await copy_handler(update, context)

# --- PASSWORD COMMAND ---
async def password_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    await password_menu(update, context)

# --- NUMBER COMMAND ---
async def number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE
    if GLOBAL_BOT_MODE == "REDIRECT":
        return
    await number_menu(update, context)

# --- ERROR HANDLER ---
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# --- CLEAR WEBHOOK ---
def clear_webhook():
    try:
        url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/deleteWebhook"
        requests.get(url)
        logger.info("Webhook cleared")
    except Exception as e:
        logger.error(f"Error clearing webhook: {e}")

# --- WEB SERVER FOR RAILWAY ---
def run_web_server():
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
        server = HTTPServer(('0.0.0.0', Config.PORT), HealthHandler)
        server.serve_forever()
    except Exception as e:
        logger.error(f"Web server error: {e}")

def main():
    clear_webhook()
    
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("password", password_command))
    application.add_handler(CommandHandler("number", number_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_range))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    logger.info(f"📹 Current Mode: {GLOBAL_BOT_MODE}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
