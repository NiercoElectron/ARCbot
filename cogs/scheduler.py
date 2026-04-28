import asyncio
import datetime

import discord
from discord.ext import commands, tasks

from config import SCHEDULES, ARC_ROLE
from utils.database import get_all_pending_schedules, mark_schedule_fired
from utils.helpers import find_channel, get_role


class Scheduler(commands.Cog):
    """Task de mensagens agendadas."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_min: str | None = None
        self.sender_loop.start()

    def cog_unload(self):
        self.sender_loop.cancel()

    @tasks.loop(seconds=5)
    async def sender_loop(self):
        now = datetime.datetime.now()
        now_min = now.strftime("%Y-%m-%d %H:%M")

        if now_min == self.last_min:
            return

        current_hm = now.strftime("%H:%M")
        for schedule in SCHEDULES:
            if schedule.get("time") != current_hm:
                continue

            channel = find_channel(
                self.bot,
                channel_name=schedule.get("channel"),
                channel_id=schedule.get("channel_id"),
            )
            if not channel:
                continue

            try:
                arc_role = get_role(channel.guild, ARC_ROLE)
                message = schedule.get("message")
                if arc_role:
                    message = f"{arc_role.mention} {message}"
                await channel.send(message)
            except Exception as e:
                print(f"Erro ao enviar mensagem agendada: {e}")

        # ── Agendamentos configurados via |setqueue ────────────────────────
        today = now.strftime('%Y-%m-%d')
        try:
            db_schedules = await get_all_pending_schedules()
        except Exception as e:
            print(f"Erro ao carregar agendamentos do banco: {e}")
            db_schedules = []

        for s in db_schedules:
            if s['time'] != current_hm:
                continue
            if not s['daily'] and s['date'] != today:
                continue

            channel = self.bot.get_channel(s['channel_id'])
            if not channel:
                continue

            try:
                await channel.send(s['message'])
            except Exception as e:
                print(f"Erro ao enviar agendamento #{s['id']}: {e}")
                continue

            if not s['daily']:
                await mark_schedule_fired(s['id'])

        self.last_min = now_min

    @sender_loop.before_loop
    async def before_sender_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Scheduler(bot))
