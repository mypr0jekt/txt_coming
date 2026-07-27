import aiosqlite

DB_PATH = "bot.db"


async def init_db():
    """Bazani va kerakli jadvallarni yaratadi (birinchi ishga tushirishda)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT
            )
            """
        )
        await db.commit()


# ---------- ADMINLAR ----------

async def add_admin(user_id: int, full_name: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO admins (user_id, full_name) VALUES (?, ?)",
            (user_id, full_name),
        )
        await db.commit()


async def remove_admin(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        await db.commit()


async def is_admin(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM admins WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row is not None


async def get_all_admins():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, full_name FROM admins")
        return await cursor.fetchall()


# ---------- GURUHLAR ----------

async def add_group(chat_id: int, title: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO groups (chat_id, title) VALUES (?, ?)",
            (chat_id, title),
        )
        await db.commit()


async def remove_group(chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM groups WHERE chat_id = ?", (chat_id,))
        await db.commit()


async def get_all_groups():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT chat_id, title FROM groups")
        return await cursor.fetchall()
        
