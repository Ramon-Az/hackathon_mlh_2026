"""Primeiro agente de IA com OpenAI.

Um agente simples que usa function calling: o modelo enxerga as ferramentas
de tools.py e decide se deve chamá-las. O programa executa a ferramenta e
devolve o resultado ao modelo, que monta a resposta final.
"""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import *

load_dotenv()

MODELO = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_TURNOS = 10

SYSTEM_PROMPT = (
    "Você é um assistente útil. Responda sempre em português do Brasil.\n"
    "Use as ferramentas quando precisar de informações que você não sabe "
    "(hora atual, cálculos, anotações) em vez de inventar dados."
)

IMPLEMENTACOES = {
    "obter_hora_atual": obter_hora_atual,
    "calcular": calcular,
    "salvar_anotacao": salvar_anotacao,
}


def executar_tool(nome: str, argumentos: dict) -> str:
    """Chama a função Python correspondente e devolve o resultado em JSON."""
    try:
        resultado = IMPLEMENTACOES[nome](**argumentos)
    except TypeError as erro:
        return json.dumps({"erro": f"argumentos inválidos: {erro}"})
    return json.dumps(resultado, ensure_ascii=False)


def agente_responder(client: OpenAI, mensagens: list) -> str:
    """Loop do agente: chama o modelo e, se ele pedir uma ferramenta,
    executa e repete até o modelo dar a resposta final."""
    for _ in range(MAX_TURNOS):
        resposta = client.responses.create(
            model=MODELO,
            input=mensagens,
            tools=definicoes, # pyright: ignore[reportArgumentType]
            tool_choice="auto",
        )

        chamadas = [item for item in resposta.output if item.type == "function_call"]

        if not chamadas:
            return resposta.output_text

        mensagens.extend(resposta.output)
        for chamada in chamadas:
            argumentos = json.loads(chamada.arguments or "{}")
            resultado = executar_tool(chamada.name, argumentos)
            mensagens.append(
                {
                    "type": "function_call_output",
                    "call_id": chamada.call_id,
                    "output": resultado,
                }
            )

    return "Limite de turnos de ferramentas atingido."


def main():
    client = OpenAI()
    mensagens = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("Agente pronto! Digite 'sair' para encerrar.")
    print("-" * 40)
    while True:
        entrada = input("Você: ").strip()
        if not entrada:
            continue
        if entrada.lower() in {"sair", "exit", "quit"}:
            print("Até mais!")
            break

        mensagens.append({"role": "user", "content": entrada})
        texto = agente_responder(client, mensagens)
        print(f"Agente: {texto}\n")
        mensagens.append({"role": "assistant", "content": texto})


if __name__ == "__main__":
    main()
