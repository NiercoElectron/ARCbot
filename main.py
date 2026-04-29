"""Bot Discord — ponto de entrada."""

import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import PREFIX

load_dotenv()

# Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Configura logging manualmente (bot.start() não aceita log_handler)
discord.utils.setup_logging(handler=handler, level=logging.DEBUG)

# Lista de cogs para carregar automaticamente
EXTENSIONS = [
    'cogs.general',
    'cogs.moderation',
    'cogs.ai',
    'cogs.events',
    'cogs.scheduler',
    'cogs.setup',
    'cogs.queue',
]


async def main():
    async with bot:
        for ext in EXTENSIONS:
            await bot.load_extension(ext)
            print(f'  ✔ {ext} carregado')
        await bot.start(os.getenv('DISCORD-TOKEN'))


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot interrompido pelo usuário')
    except Exception as e:
        print(f'Erro fatal ao rodar o bot: {e}')
        import traceback
        traceback.print_exc()