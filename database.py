import aiosqlite
from config import DATABASE_PATH


async def get_db():
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS welcome_settings (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            message TEXT DEFAULT 'Welcome {user} to {server}!',
            enabled INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS goodbye_settings (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            message TEXT DEFAULT 'Goodbye {user}! We will miss you.',
            enabled INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS autorole (
            guild_id INTEGER PRIMARY KEY,
            role_id INTEGER,
            enabled INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS logging_settings (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            msg_edit INTEGER DEFAULT 1,
            msg_delete INTEGER DEFAULT 1,
            member_join INTEGER DEFAULT 1,
            member_leave INTEGER DEFAULT 1,
            role_create INTEGER DEFAULT 1,
            role_delete INTEGER DEFAULT 1,
            channel_create INTEGER DEFAULT 1,
            channel_delete INTEGER DEFAULT 1,
            voice_update INTEGER DEFAULT 1,
            mod_actions INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            moderator_id INTEGER,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS custom_commands (
            guild_id INTEGER,
            command_name TEXT,
            response TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (guild_id, command_name)
        );

        CREATE TABLE IF NOT EXISTS automod_settings (
            guild_id INTEGER PRIMARY KEY,
            anti_spam INTEGER DEFAULT 0,
            anti_invite INTEGER DEFAULT 0,
            anti_link INTEGER DEFAULT 0,
            anti_mass_mention INTEGER DEFAULT 0,
            max_messages INTEGER DEFAULT 5,
            mute_duration INTEGER DEFAULT 300,
            log_channel_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS mutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            muted_by INTEGER,
            unmute_at TIMESTAMP,
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS afk (
            guild_id INTEGER,
            user_id INTEGER,
            reason TEXT DEFAULT 'AFK',
            since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (guild_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS starboard (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            threshold INTEGER DEFAULT 5,
            enabled INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS starboard_messages (
            guild_id INTEGER,
            original_msg_id INTEGER,
            starboard_msg_id INTEGER,
            stars INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, original_msg_id)
        );
    """)
    await db.commit()
    await db.close()


async def set_welcome(guild_id, channel_id, message=None, enabled=None):
    db = await get_db()
    await db.execute("""
        INSERT INTO welcome_settings (guild_id, channel_id, message, enabled)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET
            channel_id = COALESCE(?, channel_id),
            message = COALESCE(?, message),
            enabled = COALESCE(?, enabled)
    """, (guild_id, channel_id, message, enabled, channel_id, message, enabled))
    await db.commit()
    await db.close()


async def get_welcome(guild_id):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM welcome_settings WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None


async def set_goodbye(guild_id, channel_id, message=None, enabled=None):
    db = await get_db()
    await db.execute("""
        INSERT INTO goodbye_settings (guild_id, channel_id, message, enabled)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET
            channel_id = COALESCE(?, channel_id),
            message = COALESCE(?, message),
            enabled = COALESCE(?, enabled)
    """, (guild_id, channel_id, message, enabled, channel_id, message, enabled))
    await db.commit()
    await db.close()


async def get_goodbye(guild_id):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM goodbye_settings WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None


async def set_autorole(guild_id, role_id, enabled=None):
    db = await get_db()
    await db.execute("""
        INSERT INTO autorole (guild_id, role_id, enabled)
        VALUES (?, ?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET
            role_id = COALESCE(?, role_id),
            enabled = COALESCE(?, enabled)
    """, (guild_id, role_id, enabled, role_id, enabled))
    await db.commit()
    await db.close()


async def get_autorole(guild_id):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM autorole WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None


async def set_logging(guild_id, **kwargs):
    db = await get_db()
    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [guild_id]
    await db.execute(f"""
        INSERT INTO logging_settings (guild_id) VALUES (?)
        ON CONFLICT(guild_id) DO UPDATE SET {fields}
    """, [guild_id] + values)
    await db.commit()
    await db.close()


async def get_logging(guild_id):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM logging_settings WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None


async def add_warning(guild_id, user_id, moderator_id, reason):
    db = await get_db()
    await db.execute(
        "INSERT INTO warnings (guild_id, user_id, moderator_id, reason) VALUES (?, ?, ?, ?)",
        (guild_id, user_id, moderator_id, reason)
    )
    await db.commit()
    cursor = await db.execute("SELECT COUNT(*) as count FROM warnings WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
    row = await cursor.fetchone()
    await db.close()
    return row["count"]


async def get_warnings(guild_id, user_id):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM warnings WHERE guild_id = ? AND user_id = ? ORDER BY created_at DESC",
        (guild_id, user_id)
    )
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]


async def clear_warnings(guild_id, user_id):
    db = await get_db()
    await db.execute("DELETE FROM warnings WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
    await db.commit()
    await db.close()


async def set_custom_command(guild_id, command_name, response, created_by):
    db = await get_db()
    await db.execute("""
        INSERT INTO custom_commands (guild_id, command_name, response, created_by)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(guild_id, command_name) DO UPDATE SET response = ?
    """, (guild_id, command_name, response, created_by, response))
    await db.commit()
    await db.close()


async def get_custom_command(guild_id, command_name):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM custom_commands WHERE guild_id = ? AND command_name = ?",
        (guild_id, command_name)
    )
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None


async def delete_custom_command(guild_id, command_name):
    db = await get_db()
    await db.execute("DELETE FROM custom_commands WHERE guild_id = ? AND command_name = ?", (guild_id, command_name))
    await db.commit()
    await db.close()


async def get_all_custom_commands(guild_id):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM custom_commands WHERE guild_id = ?", (guild_id,))
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]


async def set_automod(guild_id, **kwargs):
    db = await get_db()
    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [guild_id]
    await db.execute(f"""
        INSERT INTO automod_settings (guild_id) VALUES (?)
        ON CONFLICT(guild_id) DO UPDATE SET {fields}
    """, [guild_id] + values)
    await db.commit()
    await db.close()


async def get_automod(guild_id):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM automod_settings WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None


async def add_mute(guild_id, user_id, muted_by, unmute_at):
    db = await get_db()
    await db.execute("UPDATE mutes SET active = 0 WHERE guild_id = ? AND user_id = ? AND active = 1", (guild_id, user_id))
    await db.execute(
        "INSERT INTO mutes (guild_id, user_id, muted_by, unmute_at) VALUES (?, ?, ?, ?)",
        (guild_id, user_id, muted_by, unmute_at)
    )
    await db.commit()
    await db.close()


async def remove_mute(guild_id, user_id):
    db = await get_db()
    await db.execute("UPDATE mutes SET active = 0 WHERE guild_id = ? AND user_id = ? AND active = 1", (guild_id, user_id))
    await db.commit()
    await db.close()


async def set_afk(guild_id, user_id, reason="AFK"):
    db = await get_db()
    await db.execute("""
        INSERT INTO afk (guild_id, user_id, reason) VALUES (?, ?, ?)
        ON CONFLICT(guild_id, user_id) DO UPDATE SET reason = ?, since = CURRENT_TIMESTAMP
    """, (guild_id, user_id, reason, reason))
    await db.commit()
    await db.close()


async def remove_afk(guild_id, user_id):
    db = await get_db()
    await db.execute("DELETE FROM afk WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
    await db.commit()
    await db.close()


async def get_afk(guild_id, user_id):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM afk WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None


async def set_starboard(guild_id, channel_id, threshold=None, enabled=None):
    db = await get_db()
    await db.execute("""
        INSERT INTO starboard (guild_id, channel_id, threshold, enabled)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET
            channel_id = COALESCE(?, channel_id),
            threshold = COALESCE(?, threshold),
            enabled = COALESCE(?, enabled)
    """, (guild_id, channel_id, threshold, enabled, channel_id, threshold, enabled))
    await db.commit()
    await db.close()


async def get_starboard(guild_id):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM starboard WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None
