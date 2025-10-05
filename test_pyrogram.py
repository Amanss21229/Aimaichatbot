import os
from pyrogram import Client, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
api_id = int(os.getenv("API_ID", "6"))
api_hash = os.getenv("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")

print("Creating client...")
app = Client(
    "test_bot",
    bot_token=TELEGRAM_BOT_TOKEN,
    api_id=api_id,
    api_hash=api_hash
)

@app.on_message(filters.command("start"))
async def start_test(client, message):
    print(f"RECEIVED /start from {message.from_user.id}")
    await message.reply_text("Hello! Bot is working!")

@app.on_message(filters.text)
async def echo_test(client, message):
    print(f"RECEIVED message: {message.text}")
    await message.reply_text(f"Echo: {message.text}")

print("Starting bot with app.run()...")
app.run()
print("Bot stopped")
