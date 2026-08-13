# L5 — Project for a Friend

Desafio livre do **MLH Global Hack Week Agents 2026**:
> "Create an agent that is personalized for a specific user — your friend, family member, or someone you know."

## ⚙️ O que a ferramenta faz
- Agente de IA **personalizado para um amigo** (João, investidor) — responde filtrado pelo **perfil de investidor** (conservador/moderado/arrojado)
- Carrega contexto local do amigo (perfil, transações, histórico de atendimento) via `src/dados.py`
- **Anti-alucinação**: usa base de conhecimento restrita + templates por perfil em vez de LLM livre
- **Disclaimer obrigatório** em toda resposta (não constitui aconselhamento financeiro)

## 🏗️ Arquitetura
| Camada | Implementação |
|--------|---------------|
| Dados do amigo | `src/dados.py` — `PerfilInvestidor`, carrega/salva `perfil_investidor.json`, `transacoes.csv`, `historico_atendimento.csv` |
| Agente | `src/agente.py` — `AgenteFriend` (gerar_resposta, recomendar_acoes, executar_analise) com provedores openai/anthropic/gemini/groq/ollama |
| Interface CLI | `main.py` — typer + rich (`python main.py --perfil arrojado`) |
| Interface web | `app.py` — Streamlit (chat + sidebar) |

## 🚀 Como rodar
```bash
pip install -r requirements.txt

# CLI interativa
python main.py                              # perfil moderado (padrão)
python main.py --nome "Joao" --perfil arrojado
python main.py --perfil conservador --provedor ollama

# Interface web
streamlit run app.py
```

> **Windows:** rode com `$env:PYTHONIOENCODING='utf-8'` antes (cp1252 quebra com emojis).

## 🎬 Demonstração (evidência)
```
$ python main.py --perfil moderado
┌─ Project for a Friend ─────────────────────────────────────────┐
│ L5 — Agente do Joao                                           │
│ Perfil: moderado | Provedor: groq/llama-3.3-70b-versatile     │
└────────────────────────────────────────────────────────────────┘
Você> Quero investir em acoes
Olá Joao, considerando seu perfil moderado, aqui está um
balanceamento entre segurança e crescimento:
- Mix equilibrado entre renda fixa e variável
- Diversificação setorial e geográfica
- Revisão periódica da alocação

⚠️ Disclaimer: Este agente fornece sugestões, mas não constitui
aconselhamento financeiro. Consulte um profissional qualificado.
```

## 📌 Lições aprendidas
- **`__init__.py` não deve importar o CLI** — `from . import dados, agente` (app.py/main.py ficam na raiz), senão quebra `python main.py`.
- **Pequenos bugs de sintaxe** (indentação, f-string com espaço, `-> str` sem `:`) quebram o módulo inteiro — validar sempre com `python -c "import main"`.
- **Perfil como camada de filtragem** é mais robusto que LLM livre: respostas previsíveis, sem alucinação e com disclaimer garantido.

---

Parte do repositório [hackathon_mlh_2026](https://github.com/Ramon-Az/hackathon_mlh_2026).
