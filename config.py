"""Configurações e constantes globais do bot."""

# Prefixo de comandos
PREFIX = '|'

# Roles
MEMBER_ROLE = 'Membro'
ARC_ROLE = 'ARC'

# System prompt para a IA (comando |sec)
SYSTEM_PROMPT = (
    'Você é um secretário virtual para um servidor de Discord. '
    'Sua função é responder qualquer pergunta que seja feita por um usuário. '
    'Você é um pouco caótico e tem um senso de humor um tanto ácido, mas sempre tenta ser útil quando a situação pede. '
    'Você sempre colabora na zoeira dos usuários. '
    'Você tem um conhecimento geral sobre diversos assuntos, mas não é especialista em nenhum. '
    'Você é um pouco preguiçoso, então às vezes pode demorar um pouco para responder, '
    'mas isso é porque você gosta de pensar bem antes de falar. '
    'Você tem uma personalidade única e é muito querido pelos membros do servidor.'
)

# Agendamentos: use 'channel' (nome sem '#') ou 'channel_id' (int). Horário no formato HH:MM (24h).
SCHEDULES = [
    {"time": "09:00", "channel": "geral",       "message": "Bom dia! Lembre-se das regras do servidor."},
    {"time": "18:00", "channel": "arc-eventos",  "message": "Resumo do dia: confira as novidades!"},
    # Cidade dos pássaros
    {"time": "02:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros em uma hora!"},
    {"time": "03:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros acabou de começar!"},
    {"time": "04:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros em uma hora!"},
    {"time": "05:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros acabou de começar!"},
    {"time": "06:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros em uma hora!"},
    {"time": "07:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros acabou de começar!"},
    {"time": "10:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros em uma hora!"},
    {"time": "11:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros acabou de começar!"},
    {"time": "12:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros em uma hora!"},
    {"time": "13:00", "channel": "arc-eventos",  "message": "Cidade dos pássaros acabou de começar!"},
    # Incursão Noturna
    {"time": "02:00", "channel": "arc-eventos",  "message": "Incursão Noturna em uma hora! (Stella Montis)"},
    {"time": "03:00", "channel": "arc-eventos",  "message": "Incursão Noturna acabou de começar! (Stella Montis)"},
    {"time": "04:00", "channel": "arc-eventos",  "message": "Incursão Noturna em uma hora! (Cidade Soterrada)"},
    {"time": "05:00", "channel": "arc-eventos",  "message": "Incursão Noturna acabou de começar! (Cidade Soterrada)"},
    {"time": "09:00", "channel": "arc-eventos",  "message": "Incursão Noturna em uma hora! (Espaçoporto)"},
    {"time": "18:35", "channel": "arc-eventos",  "message": "Incursão Noturna acabou de começar! (Espaçoporto)"},
    {"time": "10:01", "channel": "arc-eventos",  "message": "Incursão Noturna em uma hora! (Campos De Batalha Da Represa)"},
    {"time": "11:00", "channel": "arc-eventos",  "message": "Incursão Noturna acabou de começar! (Campos De Batalha Da Represa)"},
    {"time": "15:00", "channel": "arc-eventos",  "message": "Incursão Noturna em uma hora! (Cidade Soterrada)"},
    {"time": "16:00", "channel": "arc-eventos",  "message": "Incursão Noturna acabou de começar! (Cidade Soterrada)"},
]
