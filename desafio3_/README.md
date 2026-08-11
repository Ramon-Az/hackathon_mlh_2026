# Desafio 3 — Instalar R-CLI + Walkthrough

Evidências da submissão do **Desafio 3** do MLH Global Hack Week Agents 2026 (trilha Agentes de IA).

## 📋 O que o desafio pedia
1. Instalar o **R-CLI** da Backboard (interface de chat/agente via terminal)
2. Enviar captura mostrando:
   - `backboard --version` **e**
   - a primeira sessão executando `hello.py`
   - *(ou alternativa: Studio da Backboard com `hello.py`)*

## ✅ Status
- [x] R-CLI instalado e funcionando (`Backboard R-CLI 3.0.2`)
- [x] Print da evidência: `assets/img/01-backboard-version-vscode.png`
- [x] Texto de submissão preparado
- [ ] Submissão na plataforma MLH (aguardando upload)

## 🗂️ Evidências

> As imagens ficam em `assets/img/`, numeradas na ordem da história:

| # | Arquivo | O que mostra |
|---|---------|--------------|
| 01 | `01-backboard-version-vscode.png` | **Evidência enviada na submissão** — R-CLI no terminal do VS Code com `backboard --version` → `Backboard R-CLI 3.0.2`, ao fundo o notebook com a primeira chamada de API feita durante a live |

## 🔗 Submissão
- Link do repo: `https://github.com/Ramon-Az/hackathon_mlh_2026`
- Tech stack: Backboard, R-CLI, Python, Jupyter Notebook, VS Code

## 🎮 A história (por que não é a `hello.py` literal)
A **primeira sessão real do R-CLI** aconteceu **durante a live** do GHW Agents, usada para
uma tarefa prática da própria live — não para o `hello.py` do tutorial. A captura enviada mostra o
R-CLI rodando no VS Code com `backboard --version` (3.0.2) e, ao fundo, o notebook com a **primeira
chamada de API da Backboard feita na live**.

A `hello.py` literal **não pôde ser rodada** em nova sessão: os créditos do free trial ($5) já estavam
zerados (consumidos no R-CLI durante a live), e o R-CLI recusou a sessão com:

```
We paused LLM chat — your balance is used up. Add credits on the Billing page (or turn on auto-reload)
```

## 📌 Lições aprendidas
- **R-CLI 3.0.2** instala via npm e fica no PATH (VS Code precisa reiniciar após instalar)
- **Free trial Backboard** = $5 únicos/30 dias (mesma lição do desafio 2) — sem renovação grátis
