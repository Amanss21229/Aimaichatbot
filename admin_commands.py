"""
Admin commands for bot owners and promoted admins
Broadcast, promote, remove, stats, admin list, group list
"""

import os
import asyncio
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid
import db
import utils
from datetime import datetime

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

async def is_authorized_admin(user_id: int) -> bool:
    """Check if user is owner or bot admin"""
    if user_id == OWNER_ID:
        return True
    return await db.is_bot_admin(user_id)

async def broadcast_handler(client: Client, message: Message):
    """
    Broadcast message to all users and groups
    Must be used as reply to a message
    """
    # Check authorization
    if not await is_authorized_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized. Only bot admins can broadcast.")
        return
    
    # Check if it's a reply
    if not message.reply_to_message:
        await message.reply_text(
            "⚠️ `/broadcast` को किसी message के reply में use करें!\n\n"
            "Please reply to a message to broadcast it."
        )
        return
    
    broadcast_msg = message.reply_to_message
    
    # Get all users and groups
    users = await db.get_all_users()
    groups = await db.get_all_groups()
    
    total = len(users) + len(groups)
    success = 0
    failed = 0
    
    # Send status message
    status_msg = await message.reply_text(
        f"📢 **Broadcasting...**\n\n"
        f"Total targets: {total}\n"
        f"Progress: 0/{total}"
    )
    
    # Broadcast to users
    for idx, user in enumerate(users):
        try:
            await broadcast_msg.copy(user['uid'])
            success += 1
            await asyncio.sleep(0.35)  # Rate limit delay
            
            # Update status every 10 messages
            if (idx + 1) % 10 == 0:
                await status_msg.edit_text(
                    f"📢 **Broadcasting...**\n\n"
                    f"Total targets: {total}\n"
                    f"Progress: {idx + 1}/{total}\n"
                    f"✅ Success: {success} | ❌ Failed: {failed}"
                )
        
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await broadcast_msg.copy(user['uid'])
                success += 1
            except:
                failed += 1
        
        except (UserIsBlocked, PeerIdInvalid):
            failed += 1
        
        except Exception as e:
            print(f"Broadcast error to user {user['uid']}: {e}")
            failed += 1
    
    # Broadcast to groups
    for idx, group in enumerate(groups):
        try:
            await broadcast_msg.copy(group['gid'])
            success += 1
            await asyncio.sleep(0.35)
            
            # Update status
            if (idx + 1) % 10 == 0:
                await status_msg.edit_text(
                    f"📢 **Broadcasting...**\n\n"
                    f"Total targets: {total}\n"
                    f"Progress: {len(users) + idx + 1}/{total}\n"
                    f"✅ Success: {success} | ❌ Failed: {failed}"
                )
        
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await broadcast_msg.copy(group['gid'])
                success += 1
            except:
                failed += 1
        
        except Exception as e:
            print(f"Broadcast error to group {group['gid']}: {e}")
            failed += 1
    
    # Final status
    final_text = utils.format_broadcast_stats(total, success, failed)
    await status_msg.edit_text(final_text)
    
    # Log
    await db.log_usage(message.from_user.id, cmd="/broadcast")

async def promote_handler(client: Client, message: Message):
    """
    Promote user to bot admin
    Usage: /promote <user_id>
    """
    # Check authorization
    if not await is_authorized_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized. Only bot admins can promote.")
        return
    
    # Parse user ID
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(
            "⚠️ Usage: `/promote <user_id>`\n\n"
            "Example: `/promote 123456789`"
        )
        return
    
    try:
        user_id = int(args[1])
        
        # Add to admins
        await db.add_admin(user_id, message.from_user.id)
        
        await message.reply_text(
            f"✅ User `{user_id}` promoted to bot admin!"
        )
        
        # Notify the promoted user
        try:
            await client.send_message(
                user_id,
                "🎉 **Congratulations!**\n\n"
                "आपको bot admin बना दिया गया है!\n"
                "You have been promoted to bot admin!"
            )
        except:
            pass
        
        await db.log_usage(message.from_user.id, cmd="/promote")
    
    except ValueError:
        await message.reply_text("❌ Invalid user ID. Must be a number.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

async def remove_handler(client: Client, message: Message):
    """
    Remove user from bot admins
    Usage: /remove <user_id>
    """
    # Check authorization
    if not await is_authorized_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized. Only bot admins can remove.")
        return
    
    # Parse user ID
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(
            "⚠️ Usage: `/remove <user_id>`\n\n"
            "Example: `/remove 123456789`"
        )
        return
    
    try:
        user_id = int(args[1])
        
        # Cannot remove owner
        if user_id == OWNER_ID:
            await message.reply_text("❌ Cannot remove the owner!")
            return
        
        # Remove from admins
        await db.remove_admin(user_id)
        
        await message.reply_text(
            f"✅ User `{user_id}` removed from bot admins."
        )
        
        await db.log_usage(message.from_user.id, cmd="/remove")
    
    except ValueError:
        await message.reply_text("❌ Invalid user ID. Must be a number.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

async def adminlist_handler(client: Client, message: Message):
    """Show list of all bot admins"""
    # Check authorization
    if not await is_authorized_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized.")
        return
    
    admins = await db.get_all_admins()
    
    # Get user details for each admin
    user_details = {}
    for admin in admins:
        try:
            user = await client.get_users(admin['uid'])
            user_details[admin['uid']] = {
                'first_name': user.first_name,
                'username': user.username or 'No username'
            }
        except:
            user_details[admin['uid']] = {
                'first_name': 'Unknown',
                'username': 'No username'
            }
    
    # Format list
    admin_list_text = utils.format_admin_list(admins, user_details)
    
    await message.reply_text(admin_list_text)
    await db.log_usage(message.from_user.id, cmd="/adminlist")

async def grouplist_handler(client: Client, message: Message):
    """Show list of all groups where bot is added"""
    # Check authorization
    if not await is_authorized_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized.")
        return
    
    groups = await db.get_all_groups()
    
    # Format list
    group_list_text = utils.format_group_list(groups)
    
    await message.reply_text(group_list_text)
    await db.log_usage(message.from_user.id, cmd="/grouplist")

async def stats_handler(client: Client, message: Message):
    """Show bot statistics"""
    # Check authorization (allow in groups for group admins too)
    if message.chat.type == "private":
        if not await is_authorized_admin(message.from_user.id):
            await message.reply_text("❌ Unauthorized.")
            return
    
    # Get stats
    stats = await db.get_stats()
    
    # Calculate uptime (from bot start time, passed from main)
    uptime = utils.calculate_uptime(message.from_user.id)  # This needs to be fixed
    
    # Format stats
    stats_text = utils.format_stats_message(stats, "Runtime")
    
    await message.reply_text(stats_text)
    await db.log_usage(message.from_user.id, message.chat.id if message.chat.type != "private" else None, "/stats")

async def refresh_handler(client: Client, message: Message):
    """Refresh bot (re-init API client and reload config)"""
    # Check authorization
    is_admin = await is_authorized_admin(message.from_user.id)
    
    if message.chat.type in ["group", "supergroup"]:
        # In groups, check if user is group admin
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ["creator", "administrator"] and not is_admin:
                await message.reply_text("❌ Only admins can use this command.")
                return
        except:
            pass
    elif not is_admin:
        await message.reply_text("❌ Unauthorized.")
        return
    
    # Refresh API client
    from apiclient import api_client
    await api_client.close_session()
    await api_client.init_session()
    
    await message.reply_text(
        "✅ **Bot Refreshed!**\n\n"
        "API client restarted और config reload हो गया।\n"
        "API client restarted and config reloaded."
    )
    
    await db.log_usage(message.from_user.id, message.chat.id if message.chat.type != "private" else None, "/refresh")

async def fjoin_handler(client: Client, message: Message):
    """
    Add force join chat
    Usage: /fjoin <chat_username_or_id>
    """
    # Check authorization
    if not await is_authorized_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized. Only bot admins can add force join.")
        return
    
    # Parse chat
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(
            "⚠️ Usage: `/fjoin <chat_username or chat_id>`\n\n"
            "Example: `/fjoin @channelname` or `/fjoin -100123456789`"
        )
        return
    
    chat_input = args[1]
    
    try:
        # Get chat info
        chat = await client.get_chat(chat_input)
        
        # Add to force join
        await db.add_force_join(
            chat_id=chat.id,
            chat_type=chat.type,
            chat_title=chat.title or "Unknown",
            chat_username=chat.username or "",
            added_by=message.from_user.id
        )
        
        await message.reply_text(
            f"✅ **Force Join Added!**\n\n"
            f"Chat: {chat.title}\n"
            f"Type: {chat.type}\n"
            f"Username: @{chat.username if chat.username else 'None'}\n\n"
            "अब सभी users को इस chat में join करना होगा।"
        )
        
        await db.log_usage(message.from_user.id, cmd="/fjoin")
    
    except Exception as e:
        await message.reply_text(
            f"❌ Error: {str(e)}\n\n"
            "Make sure:\n"
            "1. Bot is member of that chat\n"
            "2. Chat username/ID is correct"
        )

async def removefjoin_handler(client: Client, message: Message):
    """
    Remove force join chat
    Usage: /removefjoin <chat_id>
    """
    # Check authorization
    if not await is_authorized_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized.")
        return
    
    # Parse chat ID
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(
            "⚠️ Usage: `/removefjoin <chat_id>`\n\n"
            "Example: `/removefjoin -100123456789`"
        )
        return
    
    try:
        chat_id = int(args[1]) if args[1].lstrip('-').isdigit() else 0
        
        if chat_id == 0:
            # Try to get chat by username
            chat = await client.get_chat(args[1])
            chat_id = chat.id
        
        # Remove from force join
        await db.remove_force_join(chat_id)
        
        await message.reply_text(
            f"✅ Force join removed for chat ID: `{chat_id}`"
        )
        
        await db.log_usage(message.from_user.id, cmd="/removefjoin")
    
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

async def dumpdb_handler(client: Client, message: Message):
    """
    Dump database file (OWNER only)
    """
    # Only owner can dump database
    if message.from_user.id != OWNER_ID:
        await message.reply_text("❌ Unauthorized. Owner only.")
        return
    
    try:
        # Send database file
        await message.reply_document(
            document="bot_data.db",
            caption="📊 Database backup\n\n— NEET AI Bot"
        )
        
        await db.log_usage(message.from_user.id, cmd="/dumpdb")
    
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

def register_admin_handlers(app: Client):
    """Register all admin command handlers"""
    app.add_handler(MessageHandler(broadcast_handler, filters.command("broadcast")))
    app.add_handler(MessageHandler(promote_handler, filters.command("promote")))
    app.add_handler(MessageHandler(remove_handler, filters.command("remove")))
    app.add_handler(MessageHandler(adminlist_handler, filters.command("adminlist")))
    app.add_handler(MessageHandler(grouplist_handler, filters.command("grouplist")))
    app.add_handler(MessageHandler(stats_handler, filters.command("stats")))
    app.add_handler(MessageHandler(refresh_handler, filters.command("refresh")))
    app.add_handler(MessageHandler(fjoin_handler, filters.command("fjoin")))
    app.add_handler(MessageHandler(removefjoin_handler, filters.command("removefjoin")))
    app.add_handler(MessageHandler(dumpdb_handler, filters.command("dumpdb")))
