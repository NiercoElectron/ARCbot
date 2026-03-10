import discord
from discord.ext import commands

from config import MEMBER_ROLE
from utils.helpers import get_role


class Moderation(commands.Cog):
    """Comandos de moderação: promote e demote."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def promote(self, ctx: commands.Context):
        role = get_role(ctx.guild, MEMBER_ROLE)
        if role:
            await ctx.author.add_roles(role, reason='Atribuição manual de Sócio')
            await ctx.send(f'Role "{MEMBER_ROLE}" atribuído com sucesso a {ctx.author.mention}!')
        else:
            await ctx.send(f'Role "{MEMBER_ROLE}" não encontrado no servidor.')

    @commands.command()
    async def demote(self, ctx: commands.Context):
        role = get_role(ctx.guild, MEMBER_ROLE)
        if role:
            await ctx.author.remove_roles(role, reason='Remoção manual de Sócio')
            await ctx.send(f'Role "{MEMBER_ROLE}" removido com sucesso de {ctx.author.mention}!')
        else:
            await ctx.send(f'Role "{MEMBER_ROLE}" não encontrado no servidor.')


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))