import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import requests

# Replace this with your bot token
BOT_TOKEN = "8032468458:AAHa43tmVZgJvaprKNynTlG63x2-wGztGRQ"

# ShrinkMe API Key
SHRINKME_API_KEY = "32974302f4ff563e2a8a47e2b60c1e2e8161c503"

# Source bot username to forward from
SOURCE_BOT_USERNAME = "@Premiummovies0_bot"

# Movie storage channel where actual files are stored
STORAGE_CHANNEL = "@Bollyhollyhub"

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a movie name to search.")

# Movie search handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    keyboard = [[InlineKeyboardButton("🔗 Get Link", callback_data=query)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"🎬 Movie found: {query}\n\nClick the button below to get the link.", reply_markup=reply_markup)

# Shortlink creation
def create_shortlink(long_url):
    response = requests.get(f"https://shrinkme.io/api?api={SHRINKME_API_KEY}&url={long_url}")
    data = response.json()
    return data.get("shortenedUrl", long_url)

# Callback query handler (when user clicks "Get Link")
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    movie_name = query.data

    # Step 1: Send verification shortlink
    verify_link = create_shortlink(f"https://t.me/{context.bot.username}?start=verified_{movie_name.replace(' ', '_')}")
    await query.message.reply_text(
        f"✅ Please verify first:\nClick below and wait 10 seconds:\n{verify_link}"
    )

# Post-verification command handler
async def start_with_param(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0].startswith("verified_"):
        movie_name = context.args[0].replace("verified_", "").replace("_", " ")

        # Forward message from source bot (or storage channel)
        try:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"📥 Downloading **{movie_name}**...")
            # You can improve this by storing actual message_id of each movie
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🎬 Movie: {movie_name}\n📦 [Forwarded from source]")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to fetch movie: {e}")
    else:
        await update.message.reply_text("Send any movie name to get started 🎬")

# Main
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_with_param))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(CommandHandler("start", start))

    print("🤖 Rozibot is running...")
    app.run_polling()
