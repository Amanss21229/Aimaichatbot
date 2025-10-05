import os
import asyncio
from pyrogram import Client, filters, idle

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
api_id = int(os.getenv("API_ID", "6"))
api_hash = os.getenv("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")

print("Creating client...")
app = Client(
    "test_async_bot",
    bot_token=TELEGRAM_BOT_TOKEN,
    api_id=api_id,
    api_hash=api_hash
)

@app.on_message(filters.command("start"))
async def start_test(client, message):
    print(f"✅ RECEIVED /start from {message.from_user.id}")
    await message.reply_text("Hello! Async bot is working!")

@app.on_message(filters.text & ~filters.command("start"))
async def echo_test(client, message):
    print(f"✅ RECEIVED message: {message.text}")
    await message.reply_text(f"Echo: {message.text}")

async def main():
    print("Starting bot...")
    await app.start()
    print("Bot started! Waiting for messages...")
    await idle()
    print("Stopping bot...")
    await app.stop()
    print("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
