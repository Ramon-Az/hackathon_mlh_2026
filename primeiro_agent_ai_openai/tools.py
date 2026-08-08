"""Ferramentas (tools) do agente.

Cada ferramenta tem duas partes:
- `definicoes`: o JSON que o modelo enxerga (nome, descrição e parâmetros).
- a função Python: o que o programa realmente executa quando o modelo pede.
"""
import ast
import datetime
import operator
from pathlib import Path

NOTAS_PATH = Path(__file__).parent / "anotacoes.txt"


def obter_hora_atual() -> str:
    """Ferramenta sem parâmetros: devolve a data e hora atuais."""
    agora = datetime.datetime.now()
    return agora.strftime("Agora são %H:%M:%S do dia %d/%m/%Y.")


_OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _avaliar(no) -> int | float:
    """Percorre a árvore da expressão executando só operações permitidas.

    Isso evita o uso de eval() direto, que executaria qualquer código.
    """
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return no.value
    if isinstance(no, ast.BinOp) and type(no.op) in _OPERADORES:
        return _OPERADORES[type(no.op)](_avaliar(no.left), _avaliar(no.right))
    if isinstance(no, ast.UnaryOp) and type(no.op) in _OPERADORES:
        return _OPERADORES[type(no.op)](_avaliar(no.operand))
    raise ValueError("expressão não suportada")


def calcular(expressao: str) -> str:
    """Calcula uma expressão aritmética simples de forma segura."""
    try:
        arvore = ast.parse(expressao, mode="eval")
        return str(_avaliar(arvore.body))
    except Exception as erro:
        return f"Não consegui calcular: {erro}"


def salvar_anotacao(conteudo: str) -> str:
    """Grava uma anotação em um arquivo local."""
    carimbo = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    with NOTAS_PATH.open("a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{carimbo}] {conteudo}\n")
    return f"Anotação salva: {conteudo}"


definicoes = [
    {
        "type": "function",
        "name": "obter_hora_atual",
        "description": "Retorna a data e a hora atuais.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "calcular",
        "description": "Calcula uma expressão aritmética simples. Ex.: '10 * (2 + 3)'.",
        "parameters": {
            "type": "object",
            "properties": {
                "expressao": {
                    "type": "string",
                    "description": "A expressão aritmética a ser calculada.",
                },
            },
            "required": ["expressao"],
        },
    },
    {
        "type": "function",
        "name": "salvar_anotacao",
        "description": "Salva um texto de anotação em um arquivo local.",
        "parameters": {
            "type": "object",
            "properties": {
                "conteudo": {
                    "type": "string",
                    "description": "O texto da anotação a salvar.",
                },
            },
            "required": ["conteudo"],
        },
    },
]
