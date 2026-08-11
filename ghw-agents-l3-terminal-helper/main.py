"""CLI interativa do Terminal AI Helper (desafio L3 GHW Agents 2026).

Traduz frases em inglês simples para comandos de terminal e pede
confirmação antes de executar.

Uso:
    python main.py                 # sessão interativa
    python main.py --shell linux   # força shell bash (ex.: WSL)
"""

from __future__ import annotations

import sys

import typer
from rich.console import Console
from rich.panel import Panel

from src.command_gen import CommandGenerator, detect_shell
from src.shell_exec import run_command

app = typer.Typer(add_completion=False)
console = Console()

RISCO_CORES = {"baixo": "green", "medio": "yellow", "alto": "red"}

OUTPUT_LIMIT = 150  # linhas máximas de output exibidas


def _ask_confirmation(risco: str) -> bool:
    """Pede confirmação. Risco alto exige digitar 'sim' completo."""
    if risco == "alto":
        resp = console.input("[bold red]⚠ RISCO ALTO. Digite 'sim' para executar: [/bold red]")
        return resp.strip().lower() == "sim"
    resp = console.input("[bold yellow]Executar? (s/N): [/bold yellow]")
    return resp.strip().lower() in ("s", "sim", "y", "yes")


def _show_output(returncode: int, stdout: str, stderr: str) -> None:
    """Mostra a saída do comando, truncada e colorida por stream."""
    if stdout:
        lines = stdout.rstrip().splitlines()
        if len(lines) > OUTPUT_LIMIT:
            lines = lines[:OUTPUT_LIMIT]
            lines.append(f"... (output truncado em {OUTPUT_LIMIT} linhas)")
        console.print("\n".join(lines))
    if stderr:
        lines = stderr.rstrip().splitlines()
        if len(lines) > OUTPUT_LIMIT:
            lines = lines[:OUTPUT_LIMIT]
            lines.append(f"... (stderr truncado em {OUTPUT_LIMIT} linhas)")
        console.print("[red]" + "\n[red]".join(lines))
    status = "✓ saída limpa" if returncode == 0 else f"✗ código de saída: {returncode}"
    console.print(f"[dim]{status}[/dim]")


@app.command()
def main(shell: str = typer.Option("auto", "--shell", help="auto, windows ou linux")) -> None:
    """Terminal AI Helper — linguagem natural vira comando de terminal (com confirmação)."""

    shell_name = detect_shell() if shell == "auto" else ("PowerShell (Windows)" if shell == "windows" else "bash (Linux/macOS)")

    console.print(
        Panel.fit(
            "[bold]Terminal AI Helper[/bold]\n"
            f"[dim]shell: {shell_name}[/dim]\n"
            "[dim]Digite em inglês ou português. Comandos: !sair | !ajuda[/dim]",
            border_style="cyan",
        )
    )

    generator = CommandGenerator()

    while True:
        try:
            phrase = console.input("[bold yellow]Você> [/bold yellow]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Até a próxima![/dim]")
            break

        if not phrase:
            continue
        if phrase.lower() in ("!sair", "sair", "!exit", "quit"):
            console.print("[dim]Até a próxima![/dim]")
            break
        if phrase.lower() in ("!ajuda", "help", "ajuda"):
            console.print(
                "[dim]Ex.: 'Find all files larger than 100MB' | 'Liste os arquivos desta pasta' "
                "| 'Encontre arquivos maiores que 1MB'[/dim]"
            )
            continue

        with console.status("[cyan]traduzindo para comando...[/cyan]"):
            proposta = generator.generate(phrase, shell=shell_name)

        comando = proposta["comando"]
        if not comando.strip():
            console.print(f"[yellow]{proposta['explicacao']}[/yellow]")
            continue

        console.print(
            Panel.fit(
                comando,
                border_style="cyan",
                title="Comando proposto",
            )
        )
        console.print(f"[dim]{proposta['explicacao']}[/dim]")
        risco_cor = RISCO_CORES.get(proposta["risco"], "yellow")
        console.print(f"[{risco_cor}]Risco: {proposta['risco'].upper()}[/{risco_cor}]")

        if not _ask_confirmation(proposta["risco"]):
            console.print("[dim]Cancelado — nada foi executado.[/dim]")
            continue

        with console.status("[cyan]executando...[/cyan]"):
            returncode, stdout, stderr = run_command(comando)

        _show_output(returncode, stdout, stderr)


if __name__ == "__main__":
    app()
