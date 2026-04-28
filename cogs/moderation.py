import discord
from discord.ext import commands

from utils.database import get_guild_config


class Moderation(commands.Cog):
    """Comandos de moderação: promote e demote."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def promote(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        config = await get_guild_config(ctx.guild.id)
        if not config['promote_role_id']:
            await ctx.send('Nenhum promote role configurado. Use `|setpromoterole @Cargo` primeiro.')
            return
        role = ctx.guild.get_role(config['promote_role_id'])
        if role:
            await target.add_roles(role, reason='Promoção manual')
            await ctx.send(f'Role **{role.name}** atribuído com sucesso a {target.mention}!')
        else:
            await ctx.send('O promote role configurado não existe mais neste servidor.')

    @commands.command()
    async def demote(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        config = await get_guild_config(ctx.guild.id)
        if not config['promote_role_id']:
            await ctx.send('Nenhum promote role configurado. Use `|setpromoterole @Cargo` primeiro.')
            return
        role = ctx.guild.get_role(config['promote_role_id'])
        if role:
            await target.remove_roles(role, reason='Remoção manual')
            await ctx.send(f'Role **{role.name}** removido com sucesso de {target.mention}!')
        else:
            await ctx.send('O promote role configurado não existe mais neste servidor.')


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))