import discord
from discord.ext import commands

from config import MEMBER_ROLE


class General(commands.Cog):
    """Comandos gerais do bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send('Pong!')

    @chamar.error
    async def chamar_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("Esse usuário não está no servidor.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Quantidade de argumentos insuficiente. Use: |chamar @usuário quantidade.")


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
