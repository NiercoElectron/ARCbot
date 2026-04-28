import datetime
import re

import discord
from discord.ext import commands

from utils.database import get_guild_config


def is_owner_or_admin():
    async def predicate(ctx: commands.Context) -> bool:
        return (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
        )
    return commands.check(predicate)


def parse_duration(value: str) -> datetime.timedelta | None:
    """Converte strings como '10m', '2h', '1d' em timedelta. Retorna None se inválido."""
    match = re.fullmatch(r'(\d+)([smhd])', value.lower())
    if not match:
        return None
    amount, unit = int(match.group(1)), match.group(2)
    return {
        's': datetime.timedelta(seconds=amount),
        'm': datetime.timedelta(minutes=amount),
        'h': datetime.timedelta(hours=amount),
        'd': datetime.timedelta(days=amount),
    }[unit]


class Moderation(commands.Cog):
    """Comandos de moderação: promote, demote, ban, kick, castigar."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── promote / demote ──────────────────────────────────────────────────────

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

    # ── ban ───────────────────────────────────────────────────────────────────

    @commands.command()
    @is_owner_or_admin()
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = 'Sem motivo informado'):
        if member == ctx.guild.owner:
            await ctx.send('Não é possível banir o dono do servidor.')
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send('Você não pode banir alguém com cargo igual ou superior ao seu.')
            return
        await member.ban(reason=f'{ctx.author} — {reason}')
        await ctx.send(f'{member.mention} foi **banido**. Motivo: {reason}')

    # ── kick ──────────────────────────────────────────────────────────────────

    @commands.command()
    @is_owner_or_admin()
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = 'Sem motivo informado'):
        if member == ctx.guild.owner:
            await ctx.send('Não é possível kickar o dono do servidor.')
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send('Você não pode kickar alguém com cargo igual ou superior ao seu.')
            return
        await member.kick(reason=f'{ctx.author} — {reason}')
        await ctx.send(f'{member.mention} foi **kickado**. Motivo: {reason}')

    # ── castigar (timeout) ────────────────────────────────────────────────────

    @commands.command(name='mute')
    @is_owner_or_admin()
    async def castigar(self, ctx: commands.Context, member: discord.Member, duracao: str, *, reason: str = 'Sem motivo informado'):
        """Coloca o membro em timeout. Duração: 10s, 5m, 2h, 1d (máx 28d).

        Uso: |castigar @membro 10m Flood
        """
        if member == ctx.guild.owner:
            await ctx.send('Não é possível castigar o dono do servidor.')
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send('Você não pode castigar alguém com cargo igual ou superior ao seu.')
            return

        delta = parse_duration(duracao)
        if delta is None:
            await ctx.send('Duração inválida. Use: `10s`, `5m`, `2h`, `1d` (máximo `28d`).')
            return
        if delta > datetime.timedelta(days=28):
            await ctx.send('A duração máxima de timeout é 28 dias.')
            return

        until = discord.utils.utcnow() + delta
        await member.timeout(until, reason=f'{ctx.author} — {reason}')
        await ctx.send(f'{member.mention} foi **castigado** por `{duracao}`. Motivo: {reason}')

    @commands.command()
    @is_owner_or_admin()
    async def liberar(self, ctx: commands.Context, member: discord.Member):
        """Remove o timeout de um membro antes do prazo.

        Uso: |liberar @membro
        """
        await member.timeout(None, reason=f'Timeout removido por {ctx.author}')
        await ctx.send(f'Timeout de {member.mention} removido.')

    # ── error handlers ────────────────────────────────────────────────────────

    @ban.error
    @kick.error
    @castigar.error
    @liberar.error
    async def mod_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Apenas o dono do servidor ou administradores podem usar esse comando.')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('Membro não encontrado. Mencione o usuário com @.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Argumento faltando. Use `{ctx.prefix}help {ctx.command.name}` para ver o uso correto.')
        elif isinstance(error, discord.Forbidden):
            await ctx.send('Não tenho permissão para executar essa ação. Verifique a hierarquia de cargos do bot.')


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
