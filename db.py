"""
Database module for Telegram Bot
SQLite database with aiosqlite for async operations
Tables: users, groups, admins, usage_logs, force_join, pending_prompt_messages
"""

import aiosqlite
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = "bot_data.db"

async def init_db():
    """
    Initialize database and create all required tables
    डेटाबेस शुरू करें और सभी टेबल बनाएं
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Users table - store all bot users
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                last_seen TIMESTAMP,
                total_questions INTEGER DEFAULT 0,
                joined_at TIMESTAMP,
                language TEXT DEFAULT 'hindi'
            )
        """)
        
        # Groups table - store all groups where bot is added
        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                gid INTEGER PRIMARY KEY,
                title TEXT,
                username TEXT,
                added_at TIMESTAMP,
                chat_on BOOLEAN DEFAULT 1
            )
        """)
        
        # Admins table - bot admins (not group admins)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                uid INTEGER PRIMARY KEY,
                promoted_by INTEGER,
                promoted_at TIMESTAMP
            )
        """)
        
        # Usage logs - track all commands and queries
        await db.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER,
                gid INTEGER,
                cmd TEXT,
                qtext TEXT,
                ts TIMESTAMP
            )
        """)
        
        # Force join - channels/groups users must join
        await db.execute("""
            CREATE TABLE IF NOT EXISTS force_join (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                chat_type TEXT,
                chat_title TEXT,
                chat_username TEXT,
                added_by INTEGER,
                added_at TIMESTAMP
            )
        """)
        
        # Pending prompt messages - store message IDs for force join prompts
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pending_prompt_messages (
                uid INTEGER PRIMARY KEY,
                message_id INTEGER,
                chat_id INTEGER
            )
        """)
        
        await db.commit()
        
        # Migration: Add language column if it doesn't exist
        try:
            await db.execute("SELECT language FROM users LIMIT 1")
        except:
            await db.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'hindi'")
            await db.commit()
            print("🔄 Added language column to existing users")
        
        print("✅ Database initialized successfully")

# ==================== USER OPERATIONS ====================

async def add_or_update_user(uid: int, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None):
    """Add new user or update existing user's last seen"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (uid, username, first_name, last_name, last_seen, joined_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(uid) DO UPDATE SET
                username = ?,
                first_name = ?,
                last_name = ?,
                last_seen = ?
        """, (uid, username, first_name, last_name, datetime.now(), datetime.now(),
              username, first_name, last_name, datetime.now()))
        await db.commit()

async def increment_user_questions(uid: int):
    """Increment user's total questions count"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET total_questions = total_questions + 1
            WHERE uid = ?
        """, (uid,))
        await db.commit()

async def set_user_language(uid: int, language: str):
    """Set user's preferred language"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET language = ?
            WHERE uid = ?
        """, (language, uid))
        await db.commit()

async def get_user_language(uid: int) -> str:
    """Get user's preferred language, default to hindi"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT language FROM users WHERE uid = ?", (uid,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row and row[0] else 'hindi'

async def get_all_users() -> List[Dict]:
    """Get all users for broadcasting"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ==================== GROUP OPERATIONS ====================

async def add_group(gid: int, title: str, username: Optional[str] = None):
    """Add new group to database"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO groups (gid, title, username, added_at, chat_on)
            VALUES (?, ?, ?, ?, 1)
        """, (gid, title, username, datetime.now()))
        await db.commit()

async def set_chat_status(gid: int, status: bool):
    """Set chat on/off status for a group"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE groups SET chat_on = ?
            WHERE gid = ?
        """, (1 if status else 0, gid))
        await db.commit()

async def get_chat_status(gid: int) -> bool:
    """Get chat on/off status for a group"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_on FROM groups WHERE gid = ?", (gid,)) as cursor:
            row = await cursor.fetchone()
            return bool(row[0]) if row else True

async def get_all_groups() -> List[Dict]:
    """Get all groups for broadcasting and listing"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM groups") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ==================== ADMIN OPERATIONS ====================

async def add_admin(uid: int, promoted_by: int):
    """Add new bot admin"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO admins (uid, promoted_by, promoted_at)
            VALUES (?, ?, ?)
        """, (uid, promoted_by, datetime.now()))
        await db.commit()

async def remove_admin(uid: int):
    """Remove bot admin"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM admins WHERE uid = ?", (uid,))
        await db.commit()

async def is_bot_admin(uid: int) -> bool:
    """Check if user is bot admin"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT uid FROM admins WHERE uid = ?", (uid,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def get_all_admins() -> List[Dict]:
    """Get all bot admins"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM admins") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ==================== USAGE LOGS ====================

async def log_usage(uid: int, gid: Optional[int] = None, cmd: Optional[str] = None, qtext: Optional[str] = None):
    """Log command or question usage"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO usage_logs (uid, gid, cmd, qtext, ts)
            VALUES (?, ?, ?, ?, ?)
        """, (uid, gid, cmd, qtext, datetime.now()))
        await db.commit()

async def get_stats() -> Dict[str, Any]:
    """Get bot statistics"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Total users
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            total_users = row[0] if row else 0
        
        # Total groups
        async with db.execute("SELECT COUNT(*) FROM groups") as cursor:
            row = await cursor.fetchone()
            total_groups = row[0] if row else 0
        
        # Total queries
        async with db.execute("SELECT COUNT(*) FROM usage_logs") as cursor:
            row = await cursor.fetchone()
            total_queries = row[0] if row else 0
        
        # Daily active users (last 24 hours)
        async with db.execute("""
            SELECT COUNT(DISTINCT uid) FROM usage_logs
            WHERE ts >= datetime('now', '-1 day')
        """) as cursor:
            row = await cursor.fetchone()
            daily_active = row[0] if row else 0
        
        return {
            "total_users": total_users,
            "total_groups": total_groups,
            "total_queries": total_queries,
            "daily_active_users": daily_active
        }

# ==================== FORCE JOIN ====================

async def add_force_join(chat_id: int, chat_type: str, chat_title: str, chat_username: str, added_by: int):
    """Add force join chat"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO force_join (chat_id, chat_type, chat_title, chat_username, added_by, added_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_id, chat_type, chat_title, chat_username, added_by, datetime.now()))
        await db.commit()

async def remove_force_join(chat_id: int):
    """Remove force join chat"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM force_join WHERE chat_id = ?", (chat_id,))
        await db.commit()

async def get_force_join_chats() -> List[Dict]:
    """Get all force join chats"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM force_join") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ==================== PENDING MESSAGES ====================

async def save_pending_message(uid: int, message_id: int, chat_id: int):
    """Save pending force join prompt message"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO pending_prompt_messages (uid, message_id, chat_id)
            VALUES (?, ?, ?)
        """, (uid, message_id, chat_id))
        await db.commit()

async def get_pending_message(uid: int) -> Optional[Dict]:
    """Get pending message for user"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM pending_prompt_messages WHERE uid = ?
        """, (uid,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def delete_pending_message(uid: int):
    """Delete pending message after user joins"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM pending_prompt_messages WHERE uid = ?", (uid,))
        await db.commit()
