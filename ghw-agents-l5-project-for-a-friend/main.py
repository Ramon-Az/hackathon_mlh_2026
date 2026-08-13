"""CLI interativa do Project for a Friend (desafio L5 GHW Agents 2026).

Agente de IA personalizado para um amigo, com perfil de investidor.

Uso:
    python main.py                          # perfil moderado (padrão)
    python main.py --nome "Joao" --perfil arrojado
    python main.py --perfil conservador --provedor ollama
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from src import dados as dados_modulo
from src.agente import AgenteFriend

app = typer.Typer(add_completion=False)
console = Console()

PERFIS = ", ".join(AgenteFriend.PERFIS_VALIDOS)


@app.command()
def main(
    nome: str = typer.Option("Joao", "--nome", "-n", help="Nome do amigo"),
    perfil: str = typer.Option("moderado", "--perfil", "-p", help=f"Perfil de investidor ({PERFIS})"),
    provedor: str = typer.Option("groq", "--provedor", help="Provedor de IA (openai/anthropic/gemini/groq/ollama)"),
) -> None:
    """Sessão interativa com o agente do amigo."""
    if perfil not in AgenteFriend.PERFIS_VALIDOS:
        console.print(f"[red]Perfil inválido: {perfil}. Use: {PERFIS}[/red]")
        raise typer.Exit(1)

    agente = AgenteFriend(nome_amigo=nome, perfil_investidor=perfil, provedor=provedor)

    # Carrega contexto do amigo se existir (perfil_investidor.json etc.)
    try:
        contexto = dados_modulo.get_contexto_amigo()
        if contexto:
            agente.carregar_contexto(contexto)
            console.print(f"[dim]Contexto carregado: {list(contexto.keys())}[/dim]")
    except Exception as e:
        console.print(f"[dim]Sem dados locais: {e}[/dim]")

    console.print(Panel(
        f"[bold cyan]L5 — Agente do {agente.nome_amigo}[/bold cyan]\n"
        f"Perfil: [yellow]{agente.perfil_investidor}[/yellow] | Provedor: {agente.provedor}/{agente.modelo}\n"
        "Comandos: !perfil | !sair",
        title="Project for a Friend",
    ))

    while True:
        try:
            msg = console.input("Você> ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Até![/dim]")
            raise typer.Exit()

        if not msg:
            continue
        if msg.lower() in ("!sair", "!exit", "sair"):
            console.print("[dim]Até![/dim]")
            break
        if msg.lower() in ("!perfil",):
            console.print(f"[yellow]Perfil atual: {agente.perfil_investidor}[/yellow]")
            continue

        try:
            resposta = agente.gerar_resposta(msg)
            console.print(resposta)
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")


if __name__ == "__main__":
    app()
