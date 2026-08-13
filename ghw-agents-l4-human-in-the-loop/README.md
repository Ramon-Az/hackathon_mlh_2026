# L4 — Human-in-the-Loop Workflow

Desafio livre do **MLH Global Hack Week Agents 2026**:
> "Create an agent workflow where a human reviews and approves actions before the agent executes them."

## ⚙️ O que a ferramenta faz
- Traduz **linguagem natural → comando de terminal real** (PowerShell no Windows, bash no Linux)
- **Classifica o risco** (baixo/médio/alto) com regras locais (sem LLM)
- **Sempre pede confirmação humana antes de executar** — risco alto exige digitar `sim` completo
- Timeout de 30s na execução e decode adaptativo de encoding no Windows

## 🏗️ Arquitetura
| Camada | Implementação |
|--------|---------------|
| Análise de comando | `src/command_gen.py` — tradução de frases + classificação de risco (regex low/medium/high) + explicação |
| Execução segura | `src/shell_exec.py` — execução no shell nativo (PowerShell/bash) com timeout (30s) e decode adaptativo (CP437/cp1252 → UTF-8) |
| CLI | `main.py` — typer + rich (painéis coloridos por risco) |

## 🔒 Camadas de segurança
1. **Comando sempre exibido antes de executar**
2. **Classificação de risco** — `baixo` (leitura/criação), `medio` (modificação), `alto` (destrutivo/irreversível)
3. **Risco alto exige `sim` completo** — "s" ou "y" não passam
4. **Timeout de 30s** — comando travado é interrompido
5. `Ctrl+C` ou resposta diferente de `sim` cancela

## 🚀 Como rodar

```powershell
pip install -r requirements.txt
$env:PYTHONIOENCODING='utf-8'   # Windows: evita erro com emojis (⚠️)
python main.py
```

Depois é só **digitar uma frase** no chat interativo:

| Você digita | Comando gerado | Risco | O que acontece |
|-------------|----------------|-------|----------------|
| `list all files` | `Get-ChildItem` | baixo | lista os arquivos + pergunta `Executar? (s/N)` |
| `create a new folder` | `New-Item -ItemType Directory` | baixo | cria a pasta + pergunta `Executar? (s/N)` |
| `pip install requests` | `pip install requests` | médio | idem (pede `s`) |
| `delete all files` | `Remove-Item * -Recurse -Force` | alto | exige digitar `sim` completo |
| `format C:` | `format C:` | alto | exige digitar `sim` completo |

Comandos especiais: `!sair` para encerrar · `!ajuda` para ajuda.

## 🎬 Demonstração (evidência)
```
Você> delete all files
┌─ Análise ────────────────────────────────────────────┐
│ Comando: Remove-Item * -Recurse -Force               │
│ Risco: HIGH                                           │
│ ⚠️ O comando 'Remove-Item * -Recurse -Force' é de    │
│ ALTO RISCO. Pode causar perda de dados ou danos ao   │
│ sistema. Confirme explicitamente com 'sim' se desejar│
│ executar.                                            │
└───────────────────────────────────────────────────────┘
⚠ RISCO ALTO. Digite 'sim' para executar: <só 's' não passa>
```

## 📌 Lições aprendidas
- **Frases de linguagem natural precisam virar comandos reais** — sem tradução, o shell tenta rodar "list all files" e falha (código 1). O mapeamento de frases → comandos resolve (PowerShell no Windows, bash no Linux).
- **`shell=True` no Windows usa cmd.exe, que não conhece cmdlets do PowerShell** (`Get-ChildItem`, `New-Item`). Solução: executar `powershell.exe -NoProfile -Command <comando>` com argumentos em lista.
- **Regex com `|` no início cria match vazio** — qualquer comando caía em "alto risco"; o fix foi ancorar os padrões.
- **Encoding no Windows**: forçar `PYTHONIOENCODING=utf-8` evita `UnicodeEncodeError` com emojis/⚠️ (cp1252).

---

Parte do repositório [hackathon_mlh_2026](https://github.com/Ramon-Az/hackathon_mlh_2026).
