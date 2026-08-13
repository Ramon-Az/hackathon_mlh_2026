"""CLI do Project Using a New Tool (desafio L6 GHW Agents 2026).

Agente que integra novas ferramentas via padrão Adapter + registry.

Uso:
    python main.py listar                        # lista adapters registrados
    python main.py testar "Ferramenta Template" '{"acao": "demo"}'
    python main.py registrar                     # registra um adapter
"""

from __future__ import annotations

import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src import nova_ferramenta as nf
from src.nova_ferramenta import AdapterTemplate

app = typer.Typer(add_completion=False, help="Integra novas ferramentas via padrão Adapter.")
console = Console()


def _registrar_template() -> None:
    """Garante que o adapter de exemplo esteja sempre registrado."""
    if "template" not in nf.listar_adapters():
        nf.registrar_adapter("template", AdapterTemplate({"ativo": True}))
        nf.registrar_adapter("Ferramenta Template", AdapterTemplate({"ativo": True}))


@app.command()
def listar() -> None:
    """Lista os adapters registrados."""
    _registrar_template()
    adapters = nf.listar_adapters()
    if not adapters:
        console.print("[yellow]Nenhum adapter registrado ainda.[/yellow]")
        return

    table = Table(title="Adapters registrados")
    table.add_column("Nome", style="cyan")
    for nome in adapters:
        adapter = nf.obter_adapter(nome)
        desc = getattr(adapter, "descricao", "") if adapter else ""
        table.add_row(nome, desc)
    console.print(table)


@app.command()
def testar(
    nome: str = typer.Argument(..., help="Nome do adapter"),
    parametros_json: str = typer.Argument("{}", help="Parâmetros em JSON"),
) -> None:
    """Testa a execução de um adapter com parâmetros JSON."""
    _registrar_template()
    adapter = nf.obter_adapter(nome)
    if not adapter:
        console.print(f"[red]Adapter não encontrado: {nome}[/red]")
        raise typer.Exit(1)

    try:
        parametros = json.loads(parametros_json)
    except json.JSONDecodeError:
        console.print("[red]❌ Parâmetros inválidos. Deve ser um JSON válido.[/red]")
        raise typer.Exit(1)

    console.print(Panel(f"[bold]Adapter:[/bold] {adapter.nome} | Parâmetros: {parametros}", title="Teste"))
    resultado = adapter.executar(parametros)
    console.print(json.dumps(resultado, indent=2, ensure_ascii=False))


@app.command()
def registrar() -> None:
    """Registra um novo adapter (exemplo)."""
    nf.registrar_adapter("novo-adapter", AdapterTemplate({"ativo": True}))
    console.print("[green]✅ Adapter registrado: novo-adapter[/green]")


def main() -> None:
    """Ponto de entrada sem argumentos (lista adapters)."""
    listar()


if __name__ == "__main__":
    app()
