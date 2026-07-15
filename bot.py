import logging
import threading
import json
import os
from datetime import datetime
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

# File to store video data
VIDEO_DATA_FILE = 'videos.json'

# Load saved videos
def load_videos():
    try:
        if os.path.exists(VIDEO_DATA_FILE):
            with open(VIDEO_DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading videos: {e}")
    return {'videos': []}

# Save videos
def save_videos(videos):
    try:
        with open(VIDEO_DATA_FILE, 'w') as f:
            json.dump(videos, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving videos: {e}")
        return False

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
            InlineKeyboardButton("👑 Join Channel", url='https://t.me/PrimeAnalysiss'),
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

# Video management handler
async def video_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    
    videos = load_videos()
    video_list = videos.get('videos', [])
    
    keyboard = [
        [InlineKeyboardButton("📤 Upload Video", callback_data='upload_video')],
        [InlineKeyboardButton("📋 View Saved Videos", callback_data='list_videos')],
        [InlineKeyboardButton("🗑️ Clear All Videos", callback_data='clear_videos')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🎬 *Video Management*\n\n"
        f"📹 Saved videos: {len(video_list)}\n\n"
        "*Options:*\n"
        "• Upload video to get its ID\n"
        "• View all saved videos\n"
        "• Clear all videos"
    )
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Handle video upload
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video uploads from users"""
    
    if not update.message.video:
        return
    
    video = update.message.video
    user = update.message.from_user
    
    # Get video details
    video_data = {
        'file_id': video.file_id,
        'file_unique_id': video.file_unique_id,
        'file_size': video.file_size,
        'width': video.width,
        'height': video.height,
        'duration': video.duration,
        'mime_type': video.mime_type,
        'uploaded_by': user.username or user.first_name,
        'user_id': user.id,
        'upload_date': datetime.now().isoformat(),
        'caption': update.message.caption or ''
    }
    
    # Save to storage
    videos = load_videos()
    videos['videos'].append(video_data)
    
    if save_videos(videos):
        # Send success message with video ID
        keyboard = [
            [InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_id_{video.file_id}')],
            [InlineKeyboardButton("🎬 Video Management", callback_data='video_manager')],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ *Video saved successfully!*\n\n"
            f"📹 *File ID:* `{video.file_id}`\n"
            f"⏱️ *Duration:* {video.duration}s\n"
            f"📏 *Size:* {video.width}x{video.height}\n"
            f"👤 *Uploaded by:* {user.first_name}\n\n"
            f"*Click the button below to copy the File ID*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Error saving video. Please try again."
        )

# List videos
async def list_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    videos = load_videos()
    video_list = videos.get('videos', [])
    
    if not video_list:
        keyboard = [
            [InlineKeyboardButton("📤 Upload Video", callback_data='upload_video')],
            [InlineKeyboardButton("🔙 Back", callback_data='video_manager')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📋 *No videos saved*\n\n"
            "Upload a video to get started.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # Show all videos
    text = "📋 *Saved Videos*\n\n"
    for i, video in enumerate(video_list, 1):
        duration = video.get('duration', 0)
        uploaded_by = video.get('uploaded_by', 'Unknown')
        file_id = video.get('file_id', '')[:15] + '...'
        
        text += f"{i}. 🎬 Duration: {duration}s\n"
        text += f"   👤 By: {uploaded_by}\n"
        text += f"   🆔 ID: `{file_id}`\n\n"
    
    # Create buttons for each video
    keyboard = []
    for i, video in enumerate(video_list[:10]):  # Show max 10 videos
        file_id = video.get('file_id', '')
        keyboard.append([
            InlineKeyboardButton(
                f"▶️ Video {i+1} (ID: {file_id[:10]}...)",
                callback_data=f'play_video_{file_id}'
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("🗑️ Clear All", callback_data='clear_videos')
    ])
    keyboard.append([
        InlineKeyboardButton("🔙 Back", callback_data='video_manager')
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Play video
async def play_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    file_id = query.data.replace('play_video_', '')
    
    # Find video in storage
    videos = load_videos()
    video_list = videos.get('videos', [])
    
    video_data = None
    for video in video_list:
        if video.get('file_id') == file_id:
            video_data = video
            break
    
    if not video_data:
        await query.edit_message_text(
            "❌ Video not found.",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [
            InlineKeyboardButton("📋 Copy File ID", callback_data=f'copy_id_{file_id}'),
            InlineKeyboardButton("🎬 Management", callback_data='video_manager')
        ],
        [
            InlineKeyboardButton("🔙 Back to List", callback_data='list_videos')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        f"🎬 *Video Details*\n\n"
        f"🆔 *File ID:* `{file_id}`\n"
        f"⏱️ *Duration:* {video_data.get('duration', 0)}s\n"
        f"📏 *Size:* {video_data.get('width', 0)}x{video_data.get('height', 0)}\n"
        f"👤 *Uploaded by:* {video_data.get('uploaded_by', 'Unknown')}\n"
        f"📅 *Date:* {video_data.get('upload_date', '')[:10]}\n\n"
        f"*Copy the File ID to use in your messages*"
    )
    
    try:
        await query.message.delete()
        await query.message.reply_video(
            video=file_id,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error playing video: {e}")
        await query.edit_message_text(
            "❌ Error playing video.",
            parse_mode='Markdown'
        )

# Clear videos
async def clear_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Ask for confirmation
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Clear", callback_data='confirm_clear'),
            InlineKeyboardButton("❌ Cancel", callback_data='video_manager')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚠️ *Are you sure you want to delete all videos?*\n\n"
        "This action cannot be undone.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Confirm clear videos
async def confirm_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    videos = load_videos()
    videos['videos'] = []
    
    if save_videos(videos):
        keyboard = [
            [InlineKeyboardButton("🎬 Video Management", callback_data='video_manager')],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🗑️ *All videos have been cleared.*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "❌ Error clearing videos.",
            parse_mode='Markdown'
        )

# Copy ID handler
async def copy_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    file_id = query.data.replace('copy_id_', '')
    
    keyboard = [
        [InlineKeyboardButton("🎬 Video Management", callback_data='video_manager')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"📋 *File ID copied to clipboard!*\n\n"
        f"`{file_id}`\n\n"
        f"*Note:* Select and copy the ID manually.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Upload video handler
async def upload_video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='video_manager')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📤 *Upload Video*\n\n"
        "Send a video to the bot to get its File ID.\n\n"
        "*Supported formats:*\n"
        "• MP4\n"
        "• AVI\n"
        "• MOV\n"
        "• MKV\n\n"
        "*Max size:* 50MB\n\n"
        "Send your video now!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'start':
        await start(update, context)
    elif data == 'video_manager':
        await video_manager(update, context)
    elif data == 'upload_video':
        await upload_video_handler(update, context)
    elif data == 'list_videos':
        await list_videos(update, context)
    elif data == 'clear_videos':
        await clear_videos(update, context)
    elif data == 'confirm_clear':
        await confirm_clear(update, context)
    elif data.startswith('play_video_'):
        await play_video(update, context)
    elif data.startswith('copy_id_'):
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
    application.add_handler(CommandHandler("video", video_manager))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Message handlers for video uploads
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Prime Analysis Bot with Video Management is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
