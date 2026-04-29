import datetime
import re

import discord
from discord.ext import commands

from utils.database import get_guild_config, add_warning, get_warnings, clear_warnings
from utils.helpers import is_owner_or_admin


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
    @is_owner_or_admin()
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
    @is_owner_or_admin()
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

        Uso: |mute @membro 10m Flood
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

    # ── warn / warnings / clearwarns ──────────────────────────────────────────

    @commands.command()
    @is_owner_or_admin()
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = 'Sem motivo informado'):
        """Registra um aviso para o membro e notifica via DM.

        Uso: |warn @membro Flood no chat
        """
        if member == ctx.guild.owner:
            await ctx.send('Não é possível advertir o dono do servidor.')
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send('Você não pode advertir alguém com cargo igual ou superior ao seu.')
            return

        created_at = discord.utils.utcnow().isoformat()
        total = await add_warning(ctx.guild.id, member.id, ctx.author.id, reason, created_at)

        await ctx.send(f'⚠️ {member.mention} recebeu um aviso. Motivo: **{reason}** (total: {total})')

        try:
            await member.send(
                f'Você recebeu um aviso em **{ctx.guild.name}**.\n'
                f'Motivo: **{reason}**\n'
                f'Total de avisos: **{total}**'
            )
        except discord.Forbidden:
            pass

    @commands.command(name='warnings')
    @is_owner_or_admin()
    async def show_warnings(self, ctx: commands.Context, member: discord.Member):
        """Lista todos os avisos de um membro.

        Uso: |warnings @membro
        """
        warns = await get_warnings(ctx.guild.id, member.id)
        if not warns:
            await ctx.send(f'{member.mention} não possui avisos.')
            return

        lines = []
        for i, w in enumerate(warns, 1):
            mod = ctx.guild.get_member(w['mod_id'])
            mod_name = mod.display_name if mod else f'ID {w["mod_id"]}'
            lines.append(f'**#{i}** — {w["reason"]} *(por {mod_name} em {w["created_at"][:10]})*')

        embed = discord.Embed(
            title=f'Avisos de {member.display_name}',
            description='\n'.join(lines),
            color=discord.Color.orange(),
        )
        embed.set_footer(text=f'Total: {len(warns)} aviso(s)')
        await ctx.send(embed=embed)

    @commands.command()
    @is_owner_or_admin()
    async def clearwarns(self, ctx: commands.Context, member: discord.Member):
        """Remove todos os avisos de um membro.

        Uso: |clearwarns @membro
        """
        removed = await clear_warnings(ctx.guild.id, member.id)
        if removed == 0:
            await ctx.send(f'{member.mention} não possui avisos para remover.')
        else:
            await ctx.send(f'✅ {removed} aviso(s) de {member.mention} removido(s).')

    # ── purge ─────────────────────────────────────────────────────────────────

    @commands.command()
    @is_owner_or_admin()
    async def purge(self, ctx: commands.Context, amount: int, member: discord.Member = None):
        """Deleta mensagens do canal. Opcionalmente filtra por membro.

        Uso: |purge 10
             |purge 10 @membro
        """
        if amount < 1 or amount > 200:
            await ctx.send('Informe um número entre 1 e 200.')
            return

        await ctx.message.delete()

        if member:
            check = lambda m: m.author == member
        else:
            check = None

        deleted = await ctx.channel.purge(limit=amount, check=check)
        confirm = await ctx.send(f'🗑 {len(deleted)} mensagem(ns) deletada(s).')
        await confirm.delete(delay=5)

    # ── unban ─────────────────────────────────────────────────────────────────

    @commands.command()
    @is_owner_or_admin()
    async def unban(self, ctx: commands.Context, user_id: int, *, reason: str = 'Sem motivo informado'):
        """Remove o ban de um usuário pelo ID.

        Uso: |unban 123456789 Apelou com sucesso
        """
        try:
            await ctx.guild.unban(discord.Object(id=user_id), reason=f'{ctx.author} — {reason}')
            await ctx.send(f'Usuário com ID `{user_id}` foi **desbanido**. Motivo: {reason}')
        except discord.NotFound:
            await ctx.send('Esse usuário não está banido neste servidor.')

    # ── softban ───────────────────────────────────────────────────────────────

    @commands.command()
    @is_owner_or_admin()
    async def softban(self, ctx: commands.Context, member: discord.Member, *, reason: str = 'Sem motivo informado'):
        """Bane e desbane imediatamente apagando as mensagens recentes (kick com purge).

        Uso: |softban @membro Flood excessivo
        """
        if member == ctx.guild.owner:
            await ctx.send('Não é possível softbanir o dono do servidor.')
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send('Você não pode softbanir alguém com cargo igual ou superior ao seu.')
            return
        await member.ban(reason=f'Softban por {ctx.author} — {reason}', delete_message_days=7)
        await ctx.guild.unban(member, reason=f'Softban (unban automático) por {ctx.author}')
        await ctx.send(f'{member.mention} foi **softbanido** (últimas mensagens deletadas). Motivo: {reason}')

    # ── error handlers ────────────────────────────────────────────────────────

    @promote.error
    @demote.error
    @ban.error
    @kick.error
    @castigar.error
    @liberar.error
    @unban.error
    @softban.error
    @purge.error
    @warn.error
    @show_warnings.error
    @clearwarns.error
    async def mod_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Apenas o dono do servidor ou administradores podem usar esse comando.')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('Membro não encontrado. Mencione o usuário com @.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Argumento faltando. Use `{ctx.prefix}help {ctx.command.name}` para ver o uso correto.')
        elif isinstance(error, commands.BadArgument):
            await ctx.send('Argumento inválido. Para `unban`, forneça o ID numérico do usuário.')
        elif isinstance(error, discord.Forbidden):
            await ctx.send('Não tenho permissão para executar essa ação. Verifique a hierarquia de cargos do bot.')


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
