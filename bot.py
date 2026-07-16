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

# Channel description - NO CONTACT INFO
CHANNEL_DESCRIPTION = (
    "🏅📊 <b>Welcome to Prime Analysis!</b>\n\n"
    "Your ultimate source for real-time sports betting insights. "
    "Get expert predictions, stats and tips to sharpen your betting game. "
    "Join us for updates and discussions as we keep you ahead of the curve 📊"
)

# Start command - shows menu with buttons only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
        ],
        [
            InlineKeyboardButton("📹 Get Video ID", callback_data='get_video')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        CHANNEL_DESCRIPTION,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

# Get video ID instruction
async def get_video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📹 <b>How to Get Video File ID</b>\n\n"
        "1. Send or forward a <b>video</b> to this bot\n"
        "2. The bot will reply with the <b>File ID</b>\n"
        "3. Copy the File ID using the button below\n\n"
        "📤 <i>Send a video now to get its File ID!</i>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

# Handle videos - get file ID and store it
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
                    "📹 Send or forward a <b>video</b> to get its File ID.\n\n"
                    "Or send /start to see the menu.",
                    parse_mode='HTML'
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
            [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send the File ID
        await message.reply_text(
            f"✅ <b>Video Received!</b>\n\n"
            f"📹 <b>File ID:</b>\n"
            f"<code>{file_id}</code>\n\n"
            f"📂 <b>File Name:</b> {file_name}\n"
            f"⏱️ <b>Duration:</b> {video.duration}s\n"
            f"📏 <b>Size:</b> {video.width}x{video.height}\n"
            f"📦 <b>File Size:</b> {video.file_size:,} bytes\n\n"
            f"Click the button below to copy the File ID",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)[:100]}\n\nPlease try again.",
            parse_mode='HTML'
        )

# Copy ID handler
async def copy_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    file_id = query.data.replace('copy_', '')
    
    keyboard = [
        [InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss')],
        [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"📋 <b>File ID copied to clipboard!</b>\n\n"
        f"<code>{file_id}</code>\n\n"
        f"<b>Use this ID to send the video:</b>\n"
        f"<code>await bot.send_video(chat_id=chat_id, video='{file_id}')</code>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

# Menu handler
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
        ],
        [
            InlineKeyboardButton("📹 Get Video ID", callback_data='get_video')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        CHANNEL_DESCRIPTION,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'menu':
        await menu_handler(update, context)
    elif data == 'get_video':
        await get_video_handler(update, context)
    elif data.startswith('copy_'):
        await copy_id(update, context)

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again.\n\n"
            "Send /start to see the menu.",
            parse_mode='HTML'
        )
    elif update and update.callback_query:
        await update.callback_query.message.reply_text(
            "❌ An error occurred. Please try again.",
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
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.ALL, handle_video))
    
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
