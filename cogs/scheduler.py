import asyncio
import datetime

import discord
from discord.ext import commands, tasks

from utils.database import get_all_pending_schedules, mark_schedule_fired


class Scheduler(commands.Cog):
    """Cog responsável por enviar mensagens agendadas automaticamente."""

    def __init__(self, bot: commands.Bot):
        # Guarda a instância do bot para acesso aos canais e ao loop de tarefas.
        self.bot = bot
        # Armazena a última marcação de minuto processada para evitar envios repetidos
        # durante o mesmo minuto, já que o loop roda a cada 5 segundos.
        self.last_min: str | None = None
        # Inicia a tarefa de envio periódico assim que o cog é carregado.
        self.sender_loop.start()

    def cog_unload(self):
        # Cancela a tarefa quando o cog for descarregado ou o bot for desligado.
        self.sender_loop.cancel()

    @tasks.loop(seconds=5)
    async def sender_loop(self):
        # Executa a cada 5 segundos para verificar se há mensagens agendadas.
        now = datetime.datetime.now()
        # Formato com data e hora até minuto para comparar se já processamos a mesma janela.
        now_min = now.strftime("%Y-%m-%d %H:%M")

        # Se já processamos este mesmo minuto, retornamos imediatamente.
        # Isso evita que o mesmo agendamento seja disparado várias vezes
        # enquanto o clock permanece no mesmo minuto.
        if now_min == self.last_min:
            return

        # Hora atual no formato HH:MM para comparar com o horário dos agendamentos.
        current_hm = now.strftime("%H:%M")
        # Data atual no formato YYYY-MM-DD para validar agendamentos únicos.
        today = now.strftime('%Y-%m-%d')
        try:
            # Busca todos os agendamentos pendentes no banco de dados.
            db_schedules = await get_all_pending_schedules()
        except Exception as e:
            # Caso haja erro ao carregar do banco, registra e usa lista vazia.
            print(f"Erro ao carregar agendamentos do banco: {e}")
            db_schedules = []

        for s in db_schedules:
            # Ignora se o agendamento não for para o horário atual.
            if s['time'] != current_hm:
                continue
            # Se o agendamento não for diário, checa se a data coincide com hoje.
            if not s['daily'] and s['date'] != today:
                continue

            # Obtém o canal a partir do ID armazenado.
            channel = self.bot.get_channel(s['channel_id'])
            if not channel:
                # Ignora se o canal não estiver disponível no cache do bot.
                continue

            try:
                # Envia a mensagem agendada para o canal.
                await channel.send(s['message'])
            except Exception as e:
                # Se ocorrer erro ao enviar, registra e segue para o próximo agendamento.
                print(f"Erro ao enviar agendamento #{s['id']}: {e}")
                continue

            # Marca como disparado apenas agendamentos que não se repetem diariamente.
            if not s['daily']:
                await mark_schedule_fired(s['id'])

        # Atualiza o último minuto processado para evitar repetições.
        self.last_min = now_min

    @sender_loop.before_loop
    async def before_sender_loop(self):
        # Aguarda até o bot estar totalmente pronto antes de iniciar o loop.
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    # Função de setup usada pelo Discord.py para adicionar este cog ao bot.
    await bot.add_cog(Scheduler(bot))
