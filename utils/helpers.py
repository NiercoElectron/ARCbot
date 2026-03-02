"""Funções auxiliares reutilizáveis."""

import discord


def find_channel(bot, channel_name: str | None = None, channel_id: int | None = None):
    """Busca um canal de texto pelo nome ou ID em todos os servidores do bot."""
    if channel_id:
        return bot.get_channel(channel_id)
    if channel_name:
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                return channel
    return None


def get_role(guild: discord.Guild, role_name: str):
    """Retorna um role pelo nome no guild, ou None se não existir."""
    return discord.utils.get(guild.roles, name=role_name)
