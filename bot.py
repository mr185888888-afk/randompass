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

# Handle video upload - get file ID and file path
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video uploads and return file ID and file path"""
    
    if not update.message.video:
        return
    
    video = update.message.video
    user = update.message.from_user
    
    # Get the file ID directly from the video object
    file_id = video.file_id
    file_unique_id = video.file_unique_id
    
    # Get file path using getFile API
    try:
        # Method 1: Using python-telegram-bot's built-in method
        file = await context.bot.get_file(file_id)
        file_path = file.file_path
        
        # Method 2: Using direct API call (optional)
        api_url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/getFile?file_id={file_id}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                api_file_path = data.get('result', {}).get('file_path')
            else:
                api_file_path = "API Error"
        else:
            api_file_path = "API Request Failed"
            
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        file_path = "Error getting file path"
        api_file_path = "Error"
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_{file_id}')],
        [InlineKeyboardButton("📋 Copy File Path", callback_data=f'copypath_{file_path}')],
        [InlineKeyboardButton("👑 Admin", url='https://t.me/PrimeAnalysiss')],
        [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ *Video uploaded successfully!*\n\n"
        f"📹 *File ID:* `{file_id}`\n"
        f"🆔 *Unique ID:* `{file_unique_id}`\n"
        f"📁 *File Path:* `{file_path}`\n"
        f"⏱️ *Duration:* {video.duration}s\n"
        f"📏 *Size:* {video.width}x{video.height}\n"
        f"📦 *File Size:* {video.file_size} bytes\n"
        f"👤 *Uploaded by:* {user.first_name}\n\n"
        f"*Click buttons below to copy the ID or path.*",
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
        f"*Note:* Select and copy the ID manually.",
        parse_mode='Markdown'
    )

# Copy File Path handler
async def copy_file_path(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    file_path = query.data.replace('copypath_', '')
    
    await query.message.reply_text(
        f"📋 *File Path copied to clipboard!*\n\n"
        f"`{file_path}`\n\n"
        f"*Note:* Select and copy the path manually.\n\n"
        f"*Download URL:*\n"
        f"`https://api.telegram.org/file/bot{Config.BOT_TOKEN}/{file_path}`",
        parse_mode='Markdown'
    )

# Get updates handler (for manual API testing)
async def get_updates_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get recent updates from Telegram API"""
    try:
        api_url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/getUpdates"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('ok'):
                updates = data.get('result', [])
                
                if updates:
                    # Find the latest video message
                    for upd in updates:
                        if 'message' in upd and upd['message'].get('video'):
                            video = upd['message']['video']
                            file_id = video.get('file_id')
                            
                            # Get file info
                            file_url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/getFile?file_id={file_id}"
                            file_response = requests.get(file_url)
                            file_data = file_response.json()
                            
                            await update.message.reply_text(
                                f"📹 *Latest Video Found in Updates*\n\n"
                                f"📹 *File ID:* `{file_id}`\n"
                                f"📁 *File Path:* `{file_data.get('result', {}).get('file_path', 'N/A')}`\n\n"
                                f"*To download:*\n"
                                f"`https://api.telegram.org/file/bot{Config.BOT_TOKEN}/{file_data.get('result', {}).get('file_path', '')}`",
                                parse_mode='Markdown'
                            )
                            return
                    
                    await update.message.reply_text(
                        "❌ No video messages found in recent updates.",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        "❌ No updates found. Send a video first!",
                        parse_mode='Markdown'
                    )
            else:
                await update.message.reply_text(
                    f"❌ API Error: {data.get('description', 'Unknown error')}",
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                f"❌ HTTP Error: {response.status_code}",
                parse_mode='Markdown'
            )
                
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}",
            parse_mode='Markdown'
        )

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith('copy_'):
        await copy_id(update, context)
    elif data.startswith('copypath_'):
        await copy_file_path(update, context)

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
    application.add_handler(CommandHandler("getupdates", get_updates_handler))
    
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
