"""
Main bot file
Initialize Pyrogram client, register handlers, start bot
"""

import os
import asyncio
from pyrogram.client import Client
from pyrogram import StopPropagation
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

# Initialize database and API client
async def init_services():
    """Initialize database and API client"""
    print("🔧 Initializing database...")
    await db.init_db()
    print("🔧 Initializing API client...")
    await api_client.init_session()

def main():
    """Main function to run the bot"""
    
    # Check for required environment variables
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("Please set the following in Replit Secrets:")
        print("- TELEGRAM_BOT_TOKEN")
        print("- OWNER_ID")
        return
    
    if not OWNER_ID or OWNER_ID == "0":
        print("⚠️ Warning: OWNER_ID not set! Bot admin features will be limited.")
    
    # Create Pyrogram client
    print("🤖 Starting Telegram Bot...")
    
    api_id = int(os.getenv("API_ID", "6"))
    api_hash = os.getenv("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
    
    app = Client(
        "neet_ai_bot",
        bot_token=TELEGRAM_BOT_TOKEN,
        api_id=api_id,
        api_hash=api_hash,
        workers=4
    )
    
    # Register all handlers
    print("📝 Registering handlers...")
    register_chat_handlers(app)
    register_group_handlers(app)
    register_admin_handlers(app)
    
    # Add startup handler
    @app.on_message()
    async def startup_check(client, message):
        # Initialize services on first message
        if not hasattr(app, '_services_initialized'):
            await init_services()
            app._services_initialized = True
            
            # Set bot username
            import utils
            me = await client.get_me()
            utils.set_bot_username(me.username)
            print(f"🎉 Bot: @{me.username}")
            print(f"👤 Owner: {OWNER_ID}")
            print(f"🌐 Using {'Mock API' if api_client.use_mock else 'Real API'}")
            print("=" * 50)
            print("🚀 Bot is processing messages!")
            print("=" * 50)
        
        # Continue propagation to other handlers
        raise StopPropagation
    
    # Run the bot
    print("✅ Starting bot...")
    app.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        print("🔚 Bot shutdown complete")
