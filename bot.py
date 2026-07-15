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
    "👑 *Acabas de entrar a la comunidad privada del REY*\n\n"
    "Aquí no entran curiosos... solo personas que realmente quieren "
    "aprender a operar y buscar resultados reales dentro del mercado.\n\n"
    "👇 *¡Haga clic en el enlace o en el botón de abajo para acceder "
    "a la comunidad del rey!*"
)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👑 Ver Canal", url='https://t.me/DavidTrader_ReydeQuotex'),
            InlineKeyboardButton("📺 YouTube", url='https://youtube.com/@reydequotex?si=PuKiLu1bDiWrvAB')
        ],
        [
            InlineKeyboardButton("📩 Contacto", url='https://t.me/REYDEQUOTEX'),
            InlineKeyboardButton("📊 Prime Analysis", url='https://t.me/PRIMEANALYS')
        ],
        [
            InlineKeyboardButton("📤 Compartir", callback_data='share'),
            InlineKeyboardButton("❓ Ayuda", callback_data='help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "👑 *David Trader | Rey de Quotex*\n\n"
        "Bienvenido a la comunidad del REY. Aquí aprenderás a operar "
        "y buscar resultados reales dentro del mercado.\n\n"
        "👇 *¡Haga clic en el botón de abajo para acceder "
        "a la comunidad del rey!*"
    )
    
    # Send logo/image if available
    if Config.IMAGE_URL:
        try:
            await update.message.reply_photo(
                photo=Config.IMAGE_URL,
                caption=welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        except Exception as e:
            logger.error(f"Failed to send image: {e}")
    
    # Fallback to text message
    await update.message.reply_text(
        welcome_text,
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
        [InlineKeyboardButton("📤 Enviar Video", callback_data='upload_video')],
        [InlineKeyboardButton("📋 Ver Videos Guardados", callback_data='list_videos')],
        [InlineKeyboardButton("🗑️ Limpiar Videos", callback_data='clear_videos')],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🎬 *Gestión de Videos*\n\n"
        f"📹 Videos guardados: {len(video_list)}\n\n"
        "*Opciones:*\n"
        "• Enviar video para guardarlo\n"
        "• Ver lista de videos guardados\n"
        "• Limpiar todos los videos"
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
        # Send success message
        keyboard = [
            [InlineKeyboardButton("🎬 Gestión de Videos", callback_data='video_manager')],
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ *Video guardado exitosamente!*\n\n"
            f"📹 *File ID:* `{video.file_id[:20]}...`\n"
            f"⏱️ *Duración:* {video.duration}s\n"
            f"📏 *Tamaño:* {video.width}x{video.height}\n"
            f"👤 *Subido por:* {user.first_name}\n\n"
            f"*Usa este ID para referenciar el video en tus mensajes.*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Error al guardar el video. Por favor intenta de nuevo."
        )

# List videos
async def list_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    videos = load_videos()
    video_list = videos.get('videos', [])
    
    if not video_list:
        keyboard = [
            [InlineKeyboardButton("📤 Subir Video", callback_data='upload_video')],
            [InlineKeyboardButton("🔙 Volver", callback_data='video_manager')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📋 *No hay videos guardados*\n\n"
            "Envía un video al bot para guardarlo.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # Show last 10 videos
    text = "📋 *Videos Guardados*\n\n"
    for i, video in enumerate(reversed(video_list[-10:]), 1):
        duration = video.get('duration', 0)
        upload_date = video.get('upload_date', '')
        uploaded_by = video.get('uploaded_by', 'Unknown')
        file_id = video.get('file_id', '')[:15] + '...'
        
        text += f"{i}. 🎬 Duración: {duration}s\n"
        text += f"   👤 Por: {uploaded_by}\n"
        text += f"   🆔 ID: `{file_id}`\n"
        text += f"   📅 {upload_date[:10]}\n\n"
    
    # Create buttons for each video
    keyboard = []
    for i, video in enumerate(reversed(video_list[-5:])):
        file_id = video.get('file_id', '')
        keyboard.append([
            InlineKeyboardButton(
                f"▶️ Video {i+1} (ID: {file_id[:10]}...)",
                callback_data=f'play_video_{file_id}'
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("🗑️ Limpiar Todo", callback_data='clear_videos')
    ])
    keyboard.append([
        InlineKeyboardButton("🔙 Volver", callback_data='video_manager')
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
            "❌ Video no encontrado. Puede haber sido eliminado.",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [
            InlineKeyboardButton("📹 Ver ID", callback_data=f'copy_id_{file_id}'),
            InlineKeyboardButton("🎬 Gestión", callback_data='video_manager')
        ],
        [
            InlineKeyboardButton("🔙 Volver a Lista", callback_data='list_videos')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        f"🎬 *Video Guardado*\n\n"
        f"🆔 *File ID:* `{file_id}`\n"
        f"⏱️ *Duración:* {video_data.get('duration', 0)}s\n"
        f"📏 *Tamaño:* {video_data.get('width', 0)}x{video_data.get('height', 0)}\n"
        f"👤 *Subido por:* {video_data.get('uploaded_by', 'Unknown')}\n"
        f"📅 *Fecha:* {video_data.get('upload_date', '')[:10]}\n\n"
        f"*Copia el File ID para usar en tus mensajes.*"
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
            "❌ Error al reproducir el video. El archivo puede haber sido eliminado.",
            parse_mode='Markdown'
        )

# Clear videos
async def clear_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Ask for confirmation
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí, Limpiar", callback_data='confirm_clear'),
            InlineKeyboardButton("❌ Cancelar", callback_data='video_manager')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚠️ *¿Estás seguro de que quieres eliminar todos los videos?*\n\n"
        "Esta acción no se puede deshacer.",
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
            [InlineKeyboardButton("🎬 Gestión de Videos", callback_data='video_manager')],
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🗑️ *Todos los videos han sido eliminados.*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "❌ Error al limpiar los videos. Por favor intenta de nuevo.",
            parse_mode='Markdown'
        )

# Copy ID handler
async def copy_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    file_id = query.data.replace('copy_id_', '')
    
    await query.message.reply_text(
        f"📋 *File ID copiado al portapapeles!*\n\n"
        f"`{file_id}`\n\n"
        f"*Nota:* Selecciona y copia el ID manualmente.",
        parse_mode='Markdown'
    )

# Upload video handler
async def upload_video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔙 Volver", callback_data='video_manager')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📤 *Subir Video*\n\n"
        "Envía un video al bot para guardarlo.\n\n"
        "*Formatos soportados:*\n"
        "• MP4\n"
        "• AVI\n"
        "• MOV\n"
        "• WMV\n"
        "• MKV\n\n"
        "*Tamaño máximo:* 50MB\n\n"
        "*También puedes agregar un pie de foto al video.*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Set state to expect video upload
    context.user_data['expecting_video'] = True

# Share handler
async def share_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    share_text = (
        "📤 *Compartir David Trader | Rey de Quotex*\n\n"
        "¡Ayuda a otros a descubrir la comunidad del REY!\n\n"
        "*Enlaces:*\n"
        "📺 YouTube: https://youtube.com/@reydequotex\n"
        "📩 Contacto: @REYDEQUOTEX\n"
        "👑 Canal: @DavidTrader_ReydeQuotex\n\n"
        "¡Comparte estos enlaces con tus amigos! 🚀"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(share_text, reply_markup=reply_markup, parse_mode='Markdown')

# Help handler
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    
    help_text = (
        "❓ *Ayuda & Comandos*\n\n"
        "*Cómo usar:*\n"
        "1. Presiona 'Ver Canal' para unirte\n"
        "2. Presiona 'YouTube' para ver los videos\n"
        "3. Presiona 'Contacto' para escribir\n\n"
        "*Comandos:*\n"
        "/start - Mostrar menú principal\n"
        "/channel - Ver descripción del canal\n"
        "/video - Gestión de videos\n"
        "/help - Mostrar esta ayuda\n"
        "/share - Compartir enlaces\n\n"
        "*Enlaces importantes:*\n"
        "👑 Canal: @DavidTrader_ReydeQuotex\n"
        "📺 YouTube: @reydequotex\n"
        "📩 Contacto: @REYDEQUOTEX"
    )
    
    if query:
        await query.edit_message_text(help_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown')

# Channel handler - shows full description
async def channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("👑 Unirse al Canal", url='https://t.me/DavidTrader_ReydeQuotex'),
            InlineKeyboardButton("📺 YouTube", url='https://youtube.com/@reydequotex?si=PuKiLu1bDiWrvAB')
        ],
        [
            InlineKeyboardButton("📩 Contactar", url='https://t.me/REYDEQUOTEX'),
            InlineKeyboardButton("📊 Prime Analysis", url='https://t.me/PRIMEANALYS')
        ],
        [
            InlineKeyboardButton("🔙 Volver al Menú", callback_data='main_menu')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send logo/image if available
    if Config.IMAGE_URL:
        try:
            if query:
                await query.message.delete()
                await query.message.reply_photo(
                    photo=Config.IMAGE_URL,
                    caption=CHANNEL_DESCRIPTION,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
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
    if query:
        await query.edit_message_text(
            CHANNEL_DESCRIPTION,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            CHANNEL_DESCRIPTION,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# Main menu handler
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'main_menu':
        await main_menu_handler(update, context)
    elif data == 'channel':
        await channel_handler(update, context)
    elif data == 'help':
        await help_handler(update, context)
    elif data == 'share':
        await share_handler(update, context)
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
    application.add_handler(CommandHandler("channel", channel_handler))
    application.add_handler(CommandHandler("video", video_manager))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("share", share_handler))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Message handlers for video uploads
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("👑 David Trader | Rey de Quotex Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
