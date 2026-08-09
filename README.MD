# HACKATHON_MLH_2026

Projetos desenvolvidos durante o **MLH Global Hack Week 2026** — trilha de Agentes de IA.

---

## 📁 Estrutura do Repositório

```
hakaton_mlh_2026/
├── primeiro_agent_ai_openai/     # Agente Python com Function Calling (OpenAI)
├── ghw-agents-day2/              # Workshop JS OpenAI: 3 passos (request → interativo → memória)
├── ghw-agents-gemini/            # Workshop JS Gemini: 4 passos (request → chat → vision → tools)
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

### 2. `ghw-agents-day2` (JavaScript/Node.js)
**Workshop oficial MLH (OpenAI)** — 3 passos progressivos:
- `step-1-first-request.js` — primeira requisição à OpenAI
- `step-2-interactive-agent.js` — loop interativo + instructions (personalidade)
- `step-3-agent-with-memory.js` — memória temporária (array `history`)

- **Como rodar:**
  ```bash
  cd ghw-agents-day2
  npm install
  cp .env.example .env   # adicione OPENAI_API_KEY
  npm run step3
  ```

### 3. `ghw-agents-gemini` (JavaScript/Node.js)
**Workshop MLH Agents Week com Google Gemini** — 4 passos progressivos + 4 tools customizadas:

| Step | Arquivo | Descrição |
|------|---------|-----------|
| 1 | `step-1-gemini.js` | Primeira requisição simples ao Gemini |
| 2 | `step-2-chat-agent.js` | Chat interativo no terminal com memória de conversa |
| 3 | `step-3-vision-agent.js` | Análise de imagem (multimodal) — envia `demo-image.jpg` |
| 4 | `step-4-tool-agent.js` | **Agente com 4 tools** — Gemini decide quando usar cada uma |

#### 🔧 Tools implementadas no Step 4:
| Tool | Função | Detalhes |
|------|--------|----------|
| `getWeather` | Clima real via **OpenWeatherMap API** | Gera múltiplas variações de query (cidade, cidade+estado, cidade+estado+país, todos estados BR). Fallback automático para mock se API key inválida (401) ou não ativada. Inclui sugestões de cidades BR. |
| `calculate` | Calculadora segura | Sanitização regex + `Function` strict mode. Ex: `"25 * 4 + 10"` |
| `searchWeb` | Busca web (mock) | Resultados simulados para: javascript, node.js, gemini api. Extensível para API real (SerpAPI, Bing). |
| `convertCurrency` | Conversor de moeda (taxas fixas) | USD, BRL, EUR, GBP, JPY. Extensível para exchangerate-api.com. |

- **Como rodar:**
  ```bash
  cd ghw-agents-gemini
  npm install
  cp .env.example .env
  # Edite .env com suas keys:
  # GEMINI_API_KEY=...
  # OPENWEATHER_API_KEY=... (opcional, tem fallback mock)
  npm run step4
  ```

- **Exemplos de uso no Step 4:**
  ```
  You: Como está o tempo em Parintins, Amazonas?
  You: Quanto é 15% de 280?
  You: Converta 100 USD para BRL
  You: Busque sobre "javascript async await"
  ```

#### 🛠️ Tech Stack:
- Node.js ESM (`"type": "module"`)
- `@google/genai` SDK oficial
- `dotenv` para config
- `readline/promises` para CLI interativo
- `fetch` nativo (Node 18+) para OpenWeatherMap

### 4. `multiagent-chat` (Python/FastAPI + Web)
**Chat com múltiplos agentes e troca automática por cota de tokens.**

- **Backend:** FastAPI + `openai` / `anthropic` SDKs
- **Frontend:** HTML/JS vanilla (static/)
- **Troca automática:** quando `token_quota` do agente ativo acaba, passa pro próximo
- **Config:** `agents.config.json` (ordem = prioridade de fallback)
  - `gpt-rapido` (4k tokens) → `claude-raciocinio` (8k) → `gpt-reserva` (6k)
- **Log:** `conversation_log.txt`

- **Como rodar:**
  ```bash
  cd multiagent-chat
  pip install -r requirements.txt
  cp .env.example .env   # chaves OpenAI/Anthropic
  uvicorn main:app --reload
  # Acesse o link gerado
  ```

### 5. `app_backboard_dashboard`
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

# Gemini (ghw-agents-gemini)
GEMINI_API_KEY=...

# OpenWeatherMap (ghw-agents-gemini step-4, opcional)
OPENWEATHER_API_KEY=...
```

> **Nunca comite `.env`** — já está no `.gitignore`.

---

## 🧠 Conceitos Explorados

| Conceito | Onde Aplicado |
|----------|---------------|
| Function Calling / Tools | `primeiro_agent_ai_openai`, `ghw-agents-gemini/step-4` |
| System Instructions (persona) | `ghw-agents-day2/step-2`, `primeiro_agent_ai_openai`, `multiagent-chat` |
| Conversation Memory | `ghw-agents-day2/step-3`, `ghw-agents-gemini/step-2`, `multiagent-chat` |
| Multi-agent Fallback | `multiagent-chat` |
| Token Quota Management | `multiagent-chat` |
| Vision / Multimodal | `ghw-agents-gemini/step-3` |
| Robust API Query Generation | `ghw-agents-gemini/step-4` (getWeather) |
| API Fallback (Mock) | `ghw-agents-gemini/step-4` (OpenWeatherMap 401/404) |
| Backboard API (unified LLM gateway) | `app_backboard_dashboard` |

---

## 📝 Próximos Passos / Ideias

- [ ] Adicionar mais tools no `primeiro_agent_ai_openai` (busca web, execução de código)
- [ ] Persistir memória em banco (SQLite/Redis) no `multiagent-chat`
- [ ] Interface web para o `primeiro_agent_ai_openai`
- [ ] Testar Backboard SDK para fallback multi-provider real
- [ ] Adicionar memory persistente (SQLite/JSON) ao `ghw-agents-gemini/step-2`

---

## 🔗 Referências

- [MLH Global Hack Week: Agents](https://events.mlh.com/events/14585)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
- [Google Gemini API](https://ai.google.dev/docs)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Backboard SDK](https://github.com/backboard/backboard-python-sdk)
- [FastAPI](https://fastapi.tiangolo.com/)