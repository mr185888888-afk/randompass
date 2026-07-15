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
            InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
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

# Handle video upload - get file ID
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video uploads and return file ID"""
    
    try:
        # Check if it's a video
        if not update.message.video:
            await update.message.reply_text(
                "❌ Please send a *video file* (MP4, AVI, MOV, etc.)\n\n"
                "Send a video to get its File ID.",
                parse_mode='Markdown'
            )
            return
        
        video = update.message.video
        user = update.message.from_user
        
        # Get the file ID directly from the video object
        file_id = video.file_id
        file_unique_id = video.file_unique_id
        
        # Get file info using the API
        try:
            file = await context.bot.get_file(file_id)
            file_path = file.file_path
        except Exception as e:
            logger.error(f"Error getting file: {e}")
            file_path = "Could not retrieve"
        
        # Create keyboard with ADmin button
        keyboard = [
            [InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_{file_id}')],
            [InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss')],
            [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send video ID info
        await update.message.reply_text(
            f"✅ *Video Received!*\n\n"
            f"📹 *File ID:* `{file_id}`\n"
            f"🆔 *Unique ID:* `{file_unique_id}`\n"
            f"📁 *File Path:* `{file_path}`\n"
            f"⏱️ *Duration:* {video.duration}s\n"
            f"📏 *Resolution:* {video.width}x{video.height}\n"
            f"📦 *File Size:* {video.file_size} bytes\n"
            f"👤 *Uploaded by:* {user.first_name}\n\n"
            f"*Click the button below to copy the File ID*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in handle_video: {e}")
        await update.message.reply_text(
            "❌ Error processing video. Please try again with a different video file.",
            parse_mode='Markdown'
        )

# Handle regular messages (text, photos, etc.)
async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-video messages"""
    
    message = update.message
    
    # Check what type of message it is
    if message.text:
        # If it's a text message, show the welcome menu
        await start(update, context)
        
    elif message.photo:
        await message.reply_text(
            "📸 I see you sent a photo!\n\n"
            "To get a File ID, please send a *video* file (MP4, AVI, MOV).\n\n"
            "Send /start to see the menu.",
            parse_mode='Markdown'
        )
        
    elif message.document:
        await message.reply_text(
            "📄 I see you sent a document!\n\n"
            "To get a File ID, please send a *video* file (MP4, AVI, MOV).\n\n"
            "Send /start to see the menu.",
            parse_mode='Markdown'
        )
        
    elif message.voice:
        await message.reply_text(
            "🎤 I see you sent a voice message!\n\n"
            "To get a File ID, please send a *video* file (MP4, AVI, MOV).\n\n"
            "Send /start to see the menu.",
            parse_mode='Markdown'
        )
        
    else:
        await message.reply_text(
            "🤖 I only process video files to give you their File ID.\n\n"
            "Send a *video* file to get started!\n"
            "Or send /start to see the menu.",
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
        f"*How to use this ID:*\n"
        f"```python\n"
        f"await bot.send_video(\n"
        f"    chat_id=chat_id,\n"
        f"    video='{file_id}',\n"
        f"    caption='Your caption'\n"
        f")\n"
        f"```\n\n"
        f"*Or use this API link:*\n"
        f"`https://api.telegram.org/bot{Config.BOT_TOKEN}/getFile?file_id={file_id}`",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith('copy_'):
        await copy_id(update, context)

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    
    # Send error message to user
    try:
        if update and update.message:
            await update.message.reply_text(
                "❌ An error occurred. Please try again.\n\n"
                "Make sure you're sending a *video file* (MP4, AVI, MOV, etc.)",
                parse_mode='Markdown'
            )
        elif update and update.callback_query:
            await update.callback_query.message.reply_text(
                "❌ An error occurred. Please try again.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending error message: {e}")

# Clear webhook before starting
def clear_webhook():
    """Delete webhook to avoid conflict"""
    try:
        url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/deleteWebhook"
        response = requests.get(url)
        logger.info(f"Webhook cleared: {response.json()}")
    except Exception as e:
        logger.error(f"Error clearing webhook: {e}")

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
    # Clear webhook before starting
    clear_webhook()
    
    # Start web server in background thread for Railway health checks
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Start Telegram bot
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Message handlers - ORDER MATTERS!
    # First: Handle video files
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Second: Handle all other messages (text, photos, documents, etc.)
    application.add_handler(MessageHandler(filters.ALL, handle_other_messages))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
