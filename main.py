"""Ponto de entrada do bot Discord.

Este módulo configura o cliente do Discord, carrega as extensões (cogs) e inicia
o bot usando o token definido em variáveis de ambiente.
"""

import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import PREFIX

# Carrega variáveis de ambiente a partir de .env
load_dotenv()

# Configura logging para salvar as mensagens de log em disco.
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Define os intents necessários para o bot operar corretamente.
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Cria a instância do bot com prefixo de comando e sem help automático.
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Inicializa o logger do discord.py com o handler configurado.
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
    """Carrega as extensões e inicia o bot."""
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