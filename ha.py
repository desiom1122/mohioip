import pymongo
import hashlib
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# Replace these with your MongoDB connection details
MONGO_URI = "mongodb+srv://medusapremia:Ahmed1122@cluster0.fblv6rt.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "test"
COLLECTION_NAME = "mohio"

# MongoDB setup
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Telegram bot token
TELEGRAM_TOKEN = "6489260167:AAF1WqIFwrNPI51r642gfs7vYc97PZTfwjo"

# Function to handle the "/start" command
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user

    # Parse user input for username, password, and ip
    input_text = update.message.text[len('/start '):].split(':')
    if len(input_text) >= 3:
        username = input_text[0].strip()
        password = hashlib.sha256(input_text[1].strip().encode()).hexdigest()
        ip = input_text[2].strip()
    else:
        update.message.reply_text('Invalid input format. Please use: /start username:password:ip')
        return

    document = {
        "username": username,
        "password": password,
        "fingerprint": {},
        "ip": ip,
        "settings": {
            "bin": "",
            "proxy": "",
            "logs": ["yellow:yellow:Welcome to mohio!"]
        },
        "role": "beta",
        "invites": {}
    }

    # Insert document into MongoDB
    collection.insert_one(document)

    update.message.reply_text('Document inserted successfully!')

def update_document(update: Updater, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Check if both username and IP are provided as arguments
    if len(context.args) >= 2:
        username_to_update = context.args[0]
        user_ip = context.args[1]

        # Find the document with the specified username and user ID
        document = collection.find_one({"username": username_to_update})

        if not document:
            update.message.reply_text(f'No document found with the username "{username_to_update}" for your user ID.')
            return

        # Update the MongoDB document
        collection.update_one(
            {"_id": document["_id"]},
            {"$set": {"ip": user_ip}},
        )

        update.message.reply_text(f'IP updated successfully for the username "{username_to_update}"! New IP: {user_ip}')
    else:
        update.message.reply_text('Please provide both username and IP as arguments. Example: /update <username> <ip>')

# Function to handle incoming text messages
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def main() -> None:
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("update", update_document, pass_args=True))

    # Message handler (echo)
    dp.add_handler(MessageHandler(filters.text & ~filters.command, echo))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
