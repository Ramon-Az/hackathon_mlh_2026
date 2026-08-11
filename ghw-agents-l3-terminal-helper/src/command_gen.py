"""Tradução de linguagem natural para comandos de terminal via Groq.

O LLM recebe a frase do usuário (inglês ou português) e o shell alvo
(PowerShell no Windows, bash no Linux) e devolve um JSON estruturado:

    {"comando": "...", "explicacao": "...", "risco": "baixo|medio|alto"}

O nível de risco é usado pelo CLI para exigir confirmação reforçada.
"""

from __future__ import annotations

import json
import os
import platform
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """Você é um assistente que traduz frases em linguagem natural
(inglês OU português) para comandos de terminal. Você NUNCA executa comandos —
apenas os propõe.

Responda SOMENTE com um JSON válido neste formato (sem markdown, sem texto fora):
{"comando": "...", "explicacao": "...", "risco": "baixo" | "medio" | "alto"}

Regras:
- Gere o comando para o shell indicado pelo usuário.
- A explicação é uma frase curta sobre o que o comando faz.
- Classifique o risco:
  - baixo: leitura/consulta (listar, ver, buscar)
  - medio: altera estado de forma reversível (criar arquivo, mover, instalar)
  - alto: destrutivo, irreversível ou que afeta o sistema (rm -rf, formatar,
    apagar tudo, desligar, derrubar serviços, alterar permissões sensíveis)
- Se a frase não pedir nenhuma ação de terminal (ex.: uma saudação ou pergunta
  sem comando), devolva {"comando": "", "explicacao": "<o que você entendeu>", "risco": "baixo"}.
- NÃO invente comandos que não resolvam o pedido. Se não tiver certeza, proponha
  o comando mais conservador.
- Se o pedido for claramente malicioso ou impossível, explique no campo
  "explicacao" e devolva comando vazio.
"""


def detect_shell() -> str:
    """Nome do shell alvo (para o LLM gerar a sintaxe certa)."""
    if platform.system() == "Windows":
        return "PowerShell (Windows)"
    return "bash (Linux/macOS)"


def _extract_json(raw: str) -> dict:
    """Parse do JSON retornado pelo LLM, tolerante a markdown/ruído."""
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {"comando": "", "explicacao": "Falha ao interpretar a resposta do LLM.", "risco": "alto"}


class CommandGenerator:
    """Gera comandos de terminal a partir de frases em linguagem natural."""

    def __init__(self) -> None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY não encontrada. Crie o arquivo .env a partir de .env.example."
            )
        self.client = OpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)

    def generate(self, phrase: str, shell: str | None = None) -> dict:
        """Recebe a frase e devolve dict {comando, explicacao, risco}."""
        shell = shell or detect_shell()

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Shell alvo: {shell}\nFrase: {phrase}",
                    },
                ],
                temperature=0.1,
            )
            raw = (response.choices[0].message.content or "").strip()
        except Exception as exc:
            return {"comando": "", "explicacao": f"Erro ao chamar o LLM: {exc}", "risco": "alto"}

        data = _extract_json(raw)
        # normaliza o campo risco
        risco = str(data.get("risco", "baixo")).lower()
        if risco not in ("baixo", "medio", "alto"):
            risco = "baixo"
        return {
            "comando": str(data.get("comando", "")),
            "explicacao": str(data.get("explicacao", "")),
            "risco": risco,
        }
