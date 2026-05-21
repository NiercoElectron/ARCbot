"""Cog que permite criar e gerenciar agendamentos de mensagens."""

import asyncio
import datetime

import discord
from discord.ext import commands

from utils.database import (
    add_guild_schedule,
    delete_guild_schedule,
    get_guild_schedules,
)
from utils.helpers import is_owner_or_admin


class Queue(commands.Cog):
    """Gerencia agendamentos de mensagens para canais do servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='setqueue')
    @is_owner_or_admin()
    async def set_queue(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        time: str,
        daily: str,
        date: str = None,
    ):
        """Cria um novo agendamento de mensagem para um canal."""
        try:
            datetime.datetime.strptime(time, '%H:%M')
        except ValueError:
            await ctx.send('Horário inválido. Use o formato HH:MM (ex: `09:00`).')
            return

        daily_bool = daily.lower() in ('sim', 's')

        if not daily_bool and date is None:
            await ctx.send('Para agendamentos não diários informe a data: `dd/mm/yyyy`.')
            return

        parsed_date = None
        if not daily_bool:
            try:
                dt = datetime.datetime.strptime(date, '%d/%m/%Y')
                if dt.date() < datetime.date.today():
                    await ctx.send('A data informada já passou.')
                    return
                parsed_date = dt.strftime('%Y-%m-%d')
            except ValueError:
                await ctx.send('Data inválida. Use o formato `dd/mm/yyyy` (ex: `25/12/2026`).')
                return

        prompt = await ctx.send('Qual a mensagem a ser enviada? *(responda em até 60 segundos)*')
        try:
            reply = await self.bot.wait_for(
                'message',
                timeout=60.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
        except asyncio.TimeoutError:
            await prompt.edit(content='Tempo esgotado. Execute o comando novamente.')
            return

        schedule_id = await add_guild_schedule(
            guild_id=ctx.guild.id,
            channel_id=channel.id,
            time=time,
            message=reply.content,
            daily=daily_bool,
            date=parsed_date,
        )

        recurrence = 'diariamente' if daily_bool else f'em **{date}**'
        await ctx.send(
            f'Agendamento **`#{schedule_id}`** criado!\n'
            f'{channel.mention} · `{time}` · {recurrence}'
        )

    @commands.command(name='listqueue')
    @is_owner_or_admin()
    async def list_queue(self, ctx: commands.Context):
        """Exibe todos os agendamentos do servidor."""
        schedules = await get_guild_schedules(ctx.guild.id)

        if not schedules:
            await ctx.send('Nenhum agendamento configurado. Use `|setqueue` para criar um.')
            return

        embed = discord.Embed(
            title='Agendamentos do servidor',
            color=discord.Color.blurple(),
        )
        for s in schedules:
            channel = ctx.guild.get_channel(s['channel_id'])
            channel_str = channel.mention if channel else '*(canal removido)*'

            if s['daily']:
                recurrence = '🔁 Diário'
            elif s['fired']:
                recurrence = f'✅ Único — {s["date"]} *(já enviado)*'
            else:
                recurrence = f'📅 Único — {s["date"]}'

            embed.add_field(
                name=f'#{s["id"]} — {s["time"]}  |  {channel_str}',
                value=f'{recurrence}\n> {s["message"][:120]}',
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command(name='delqueue')
    @is_owner_or_admin()
    async def del_queue(self, ctx: commands.Context, schedule_id: int):
        """Remove um agendamento existente pelo seu ID."""
        removed = await delete_guild_schedule(schedule_id, ctx.guild.id)
        if removed:
            await ctx.send(f'Agendamento **`#{schedule_id}`** removido.')
        else:
            await ctx.send(f'Agendamento `#{schedule_id}` não encontrado neste servidor.')

    @set_queue.error
    @list_queue.error
    @del_queue.error
    async def queue_error(self, ctx: commands.Context, error: commands.CommandError):
        """Tratamento de erros comuns dos comandos de agendamento."""
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Apenas o dono do servidor ou administradores podem usar esse comando.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f'Uso correto:\n'
                f'`{ctx.prefix}setqueue #canal HH:MM sim`\n'
                f'`{ctx.prefix}setqueue #canal HH:MM não dd/mm/yyyy`'
            )
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send('Canal não encontrado. Mencione o canal com `#`.')
        elif isinstance(error, commands.BadArgument):
            await ctx.send('Argumento inválido. Verifique o ID ou o canal informado.')


async def setup(bot: commands.Bot):
    """Adiciona o cog Queue ao bot."""
    await bot.add_cog(Queue(bot))
