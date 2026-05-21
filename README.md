# 🤖 ARC Bot

> Bot Discord multi-servidor com IA, moderação completa e agendamento de mensagens.

---

## ✨ Funcionalidades

### 🧠 Inteligência Artificial

Assistente com personalidade própria alimentado pelo modelo **GPT-5-mini**. Usa o histórico recente do canal como contexto para respostas mais relevantes. Cooldown de 30 s por usuário.

| Comando | Descrição |
|---------|-----------|
| \|sec <pergunta> | Consulta a IA com contexto das últimas mensagens do canal |

### 🎉 Comandos Gerais

| Comando | Descrição |
|---------|-----------|
| \|ping | Verifica a latência do bot |
| \|serverinfo | Mostra informações do servidor em embed |
| \|userinfo [@membro] | Exibe dados de um membro (padrão: autor do comando) |
| \|avatar [@membro] | Mostra o avatar em tamanho grande |
| \|help | Mostra os comandos disponíveis para você de acordo com suas permissões |

### 🛡️ Moderação *(apenas dono/admin)*

| Comando | Descrição |
|---------|-----------|
| \|promote [@membro] | Atribui o promote role ao membro |
| \|demote [@membro] | Remove o promote role do membro |
| \|ban @membro [motivo] | Bane o membro do servidor |
| \|kick @membro [motivo] | Expulsa o membro do servidor |
| \|mute @membro <duração> [motivo] | Timeout por 10s, 5m, 2h ou 1d (máx 28d) |
| \|liberar @membro | Remove o timeout antes do prazo |
| \|warn @membro [motivo] | Registra um aviso para o membro |
| \|warnings @membro | Lista os avisos do membro |
| \|clearwarns @membro | Remove todos os avisos do membro |
| \|purge <quantidade> [@membro] | Deleta mensagens no canal, opcionalmente filtrando por membro |
| \|unban <user_id> [motivo] | Remove o ban de um usuário pelo ID |
| \|softban @membro [motivo] | Bane e desbane o membro para apagar mensagens recentes |

### ⚙️ Configuração *(apenas dono/admin)*

| Comando | Descrição |
|---------|-----------|
| \|setautorole @Cargo | Define o cargo dado automaticamente a novos membros |
| \|setwelcome <mensagem|off> | Define ou desativa a mensagem de boas-vindas em DM |
| \|setpromoterole @Cargo | Define o cargo usado pelos comandos de promoção |
| \|showconfig | Exibe a configuração atual do bot no servidor |
| \|status | Mostra latência, módulos e permissões do bot |
| \|reload <módulo> | Recarrega um módulo (cog) sem reiniciar o bot |
| \|reloadall | Recarrega todos os módulos carregados |

### 📅 Agendador de Mensagens *(apenas dono/admin)*

Crie mensagens automáticas por servidor, diárias ou únicas em data futura.

| Comando | Descrição |
|---------|-----------|
| \|setqueue #canal HH:MM sim | Cria um agendamento diário no canal |
| \|setqueue #canal HH:MM não dd/mm/yyyy | Cria um agendamento único para uma data específica |
| \|listqueue | Lista todos os agendamentos do servidor |
| \|delqueue <id> | Remove um agendamento pelo ID |

### 👋 Automações de Eventos

- **Boas-vindas** — DM automática ao novo membro ao entrar no servidor
- **Autorole** — cargo atribuído automaticamente (configurável via |setautorole)
- **Verificação de permissões** — ao entrar em um servidor, o bot avisa o dono caso falte alguma permissão necessária

---

## 🗂️ Estrutura do Projeto

```
.
├── main.py            # Ponto de entrada do bot
├── config.py          # Prefixo e system prompt da IA
├── requirements.txt   # Dependências Python
├── cogs/
│   ├── ai.py          # Comando |sec (OpenAI GPT-5-mini)
│   ├── events.py      # Listeners: on_ready, on_guild_join, on_member_join, on_message
│   ├── general.py     # Comandos gerais (ping, serverinfo, userinfo, avatar, help)
│   ├── moderation.py  # Moderação (ban, kick, mute, warn, purge, unban, softban)
│   ├── queue.py       # Gerenciamento de agendamentos (setqueue, listqueue, delqueue)
│   ├── scheduler.py   # Loop que dispara as mensagens agendadas
│   └── setup.py       # Configuração do servidor (setautorole, setwelcome, setpromoterole, status, reload)
└── utils/
    ├── database.py    # SQLite — histórico de mensagens, config por guild, agendamentos e avisos
    └── helpers.py     # Funções utilitárias (is_owner_or_admin, find_channel, get_role)
```

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.11+
- Uma aplicação registrada no [Discord Developer Portal](https://discord.com/developers/applications)
- Chave de API da [OpenAI](https://platform.openai.com/)

### Passo a passo

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd BotPublic

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

### Variáveis de ambiente (`.env`)

```env
DISCORD-TOKEN=seu_token_aqui
API_KEY=sua_chave_openai_aqui
```

### Rodar

```bash
python main.py
```

---

## ⚙️ Configuração

Todas as configurações ficam em `config.py`:

| Variável | Descrição |
|----------|-----------|
| `PREFIX` | Prefixo dos comandos (padrão: `|`) |
| `SYSTEM_PROMPT` | Personalidade e instruções da IA |

---

## 🤝 Contribuindo

Por ser uma **Alpha Fechada**, contribuições externas não estão abertas por enquanto. Encontrou um bug ou tem uma sugestão? Entre em contato com a equipe diretamente no servidor.

---

## 📄 Licença

Distribuído para uso restrito durante o período de Alpha. Todos os direitos reservados.
