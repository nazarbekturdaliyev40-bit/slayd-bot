import aiosqlite
import os
import logging
import config

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "bot_database.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                free_limit INTEGER DEFAULT 2,
                paid_balance INTEGER DEFAULT 0,
                total_generated INTEGER DEFAULT 0,
                referrer_id INTEGER DEFAULT NULL,
                invited_count INTEGER DEFAULT 0,
                is_unlimited BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                topic TEXT,
                file_name TEXT,
                file_id TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                file_type TEXT DEFAULT 'pptx',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_user_files_tid ON user_files (telegram_id)")
        await db.commit()

        # Migrations for existing tables
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = [row[1] for row in await cursor.fetchall()]

        if "referrer_id" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN referrer_id INTEGER DEFAULT NULL")
            await db.commit()

        if "invited_count" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN invited_count INTEGER DEFAULT 0")
            await db.commit()

        if "is_unlimited" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN is_unlimited BOOLEAN DEFAULT 0")
            await db.commit()

        if "subscription_until" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN subscription_until TIMESTAMP DEFAULT NULL")
            await db.commit()

        if "language" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'uz'")
            await db.commit()

        # Nazarbek akkauntlarini doimiy cheksiz (bez limit) qilib sozlash
        for uid in config.UNLIMITED_USERS:
            await db.execute("UPDATE users SET is_unlimited = 1 WHERE telegram_id = ?", (uid,))
        await db.commit()

async def set_user_language(telegram_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (lang, telegram_id))
        await db.commit()

async def get_user_language(telegram_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT language FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                return row[0]
            return "uz"

def is_subscription_active(user: dict) -> bool:
    if not user:
        return False
    sub_until = user.get("subscription_until")
    if not sub_until:
        return False
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(sub_until)
        return dt > datetime.now()
    except Exception:
        return False

async def get_or_create_user(telegram_id: int, username: str = "", full_name: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
            if user:
                if username or full_name:
                    await db.execute(
                        "UPDATE users SET username = COALESCE(NULLIF(?, ''), username), full_name = COALESCE(NULLIF(?, ''), full_name) WHERE telegram_id = ?",
                        (username or "", full_name or "", telegram_id)
                    )
                    await db.commit()
                return dict(user)

        is_unlimited = 1 if config.is_unlimited(telegram_id) else 0

        # Create new user with 2 free limits
        await db.execute("""
            INSERT OR IGNORE INTO users (telegram_id, username, full_name, free_limit, paid_balance, total_generated, invited_count, is_unlimited)
            VALUES (?, ?, ?, 2, 0, 0, 0, ?)
        """, (telegram_id, username or "", full_name or "", is_unlimited))
        await db.commit()

        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
            return dict(user) if user else None

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
            return dict(user) if user else None

async def has_limit(telegram_id: int) -> bool:
    if config.is_unlimited(telegram_id):
        return True
    user = await get_user(telegram_id)
    if not user:
        return False
    if user.get("is_unlimited") or is_subscription_active(user):
        return True
    return (user["free_limit"] + user["paid_balance"]) > 0

async def consume_limit(telegram_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                return {"success": False, "free_limit": 0, "paid_balance": 0, "is_unlimited": False, "is_subscribed": False}

            total_generated = user["total_generated"] + 1
            user_dict = dict(user)
            is_sub = is_subscription_active(user_dict)
            is_unlimited = bool(user["is_unlimited"]) or config.is_unlimited(telegram_id) or is_sub

            # Agar cheksiz yoki obunasi bo'lsa, limit kamaytirilmaydi, faqat generatsiya soni oshadi
            if is_unlimited:
                await db.execute("""
                    UPDATE users
                    SET total_generated = ?
                    WHERE telegram_id = ?
                """, (total_generated, telegram_id))
                await db.commit()
                return {
                    "success": True,
                    "free_limit": user["free_limit"],
                    "paid_balance": user["paid_balance"],
                    "total_generated": total_generated,
                    "is_unlimited": bool(user["is_unlimited"]) or config.is_unlimited(telegram_id),
                    "is_subscribed": is_sub,
                    "subscription_until": user_dict.get("subscription_until")
                }

            free_limit = user["free_limit"]
            paid_balance = user["paid_balance"]

            if free_limit > 0:
                free_limit -= 1
            elif paid_balance > 0:
                paid_balance -= 1
            else:
                return {"success": False, "free_limit": 0, "paid_balance": 0, "is_unlimited": False, "is_subscribed": False}

            await db.execute("""
                UPDATE users
                SET free_limit = ?, paid_balance = ?, total_generated = ?
                WHERE telegram_id = ?
            """, (free_limit, paid_balance, total_generated, telegram_id))
            await db.commit()

            return {
                "success": True,
                "free_limit": free_limit,
                "paid_balance": paid_balance,
                "total_generated": total_generated,
                "is_unlimited": False,
                "is_subscribed": False
            }
use_limit = consume_limit

async def activate_subscription(telegram_id: int, days: int = 30) -> dict:
    from datetime import datetime, timedelta
    user = await get_user(telegram_id)
    if not user:
        return {"success": False, "expires_at": None}
    
    now = datetime.now()
    current_sub = user.get("subscription_until")
    if current_sub:
        try:
            cur_dt = datetime.fromisoformat(current_sub)
            if cur_dt > now:
                new_dt = cur_dt + timedelta(days=days)
            else:
                new_dt = now + timedelta(days=days)
        except Exception:
            new_dt = now + timedelta(days=days)
    else:
        new_dt = now + timedelta(days=days)

    new_sub_str = new_dt.strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET subscription_until = ? WHERE telegram_id = ?", (new_sub_str, telegram_id))
        await db.commit()
    return {"success": True, "expires_at": new_sub_str}

async def add_paid_limit(telegram_id: int, amount: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT telegram_id, paid_balance FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                return False
            new_balance = user[1] + amount
            await db.execute("UPDATE users SET paid_balance = ? WHERE telegram_id = ?", (new_balance, telegram_id))
            await db.commit()
            return True

async def set_unlimited_user(telegram_id: int, status: bool = True) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            await db.execute(
                "INSERT INTO users (telegram_id, free_limit, paid_balance, is_unlimited) VALUES (?, 0, 0, ?)",
                (telegram_id, 1 if status else 0)
            )
        else:
            await db.execute("UPDATE users SET is_unlimited = ? WHERE telegram_id = ?", (1 if status else 0, telegram_id))
        await db.commit()

    if status:
        if telegram_id not in config.UNLIMITED_USERS:
            config.UNLIMITED_USERS.append(telegram_id)
    else:
        if telegram_id in config.UNLIMITED_USERS and telegram_id not in [8597458619, 6792644733]:
            config.UNLIMITED_USERS.remove(telegram_id)
    return True

async def process_referral(new_telegram_id: int, referrer_id: int) -> dict:
    if not referrer_id or new_telegram_id == referrer_id:
        return {"success": False, "reward_given": False, "new_invited_count": 0}

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Referrer bormi?
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (referrer_id,)) as cur:
            referrer = await cur.fetchone()
            if not referrer:
                return {"success": False, "reward_given": False, "new_invited_count": 0}

        # Ushbu foydalanuvchi oldin taklif qilinganmi?
        async with db.execute("SELECT * FROM referrals WHERE referred_id = ?", (new_telegram_id,)) as cur:
            existing = await cur.fetchone()
            if existing:
                return {"success": False, "reward_given": False, "new_invited_count": 0}

        # Referalni yozish
        await db.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)", (referrer_id, new_telegram_id))
        await db.execute("UPDATE users SET referrer_id = ? WHERE telegram_id = ?", (referrer_id, new_telegram_id))

        new_count = (referrer["invited_count"] or 0) + 1
        reward_given = (new_count % 2 == 0)

        if reward_given:
            new_balance = (referrer["paid_balance"] or 0) + 1
            await db.execute(
                "UPDATE users SET invited_count = ?, paid_balance = ? WHERE telegram_id = ?",
                (new_count, new_balance, referrer_id)
            )
        else:
            await db.execute(
                "UPDATE users SET invited_count = ? WHERE telegram_id = ?",
                (new_count, referrer_id)
            )

        await db.commit()

        return {
            "success": True,
            "reward_given": reward_given,
            "new_invited_count": new_count,
            "referrer_name": referrer["full_name"] or referrer["username"] or "Foydalanuvchi"
        }

async def get_referral_stats(telegram_id: int) -> dict:
    user = await get_user(telegram_id)
    if not user:
        return {"invited_count": 0, "earned_limits": 0, "needed_for_next": 2}
    invited = user.get("invited_count", 0) or 0
    earned = invited // 2
    needed = 2 - (invited % 2)
    return {
        "invited_count": invited,
        "earned_limits": earned,
        "needed_for_next": needed
    }

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*), SUM(total_generated) FROM users") as cursor:
            row = await cursor.fetchone()
            total_users = row[0] or 0
            total_slides = row[1] or 0

        async with db.execute("SELECT COUNT(*) FROM users WHERE total_generated > 0") as cursor:
            act_row = await cursor.fetchone()
            active_users = act_row[0] or 0

        async with db.execute("SELECT COUNT(*) FROM referrals") as cursor:
            ref_row = await cursor.fetchone()
            total_referrals = ref_row[0] or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_slides": total_slides,
            "total_referrals": total_referrals
        }

async def save_user_file(telegram_id: int, topic: str, file_name: str, file_id: str = "", file_path: str = "", file_type: str = "pptx") -> int:
    """Foydalanuvchi yaratgan slayd faylini ma'lumotlar bazasiga saqlash."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO user_files (telegram_id, topic, file_name, file_id, file_path, file_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (telegram_id, topic, file_name, file_id or "", file_path or "", file_type))
        await db.commit()
        return cursor.lastrowid

async def get_user_files(telegram_id: int, limit: int = 50) -> list:
    """Foydalanuvchining barcha saqlangan slayd fayllari ro'yxatini olish (eng yangilari birinchi)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM user_files 
            WHERE telegram_id = ? 
            ORDER BY id DESC 
            LIMIT ?
        """, (telegram_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

