import logging
import threading
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
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("share", share_handler))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("👑 David Trader | Rey de Quotex Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
