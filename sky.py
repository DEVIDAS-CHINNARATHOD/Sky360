import firebase_admin
from firebase_admin import credentials, firestore

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8780762202:AAFm-wl09rl7VbFP18uIW2tgp1AVjQ84KkI"

# Firebase initialization
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

incident_data = {}

# Function to clear previous incidents
def clear_previous_incidents():
    docs = db.collection("incidents").stream()
    for doc in docs:
        db.collection("incidents").document(doc.id).delete()


# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🚁 AI Drone Dispatch System\n\n"
        "Commands:\n"
        "/report - Report an incident\n"
        "/stop - Cancel reporting"
    )


# START REPORT
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id
    incident_data[user] = {}

    await update.message.reply_text(
        "🚨 Incident reporting started.\n\nSend incident name."
    )


# STOP REPORT
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user in incident_data:
        del incident_data[user]

    await update.message.reply_text("❌ Incident reporting cancelled.")


# INCIDENT NAME
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user not in incident_data:
        await update.message.reply_text("Use /report first.")
        return

    if "incident" not in incident_data[user]:

        incident_data[user]["incident"] = update.message.text

        await update.message.reply_text("📷 Upload incident photo")


# PHOTO
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user not in incident_data:
        await update.message.reply_text("Use /report first.")
        return

    photo = update.message.photo[-1]

    file = await photo.get_file()

    path = f"incident_{user}.jpg"

    await file.download_to_drive(path)

    incident_data[user]["photo"] = path

    await update.message.reply_text(
        "📍 Send location using Telegram location sharing"
    )


# LOCATION
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user not in incident_data:
        await update.message.reply_text("Use /report first.")
        return

    loc = update.message.location

    geo_point = firestore.GeoPoint(loc.latitude, loc.longitude)

    # Clear previous incidents
    clear_previous_incidents()

    data = {
        "incident": incident_data[user]["incident"],
        "photo_path": incident_data[user]["photo"],
        "location": geo_point,
        "status": "pending"
    }

    db.collection("incidents").add(data)

    print("🚨 Incident pushed to Firebase")
    print(data)

    await update.message.reply_text(
        f"""
✅ Incident Submitted

Type: {data['incident']}
Location stored as GeoPoint

Previous incidents cleared.
"""
    )

    del incident_data[user]


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("stop", stop))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))

    print("🤖 Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()