import logging
import threading
import requests
import re
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

# Escape Markdown characters
def escape_markdown(text):
    """Escape special characters for Markdown"""
    if not text:
        return text
    escape_chars = r'_*[]()~`>#+\-=|{}.!'
    return re.sub(r'([{}])'.format(re.escape(escape_chars)), r'\\\1', str(text))

# Start command - shows video if available
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if we have a video ID stored
    video_id = context.bot_data.get('video_file_id')
    
    keyboard = [
        [
            InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss'),
            InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')
        ]
    ]
    
    if video_id:
        # Add copy button if video exists
        keyboard.append([InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_{video_id}')])
        
        caption = (
            f"{CHANNEL_DESCRIPTION}\n\n"
            f"📹 *Video File ID:*\n"
            f"<code>{video_id}</code>\n\n"
            f"Click the button below to copy the File ID"
        )
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            # Send video with caption using HTML (safer than Markdown)
            await update.message.reply_video(
                video=video_id,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            return
        except Exception as e:
            logger.error(f"Failed to send video: {e}")
            # If video fails, show text with ID
            await update.message.reply_text(
                f"{CHANNEL_DESCRIPTION}\n\n"
                f"📹 *Video File ID:*\n"
                f"<code>{video_id}</code>\n\n"
                f"Click the button below to copy the File ID\n\n"
                f"⚠️ Note: The video file may be expired. "
                f"Please send a new video to update it.",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    else:
        # No video stored - show instructions
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{CHANNEL_DESCRIPTION}\n\n"
            "📹 *No video uploaded yet!*\n\n"
            "Please send or forward a *video* to this bot.\n"
            "The bot will save the video ID and show it here.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# Handle videos - get file ID and store it
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video and return file ID - works with direct and forwarded videos"""
    
    try:
        message = update.message
        video = None
        
        # Check for video in multiple locations
        # 1. Direct video in message
        if hasattr(message, 'video') and message.video:
            video = message.video
            logger.info("Video found in message.video")
        
        # 2. Check if it's a forwarded video (various forward types)
        elif hasattr(message, 'forward_from') and message.forward_from:
            # Check the original message for video
            if hasattr(message, 'video') and message.video:
                video = message.video
                logger.info("Video found in forwarded message")
        
        # 3. Check if message has media group (album)
        elif hasattr(message, 'media_group_id') and message.media_group_id:
            if hasattr(message, 'video') and message.video:
                video = message.video
                logger.info("Video found in media group")
        
        # 4. Check for caption entities
        elif hasattr(message, 'caption_entities') and message.caption_entities:
            # Try to get video from caption
            if hasattr(message, 'video') and message.video:
                video = message.video
                logger.info("Video found with caption entities")
        
        # If still no video, try to get it from the message object directly
        if not video:
            # Sometimes video is nested differently
            if hasattr(message, 'video'):
                video = message.video
                if video:
                    logger.info("Video found in message.video (direct)")
        
        # If no video found, handle as normal message
        if not video:
            if message.text and message.text.startswith('/start'):
                await start(update, context)
            else:
                await message.reply_text(
                    "📹 Please send or forward a *video* file.\n\n"
                    "I didn't detect a video in this message.\n\n"
                    "Supported formats: MP4, AVI, MOV, MKV",
                    parse_mode='Markdown'
                )
            return
        
        # --- VIDEO FOUND - PROCESS IT ---
        # Get File ID directly from the video object
        file_id = video.file_id
        
        # Store the video ID in bot_data for persistence
        context.bot_data['video_file_id'] = file_id
        
        # Log the file ID
        logger.info(f"Video File ID saved: {file_id}")
        
        # Get video details
        file_name = getattr(video, 'file_name', 'Unknown')
        safe_file_name = escape_markdown(file_name)
        
        # Create keyboard with buttons
        keyboard = [
            [InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_{file_id}')],
            [InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss')],
            [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')],
            [InlineKeyboardButton("🔄 Test Video", callback_data=f'test_{file_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Check if it was forwarded
        is_forwarded = bool(message.forward_from or message.forward_origin)
        
        # Show File ID using HTML
        forward_text = "🔄 *Forwarded:* Yes" if is_forwarded else "📤 *Direct Upload:* Yes"
        
        await message.reply_text(
            f"✅ <b>Video File ID Saved!</b>\n\n"
            f"<code>{file_id}</code>\n\n"
            f"📂 <b>File Name:</b> {safe_file_name}\n"
            f"⏱️ <b>Duration:</b> {video.duration}s\n"
            f"📏 <b>Size:</b> {video.width}x{video.height}\n"
            f"📦 <b>File Size:</b> {video.file_size:,} bytes\n"
            f"{forward_text}\n\n"
            f"This video will now show when users send /start\n\n"
            f"Click the button below to copy the File ID",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in handle_video: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Error processing video: {str(e)[:100]}\n\n"
            "Please try sending the video again directly (not forwarded).",
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
        f"📋 <b>File ID copied to clipboard!</b>\n\n"
        f"<code>{file_id}</code>\n\n"
        f"<b>Use this ID to send the video:</b>\n"
        f"<code>await bot.send_video(\n"
        f"    chat_id=chat_id,\n"
        f"    video='{file_id}'\n"
        f")</code>\n\n"
        f"Or send this ID to any bot to use the video.",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

# Test video handler
async def test_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    file_id = query.data.replace('test_', '')
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_{file_id}')],
        [InlineKeyboardButton("👑 ADmin", url='https://t.me/PrimeAnalysiss')],
        [InlineKeyboardButton("📊 View Channel", url='https://t.me/PRIMEANALYS')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        f"✅ <b>Video Test</b>\n\n"
        f"📹 <b>File ID:</b>\n"
        f"<code>{file_id}</code>\n\n"
        f"Click the button below to copy the File ID"
    )
    
    try:
        await query.message.delete()
        await query.message.reply_video(
            video=file_id,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error playing video: {e}")
        await query.message.reply_text(
            f"❌ <b>Error playing video:</b>\n\n"
            f"<code>{file_id}</code>\n\n"
            f"The video file may have expired. Please upload a new video.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith('copy_'):
        await copy_id(update, context)
    elif data.startswith('test_'):
        await test_video(update, context)

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
    
    # Handle ALL messages - check for video everywhere
    application.add_handler(MessageHandler(filters.ALL, handle_video))
    
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
