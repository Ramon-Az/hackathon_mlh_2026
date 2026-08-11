"""CLI do agente com memória de longo prazo.

Uso:
    python main.py                # inicia o chat
    python main.py --nova-sessao  # força sessão nova (demo de persistência)
    python main.py --memorias     # lista as memórias salvas
    python main.py --esquecer     # apaga todas as memórias
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from src.agent import LongTermMemoryAgent
from src.memory import MemoryStore

app = typer.Typer(add_completion=False)
console = Console()


def _show_memories(memory_path: str = "data") -> None:
    store = MemoryStore(path=memory_path)
    mems = store.all()
    if not mems:
        console.print("[yellow]Nenhuma memória salva ainda.[/yellow]")
        return
    console.print(Panel.fit(f"[bold cyan]Memórias salvas: {len(mems)}[/bold cyan]"))
    for m in mems:
        meta = m["metadata"]
        console.print(
            f"[green]{meta.get('ts', '?')}[/green] "
            f"[dim]({meta.get('kind', '?')})[/dim] {m['text']}"
        )


@app.command()
def main(
    nova_sessao: bool = typer.Option(False, "--nova-sessao", help="Força uma sessão nova"),
    memorias: bool = typer.Option(False, "--memorias", help="Lista memórias e sai"),
    esquecer: bool = typer.Option(False, "--esquecer", help="Apaga memórias e sai"),
) -> None:
    """Agente com memória de longo prazo (ChromaDB + Groq)."""

    if memorias:
        _show_memories()
        return
    if esquecer:
        MemoryStore(path="data").clear()
        console.print("[green]Memórias apagadas.[/green]")
        return

    import uuid

    session = f"sessao-{uuid.uuid4().hex[:8]}" if nova_sessao else "sessao-demo"
    agent = LongTermMemoryAgent(memory_path="data", session_id=session)

    console.print(
        Panel.fit(
            "[bold]Agente com Memória de Longo Prazo[/bold]\n"
            f"[dim]Sessão: {session}[/dim]\n"
            "[dim]Comandos: !memorias | !esquecer | !sair[/dim]",
            border_style="cyan",
        )
    )

    while True:
        try:
            user = console.input("[bold yellow]Você> [/bold yellow]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Até a próxima![/dim]")
            break

        if not user:
            continue
        if user.lower() in ("!sair","sair", "!exit", "quit"):
            console.print("[dim]Até a próxima![/dim]")
            break
        if user.lower() in ("!memorias", "memorias","memoria"):
            _show_memories()
            continue
        if user.lower() in("!esquecer", "esquecer"):
            agent.memory.clear()
            console.print("[green]Memórias apagadas.[/green]")
            continue

        with console.status("[cyan]pensando...[/cyan]"):
            answer = agent.chat(user)
        console.print(Panel(answer, border_style="green", title="Agente"))
        console.print(
            f"[dim]Memórias no banco: {agent.memory.count()}[/dim]"
        )


if __name__ == "__main__":
    app()
