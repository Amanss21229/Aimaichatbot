"""
Utility functions for bot
Formatters, buttons, rate-limit helpers
"""

import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import os

# Bot constants
OWNER_USERNAME = "TheGodOfTgBot"
UPDATES_CHANNEL = "aimaibotupdates"

# Global bot username - set by main.py after bot starts
_bot_username = None

def set_bot_username(username: str):
    """Set bot username globally for use in buttons"""
    global _bot_username
    _bot_username = username

def get_start_buttons(bot_username: str = None):
    """
    Get inline keyboard for /start command
    /start कमांड के लिए इनलाइन बटन
    """
    if not bot_username:
        bot_username = _bot_username or os.getenv("BOT_USERNAME", "your_bot")
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ मुझे अपने ग्रुप में जोड़ें", 
                             url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("👤 Bot Owner से मिलें", 
                             url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("📢 Bot Updates के लिए Join करें", 
                             url=f"https://t.me/{UPDATES_CHANNEL}")]
    ])

def get_solution_button(url: str):
    """
    Get inline keyboard with 'See detailed solution' button
    विस्तृत समाधान के लिए बटन
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 विस्तृत समाधान देखें | See Detailed Solution", url=url)]
    ])

def get_force_join_button(chat_username: str, chat_title: str, chat_type: str, bot_username: str = None):
    """
    Get force join button for gating
    Force join के लिए बटन
    """
    # Create join link
    if chat_username:
        if chat_type == "channel":
            url = f"https://t.me/{chat_username}"
        else:
            url = f"https://t.me/{chat_username}"
    else:
        # If no username, can't create direct link
        # Bot should be able to export invite link
        if not bot_username:
            bot_username = _bot_username or os.getenv("BOT_USERNAME", "your_bot")
        url = f"https://t.me/{bot_username}"
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ {chat_title} Join करें", url=url)]
    ])

# Language messages
MESSAGES = {
    "hindi": {
        "start": """🎓 **NEET AI Bot में आपका स्वागत है!**

मैं आपके NEET/JEE के सवालों का जवाब दे सकता हूं। 

**📚 Features:**
• किसी भी Physics, Chemistry, Biology या Math के सवाल का तुरंत जवाब
• Short answer + विस्तृत समाधान की वेबसाइट लिंक
• Group में भी काम करता हूं - किसी message को reply करके /sol टाइप करें
• 24/7 Available

**💡 कैसे इस्तेमाल करें:**
1️⃣ बस अपना सवाल टाइप करें
2️⃣ या सवाल की फोटो भेजें
3️⃣ मैं तुरंत short answer दूंगा + detailed solution का link

Language बदलने के लिए /lang टाइप करें
नीचे के बटन से मुझे अपने ग्रुप में add करें! 👇

— NEET AI Bot ✨""",
        "question_too_long": "❌ सवाल बहुत लंबा है! कृपया 2000 characters से कम में लिखें।",
        "finding_answer": "🔍 जवाब ढूंढ रहा हूं...",
        "error_occurred": "❌ क्षमा करें, कुछ गड़बड़ हुई। कृपया फिर से try करें।",
        "processing_image": "📸 इमेज प्रोसेस कर रहा हूं...",
        "image_error": "❌ इमेज प्रोसेस नहीं हो सकी। Text में सवाल भेजें।",
        "question": "❓ सवाल:",
        "answer": "✅ जवाब:"
    },
    "english": {
        "start": """🎓 **Welcome to NEET AI Bot!**

I can answer your NEET/JEE questions instantly.

**📚 Features:**
• Instant answers to Physics, Chemistry, Biology, and Math questions
• Short answer + detailed solution website link
• Works in groups too - reply to any message with /sol
• 24/7 Available

**💡 How to use:**
1️⃣ Just type your question
2️⃣ Or send a photo of your question
3️⃣ I'll instantly give you a short answer + detailed solution link

Type /lang to change language
Add me to your group using the button below! 👇

— NEET AI Bot ✨""",
        "question_too_long": "❌ Question is too long! Please keep it under 2000 characters.",
        "finding_answer": "🔍 Finding answer...",
        "error_occurred": "❌ Sorry, something went wrong. Please try again.",
        "processing_image": "📸 Processing image...",
        "image_error": "❌ Could not process image. Please send question as text.",
        "question": "❓ Question:",
        "answer": "✅ Answer:"
    },
    "hinglish": {
        "start": """🎓 **NEET AI Bot mein aapka swagat hai!**

Main aapke NEET/JEE ke sawaalon ka jawab de sakta hoon.

**📚 Features:**
• Kisi bhi Physics, Chemistry, Biology ya Math ke sawal ka turant jawab
• Short answer + detailed solution ki website link
• Group mein bhi kaam karta hoon - kisi message ko reply karke /sol type karein
• 24/7 Available

**💡 Kaise use karein:**
1️⃣ Bas apna sawal type karein
2️⃣ Ya sawal ki photo bhejein
3️⃣ Main turant short answer dunga + detailed solution ka link

Language change karne ke liye /lang type karein
Neeche ke button se mujhe apne group mein add karein! 👇

— NEET AI Bot ✨""",
        "question_too_long": "❌ Sawal bahut lamba hai! Kripya 2000 characters se kam mein likhein.",
        "finding_answer": "🔍 Jawab dhoond raha hoon...",
        "error_occurred": "❌ Sorry, kuch gadbad hui. Please fir se try karein.",
        "processing_image": "📸 Image process kar raha hoon...",
        "image_error": "❌ Image process nahi ho saki. Text mein sawal bhejein.",
        "question": "❓ Sawal:",
        "answer": "✅ Jawab:"
    }
}

def format_start_message(lang="hindi"):
    """
    Format welcome message for /start command
    """
    return MESSAGES.get(lang, MESSAGES["hindi"])["start"]

def format_answer_message(question: str, answer: str, lang="hindi"):
    """
    Format answer message with branding
    """
    # Truncate question if too long
    q_display = question[:100] + "..." if len(question) > 100 else question
    
    q_label = MESSAGES.get(lang, MESSAGES["hindi"])["question"]
    a_label = MESSAGES.get(lang, MESSAGES["hindi"])["answer"]
    
    return f"""**{q_label}** {q_display}

**{a_label}**
{answer}

— NEET AI Bot ✨"""

def get_message(key: str, lang="hindi") -> str:
    """
    Get a message in specified language
    """
    return MESSAGES.get(lang, MESSAGES["hindi"]).get(key, "")

def format_stats_message(stats: dict, uptime: str):
    """
    Format stats message for /stats command
    """
    return f"""📊 **Bot Statistics**

👥 Total Users: {stats.get('total_users', 0)}
👥 Total Groups: {stats.get('total_groups', 0)}
📝 Total Queries: {stats.get('total_queries', 0)}
🔥 Daily Active Users: {stats.get('daily_active_users', 0)}
⏱️ Uptime: {uptime}

— NEET AI Bot"""

def format_admin_list(admins: list, user_details: dict):
    """
    Format admin list message
    """
    if not admins:
        return "❌ कोई admin नहीं है।"
    
    msg = "👥 **Bot Admins:**\n\n"
    for admin in admins:
        uid = admin['uid']
        details = user_details.get(uid, {})
        name = details.get('first_name', 'Unknown')
        username = details.get('username', 'No username')
        msg += f"• {name} (@{username}) - ID: {uid}\n"
    
    return msg

def format_group_list(groups: list):
    """
    Format group list message
    """
    if not groups:
        return "❌ Bot किसी group में नहीं है।"
    
    msg = "📋 **Bot Groups:**\n\n"
    for idx, group in enumerate(groups, 1):
        title = group.get('title', 'Unknown')
        username = group.get('username', 'No username')
        gid = group.get('gid')
        chat_on = "🟢 Chat ON" if group.get('chat_on') else "🔴 Chat OFF"
        
        if username:
            msg += f"{idx}. **{title}** (@{username}) - {chat_on}\n"
        else:
            msg += f"{idx}. **{title}** (ID: {gid}) - {chat_on}\n"
    
    return msg

def format_force_join_message(chat_title: str, user_name: str):
    """
    Format force join branded message in Hindi
    """
    return f"""🔒 **रुकिए {user_name}!**

Bot का इस्तेमाल करने के लिए आपको हमारे channel/group में join करना होगा।

**📢 Group:** {chat_title}

नीचे के बटन से join करें और फिर वापस आएं! 👇

— NEET AI Bot"""

async def rate_limit_handler(func, *args, delay: float = 0.35, **kwargs):
    """
    Handle rate limiting with delay
    Rate limit को handle करने के लिए delay के साथ
    """
    try:
        result = await func(*args, **kwargs)
        await asyncio.sleep(delay)
        return result, None
    except Exception as e:
        return None, str(e)

def format_broadcast_stats(total: int, success: int, failed: int):
    """
    Format broadcast statistics message
    """
    return f"""📢 **Broadcast Complete!**

✅ Sent: {success}/{total}
❌ Failed: {failed}

— NEET AI Bot"""

def get_current_time():
    """Get current timestamp"""
    return datetime.now()

def calculate_uptime(start_time: datetime):
    """Calculate bot uptime"""
    delta = datetime.now() - start_time
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
