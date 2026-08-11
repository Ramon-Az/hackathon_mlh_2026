"""CLI do Git Commit & PR Agent (desafio L2 GHW Agents 2026).

Uso:
    python main.py                # mensagem de commit (diff do working tree)
    python main.py --staged       # mensagem de commit (diff do index)
    python main.py --pr           # resumo de PR
    python main.py --pr --staged  # resumo de PR do staged
    python main.py --limit 150    # limita linhas do diff enviadas ao LLM
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from src import git_diff
from src.commit_agent import CommitAgent

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    staged: bool = typer.Option(
        False, "--staged", help="Usa o diff do index (git diff --staged)"
    ),
    pr: bool = typer.Option(
        False, "--pr", help="Gera resumo de PR em vez de mensagem de commit"
    ),
    limit: int = typer.Option(
        300, "--limit", help="Máximo de linhas do diff enviadas ao LLM"
    ),
    idioma: str = typer.Option(
        "auto", "--idioma", help="Idioma da resposta: auto (detecta do repo), en, pt"
    ),
) -> None:
    """Git Commit & PR Agent — lê o git diff local e gera mensagens com Groq."""

    console.print(
        Panel.fit(
            "[bold]Git Commit & PR Agent[/bold]\n"
            f"[dim]modo: {'resumo de PR' if pr else 'mensagem de commit'} | "
            f"{'staged' if staged else 'working tree'} | branch: {git_diff.get_current_branch()}[/dim]",
            border_style="cyan",
        )
    )

    with console.status("[cyan]analisando repositório...[/cyan]"):
        diff = git_diff.get_diff(staged=staged, limit=limit)
        status = git_diff.get_status()
        recent = git_diff.get_recent_commits(5)
        branch = git_diff.get_current_branch()

    if not diff:
        console.print("[yellow]Nada para analisar: diff vazio.[/yellow]")
        console.print("[dim]Faça alterações nos arquivos e rode novamente.[/dim]")
        raise typer.Exit(0)

    console.print("[dim]Arquivos afetados:[/dim]")
    for line in status.splitlines():
        console.print(f"  [dim]{line}[/dim]")

    with console.status("[cyan]gerando com o LLM...[/cyan]"):
        agent = CommitAgent()
        try:
            result = agent.generate(
                diff=diff,
                status=status,
                recent_commits=recent,
                branch=branch,
                pr=pr,
                language=idioma,
            )
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc

    title = "Resumo de PR" if pr else "Mensagem de commit"
    console.print()
    console.print(Panel(result, border_style="green", title=title))


if __name__ == "__main__":
    app()
