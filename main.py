"""
Main bot file
Initialize Pyrogram client, register handlers, start bot
"""

import os
import asyncio
from pyrogram.client import Client
from pyrogram import StopPropagation, filters
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
import db
from apiclient import api_client
from handlers_chat import register_chat_handlers
from handlers_group import register_group_handlers
from admin_commands import register_admin_handlers

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OWNER_ID = os.getenv("OWNER_ID", "0")

# Bot start time for uptime calculation
bot_start_time = datetime.now()

async def main():
    """Main function to run the bot"""
    
    # Check for required environment variables
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    if not OWNER_ID or OWNER_ID == "0":
        print("⚠️ Warning: OWNER_ID not set!")
    
    # Initialize services
    print("🔧 Initializing database...")
    await db.init_db()
    print("✅ Database initialized")
    
    print("🔧 Initializing API client...")
    await api_client.init_session()
    print("✅ API client initialized")
    
    # Create Pyrogram client
    print("🤖 Creating Telegram Bot...")
    
    api_id = int(os.getenv("API_ID", "6"))
    api_hash = os.getenv("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
    
    app = Client(
        "neet_ai_bot",
        bot_token=TELEGRAM_BOT_TOKEN,
        api_id=api_id,
        api_hash=api_hash,
        workers=4
    )
    
    # Add a simple test handler using decorator
    @app.on_message(filters.command("test"))
    async def test_handler(client, message):
        print(f"🧪 TEST HANDLER triggered by {message.from_user.id}")
        await message.reply_text("Test handler is working!")
    
    @app.on_message(filters.text)
    async def catch_all_handler(client, message):
        print(f"🔍 CATCH-ALL: Received message from {message.from_user.id}: {message.text[:50]}")
    
    # Register all handlers
    print("📝 Registering handlers...")
    register_chat_handlers(app)
    register_group_handlers(app)
    register_admin_handlers(app)
    print("✅ All handlers registered successfully")
    
    # Start the bot
    print("🚀 Starting bot...")
    await app.start()
    
    # Set bot username
    import utils
    me = await app.get_me()
    utils.set_bot_username(me.username)
    print(f"🎉 Bot: @{me.username}")
    print(f"👤 Owner: {OWNER_ID}")
    print(f"🌐 Using {'Mock API' if api_client.use_mock else 'Real API'}")
    print("=" * 50)
    print("🚀 Bot is ready and listening for messages!")
    print("=" * 50)
    
    # Keep running with infinite loop
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping bot...")
    finally:
        await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔚 Bot shutdown complete")
