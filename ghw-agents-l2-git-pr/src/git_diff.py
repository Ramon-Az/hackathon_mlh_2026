"""Coleta de contexto git via subprocess (diff, status, commits recentes).

O agente do desafio L2 (Git Commit & PR Agent) precisa enxergar o estado
do repositório antes de gerar mensagens. Aqui ficam as chamadas reais ao
git — rodadas em subprocess para não depender de bibliotecas C (pygit2).
"""

from __future__ import annotations

import subprocess
from typing import Optional


def _run(args: list[str], cwd: Optional[str] = None) -> str:
    """Executa um comando git e devolve a saída stdout (sem erro)."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_diff(staged: bool = False, limit: int = 300) -> str:
    """Diff do working tree (`git diff`) ou do index (`git diff --staged`).

    `limit` corta o diff em linhas para não estourar o contexto do LLM.
    Inclui o `--stat` no topo (resumo em poucas linhas) e depois o diff
    completo truncado.
    """
    args = ["diff", "--stat"] if not staged else ["diff", "--staged", "--stat"]
    stat = _run(args)
    args = ["diff"] if not staged else ["diff", "--staged"]
    diff = _run(args)

    lines = diff.splitlines()
    if len(lines) > limit:
        lines = lines[:limit]
        lines.append(f"... (diff truncado em {limit} linhas)")
    diff = "\n".join(lines)

    return f"{stat}\n\n{diff}".strip() if diff else ""


def get_status() -> str:
    """`git status --short` — lista arquivos modificados/novos/removidos."""
    return _run(["status", "--short"])


def get_recent_commits(n: int = 5) -> str:
    """`git log --oneline -n` — exemplos do estilo de commit do repo."""
    return _run(["log", "--oneline", f"-n {n}"])


def get_current_branch() -> str:
    """Nome da branch atual (ou 'detached')."""
    return _run(["rev-parse", "--abbrev-ref", "HEAD"]) or "(detached)"


def detect_language(recent_commits: str) -> str:
    """Detecta o idioma dos commits recentes (heurística simples).

    Se os commits usarem prefixos/palavras-chave em inglês (feat:, fix:,
    add, update...), assume 'en'; caso contrário, 'pt'. Usada para instruir
    o LLM a responder no mesmo idioma do repositório.
    """
    text = recent_commits.lower()
    en_hits = sum(
        1
        for w in ("feat:", "fix:", "refactor:", "chore:", "docs:", "test:", "add ", "update ", "remove ", "optimize ")
        if w in text
    )
    pt_hits = sum(
        1
        for w in ("adiciona", "corrige", "atualiza", "remove", "cria", "implementa", "ajuste")
        if w in text
    )
    return "pt" if pt_hits > en_hits else "en"
