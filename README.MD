# HACKATHON_MLH_2026

Projetos desenvolvidos durante o **MLH Global Hack Week 2026** — trilha de Agentes de IA.

---

## 📁 Estrutura do Repositório

```
hakaton_mlh_2026/
├── primeiro_agent_ai_openai/     # Agente Python com Function Calling (OpenAI)
├── ghw-agents-day1/              # Workshop JS: 3 passos (request → interativo → memória)
├── multiagent-chat/              # Chat multi-agente (FastAPI + Web) com troca automática
├── app_backboard_dashboard/      # Experimentação com Backboard API
└── .venv/                        # Ambiente virtual Python (ignorado no git)
```

---

## 🎯 Projetos Principais

### 1. `primeiro_agent_ai_openai` (Python)
**Agente com Function Calling** — usa `openai` SDK + `Responses API`.

- **Ferramentas:** hora atual, cálculo seguro (AST), salvar anotações
- **Loop:** modelo decide chamar tool → executa → devolve resultado → responde
- **Como rodar:**
  ```bash
  cd primeiro_agent_ai_openai
  pip install -r requirements.txt
  cp .env.example .env   # adicione OPENAI_API_KEY
  python main.py
  ```

### 2. `ghw-agents-day1` (JavaScript/Node.js)
**Workshop oficial MLH** — 3 passos progressivos:
- `step-1-first-request.js` — primeira requisição à OpenAI
- `step-2-interactive-agent.js` — loop interativo + instructions (personalidade)
- `step-3-agent-with-memory.js` — memória temporária (array `history`)

- **Como rodar:**
  ```bash
  cd ghw-agents-day1
  npm install
  cp .env.example .env   # adicione OPENAI_API_KEY
  npm run step3
  ```

### 3. `multiagent-chat` (Python/FastAPI + Web)
**Chat com múltiplos agentes e troca automática por cota de tokens.**

- **Backend:** FastAPI + `openai` / `anthropic` SDKs
- **Frontend:** HTML/JS vanilla (static/)
- **Troca automática:** quando `token_quota` do agente ativo acaba, passa pro próximo
- **Config:** `agents.config.json` (ordem = prioridade de fallback)
- **Log:** `conversation_log.txt`

- **Como rodar:**
  ```bash
  cd multiagent-chat
  pip install -r requirements.txt
  cp .env.example .env   # chaves OpenAI/Anthropic
  uvicorn main:app --reload
  # Acesse http://127.0.0.1:8000
  ```

### 4. `app_backboard_dashboard`
**Testes com Backboard API** (One API for all LLMs).
- Notebook `primeira_chamada_api.ipynb` com `backboard-sdk`
- Descobriu: Backboard **não** tem endpoint OpenAI-compatível (`/chat/completions`)
- API real: `POST /api/threads/messages` via SDK

---

## ⚙️ Configuração Comum

Todos os projetos usam `.env` para chaves de API:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic (multiagent-chat)
ANTHROPIC_API_KEY=sk-ant-...
```

> **Nunca comite `.env`** — já está no `.gitignore`.

---

## 🧠 Conceitos Explorados

| Conceito | Onde Aplicado |
|----------|---------------|
| Function Calling / Tools | `primeiro_agent_ai_openai` |
| System Instructions (persona) | `ghw-agents-day1/step-2`, `primeiro_agent_ai_openai` |
| Conversation Memory | `ghw-agents-day1/step-3`, `multiagent-chat` |
| Multi-agent Fallback | `multiagent-chat` |
| Token Quota Management | `multiagent-chat` |
| Backboard API (unified LLM gateway) | `app_backboard_dashboard` |

---

## 📝 Próximos Passos / Ideias

- [ ] Adicionar mais tools no `primeiro_agent_ai_openai` (busca web, execução de código)
- [ ] Persistir memória em banco (SQLite/Redis) no `multiagent-chat`
- [ ] Interface web para o `primeiro_agent_ai_openai`
- [ ] Testar Backboard SDK para fallback multi-provider real

---

## 🔗 Referências

- [MLH Global Hack Week: Agents](https://events.mlh.com/events/14585)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
- [Backboard SDK](https://github.com/backboard/backboard-python-sdk)
- [FastAPI](https://fastapi.tiangolo.com/)