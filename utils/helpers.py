"""Funções utilitárias de uso geral no bot."""

import discord
from discord.ext import commands


def is_owner_or_admin():
    """Retorna um check para comandos de administrador.

    O comando só passa se o autor for o dono do servidor ou tiver permissão de administrador.
    """
    async def predicate(ctx: commands.Context) -> bool:
        return (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
        )
    return commands.check(predicate)


def find_channel(bot, channel_name: str | None = None, channel_id: int | None = None):
    """Busca por um canal de texto usando nome ou ID.

    Se o ID for fornecido, retorna diretamente o canal do cache do bot.
    Caso contrário, procura em todos os guilds pelo nome do canal.
    """
    if channel_id:
        return bot.get_channel(channel_id)
    if channel_name:
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                return channel
    return None


def get_role(guild: discord.Guild, role_name: str):
    """Retorna um cargo pelo nome dentro de um guild.

    Retorna None se o cargo não existir.
    """
    return discord.utils.get(guild.roles, name=role_name)
