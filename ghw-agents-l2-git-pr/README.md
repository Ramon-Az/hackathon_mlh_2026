# L2 — Agente de Git Commit & PR (Git Commit & PR Agent)

Desafio livre do **MLH Global Hack Week Agents 2026**:
> "Create a tool that reads your local git diff output and automatically generates concise commit messages or Pull Request summaries."

## ⚙️ O que a ferramenta faz
- Lê o **diff real do seu repositório** (`git diff` ou `git diff --staged`) via subprocess
- Coleta contexto: `git status --short`, commits recentes (`git log --oneline -5`) e branch atual
- Um **LLM (Groq)** gera a mensagem de commit ou o resumo de PR pronto para usar
- **Segue o estilo do repo:** usa os commits recentes como exemplo e detecta o idioma (auto) — ou force com `--idioma en|pt`

## 🏗️ Arquitetura
| Camada | Implementação |
|--------|---------------|
| Coleta de contexto git | `src/git_diff.py` — subprocess `git diff/status/log` (sem depender de libs C) |
| Geração | `src/commit_agent.py` — Groq (`llama-3.3-70b-versatile`) via OpenAI SDK, prompts EN/PT duplos |
| CLI | `main.py` — typer + rich (paleta cyan/green/yellow/dim, spinner, painéis) |

## 🚀 Como rodar
```bash
pip install -r requirements.txt
cp .env.example .env   # GROQ_API_KEY

# Mensagem de commit do working tree (mudanças não-stageadas)
python main.py

# Mensagem de commit do index (stageadas)
python main.py --staged

# Resumo de PR
python main.py --staged --pr

# Controles
python main.py --limit 150    # limita linhas do diff enviadas ao LLM
python main.py --idioma en    # força inglês (auto = detecta do repo)
```

## 🎬 Demonstração (evidência)
Rodado no próprio repositório com os arquivos do L2 stageados:

```
$ python main.py --staged
+--------------------------------------------------+
| Git Commit & PR Agent                            |
| modo: mensagem de commit | staged | branch: main |
+--------------------------------------------------+
Arquivos afetados:
  A  .env.example
  A  main.py
  ...

+---------------------------- Mensagem de commit -----------------------------+
| feat: add Git Commit & PR Agent with LLM integration for commit messages    |
| and PR summaries                                                            |
|                                                                             |
| - Added `.env.example` for GROQ API key and model configuration             |
| - Implemented `main.py` as the entry point for the Git Commit & PR Agent    |
| ...
+-----------------------------------------------------------------------------+
```

E `python main.py --staged --pr` gera o resumo de PR (título + bullets + seção `## Test`).

## 📌 Lições aprendidas
- **Subprocess para git é suficiente** — não precisa de pygit2/bibliotecas C; `git diff`,
  `git status --short` e `git log --oneline` via subprocess cobrem o caso.
- **Truncar o diff** (`--limit`) é essencial: diffs grandes estouram o contexto do LLM.
  Incluir `git diff --stat` no topo ajuda o modelo a ver o resumo antes das linhas.
