"""Execução de comandos no shell do sistema com timeout.

A execução só acontece DEPOIS da confirmação do usuário (o CLI cuida disso).
Este módulo apenas roda o comando e devolve a saída, com um timeout para
não travar o terminal.
"""

from __future__ import annotations

import platform
import subprocess
from typing import Optional


def _shell_command() -> list[str]:
    """Prefixo do shell alvo para o subprocess."""
    if platform.system() == "Windows":
        return ["powershell", "-NoProfile", "-Command"]
    return ["bash", "-c"]


def _decode(data: bytes) -> str:
    """Decodifica a saída do shell de forma adaptativa.

    O PowerShell no Windows pode emitir em UTF-8, cp850 (OEM) ou cp1252.
    Tenta cada um; no pior caso, usa replacement chars.
    """
    for enc in ("utf-8", "cp850", "cp1252"):
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")


def run_command(command: str, timeout: int = 30) -> tuple[int, str, str]:
    """Executa o comando no shell do sistema.

    Retorna (returncode, stdout, stderr). Em caso de timeout, retorna
    returncode -1 com mensagem de erro.
    """
    if not command.strip():
        return (0, "", "(comando vazio — nada a executar)")

    if platform.system() == "Windows":
        command = f"[Console]::OutputEncoding=[Text.Encoding]::UTF8; {command}"

    try:
        result = subprocess.run(
            [*_shell_command(), command],
            capture_output=True,
            timeout=timeout,
        )
        return (result.returncode, _decode(result.stdout), _decode(result.stderr))
    except subprocess.TimeoutExpired:
        return (-1, "", f"(comando excedeu o timeout de {timeout}s e foi interrompido)")
    except Exception as exc:
        return (-1, "", f"(falha ao executar: {exc})")
