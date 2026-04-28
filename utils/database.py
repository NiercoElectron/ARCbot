"""Módulo de banco de dados SQLite — armazena histórico de mensagens por canal."""

import aiosqlite

DB_PATH = 'bot_data.db'
MAX_MESSAGES_PER_CHANNEL = 10


async def init_db():
    """Cria as tabelas necessárias se não existirem."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id  INTEGER NOT NULL,
                author_name TEXT    NOT NULL,
                content     TEXT    NOT NULL,
                created_at  TEXT    NOT NULL
            )
        ''')
        await db.execute('''
            CREATE INDEX IF NOT EXISTS idx_channel_created
            ON messages (channel_id, created_at)
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id         INTEGER PRIMARY KEY,
                autorole_id      INTEGER,
                promote_role_id  INTEGER
            )
        ''')
        await db.commit()


async def set_guild_config(guild_id: int, **kwargs):
    """Atualiza campos de configuração do servidor. Kwargs aceitos: autorole_id, promote_role_id."""
    allowed = {'autorole_id', 'promote_role_id'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO guild_config (guild_id) VALUES (?) ON CONFLICT(guild_id) DO NOTHING',
            (guild_id,)
        )
        for column, value in fields.items():
            await db.execute(
                f'UPDATE guild_config SET {column} = ? WHERE guild_id = ?',
                (value, guild_id)
            )
        await db.commit()


async def get_guild_config(guild_id: int) -> dict:
    """Retorna a configuração do servidor ou um dict vazio."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT autorole_id, promote_role_id FROM guild_config WHERE guild_id = ?',
            (guild_id,)
        )
        row = await cursor.fetchone()
    if row:
        return dict(row)
    return {'autorole_id': None, 'promote_role_id': None}


async def save_message(channel_id: int, author_name: str, content: str, created_at: str):
    """Salva uma mensagem e mantém no máximo MAX_MESSAGES_PER_CHANNEL por canal."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO messages (channel_id, author_name, content, created_at) '
            'VALUES (?, ?, ?, ?)',
            (channel_id, author_name, content, created_at),
        )
        # Remove mensagens antigas, mantendo apenas as últimas N
        await db.execute('''
            DELETE FROM messages
            WHERE channel_id = ? AND id NOT IN (
                SELECT id FROM messages
                WHERE channel_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            )
        ''', (channel_id, channel_id, MAX_MESSAGES_PER_CHANNEL))
        await db.commit()


async def get_recent_messages(channel_id: int, limit: int = MAX_MESSAGES_PER_CHANNEL):
    """Retorna as últimas `limit` mensagens de um canal, em ordem cronológica."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT author_name, content, created_at FROM messages '
            'WHERE channel_id = ? ORDER BY created_at DESC LIMIT ?',
            (channel_id, limit),
        )
        rows = await cursor.fetchall()
    # Inverte para ordem cronológica (mais antiga → mais recente)
    return [
        {'author': row['author_name'], 'content': row['content'], 'created_at': row['created_at']}
        for row in reversed(rows)
    ]
