"""Agente com memória de longo prazo.

Loop clássico de agentes com function calling:
1. Monta o contexto: system prompt + memórias relevantes recuperadas do ChromaDB
2. Chama o LLM (Groq) — o modelo decide se usa tools (salvar/buscar memória)
3. Executa as tools e devolve os resultados
4. Repete até o modelo responder sem tools

Após cada turno, um LLM "extrator" analisa a conversa e transforma
informações úteis em fatos persistidos no ChromaDB (memória semântica).
"""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import BadRequestError, OpenAI

from src.memory import MemoryStore

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """Você é um assistente pessoal com memória de longo prazo.
Você lembra fatos e preferências do usuário entre sessões, graças a um banco
vetorial (ChromaDB). Use as ferramentas disponíveis:

- buscar_memoria: SEMPRE que o usuário perguntar algo sobre ele mesmo
  (nome, preferências, projetos, fatos passados), antes de responder.
- salvar_memoria: quando o usuário revelar uma preferência ou fato novo
  que valha a pena lembrar depois.

Regras:
- Se o usuário mencionar nome, linguagem, ferramentas, gostos, projetos ou
  qualquer fato pessoal, salve como memória.
- Responda de forma natural, curta e útil.
- Quando recuperar memórias, use-as na resposta com naturalidade."""

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "salvar_memoria",
            "description": "Salva um fato/preferência do usuário na memória de longo prazo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Fato em 1 frase, ex.: 'Usuário se chama João'",
                    }
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_memoria",
            "description": "Busca memórias relevantes na memória de longo prazo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Pergunta/assunto para buscar memórias relacionadas",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

EXTRACT_PROMPT = """Analise a conversa abaixo e extraia fatos duráveis sobre o
usuário que valham a pena lembrar em sessões futuras (nome, preferências,
linguagens, ferramentas, projetos, gostos, planos, dados pessoais).

Retorne SOMENTE uma lista de fatos, um por linha, sem numeração e sem
introdução. Cada fato deve ser uma frase objetiva começando com "Usuário".
Se não houver fatos novos relevantes, retorne a palavra "NENHUM".

Conversa:
"""


class LongTermMemoryAgent:
    """Agente que lembra do usuário entre sessões."""

    def __init__(self, memory_path: str = "data", session_id: str = "sessao-atual") -> None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY não encontrada. Crie o arquivo .env a partir de .env.example."
            )
        self.client = OpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)
        self.memory = MemoryStore(path=memory_path)
        self.session_id = session_id
        self.history: list[dict[str, str]] = []

    # ---------------------------------------------------------------- tools
    def _salvar_memoria(self, text: str) -> str:
        self.memory.add(text, kind="fact", session=self.session_id)
        return f"Memória salva: {text}"

    def _buscar_memoria(self, query: str) -> str:
        hits = self.memory.search(query, top_k=5)
        if not hits:
            return "Nenhuma memória encontrada."
        return "\n".join(f"- ({h['metadata'].get('ts', '?')}) {h['text']}" for h in hits)

    def _run_tool(self, name: str, args: dict[str, Any]) -> str:
        if name == "salvar_memoria":
            return self._salvar_memoria(args["text"])
        if name == "buscar_memoria":
            return self._buscar_memoria(args["query"])
        return f"Ferramenta desconhecida: {name}"

    # ------------------------------------------------------- ciclo principal
    def _llm_call(
        self, messages: list[dict[str, Any]], *, tool_choice: str = "auto"
    ) -> Any | None:
        """Chama o LLM com fallback para o erro intermitente `tool_use_failed`.

        O Groq às vezes gera chamada de função com sintaxe inválida
        (ex.: `buscar_memoria[]{"query": ...}` em vez de
        `buscar_memoria({"query": ...})`), o que retorna HTTP 400
        `tool_use_failed`. Nesse caso, re-tenta sem tools: o recall de
        memórias já está no system prompt, então a resposta ainda é útil.
        """
        try:
            return self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,  # type: ignore[reportArgumentType]
                tools=TOOLS,  # type: ignore[reportArgumentType]
                tool_choice=tool_choice,
            )
        except BadRequestError as exc:
            if getattr(exc, "code", None) == "tool_use_failed" or exc.status_code == 400:
                print("  [aviso] tool_use_failed detectado — re-tentando sem tools")
                try:
                    return self.client.chat.completions.create(
                        model=GROQ_MODEL,
                        messages=messages,  # type: ignore[reportArgumentType]
                    )
                except Exception as retry_exc:
                    print(f"  [erro] fallback sem tools falhou: {retry_exc}")
                    return None
            print(f"  [erro] BadRequestError: {exc}")
            return None
        except Exception as exc:
            print(f"  [erro] chamada LLM falhou: {exc}")
            return None

    def chat(self, user_message: str, max_turns: int = 8) -> str:
        """Envia mensagem do usuário, roda o loop de tools e retorna a resposta."""
        self.history.append({"role": "user", "content": user_message})

        # recall: injeta memórias relevantes no contexto
        recalled = self.memory.search(user_message, top_k=4)
        recall_text = (
            "\n".join(f"- {h['text']}" for h in recalled)
            if recalled
            else "(nenhuma memória relevante)"
        )
        system = f"{SYSTEM_PROMPT}\n\n## Memórias relevantes recuperadas:\n{recall_text}"

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system},
            *self.history,
        ]

        final_answer = ""
        for _ in range(max_turns):
            response = self._llm_call(messages)
            if response is None:
                final_answer = "(falha na chamada ao LLM — tente novamente em instantes)"
                break
            message = response.choices[0].message

            if message.tool_calls:
                messages.append(message.model_dump(exclude_none=True))
                for call in message.tool_calls:
                    args = json.loads(call.function.arguments or "{}")  # type: ignore
                    result = self._run_tool(call.function.name, args)  # type: ignore
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": result,
                        }
                    )
                continue

            final_answer = message.content or ""
            self.history.append({"role": "assistant", "content": final_answer})
            break

        if not final_answer:
            final_answer = "(o agente não respondeu — verifique o provider/modelo)"

        # pós-turno: extrai fatos novos e persiste na memória semântica
        self._extract_and_store()
        return final_answer

    # ------------------------------------------------------- memória semântica
    def _extract_and_store(self) -> list[str]:
        """Pede a um LLM extrator para transformar o turno em fatos duráveis."""
        transcript = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in self.history[-4:]
        )
        if not transcript.strip():
            return []

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": EXTRACT_PROMPT + transcript},
                ],
                temperature=0.0,
            )
            raw = (response.choices[0].message.content or "").strip()
        except Exception as exc:  # extração não pode derrubar o chat
            print(f"  [aviso] extração de fatos falhou: {exc}")
            return []

        facts = [
            line.strip("- ").strip()
            for line in raw.splitlines()
            if line.strip() and line.strip().upper() != "NENHUM"
        ]
        stored: list[str] = []
        for fact in facts:
            # dedup: pula fato que já existe com quase o mesmo sentido (semântico)
            similar = self.memory.search(fact, top_k=1)
            if similar and similar[0]["distance"] is not None and similar[0]["distance"] < 0.15:
                continue
            self.memory.add(fact, kind="fact", session=self.session_id)
            stored.append(fact)
        return stored
