import logging
import threading
import requests
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

# Default Video File ID (from your API)
DEFAULT_VIDEO_ID = "BAACAgQAAxkBAAOqalhoF0J6aDBYMwqetdkzy7p5gMAAAgUfAALKX8LSBkXisCadrWY9BA"

# Welcome message
WELCOME_MESSAGE = (
    "🏅📊 <b>Welcome to Prime Analysis!</b>\n\n"
    "Your ultimate source for real-time sports betting insights. "
    "Get expert predictions, stats and tips to sharpen your betting game. "
    "Join us for updates and discussions as we keep you ahead of the curve 📊"
)

# Start command - shows video with welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get video ID from bot_data or use default
    video_id = context.bot_data.get('video_file_id', DEFAULT_VIDEO_ID)
    
    try:
        # Try to send the video
        await update.message.reply_video(
            video=video_id,
            caption=WELCOME_MESSAGE,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        logger.info("Video sent successfully!")
    except Exception as e:
        logger.error(f"Failed to send video: {e}")
        # If video fails, send just the text
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

# Handle video uploads - update the video ID
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video uploads and update the video ID"""
    
    try:
        message = update.message
        video = message.video
        
        if not video:
            # If not video, show help
            await message.reply_text(
                "📹 Send or forward a <b>video</b> to update the welcome video.",
                parse_mode='HTML'
            )
            return
        
        # Get new File ID
        new_video_id = video.file_id
        
        # Store in bot_data
        context.bot_data['video_file_id'] = new_video_id
        
        # Get video details
        file_name = getattr(video, 'file_name', 'Unknown')
        
        keyboard = [
            [InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss')],
            [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            f"✅ <b>Video Updated!</b>\n\n"
            f"📂 <b>File Name:</b> {file_name}\n"
            f"⏱️ <b>Duration:</b> {video.duration}s\n"
            f"📏 <b>Size:</b> {video.width}x{video.height}\n\n"
            f"Send /start to see the new video in the welcome message.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        logger.info(f"Video updated: {new_video_id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)[:100]}\n\nPlease try again.",
            parse_mode='HTML'
        )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again.\n\n"
            "Send /start to see the menu.",
            parse_mode='HTML'
        )

# Clear webhook
def clear_webhook():
    try:
        url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/deleteWebhook"
        response = requests.get(url)
        logger.info(f"Webhook cleared: {response.json()}")
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
        logger.info(f"Web server running on port {Config.PORT}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Web server error: {e}")

def main():
    clear_webhook()
    
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    logger.info(f"📹 Default Video ID: {DEFAULT_VIDEO_ID}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
