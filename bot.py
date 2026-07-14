import logging
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
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

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👉 Join Our Channel", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
        ],
        [
            InlineKeyboardButton("📢 Share Bot", callback_data='share'),
            InlineKeyboardButton("❓ Help", callback_data='help')
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data='about')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🏅📊 *Welcome to Prime Analysis!*\n\n"
        "Your ultimate source for real-time sports betting insights. "
        "Get expert predictions, stats and tips to sharpen your betting game. "
        "Join us for updates and discussions as we keep you ahead of the curve 📊\n\n"
        "👇 *Click the button below to join our channel!*"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Help handler
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    
    help_text = (
        "❓ *Help & Commands*\n\n"
        "*How to use:*\n"
        "1. Click 'Join Our Channel' to join\n"
        "2. Click 'View Channel' to preview\n"
        "3. Share with friends!\n\n"
        "*Commands:*\n"
        "/start - Show main menu\n"
        "/help - Show this help\n"
        "/about - About Prime Analysis\n"
        "/channel - Get channel link\n\n"
        "*What you'll get:*\n"
        "📊 Real-time sports betting insights\n"
        "🎯 Expert predictions and tips\n"
        "📈 Stats and analytics\n"
        "💬 Community discussions\n\n"
        "👉 @PrimeAnalysiss"
    )
    
    if query:
        await query.edit_message_text(help_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown')

# About handler
async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    
    about_text = (
        "ℹ️ *About Prime Analysis*\n\n"
        "🏅 *Prime Analysis Premium* is your ultimate source for real-time sports betting insights.\n\n"
        "*What we offer:*\n"
        "• Expert predictions\n"
        "• Real-time stats\n"
        "• Betting tips\n"
        "• Community discussions\n"
        "• Daily updates\n\n"
        "*Join us:* @PrimeAnalysiss\n\n"
        "🔒 Free and open to all sports enthusiasts!"
    )
    
    if query:
        await query.edit_message_text(about_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(about_text, parse_mode='Markdown')

# Channel handler
async def channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👉 Join Now", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 Preview", url='https://t.me/PRIMEANALYS')
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data='main_menu')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    channel_text = (
        "📊 *Prime Analysis Premium*\n\n"
        "🔗 *Channel Link:* @PrimeAnalysiss\n\n"
        "Don't miss out on expert sports betting insights!\n"
        "Click the button below to join now 👇"
    )
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(channel_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(channel_text, reply_markup=reply_markup, parse_mode='Markdown')

# Share handler
async def share_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    share_text = (
        "📢 *Share Prime Analysis*\n\n"
        "Help others discover the best sports betting insights!\n\n"
        "*Bot Link:*\n"
        "`https://t.me/PRIMEANALYS_BOT`\n\n"
        "*Channel Link:*\n"
        "`https://t.me/PrimeAnalysiss`\n\n"
        "Share these links with your friends! 🚀"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(share_text, reply_markup=reply_markup, parse_mode='Markdown')

# Main menu handler
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'main_menu':
        await main_menu_handler(update, context)
    elif data == 'help':
        await help_handler(update, context)
    elif data == 'about':
        await about_handler(update, context)
    elif data == 'share':
        await share_handler(update, context)

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# Simple web server for Railway
def run_web_server():
    """Run a simple HTTP server for Railway health checks"""
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
        
        server = HTTPServer(('0.0.0.0', Config.PORT), HealthHandler)
        logger.info(f"Web server running on port {Config.PORT}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Web server error: {e}")

def main():
    """Start the bot"""
    # Start web server in background thread for Railway health checks
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Start Telegram bot
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("about", about_handler))
    application.add_handler(CommandHandler("channel", channel_handler))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
