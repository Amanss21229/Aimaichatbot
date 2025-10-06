"""
Personal chat handlers for the bot
/start command and question-answering in private messages
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

async def check_force_join(client: Client, message: Message) -> bool:
    """
    Check if user has joined required force join chats
    Returns True if all checks passed, False if blocked
    """
    force_chats = await db.get_force_join_chats()
    
    if not force_chats:
        return True
    
    # Owner bypasses force join
    if message.from_user.id == OWNER_ID:
        return True
    
    # Check membership in all force join chats
    for chat in force_chats:
        try:
            member = await client.get_chat_member(chat['chat_id'], message.from_user.id)
            
            # If user is kicked or left, block them
            if member.status in ["left", "kicked"]:
                # Send force join message
                user_name = message.from_user.first_name or "दोस्त"
                chat_title = chat.get('chat_title', 'Required Group')
                chat_username = chat.get('chat_username', '')
                
                force_msg = utils.format_force_join_message(chat_title, user_name)
                keyboard = utils.get_force_join_button(chat_username, chat_title, chat['chat_type'])
                
                # Send branded message
                sent_msg = await message.reply_text(
                    force_msg,
                    reply_markup=keyboard
                )
                
                # Save message ID for later deletion
                await db.save_pending_message(message.from_user.id, sent_msg.id, message.chat.id)
                
                return False
        
        except Exception as e:
            print(f"Error checking membership: {e}")
            continue
    
    # Delete any pending force join messages if user has joined
    pending = await db.get_pending_message(message.from_user.id)
    if pending:
        try:
            await client.delete_messages(pending['chat_id'], pending['message_id'])
            await db.delete_pending_message(message.from_user.id)
        except:
            pass
    
    return True

async def lang_handler(client: Client, message: Message):
    """
    Handle /lang command - let user choose language
    """
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    # Add/update user
    await db.add_or_update_user(
        uid=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Get current language
    current_lang = await db.get_user_language(message.from_user.id)
    
    # Language selection buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇳 हिंदी", callback_data="lang_hindi")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_english")],
        [InlineKeyboardButton("🔄 Hinglish", callback_data="lang_hinglish")]
    ])
    
    lang_text = f"""🌐 **Language Selection / भाषा चुनें**

Current Language: **{current_lang.title()}**

Please select your preferred language:
कृपया अपनी पसंदीदा भाषा चुनें:"""
    
    await message.reply_text(lang_text, reply_markup=keyboard)

async def start_handler(client: Client, message: Message):
    """
    Handle /start command in private chat
    Send welcome message with features and inline buttons
    """
    print(f"✅ START HANDLER CALLED by user {message.from_user.id}")
    
    # Add/update user in database
    await db.add_or_update_user(
        uid=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Check force join
    if not await check_force_join(client, message):
        print(f"⚠️ Force join check failed for user {message.from_user.id}")
        return
    
    # Log usage
    await db.log_usage(message.from_user.id, cmd="/start")
    
    # Get user's language
    user_lang = await db.get_user_language(message.from_user.id)
    
    # Send welcome message
    welcome_text = utils.format_start_message(user_lang)
    buttons = utils.get_start_buttons()
    
    print(f"📤 Sending welcome message to user {message.from_user.id}")
    await message.reply_text(
        welcome_text,
        reply_markup=buttons
    )
    print(f"✅ Welcome message sent successfully!")

async def question_handler(client: Client, message: Message):
    """
    Handle text questions in private chat
    Call API and send short answer with detailed solution button
    """
    # Add/update user
    await db.add_or_update_user(
        uid=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Check force join
    if not await check_force_join(client, message):
        return
    
    # Get user's language
    user_lang = await db.get_user_language(message.from_user.id)
    
    # Validate question length
    if len(message.text) > 2000:
        await message.reply_text(utils.get_message("question_too_long", user_lang))
        return
    
    # Send processing message
    processing_msg = await message.reply_text(utils.get_message("finding_answer", user_lang))
    
    try:
        # Get answer from API
        result = await api_client.get_answer(
            question=message.text,
            uid=message.from_user.id,
            mode="short"
        )
        
        # Delete processing message
        await processing_msg.delete()
        
        if result.get('success'):
            # Format answer
            answer_text = utils.format_answer_message(
                question=message.text,
                answer=result['short_answer'],
                lang=user_lang
            )
            
            # Create solution button
            solution_button = utils.get_solution_button(result['detailed_url'])
            
            # Send answer
            await message.reply_text(
                answer_text,
                reply_markup=solution_button
            )
            
            # Log usage and increment counter
            await db.log_usage(
                uid=message.from_user.id,
                cmd="question",
                qtext=message.text[:200]
            )
            await db.increment_user_questions(message.from_user.id)
        
        else:
            await message.reply_text(utils.get_message("error_occurred", user_lang))
    
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await processing_msg.edit_text(
            f"⏳ Rate limit! {e.value} seconds में फिर से try करें।"
        )
    
    except Exception as e:
        print(f"Error in question handler: {e}")
        await processing_msg.delete()
        await message.reply_text(utils.get_message("error_occurred", user_lang))

async def image_handler(client: Client, message: Message):
    """
    Handle image questions in private chat
    Download image and call API
    """
    # Add/update user
    await db.add_or_update_user(
        uid=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Check force join
    if not await check_force_join(client, message):
        return
    
    # Get user's language
    user_lang = await db.get_user_language(message.from_user.id)
    
    # Send processing message
    processing_msg = await message.reply_text(utils.get_message("processing_image", user_lang))
    
    try:
        # Download image
        file_path = await message.download()
        
        # Get answer from API
        result = await api_client.get_image_answer(file_path, message.from_user.id)
        
        # Delete processing message
        await processing_msg.delete()
        
        if result.get('success'):
            # Format answer
            answer_text = utils.format_answer_message(
                question="Image Question",
                answer=result['short_answer'],
                lang=user_lang
            )
            
            # Create solution button
            solution_button = utils.get_solution_button(result['detailed_url'])
            
            # Send answer
            await message.reply_text(
                answer_text,
                reply_markup=solution_button
            )
            
            # Log usage
            await db.log_usage(
                uid=message.from_user.id,
                cmd="image_question",
                qtext="Image uploaded"
            )
            await db.increment_user_questions(message.from_user.id)
        
        else:
            await message.reply_text(utils.get_message("image_error", user_lang))
    
    except Exception as e:
        print(f"Error in image handler: {e}")
        await processing_msg.delete()
        await message.reply_text(utils.get_message("error_occurred", user_lang))

async def lang_callback_handler(client: Client, callback_query):
    """
    Handle language selection callbacks
    """
    from pyrogram.types import CallbackQuery
    
    data = callback_query.data
    uid = callback_query.from_user.id
    
    # Extract language from callback data
    if data.startswith("lang_"):
        lang = data.replace("lang_", "")
        
        # Update user language
        await db.set_user_language(uid, lang)
        
        # Language confirmation messages
        lang_msgs = {
            "hindi": "✅ भाषा बदल दी गई! अब सभी messages हिंदी में होंगे।",
            "english": "✅ Language changed! All messages will now be in English.",
            "hinglish": "✅ Language change ho gayi! Ab sab messages Hinglish mein honge."
        }
        
        await callback_query.answer(lang_msgs.get(lang, "✅ Language updated!"), show_alert=True)
        
        # Update the message
        await callback_query.message.edit_text(
            f"🌐 {lang_msgs.get(lang, 'Language updated!')}\n\nType /start to see changes."
        )

def register_chat_handlers(app: Client):
    """Register all private chat handlers"""
    from pyrogram.handlers import CallbackQueryHandler
    
    app.add_handler(MessageHandler(lang_handler, filters.command("lang") & filters.private))
    app.add_handler(MessageHandler(start_handler, filters.command("start") & filters.private))
    app.add_handler(MessageHandler(question_handler, filters.text & filters.private & ~filters.command(["start", "lang"])))
    app.add_handler(MessageHandler(image_handler, filters.photo & filters.private))
    app.add_handler(CallbackQueryHandler(lang_callback_handler, filters.regex("^lang_")))
    print("✅ Chat handlers registered")
