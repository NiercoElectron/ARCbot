import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import datetime
from openai import AsyncOpenAI

load_dotenv()
token = os.getenv('DISCORD-TOKEN')
GAPI_KEY = os.getenv('API_KEY')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='|', intents=intents)
openai = AsyncOpenAI(api_key=GAPI_KEY)

SYSTEM_PROMPT = 'Você é um secretário virtual para um servidor de Discord. Sua função é responder qualquer pergunta que seja feita por um usuário. Você é um pouco caótico e tem um senso de humor um tanto ácido, mas sempre tenta ser útil quando a situação pede. Você sempre colabora na zoeira dos usuários. Você tem um conhecimento geral sobre diversos assuntos, mas não é especialista em nenhum. Você é um pouco preguiçoso, então às vezes pode demorar um pouco para responder, mas isso é porque você gosta de pensar bem antes de falar. Você tem uma personalidade única e é muito querido pelos membros do servidor.'

srole = 'Membro'
arole = 'ARC'

# Exemplo de agendamentos: use 'channel' (nome sem '#') ou 'channel_id' (int). Horário no formato HH:MM (24h).
# Canal informado pelo usuário: arc-eventos
SCHEDULES = [
    {"time": "09:00", "channel": "geral", "message": "Bom dia! Lembre-se das regras do servidor."},
    {"time": "18:00", "channel": "arc-eventos", "message": "Resumo do dia: confira as novidades!"},
    {"time": "02:00", "channel": "arc-eventos", "message": "Cidade dos pássaros em uma hora!"},
    {"time": "03:00", "channel": "arc-eventos", "message": "Cidade dos pássaros acabou de começar!"},
    {"time": "04:00", "channel": "arc-eventos", "message": "Cidade dos pássaros em uma hora!"},
    {"time": "05:00", "channel": "arc-eventos", "message": "Cidade dos pássaros acabou de começar!"},
    {"time": "06:00", "channel": "arc-eventos", "message": "Cidade dos pássaros em uma hora!"},
    {"time": "07:00", "channel": "arc-eventos", "message": "Cidade dos pássaros acabou de começar!"},
    {"time": "10:00", "channel": "arc-eventos", "message": "Cidade dos pássaros em uma hora!"},
    {"time": "11:00", "channel": "arc-eventos", "message": "Cidade dos pássaros acabou de começar!"},
    {"time": "12:00", "channel": "arc-eventos", "message": "Cidade dos pássaros em uma hora!"},
    {"time": "13:00", "channel": "arc-eventos", "message": "Cidade dos pássaros acabou de começar!"},
    {"time": "02:00", "channel": "arc-eventos", "message": "Incursão Noturna em uma hora! (Stella Montis)"},
    {"time": "03:00", "channel": "arc-eventos", "message": "Incursão Noturna acabou de começar! (Stella Montis)"},
    {"time": "04:00", "channel": "arc-eventos", "message": "Incursão Noturna em uma hora! (Cidade Soterrada)"},
    {"time": "05:00", "channel": "arc-eventos", "message": "Incursão Noturna acabou de começar! (Cidade Soterrada)"},
    {"time": "09:00", "channel": "arc-eventos", "message": "Incursão Noturna em uma hora! (Espaçoporto)"},
    {"time": "18:35", "channel": "arc-eventos", "message": "Incursão Noturna acabou de começar! (Espaçoporto)"},
    {"time": "10:01", "channel": "arc-eventos", "message": "Incursão Noturna em uma hora! (Campos De Batalha Da Represa)"},
    {"time": "11:00", "channel": "arc-eventos", "message": "Incursão Noturna acabou de começar! (Campos De Batalha Da Represa)"},
    {"time": "15:00", "channel": "arc-eventos", "message": "Incursão Noturna em uma hora! (Cidade Soterrada)"},
    {"time": "16:00", "channel": "arc-eventos", "message": "Incursão Noturna acabou de começar! (Cidade Soterrada)"},
]

async def scheduled_sender():
    await bot.wait_until_ready()
    last_min = None
    while not bot.is_closed():
        now = datetime.datetime.now()
        now_min = now.strftime("%Y-%m-%d %H:%M")
        if now_min != last_min:
            current_hm = now.strftime("%H:%M")
            for s in SCHEDULES:
                if s.get("time") == current_hm:
                    channel = None
                    if s.get("channel_id"):
                        channel = bot.get_channel(s["channel_id"])
                    else:
                        for g in bot.guilds:
                            channel = discord.utils.get(g.text_channels, name=s.get("channel"))
                            if channel:
                                break
                    if channel:
                        try:
                            arl = discord.utils.get(channel.guild.roles, name=arole)
                            message_to_send = s.get("message")
                            if arl:
                                message_to_send = f"{arl.mention} {message_to_send}"
                            await channel.send(message_to_send)
                        except Exception as e:
                            print(f"Erro ao enviar mensagem agendada: {e}")
            last_min = now_min
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f'Estamos prontos, {bot.user}')
    # Inicia a task que envia mensagens agendadas (apenas uma vez)
    if not hasattr(bot, 'scheduled_task'):
        bot.scheduled_task = bot.loop.create_task(scheduled_sender())

@bot.event
async def on_member_join(member):
    try:
        await member.send(f'Bem-vindo ao nosso café virtual, {member.name}!')
    except Exception:
        pass

    role = discord.utils.get(member.guild.roles, name=srole)
    if role:
        try:
            await member.add_roles(role, reason='Atribuição automática de Sócio')
        except Exception as e:
            print(f"Não foi possível atribuir o role: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('<>'):
        await message.channel.send('Comando recebido!')
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def promote(ctx):
    role = discord.utils.get(ctx.guild.roles, name=srole)
    if role:
        await ctx.author.add_roles(role, reason='Atribuição manual de Sócio')
        await ctx.send(f'Role "{srole}" atribuído com sucesso a {ctx.author.mention}!')
    else:
        await ctx.send(f'Role "{srole}" não encontrado no servidor.')

@bot.command()
async def demote(ctx):
    role = discord.utils.get(ctx.guild.roles, name=srole)
    if role:
        await ctx.author.remove_roles(role, reason='Remoção manual de Sócio')
        await ctx.send(f'Role "{srole}" removido com sucesso de {ctx.author.mention}!')
    else:
        await ctx.send(f'Role "{srole}" não encontrado no servidor.')

@bot.command()
async def chamar(ctx, member: discord.Member, qnt: int):
    if qnt < 1:
        await ctx.send('Se você quer chamar alguém, com certeza é para chamar mais de uma vez, né?')
        return
    if qnt > 50:
        await ctx.send('Zero é pouco e 50 é demais, vamos manter a quantidade entre 1 e 50 para evitar spam.')
        return
    if member == ctx.author:
        await ctx.send('Você não pode se mencionar, escolha outra pessoa para chamar!')
        return
    if member == bot.user:
        await ctx.send('Eu sou um bot, não posso ser mencionado dessa forma! Escolha outra pessoa para chamar!')
        return
    await ctx.send(f'Vítima da vez: {member.mention}, mencionado {qnt} vezes! \n{member.mention * qnt}')

@chamar.error
async def chamar_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Esse usuário não está no servidor.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Quantidade de argumentos insuficiente. Use: |chamar @usuário quantidade.")

@bot.command()
async def sec(ctx, *, question):
    async with ctx.typing():
        resp = await openai.responses.create(
            model="gpt-5-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=1.0,
            max_output_tokens=500,
        )

    await ctx.send(resp.output_text)

try:
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
except KeyboardInterrupt:
    print('Bot interrompido pelo usuário')
except Exception as e:
    print(f'Erro fatal ao rodar o bot: {e}')
    import traceback
    traceback.print_exc()