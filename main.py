import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# CONFIG: usa variabili ambiente per sicurezza
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7891425503"))
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_LINK = "https://t.me/solo_giveaway"

# Stato globale
partecipanti = 0
obiettivo_raggiunto = False

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global partecipanti, obiettivo_raggiunto
    user_id = update.effective_user.id

    if obiettivo_raggiunto:
        text = f"🎉 Partecipanti raggiunti ({partecipanti})!\n"
        text += "Segui il canale per i prossimi giveaway 🎁\n"
        text += f"👉 {CHANNEL_LINK}"
        await update.message.reply_text(text)
        return

    text = f"🎁 Partecipanti attuali: {partecipanti}"

    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("➖ -1", callback_data='remove')],
            [InlineKeyboardButton("➕ +1", callback_data='add')],
            [InlineKeyboardButton("🎯 Obiettivo Raggiunto", callback_data='done')]
        ]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        text += (
            f"\n\nVuoi che il giveaway si faccia più in fretta?"
            f"\nInvita un amico 👉 {CHANNEL_LINK}"
            f"\nPiù siamo, prima si chiude l’estrazione! 🎉"
        )
        await update.message.reply_text(text)

# Bottoni
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global partecipanti, obiettivo_raggiunto
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    await query.answer()

    if user_id != ADMIN_ID:
        await query.edit_message_text("Non puoi usare questi bottoni.")
        return

    if data == "add":
        partecipanti += 1
    elif data == "remove" and partecipanti > 0:
        partecipanti -= 1
    elif data == "done":
        obiettivo_raggiunto = True
        keyboard = [
            [InlineKeyboardButton("✅ Sì", callback_data="restart")],
            [InlineKeyboardButton("❌ No", callback_data="close")]
        ]
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="✅ Obiettivo raggiunto! Vuoi lanciare un altro giveaway?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.edit_message_text(
            text=f"🎉 Partecipanti raggiunti ({partecipanti})!\n"
                 f"Segui il canale per i prossimi giveaway 🎁\n👉 {CHANNEL_LINK}"
        )
        return
    elif data == "close":
        keyboard = [[InlineKeyboardButton("🔁 Nuovo Giveaway", callback_data="restart")]]
        await query.edit_message_text("Ok, a presto!", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "restart":
        partecipanti = 0
        obiettivo_raggiunto = False
        text = f"🎁 Partecipanti attuali: {partecipanti}"
        keyboard = [
            [InlineKeyboardButton("➖ -1", callback_data='remove')],
            [InlineKeyboardButton("➕ +1", callback_data='add')],
            [InlineKeyboardButton("🎯 Obiettivo Raggiunto", callback_data='done')]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # aggiornamento normale dopo +1 / -1
    keyboard = [
        [InlineKeyboardButton("➖ -1", callback_data='remove')],
        [InlineKeyboardButton("➕ +1", callback_data='add')],
        [InlineKeyboardButton("🎯 Obiettivo Raggiunto", callback_data='done')]
    ]
    await query.edit_message_text(f"🎁 Partecipanti attuali: {partecipanti}", reply_markup=InlineKeyboardMarkup(keyboard))

# Avvio
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot avviato.")
    app.run_polling()

if __name__ == "__main__":
    main()
