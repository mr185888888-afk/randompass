import logging
import threading
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

from config import Config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# YOUR VIDEO FILE ID
VIDEO_FILE_ID = "BAACAgQAAxkBAAOqalhoF0J6aDBYMwqetdkzy7p5gMAAAgUfAALKX8LSBkXisCadrWY9BA"

# Welcome message - NO FILE ID TEXT
WELCOME_MESSAGE = (
    "🏅📊 <b>Welcome to Prime Analysis!</b>\n\n"
    "Your ultimate source for real-time sports betting insights. "
    "Get expert predictions, stats and tips to sharpen your betting game. "
    "Join us for updates and discussions as we keep you ahead of the curve 📊"
)

# Start command - shows VIDEO with welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Send the VIDEO (not the ID) with welcome message
        await update.message.reply_video(
            video=VIDEO_FILE_ID,
            caption=WELCOME_MESSAGE,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        logger.info("✅ Video sent successfully!")
    except Exception as e:
        logger.error(f"Failed to send video: {e}")
        # If video fails, send text only
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# Clear webhook
def clear_webhook():
    try:
        url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/deleteWebhook"
        requests.get(url)
        logger.info("Webhook cleared")
    except Exception as e:
        logger.error(f"Error clearing webhook: {e}")

# Web server for Railway
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
    
    application.add_handler(CommandHandler("start", start))
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
