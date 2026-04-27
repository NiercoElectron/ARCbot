# 🤖 ARC Bot — Alpha Fechado

> Bot Discord para o servidor **ARC** — gerenciamento, IA e notificações de eventos, tudo em um só lugar.

---

## ⚠️ Estado atual: Alpha Fechado

Esta é uma versão **Alpha Fechada**. O acesso é restrito e a funcionalidade pode mudar sem aviso prévio. Bugs são esperados — e bem-vindos como feedback.

---

## ✨ Funcionalidades

### 🧠 Inteligência Artificial
Integração com a OpenAI para um assistente virtual com personalidade própria. Ele lembra do contexto recente do canal para dar respostas mais relevantes.

| Comando | Descrição |
|---------|-----------|
| `\|sec <pergunta>` | Consulta a IA com contexto das últimas mensagens do canal |

### 🛡️ Moderação
Gerenciamento de roles diretamente pelo chat.

| Comando | Descrição |
|---------|-----------|
| `\|promote` | Atribui o role **Membro** ao autor |
| `\|demote` | Remove o role **Membro** do autor |

### 🎉 Comandos Gerais

| Comando | Descrição |
|---------|-----------|
| `\|ping` | Verifica se o bot está online |
| `\|chamar @usuário <n>` | Menciona um usuário `n` vezes (1–50) |

### 📅 Agendador de Eventos
Mensagens automáticas configuradas para notificar eventos recorrentes do jogo no canal `#arc-eventos`, incluindo:

- **Cidade dos Pássaros** — avisos de início e contagem regressiva
- **Incursão Noturna** — múltiplas localidades (Stella Montis, Cidade Soterrada, Espaçoporto, Campos de Batalha da Represa)
- **Bom dia** e resumo diário no canal `#geral`

### 👋 Boas-vindas Automáticas
Ao entrar no servidor, o membro recebe uma DM de boas-vindas e o role **Membro** é atribuído automaticamente.

---

## 🗂️ Estrutura do Projeto

```
.
├── main.py            # Ponto de entrada do bot
├── config.py          # Prefixo, roles, system prompt e agendamentos
├── Requirements.txt   # Dependências
├── cogs/
│   ├── ai.py          # Comando |sec (OpenAI)
│   ├── events.py      # Listeners: on_ready, on_member_join, on_message
│   ├── general.py     # Comandos gerais (ping, chamar)
│   ├── moderation.py  # Comandos promote e demote
│   └── scheduler.py   # Agendador de mensagens
└── utils/
    ├── database.py    # SQLite — histórico de mensagens por canal
    └── helpers.py     # Funções utilitárias
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
pip install -r Requirements.txt

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
| `PREFIX` | Prefixo dos comandos (padrão: `\|`) |
| `MEMBER_ROLE` | Nome do role atribuído aos membros |
| `ARC_ROLE` | Role de administração |
| `SYSTEM_PROMPT` | Personalidade e instruções da IA |
| `SCHEDULES` | Lista de mensagens agendadas com horário e canal |

---

## 🤝 Contribuindo

Por ser uma **Alpha Fechada**, contribuições externas não estão abertas por enquanto. Encontrou um bug ou tem uma sugestão? Entre em contato com a equipe diretamente no servidor.

---

## 📄 Licença

Distribuído para uso restrito durante o período de Alpha. Todos os direitos reservados.
