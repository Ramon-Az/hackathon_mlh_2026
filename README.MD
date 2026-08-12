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
├── ghw-agents-real-apis/         # Workshop MLH: agente com APIs reais (Groq + Open-Meteo/CountriesNow/ExchangeRate)
├── desafio2_dashboard-nash-demo/ # Evidências do desafio 2 GHW Agents (Dashboard Walkthrough + Nash Demo)
├── desafio3_rcli-walkthrough/     # Evidências do desafio 3 GHW Agents (Instalar R-CLI + Walkthrough)
├── ghw-agents-l1-memory/          # Desafio L1 GHW Agents (Agente com Memória de Longo Prazo via ChromaDB)
├── ghw-agents-l2-git-pr/          # Desafio L2 GHW Agents (Git Commit & PR Agent via Groq)
├── ghw-agents-l3-terminal-helper/ # Desafio L3 GHW Agents (Terminal AI Helper: linguagem natural → comando)
├── desafio1_github-skills-intro-github/ # GitHub Skills: Introduction to GitHub (12/08)
├── desafio2_github-skills-copilot/      # GitHub Skills: Getting Started with Copilot (12/08)
├── desafio3_github-skills-codespace/    # GitHub Skills: Code with Codespaces (12/08)
├── ghw-agents-frameworks/              # Frameworks e templates de agentes
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

### 6. `ghw-agents-real-apis` (JavaScript/Node.js)
**Workshop MLH Agents Week — agente com APIs reais (Groq).** SDK OpenAI apontado para `https://api.groq.com/openai/v1` + modelo `llama-3.3-70b-versatile`. 4 steps progressivos:

| Step | Arquivo | Descrição |
|------|---------|-----------|
| 1 | `step-1-first-real-api.js` | Chamada direta à API real de clima (Open-Meteo) |
| 2 | `step-2-api-as-a-tool.js` | API vira função reutilizável `getWeather(city)` com geocoding real |
| 3 | `step-3-real-api-agent.js` | Groq decide quando chamar a tool `getWeather` |
| 4 | `step-4-smart-travel-agent.js` | **Agente completo** com 3 tools reais + loop + memória entre turnos |

#### 🔧 Tools reais no Step 4:
| Tool | API | Detalhes |
|------|-----|----------|
| `getWeather` | Open-Meteo (geocoding + clima) | Traduz código WMO para `sky: "clear sky"` (anti-alucinação) |
| `getCountryInfo` | CountriesNow | Capital, população e moeda (3 chamadas paralelas, cache 1x/sessão) |
| `convertCurrency` | ExchangeRate-API | Taxas reais, cache com TTL de 1h |

#### ✨ Destaques do Step 4:
- 🧠 **Memória entre turnos** — janela deslizante de 10 mensagens; follow-ups tipo *"e em Tóquio?"* mantêm contexto
- 🛡️ **Anti-alucinação** — dados brutos são traduzidos antes de ir ao modelo (`weather_code` → descrição legível)
- ⚡ **Caches** — países 1x/sessão, taxas TTL 1h, geocoding por cidade
- 🔁 **Robustez** — timeout 10s em toda chamada, parse seguro de argumentos, erro de tool vira mensagem pro modelo
- 🛟 **Recuperação de erro 400 do Groq** — `parallel_tool_calls: false` + retry automático

- **Como rodar:**
  ```bash
  cd ghw-agents-real-apis
  npm install
  cp .env.example .env   # GROQ_API_KEY + GROQ_MODEL
  npm run step4
  ```

- **Exemplos de conversa no Step 4:**
  ```
  You: qual o clima em Manaus?
  You: e em Tóquio?
  You: qual a moeda do Japão e quanto são 100 reais?
  ```

### 7. `desafio2_dashboard-nash-demo`
**Evidências da submissão do Desafio 2 do GHW Agents 2026** (Dashboard Walkthrough + Nash Demo).
- Prints numerados em `assets/img/` (`01`–`10`) com a história da tentativa: dashboard Backboard, chat, memória salva, erro por créditos, Nash free tier e a colagem final (`10-desafio2-colagem-final.png`)
- Submissão: link do repo + tech stack (Backboard, Nash, Python, Backboard SDK, Jupyter Notebook)
- Detalhes completos em `desafio2_dashboard-nash-demo/README.md`

### 8. `desafio3_rcli-walkthrough`
**Evidências da submissão do Desafio 3 do GHW Agents 2026** (Instalar R-CLI + Walkthrough).
- R-CLI instalado e funcionando: `backboard --version` → `Backboard R-CLI 3.0.2`
- Print da evidência em `assets/img/` (`01-backboard-version-vscode.png`): R-CLI no VS Code + notebook da primeira chamada de API da live ao fundo
- A `hello.py` literal não rodou por créditos zerados — a 1ª sessão real do R-CLI foi a da live (detalhes no README local)
- Detalhes completos em `desafio3_rcli-walkthrough/README.md`

### 9. `ghw-agents-l1-memory` (Python)
**Desafio L1 do GHW Agents 2026** (Give Your Agent Long-Term Memory) — agente que memoriza preferências e fatos do usuário **entre sessões** usando **ChromaDB** (armazenamento vetorial).

- 🧠 **Memória semântica:** um LLM extrator transforma cada conversa em fatos duráveis ("Usuário se chama João", "Usuário prefere Python para backend")
- 🔍 **Recall por similaridade:** embeddings locais `all-MiniLM-L6-v2` (ONNX, sem PyTorch) + busca por cosseno injetada no system prompt
- 🛠️ **Tools nativas:** `salvar_memoria` / `buscar_memoria` via function calling (Groq, `llama-3.3-70b-versatile`)
- 💾 **Persistência real:** banco vetorial em `data/` (ignorado no git) — fechar o programa e reabrir faz a sessão 2 lembrar da sessão 1
- 🛟 **Robustez:** fallback automático para o erro intermitente `tool_use_failed` do Groq (re-tenta sem tools)
- 🖥️ **CLI:** typer + rich, comandos `!memorias` / `!esquecer` / `!sair`

- **Como rodar:**
  ```bash
  cd ghw-agents-l1-memory
  pip install -r requirements.txt
  cp .env.example .env   # GROQ_API_KEY
  python main.py
  ```

- Detalhes completos em `ghw-agents-l1-memory/README.md`

### 10. `ghw-agents-l2-git-pr` (Python)
**Desafio L2 do GHW Agents 2026** (Git Commit & PR Agent) — ferramenta que lê o `git diff` local e gera mensagens de commit ou resumos de PR com Groq.

- 🔍 **Contexto git real:** `git diff`/`--staged`, `status --short`, `log --oneline -5` e branch via subprocess (sem libs C)
- 🧠 **LLM (Groq):** `llama-3.3-70b-versatile` gera mensagem conventional ou PR summary (título + bullets + `## Test`)
- 🌐 **Idioma inteligente:** detecta o idioma dos commits recentes (`auto`) ou força com `--idioma en|pt`; prompts EN/PT duplos
- 🖥️ **CLI:** typer + rich — flags `--staged`, `--pr`, `--limit N`
- 🪞 **Demo meta:** o commit deste projeto (`559ca99`) foi escrito pelo próprio agente

- **Como rodar:**
  ```bash
  cd ghw-agents-l2-git-pr
  pip install -r requirements.txt
  cp .env.example .env   # GROQ_API_KEY
  python main.py --staged          # mensagem de commit
  python main.py --staged --pr     # resumo de PR
  ```

- Detalhes completos em `ghw-agents-l2-git-pr/README.md`

### 11. `ghw-agents-l3-terminal-helper` (Python)
**Desafio L3 do GHW Agents 2026** (Terminal AI Helper) — agente CLI que traduz linguagem natural (inglês ou português) em comandos de terminal e **pede confirmação antes de executar**.

- 🗣️ **Linguagem natural → comando:** Groq devolve JSON `{comando, explicacao, risco}` (PowerShell no Windows, bash no Linux)
- 🔒 **Segurança em camadas:** confirmação sempre, classificação de risco (baixo/médio/alto), risco alto exige digitar `sim` completo, timeout de 30s
- 🖥️ **CLI:** typer + rich — prompt `Você>`, spinner "traduzindo...", painéis

- **Como rodar:**
  ```bash
  cd ghw-agents-l3-terminal-helper
  pip install -r requirements.txt
  cp .env.example .env   # GROQ_API_KEY
  python main.py
  # Ex.: Find all files larger than 100MB | Encontre arquivos maiores que 1MB nesta pasta
  ```

- Detalhes completos em `ghw-agents-l3-terminal-helper/README.md`

### 12. `desafio1_github-skills-intro-github`
**GitHub Skills: Introduction to GitHub** — conclusão do curso oficial do GitHub Skills (12/08).
- 📝 **Objetivo:** aprender fluxo básico de GitHub — criar branch, fazer commit, abrir Pull Request, mergear
- ✅ **Evidência:** print de conclusão no repositório `Ramon-Az/introduction-to-github` (badge "Congratulations!")
- 📦 **Submissão:** link do repo + screenshot no GHW Agents 2026
- 🔗 **Detalhes:** `desafio1_github-skills-intro-github/README.md`

### 13. `desafio2_github-skills-copilot`
**GitHub Skills: Getting Started with Copilot** — conclusão do curso de GitHub Copilot (12/08).
- 🤖 **Objetivo:** usar Copilot no VS Code/Codespaces — Ask mode, Edit mode, Inline Chat, revisão de PR
- ✅ **Evidência:** conclusão do exercício guiado pelo bot "Mona" no Codespace
- 📦 **Submissão:** link do repo + screenshot no GHW Agents 2026
- 🔗 **Detalhes:** `desafio2_github-skills-copilot/README.md`

### 14. `desafio3_github-skills-codespace`
**GitHub Skills: Code with Codespaces** — conclusão do curso de Codespaces (12/08).
- ☁️ **Objetivo:** criar e configurar ambiente de dev no GitHub Codespaces — VS Code no navegador, edição direta
- ✅ **Evidência:** print do Codespace funcionando (`assets/img/01-github-codespace.png`)
- 📦 **Submissão:** link do repo + screenshot no GHW Agents 2026
- 🔗 **Detalhes:** `desafio3_github-skills-codespace/README.md`

### 15. `ghw-agents-frameworks` (TypeScript/Python)
**Frameworks de Agentes Multi-provider** — templates experimentais com LangChain + NestJS + React (11/08).
- 🏗️ **Backend LangChain:** multi-agente para planejamento de eventos (supervisor + 5 agentes especializados: catering, marketing, sponsor, venue, lead)
- 🎨 **Frontend Vite + React:** interface de chat com agents em tempo real
- 📚 **Slides:** 2 sessões de apresentação (Markdown/HTML)
- 🛠️ **Stack:** TypeScript, NestJS, LangChain, LangGraph, Vite, React
- 🔗 **Detalhes:** `ghw-agents-frameworks/README.md` + `ghw-agents-frameworks/services/backend-langchain/README.md`

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

# Groq (ghw-agents-real-apis)
GROQ_API_KEY=...
GROQ_MODEL=llama-3.3-70b-versatile
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
| Tool Calling via Groq (OpenAI-compatível) | `ghw-agents-real-apis/step-3, step-4` |
| Agent Loop multi-step com tools | `ghw-agents-real-apis/step-4` |
| Conversation Memory (janela deslizante) | `ghw-agents-real-apis/step-4` |
| Anti-hallucination (tradução de dados brutos) | `ghw-agents-real-apis/step-4` |
| Caching + Timeout em tools | `ghw-agents-real-apis/step-4` |
| Long-Term Memory (vetorial/ChromaDB) | `ghw-agents-l1-memory` |
| Embeddings locais (ONNX, sem PyTorch) | `ghw-agents-l1-memory` |
| Semantic Search / Recall por similaridade | `ghw-agents-l1-memory` |
| Extração automática de fatos (memória semântica) | `ghw-agents-l1-memory` |
| Function Calling + fallback de erro (Groq) | `ghw-agents-l1-memory` |
| Git subprocess (diff/status/log) | `ghw-agents-l2-git-pr` |
| Geração de commit message / PR summary via LLM | `ghw-agents-l2-git-pr` |
| Detecção de idioma no prompt (EN/PT) | `ghw-agents-l2-git-pr` |
| NL → comando de terminal (LLM + JSON estruturado) | `ghw-agents-l3-terminal-helper` |
| Confirmação humana antes de executar (safety) | `ghw-agents-l3-terminal-helper` |
| Classificação de risco de comandos | `ghw-agents-l3-terminal-helper` |
| Execução subprocess cross-shell (PS/bash) | `ghw-agents-l3-terminal-helper` |

---

## 📝 Próximos Passos / Ideias

- [ ] Adicionar mais tools no `primeiro_agent_ai_openai` (busca web, execução de código)
- [ ] Persistir memória em banco (SQLite/Redis) no `multiagent-chat`
- [ ] Interface web para o `primeiro_agent_ai_openai`
- [ ] Testar Backboard SDK para fallback multi-provider real
- [ ] Adicionar memory persistente (SQLite/JSON) ao `ghw-agents-gemini/step-2`
- [ ] Adicionar mais tools ao `ghw-agents-real-apis/step-4` (notícias, GitHub, busca)
- [ ] Persistir memória do `ghw-agents-real-apis/step-4` em arquivo/SQLite

---

## 🔗 Referências

- [MLH Global Hack Week: Agents](https://events.mlh.com/events/14585)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
- [Google Gemini API](https://ai.google.dev/docs)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Backboard SDK](https://github.com/backboard/backboard-python-sdk)
- [FastAPI](https://fastapi.tiangolo.com/)