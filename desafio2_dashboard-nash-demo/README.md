# Desafio 2 — Dashboard Walkthrough + Nash Demo

Evidências da submissão do **Desafio 2** do MLH Global Hack Week Agents 2026 (trilha Agentes de IA).

## 📋 O que o desafio pedia
1. **Parte A — Backboard:** demonstrar o uso do dashboard/API da Backboard (plataforma unificada de LLMs)
2. **Parte B — Nash:** demonstrar o uso do Nash (app de memória/RAG para agentes)

## ✅ Status
- [x] Evidências coletadas (10 prints)
- [x] Colagem final gerada: `assets/img/10-desafio2-colagem-final.png`
- [x] Texto de submissão preparado
- [ ] Submissão na plataforma MLH (aguardando upload)

## 🗂️ Evidências

> As 10 imagens ficam em `assets/img/`, numeradas na ordem da história:

| # | Arquivo | O que mostra |
|---|---------|--------------|
| 01 | `01-dashboard-uso-modelos.png` | Dashboard Backboard — uso de modelos |
| 02 | `02-dashboard-grafico-pizza-modelos.png` | Dashboard — gráfico de pizza (distribuição de modelos) |
| 03 | `03-chat-inicial.png` | Chat Backboard — primeira conversa |
| 04 | `04-chat-troca-modelo.png` | Chat — troca de modelo |
| 05 | `05-memoria-fato-salvo.png` | **Parte A:** Backboard salvou fato "ramo ficou sem créditos" na memória (~10/08) |
| 06 | `06-api-key.png` | API key da conta Backboard |
| 07 | `07-erro-chat-sem-creditos.png` | Chat Backboard sem resposta — créditos $5 esgotados (limite do free trial) |
| 08 | `08-nash-chat-aviso-creditos.png` | **Parte B:** Nash — chat com aviso de free tier |
| 09 | `09-nash-troca-modelo.png` | Nash — troca de modelo |
| 10 | `10-desafio2-colagem-final.png` | **Colagem enviada na submissão** (05 em cima + 08 embaixo) |

## 🔗 Submissão
- Link do repo: `https://github.com/Ramon-Az/hackathon_mlh_2026`
- Tech stack: Backboard, Nash, Python, Backboard SDK, Jupyter Notebook
- Observação no texto: créditos $5 consumidos no R-CLI (desafio 3), por isso o chat Backboard não respondia nos prints finais — tentativa documentada como evidência de uso.

## 📌 Lições aprendidas
- **Backboard:** free trial = $5 únicos/30 dias, sem renovação grátis (site: backboard.io, não .ai)
- **Nash:** free tier só tem memória/RAG — sem tokens de chat LLM (testado com 2 contas)
- **Self-host do Nash:** inviável de forma limpa (backend PyPI depende 100% da Backboard API; repo privado)
- Prints deste desafio ficam AQUI em `assets/img/` (padrão: `NN-descricao.png`), não na raiz do repo
