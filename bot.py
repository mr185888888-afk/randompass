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

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👑 Admin", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
        ],
        [
            InlineKeyboardButton("🎬 Get Video ID", callback_data='video_help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send logo/image if available
    if Config.IMAGE_URL:
        try:
            await update.message.reply_photo(
                photo=Config.IMAGE_URL,
                caption=CHANNEL_DESCRIPTION,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        except Exception as e:
            logger.error(f"Failed to send image: {e}")
    
    # Fallback to text message
    await update.message.reply_text(
        CHANNEL_DESCRIPTION,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Video help handler
async def video_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    help_text = (
        "🎬 *How to Get Video File ID*\n\n"
        "*Method 1: Send Video to Bot*\n"
        "1. Send a video to this bot\n"
        "2. Bot will reply with the File ID\n"
        "3. Copy and use the ID anywhere\n\n"
        "*Method 2: Use getUpdates API*\n"
        "1. Send a video to your bot\n"
        "2. Visit this URL:\n"
        f"`https://api.telegram.org/bot{Config.BOT_TOKEN}/getUpdates`\n"
        "3. Find the 'file_id' in the response\n\n"
        "*Method 3: Use getFile API*\n"
        "1. After getting file_id, use:\n"
        f"`https://api.telegram.org/bot{Config.BOT_TOKEN}/getFile?file_id=YOUR_FILE_ID`\n\n"
        "*How to use File ID:*\n"
        "```python\n"
        "await bot.send_video(\n"
        "    chat_id=chat_id,\n"
        "    video='FILE_ID_HERE',\n"
        "    caption='Your caption'\n"
        ")\n"
        "```\n\n"
        "📤 *Send a video now to get its ID!*"
    )
    
    keyboard = [
        [InlineKeyboardButton("👑 Admin", url='https://t.me/PrimeAnalysiss')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Handle video upload - get file ID
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video uploads and return file ID"""
    
    if not update.message.video:
        return
    
    video = update.message.video
    user = update.message.from_user
    
    # Get the file ID directly from the video object
    file_id = video.file_id
    file_unique_id = video.file_unique_id
    
    # Try to get more info using the API
    try:
        file = await context.bot.get_file(file_id)
        file_path = file.file_path
    except Exception as e:
        logger.error(f"Error getting file: {e}")
        file_path = "Could not retrieve"
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_{file_id}')],
        [InlineKeyboardButton("👑 Admin", url='https://t.me/PrimeAnalysiss')],
        [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ *Video Received!*\n\n"
        f"📹 *File ID:* `{file_id}`\n"
        f"🆔 *Unique ID:* `{file_unique_id}`\n"
        f"📁 *File Path:* `{file_path}`\n"
        f"⏱️ *Duration:* {video.duration}s\n"
        f"📏 *Resolution:* {video.width}x{video.height}\n"
        f"👤 *Uploaded by:* {user.first_name}\n\n"
        f"*Click the button below to copy the File ID*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Copy ID handler
async def copy_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    file_id = query.data.replace('copy_', '')
    
    await query.message.reply_text(
        f"📋 *File ID copied to clipboard!*\n\n"
        f"`{file_id}`\n\n"
        f"*How to use this ID:*\n"
        f"```python\n"
        f"await bot.send_video(\n"
        f"    chat_id=chat_id,\n"
        f"    video='{file_id}',\n"
        f"    caption='Your caption'\n"
        f")\n"
        f"```",
        parse_mode='Markdown'
    )

# Start from callback
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'start':
        await start_callback(update, context)
    elif data == 'video_help':
        await video_help(update, context)
    elif data.startswith('copy_'):
        await copy_id(update, context)

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
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Message handlers for video uploads
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
