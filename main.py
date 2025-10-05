"""
Main bot file
Initialize Pyrogram client, register handlers, start bot
"""

import os
import asyncio
from pyrogram.client import Client
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
API_ID = os.getenv("API_ID", "")
API_HASH = os.getenv("API_HASH", "")

# Bot start time for uptime calculation
bot_start_time = datetime.now()

async def main():
    """Main function to run the bot"""
    
    # Check for required environment variables
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("Please set the following in Replit Secrets:")
        print("- TELEGRAM_BOT_TOKEN")
        print("- OWNER_ID")
        print("- WEBSITE_API_URL (optional)")
        print("- WEBSITE_API_KEY (optional)")
        return
    
    if not OWNER_ID or OWNER_ID == "0":
        print("⚠️ Warning: OWNER_ID not set! Bot admin features will be limited.")
    
    # Initialize database
    print("🔧 Initializing database...")
    await db.init_db()
    
    # Initialize API client
    print("🔧 Initializing API client...")
    await api_client.init_session()
    
    # Create Pyrogram client
    print("🤖 Starting Telegram Bot...")
    
    app = Client(
        "neet_ai_bot",
        bot_token=TELEGRAM_BOT_TOKEN,
        api_id=API_ID if API_ID else None,
        api_hash=API_HASH if API_HASH else None,
        workers=4
    )
    
    # Register all handlers
    print("📝 Registering handlers...")
    register_chat_handlers(app)
    register_group_handlers(app)
    register_admin_handlers(app)
    
    # Start the bot
    print("✅ Bot is starting...")
    
    async with app:
        # Get bot info
        me = await app.get_me()
        print(f"🎉 Bot started successfully!")
        print(f"📛 Bot Name: {me.first_name}")
        print(f"🆔 Bot Username: @{me.username}")
        print(f"👤 Owner ID: {OWNER_ID}")
        print(f"🌐 Using {'Mock API' if api_client.use_mock else 'Real API'}")
        print(f"⏰ Started at: {bot_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print("🚀 Bot is now running! Press Ctrl+C to stop.")
        print("=" * 50)
        
        # Update bot username in utils (for buttons)
        os.environ["BOT_USERNAME"] = me.username
        
        # Keep the bot running
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        print("🔚 Bot shutdown complete")
