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

# Video File ID - Replace this with your actual video file ID
VIDEO_FILE_ID = "BAACAgQAAxkBAANoalfph7q54EiiNPyM-8stDa_gEEUAAqQeAALKX8FSv2h-4Ju__Bc9BA"

# Start command - sends video first with File ID
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
        ],
        [
            InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_{VIDEO_FILE_ID}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        f"{CHANNEL_DESCRIPTION}\n\n"
        f"📹 *Video File ID:*\n"
        f"`{VIDEO_FILE_ID}`\n\n"
        f"*Click the button below to copy the File ID*"
    )
    
    try:
        # Send video first with caption
        await update.message.reply_video(
            video=VIDEO_FILE_ID,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send video: {e}")
        # Fallback to text message if video fails
        await update.message.reply_text(
            f"{CHANNEL_DESCRIPTION}\n\n"
            f"📹 *Video File ID:*\n"
            f"`{VIDEO_FILE_ID}`\n\n"
            f"*Click the button below to copy the File ID*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# Handle videos - get file ID
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video and return file ID"""
    
    try:
        message = update.message
        video = message.video
        
        if not video:
            # If not video, show help
            if message.text and message.text.startswith('/start'):
                await start(update, context)
            else:
                await message.reply_text(
                    "📹 Send or forward a *video* to get its File ID.\n\n"
                    "Or send /start to see the video with the File ID.",
                    parse_mode='Markdown'
                )
            return
        
        # Get File ID directly from the video object
        file_id = video.file_id
        
        # Create keyboard with ADmin button
        keyboard = [
            [InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_{file_id}')],
            [InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss')],
            [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Show File ID
        await message.reply_text(
            f"✅ *Video File ID*\n\n"
            f"`{file_id}`\n\n"
            f"📂 *File Name:* {getattr(video, 'file_name', 'Unknown')}\n"
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
            "❌ Error processing video. Please try again.",
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
        f"```python\n"
        f"await bot.send_video(\n"
        f"    chat_id=chat_id,\n"
        f"    video='{file_id}'\n"
        f")\n"
        f"```\n\n"
        f"*Or send this ID to any bot to use the video.*",
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
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again.",
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
    
    # Handle video messages (including forwarded)
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Handle all other messages
    application.add_handler(MessageHandler(filters.ALL, handle_video))
    
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
