# NEET/JEE AI Telegram Bot

## Overview
Full-featured Telegram Bot for NEET/JEE question-answering with group and personal chat support, admin panel, broadcasting, and force-join gating functionality.

## Project Status
✅ **Complete and Operational**
- Bot is running successfully on Replit
- Using Mock API for testing (can be replaced with real API)
- All features implemented and tested

## Recent Changes (October 2025)
- Initial project setup with complete codebase
- Database schema created with SQLite/aiosqlite
- Personal and group chat handlers implemented
- Admin command system with broadcast functionality
- Force-join gating system implemented
- Mock API module for testing without external dependencies

## Project Architecture

### Core Files
- **main.py** - Bot initialization, Pyrogram client setup, handler registration
- **db.py** - SQLite database operations (async with aiosqlite)
- **apiclient.py** - Website API client with retry logic and fallback to mock
- **mock_api.py** - Mock API for testing without real website integration
- **utils.py** - Utility functions, formatters, button creators
- **handlers_chat.py** - Personal chat handlers (/start, questions, images)
- **handlers_group.py** - Group chat handlers (/sol, chat on/off)
- **admin_commands.py** - Admin commands (broadcast, promote, stats, etc.)

### Database Schema
1. **users** - All bot users with stats
2. **groups** - Groups where bot is added with chat_on status
3. **admins** - Bot admins (promoted by owner)
4. **usage_logs** - Command and query usage tracking
5. **force_join** - Required groups/channels for bot access
6. **pending_prompt_messages** - Force join prompt messages to delete

### Technology Stack
- **Python 3.11** - Runtime
- **Pyrogram 2.0** - Telegram Bot framework
- **TgCrypto** - Encryption for Pyrogram
- **aiohttp** - Async HTTP client
- **aiosqlite** - Async SQLite database
- **python-dotenv** - Environment variables

## Features Implemented

### Personal Chat Features
- `/start` - Welcome message with inline buttons (Add to group, Meet owner, Join updates)
- Text questions - Get short answer + detailed solution link
- Image questions - Process image and provide answer
- Force-join gating with branded Hindi messages

### Group Chat Features
- `/sol` - Reply-based quick answer with website link
- `/chaton` - Enable free chat mode (group admins only)
- `/chatoff` - Disable free chat mode (group admins only)
- Auto-detection of questions when chat is on

### Admin Commands (Owner + Bot Admins)
- `/broadcast` - Broadcast to all users and groups
- `/promote <uid>` - Promote user to bot admin
- `/remove <uid>` - Remove bot admin
- `/adminlist` - List all bot admins
- `/grouplist` - List all groups
- `/stats` - Bot statistics
- `/refresh` - Refresh bot and API client
- `/fjoin <chat>` - Add force join requirement
- `/removefjoin <chat>` - Remove force join
- `/dumpdb` - Export database (Owner only)

## Environment Variables

### Required (Already Set)
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `OWNER_ID` - Owner's Telegram user ID

### Optional
- `WEBSITE_API_URL` - Real API endpoint (uses mock if not set)
- `WEBSITE_API_KEY` - API authentication key
- `API_ID` - Custom Pyrogram API ID (has default)
- `API_HASH` - Custom Pyrogram API Hash (has default)

## Bot Information
- **Bot Username**: @AimAiChatBot
- **Bot Name**: AimAi
- **Status**: Running
- **API Mode**: Mock (for testing)

## How to Use

### For Users
1. Start bot in personal chat - get welcome message
2. Ask any NEET/JEE question - get short answer + detailed link
3. Send question image - bot will process and answer
4. Add to groups and use /sol command on any message

### For Admins
1. Use `/promote <user_id>` to add admins
2. Use `/broadcast` to send messages to all users
3. Use `/fjoin <group_link>` to require users to join specific groups
4. Use `/stats` to see bot statistics

### For Group Admins
1. Use `/chaton` to enable free chat
2. Use `/chatoff` to disable free chat (only /sol works)
3. Use `/sol` as reply to any question message

## API Integration

### Current: Mock API
Bot is using mock API module that returns realistic NEET/JEE answers for testing.

### To Enable Real API
1. Set `WEBSITE_API_URL` in Replit Secrets
2. Optionally set `WEBSITE_API_KEY` if required
3. Restart bot - it will automatically use real API

### API Format Expected
```bash
# POST Request
curl -X POST "${WEBSITE_API_URL}" \
  -H "Authorization: Bearer ${WEBSITE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is photosynthesis?", "uid": 123456, "mode": "short"}'

# Response
{
  "success": true,
  "short_answer": "Answer text here...",
  "detailed_url": "https://website.com/solution/123",
  "solution_id": "bio_001"
}
```

## Code Quality
- Fully typed with proper error handling
- Rate-limit handling with FloodWait exceptions
- Retry logic with exponential backoff
- Bilingual messages (Hindi primary, English fallback)
- Inline comments in both languages
- Secure secret management

## Future Enhancements (Not Implemented)
- OCR support for image questions
- Multi-language support beyond Hindi/English
- Webhook mode for better performance
- Question history and favorites
- Analytics dashboard
