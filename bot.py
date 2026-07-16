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

# Channel description
CHANNEL_DESCRIPTION = (
    "🏅📊 *Welcome to Prime Analysis!*\n\n"
    "Your ultimate source for real-time sports betting insights. "
    "Get expert predictions, stats and tips to sharpen your betting game. "
    "Join us for updates and discussions as we keep you ahead of the curve 📊"
)

# Start command - shows welcome message with buttons (no video)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{CHANNEL_DESCRIPTION}\n\n"
        "📹 *Send or forward a video* to this bot to get its File ID.\n\n"
        "The bot will save the File ID and show it to you.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Handle videos - get file ID and show it
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video and return file ID"""
    
    try:
        message = update.message
        
        # Check for video
        video = None
        if message.video:
            video = message.video
        elif hasattr(message, 'video') and message.video:
            video = message.video
        
        if not video:
            # If not video, show menu
            if message.text and message.text.startswith('/start'):
                await start(update, context)
            else:
                await message.reply_text(
                    "📹 Send or forward a *video* to get its File ID.\n\n"
                    "Or send /start to see the menu.",
                    parse_mode='Markdown'
                )
            return
        
        # Get File ID
        file_id = video.file_id
        file_name = getattr(video, 'file_name', 'Unknown')
        
        # Store in bot_data
        context.bot_data['video_file_id'] = file_id
        
        # Create keyboard with buttons
        keyboard = [
            [InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_{file_id}')],
            [InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss')],
            [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send the File ID
        await message.reply_text(
            f"✅ *Video Received!*\n\n"
            f"📹 *File ID:*\n"
            f"`{file_id}`\n\n"
            f"📂 *File Name:* {file_name}\n"
            f"⏱️ *Duration:* {video.duration}s\n"
            f"📏 *Size:* {video.width}x{video.height}\n"
            f"📦 *File Size:* {video.file_size:,} bytes\n\n"
            f"*Click the button below to copy the File ID*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)[:100]}\n\nPlease try again.",
            parse_mode='Markdown'
        )

# Copy ID handler
async def copy_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    file_id = query.data.replace('copy_', '')
    
    keyboard = [
        [InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss')],
        [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"📋 *File ID copied to clipboard!*\n\n"
        f"`{file_id}`\n\n"
        f"*Use this ID to send the video:*\n"
        f"```\n"
        f"https://api.telegram.org/bot{Config.BOT_TOKEN}/getFile?file_id={file_id}\n"
        f"```\n\n"
        f"*Or use in Python:*\n"
        f"```python\n"
        f"await bot.send_video(chat_id=chat_id, video='{file_id}')\n"
        f"```",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data.startswith('copy_'):
        await copy_id(update, context)

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again.\n\n"
            "Send /start to see the menu.",
            parse_mode='Markdown'
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
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.ALL, handle_video))
    
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
