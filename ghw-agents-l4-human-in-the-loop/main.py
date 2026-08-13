"""CLI interativa do Human-in-the-Loop Workflow (desafio L4 GHW Agents 2026).

Traduz comandos em linguagem natural, classifica o risco e pede
confirmação humana antes de executar.

Uso:
    python main.py                 # sessão interativa
"""

from __future__ import annotations

import sys

import typer
from rich.console import Console
from rich.panel import Panel

from src.command_gen import analisar_comando, RiskLevel
from src.shell_exec import _safe_run

app = typer.Typer(add_completion=False)
console = Console()

RISCO_CORES = {"low": "green", "medium": "yellow", "high": "red"}


def _ask_confirmation(risco: RiskLevel) -> bool:
    """Pede confirmação. Risco alto exige digitar 'sim' completo."""
    if risco == RiskLevel.HIGH:
        resp = console.input("[bold red]⚠ RISCO ALTO. Digite 'sim' para executar: [/bold red]")
        return resp.strip().lower() == "sim"
    resp = console.input("[bold yellow]Executar? (s/N): [/bold yellow]")
    return resp.strip().lower() in ("s", "sim", "y", "yes")


def _handle_comando(texto: str) -> None:
    """Analisa e executa um comando com protocolo HITL."""
    resultado = analisar_comando(texto)
    cor = RISCO_CORES[resultado.risco.value]

    console.print(Panel(
        f"[bold]Comando:[/bold] {resultado.comando}\n"
        f"[{cor}]Risco: {resultado.risco.value.upper()}[/{cor}]\n"
        f"{resultado.explicacao}",
        title="Análise",
        border_style=cor,
    ))

    if not _ask_confirmation(resultado.risco):
        console.print("[dim]Cancelado.[/dim]")
        return

    console.print("[dim]Executando...[/dim]")
    code, out, err = _safe_run(resultado.comando, timeout=30)

    if code == 0:
        console.print(f"[green]OK (código {code})[/green]")
        if out.strip():
            console.print(out[:2000])
    else:
        console.print(f"[red]Falha (código {code})[/red]")
        if err.strip():
            console.print(err[:2000])


@app.command()
def main() -> None:
    """Sessão interativa Human-in-the-Loop."""
    console.print("[bold cyan]L4 — Human-in-the-Loop Workflow[/bold cyan]")
    console.print("Digite um comando em linguagem natural. Comandos: !sair | !ajuda\n")

    while True:
        try:
            texto = console.input("Você> ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Até![/dim]")
            raise typer.Exit()

        if not texto:
            continue
        if texto.lower() in ("!sair", "!exit", "sair"):
            console.print("[dim]Até![/dim]")
            break
        if texto.lower() in ("!ajuda", "!help"):
            console.print("[dim]Comandos: !sair | !ajuda. Ex.: 'list files', 'delete all files'[/dim]")
            continue

        try:
            _handle_comando(texto)
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")


if __name__ == "__main__":
    app()
