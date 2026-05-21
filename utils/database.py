"""Módulo de acesso ao banco de dados SQLite.

Este módulo gerencia o armazenamento de mensagens, configurações do servidor,
avisos e agendamentos de mensagem.
"""

import aiosqlite

# Caminho do arquivo SQLite usado pelo bot.
DB_PATH = 'bot_data.db'
# Quantidade máxima de mensagens armazenadas por canal para contexto da IA.
MAX_MESSAGES_PER_CHANNEL = 10
# Tempo de vida das mensagens em horas antes de serem removidas.
MESSAGE_TTL_HOURS = 24  # mensagens mais antigas que isso são removidas automaticamente


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
                promote_role_id  INTEGER,
                welcome_message  TEXT
            )
        ''')
        # migração: adiciona coluna se banco já existia sem ela
        try:
            await db.execute('ALTER TABLE guild_config ADD COLUMN welcome_message TEXT')
        except Exception:
            pass
        await db.execute('''
            CREATE TABLE IF NOT EXISTS guild_schedules (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                time       TEXT    NOT NULL,
                message    TEXT    NOT NULL,
                daily      INTEGER NOT NULL DEFAULT 1,
                date       TEXT,
                fired      INTEGER NOT NULL DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER NOT NULL,
                user_id    INTEGER NOT NULL,
                mod_id     INTEGER NOT NULL,
                reason     TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            )
        ''')
        await db.execute('''
            CREATE INDEX IF NOT EXISTS idx_warnings_guild_user
            ON warnings (guild_id, user_id)
        ''')
        await db.commit()


async def set_guild_config(guild_id: int, **kwargs):
    """Atualiza campos de configuração do servidor. Kwargs aceitos: autorole_id, promote_role_id, welcome_message."""
    allowed = {'autorole_id', 'promote_role_id', 'welcome_message'}
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
            'SELECT autorole_id, promote_role_id, welcome_message FROM guild_config WHERE guild_id = ?',
            (guild_id,)
        )
        row = await cursor.fetchone()
    if row:
        return dict(row)
    return {'autorole_id': None, 'promote_role_id': None, 'welcome_message': None}


async def save_message(channel_id: int, author_name: str, content: str, created_at: str):
    """Salva uma mensagem e mantém no máximo MAX_MESSAGES_PER_CHANNEL por canal, com TTL."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO messages (channel_id, author_name, content, created_at) '
            'VALUES (?, ?, ?, ?)',
            (channel_id, author_name, content, created_at),
        )
        # Remove mensagens expiradas (mais antigas que MESSAGE_TTL_HOURS)
        await db.execute(
            "DELETE FROM messages WHERE channel_id = ? AND created_at < datetime('now', ? || ' hours')",
            (channel_id, f'-{MESSAGE_TTL_HOURS}'),
        )
        # Remove mensagens antigas além do limite por canal
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


# ── warnings ──────────────────────────────────────────────────────────────────

async def add_warning(guild_id: int, user_id: int, mod_id: int, reason: str, created_at: str) -> int:
    """Adiciona um aviso e retorna o total de avisos do usuário no servidor."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO warnings (guild_id, user_id, mod_id, reason, created_at) VALUES (?, ?, ?, ?, ?)',
            (guild_id, user_id, mod_id, reason, created_at),
        )
        await db.commit()
        cursor = await db.execute(
            'SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?',
            (guild_id, user_id),
        )
        row = await cursor.fetchone()
    return row[0]


async def get_warnings(guild_id: int, user_id: int) -> list[dict]:
    """Retorna todos os avisos de um usuário no servidor."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT id, mod_id, reason, created_at FROM warnings '
            'WHERE guild_id = ? AND user_id = ? ORDER BY created_at ASC',
            (guild_id, user_id),
        )
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def clear_warnings(guild_id: int, user_id: int) -> int:
    """Remove todos os avisos de um usuário. Retorna quantos foram removidos."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?',
            (guild_id, user_id),
        )
        row = await cursor.fetchone()
        count = row[0]
        await db.execute(
            'DELETE FROM warnings WHERE guild_id = ? AND user_id = ?',
            (guild_id, user_id),
        )
        await db.commit()
    return count


# ── guild_schedules ────────────────────────────────────────────────────────────

async def add_guild_schedule(
    guild_id: int,
    channel_id: int,
    time: str,
    message: str,
    daily: bool,
    date: str | None = None,
) -> int:
    """Insere um agendamento e retorna o ID gerado."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            '''INSERT INTO guild_schedules (guild_id, channel_id, time, message, daily, date, fired)
               VALUES (?, ?, ?, ?, ?, ?, 0)''',
            (guild_id, channel_id, time, message, int(daily), date),
        )
        await db.commit()
        return cursor.lastrowid


async def get_guild_schedules(guild_id: int) -> list[dict]:
    """Retorna todos os agendamentos de um servidor."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM guild_schedules WHERE guild_id = ? ORDER BY time',
            (guild_id,),
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_all_pending_schedules() -> list[dict]:
    """Retorna agendamentos diários e one-time ainda não disparados."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM guild_schedules WHERE daily = 1 OR fired = 0',
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def delete_guild_schedule(schedule_id: int, guild_id: int) -> bool:
    """Remove um agendamento do servidor. Retorna True se existia."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'DELETE FROM guild_schedules WHERE id = ? AND guild_id = ?',
            (schedule_id, guild_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def mark_schedule_fired(schedule_id: int):
    """Marca um agendamento one-time como disparado."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE guild_schedules SET fired = 1 WHERE id = ?',
            (schedule_id,),
        )
        await db.commit()
