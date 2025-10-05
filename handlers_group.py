"""
Group chat handlers for the bot
/sol command, chat on/off, group admin commands
"""

import os
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
from pyrogram.errors import FloodWait
import asyncio
import db
import utils
from apiclient import api_client

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

@filters.create
async def group_filter(_, __, message: Message):
    """Filter for group messages only"""
    return message.chat.type in ["group", "supergroup"]

async def is_group_admin(client: Client, chat_id: int, user_id: int) -> bool:
    """Check if user is admin in the group"""
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ["creator", "administrator"]
    except:
        return False

async def new_chat_handler(client: Client, message: Message):
    """
    Handle bot being added to a new group
    Register group in database
    """
    # Check if bot was added
    for member in message.new_chat_members:
        if member.id == client.me.id:
            # Add group to database
            await db.add_group(
                gid=message.chat.id,
                title=message.chat.title,
                username=message.chat.username
            )
            
            # Send welcome message
            await message.reply_text(
                f"🎓 **NEET AI Bot को {message.chat.title} में add करने के लिए धन्यवाद!**\n\n"
                "**📚 Group Features:**\n"
                "• किसी भी message को reply करके `/sol` टाइप करें - मैं उस question का जवाब दूंगा\n"
                "• Admins `/chaton` और `/chatoff` से bot के free chat को control कर सकते हैं\n"
                "• `/refresh` से bot को refresh करें\n"
                "• `/stats` से statistics देखें\n\n"
                "— NEET AI Bot ✨"
            )
            
            print(f"✅ Added to group: {message.chat.title} ({message.chat.id})")

async def sol_command_handler(client: Client, message: Message):
    """
    Handle /sol command in groups
    Must be used as reply to a message containing a question
    """
    # Check if it's a reply
    if not message.reply_to_message:
        await message.reply_text(
            "⚠️ `/sol` command को किसी message के reply में use करें!\n\n"
            "Please use `/sol` as a reply to a question message."
        )
        return
    
    # Get the question from replied message
    replied_msg = message.reply_to_message
    question_text = replied_msg.text or replied_msg.caption or ""
    
    if not question_text:
        await message.reply_text(
            "❌ Reply किये गए message में कोई text नहीं है।\n\n"
            "The replied message has no text."
        )
        return
    
    # Validate length
    if len(question_text) > 2000:
        await message.reply_text(
            "❌ Question बहुत लंबा है! 2000 characters से कम होना चाहिए।"
        )
        return
    
    # Send processing message
    processing_msg = await message.reply_text("🔍 जवाब ढूंढ रहा हूं... | Finding answer...")
    
    try:
        # Get answer from API
        result = await api_client.get_answer(
            question=question_text,
            uid=message.from_user.id,
            mode="short"
        )
        
        # Delete processing message
        await processing_msg.delete()
        
        if result.get('success'):
            # Format answer for group
            answer_text = utils.format_answer_message(
                question=question_text,
                answer=result['short_answer']
            )
            
            # Create solution button
            solution_button = utils.get_solution_button(result['detailed_url'])
            
            # Send answer as reply to original question
            await replied_msg.reply_text(
                answer_text,
                reply_markup=solution_button
            )
            
            # Log usage
            await db.log_usage(
                uid=message.from_user.id,
                gid=message.chat.id,
                cmd="/sol",
                qtext=question_text[:200]
            )
        
        else:
            await message.reply_text(
                "❌ क्षमा करें, कुछ गड़बड़ हुई। फिर से try करें।"
            )
    
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await processing_msg.edit_text(f"⏳ Rate limit! {e.value}s wait...")
    
    except Exception as e:
        print(f"Error in /sol handler: {e}")
        await processing_msg.delete()
        await message.reply_text(f"❌ Error: {str(e)}")

async def chaton_handler(client: Client, message: Message):
    """
    Handle /chaton command - enable free chat in group
    Only for group admins or bot admins
    """
    # Check if user is group admin or bot admin
    is_admin = await is_group_admin(client, message.chat.id, message.from_user.id)
    is_bot_admin = await db.is_bot_admin(message.from_user.id)
    
    if not is_admin and not is_bot_admin and message.from_user.id != OWNER_ID:
        await message.reply_text("❌ Only group admins can use this command.")
        return
    
    # Enable chat
    await db.set_chat_status(message.chat.id, True)
    await message.reply_text(
        "✅ **Chat Mode: ON**\n\n"
        "Bot अब group में free chat करेगा।\n"
        "Bot will now respond to free chat in the group."
    )
    
    await db.log_usage(message.from_user.id, message.chat.id, "/chaton")

async def chatoff_handler(client: Client, message: Message):
    """
    Handle /chatoff command - disable free chat in group
    Only for group admins or bot admins
    """
    # Check if user is group admin or bot admin
    is_admin = await is_group_admin(client, message.chat.id, message.from_user.id)
    is_bot_admin = await db.is_bot_admin(message.from_user.id)
    
    if not is_admin and not is_bot_admin and message.from_user.id != OWNER_ID:
        await message.reply_text("❌ Only group admins can use this command.")
        return
    
    # Disable chat
    await db.set_chat_status(message.chat.id, False)
    await message.reply_text(
        "🔴 **Chat Mode: OFF**\n\n"
        "Bot अब केवल `/sol` command पर respond करेगा।\n"
        "Bot will only respond to `/sol` commands now."
    )
    
    await db.log_usage(message.from_user.id, message.chat.id, "/chatoff")

async def group_text_handler(client: Client, message: Message):
    """
    Handle normal text in groups (only if chat_on is True)
    """
    # Check chat status
    chat_on = await db.get_chat_status(message.chat.id)
    
    if not chat_on:
        return
    
    # Get question
    question_text = message.text
    
    if len(question_text) > 2000:
        return
    
    # Simple detection: if message ends with ? or contains question words
    question_indicators = ['?', 'क्या', 'कैसे', 'क्यों', 'कौन', 'what', 'how', 'why', 'who', 'when']
    
    is_question = any(indicator in question_text.lower() for indicator in question_indicators)
    
    if not is_question:
        return
    
    # Process as question
    processing_msg = await message.reply_text("🔍 जवाब ढूंढ रहा हूं...")
    
    try:
        result = await api_client.get_answer(
            question=question_text,
            uid=message.from_user.id,
            mode="short"
        )
        
        await processing_msg.delete()
        
        if result.get('success'):
            answer_text = utils.format_answer_message(
                question=question_text,
                answer=result['short_answer']
            )
            
            solution_button = utils.get_solution_button(result['detailed_url'])
            
            await message.reply_text(
                answer_text,
                reply_markup=solution_button
            )
            
            await db.log_usage(
                uid=message.from_user.id,
                gid=message.chat.id,
                cmd="group_question",
                qtext=question_text[:200]
            )
    
    except Exception as e:
        print(f"Error in group text handler: {e}")
        await processing_msg.delete()

def register_group_handlers(app: Client):
    """Register all group handlers"""
    app.add_handler(MessageHandler(new_chat_handler, filters.new_chat_members & group_filter))
    app.add_handler(MessageHandler(sol_command_handler, filters.command("sol") & group_filter))
    app.add_handler(MessageHandler(chaton_handler, filters.command("chaton") & group_filter))
    app.add_handler(MessageHandler(chatoff_handler, filters.command("chatoff") & group_filter))
    app.add_handler(MessageHandler(group_text_handler, filters.text & group_filter & ~filters.command(["sol", "chaton", "chatoff", "stats", "refresh"])))
