"""Agente que gera mensagens de commit e resumos de PR via Groq.

Recebe o diff real do repositório (coletado por `git_diff`) e devolve
texto pronto para usar: mensagem de commit conventional ou resumo de PR.
Segue o idioma/estilo dos commits recentes do próprio repositório
(detectado em `git_diff.detect_language` ou forçado via `--idioma`).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT_PT = """Você é um agente especialista em git (Git Commit & PR Agent).
Analise o diff fornecido pelo usuário e gere texto pronto para uso.

Regras:
- **Mensagem de commit**: UMA linha principal seguindo Conventional Commits
  (feat:, fix:, refactor:, docs:, chore:, test:, build:, style:). Se a mudança
  tiver partes distintas, adicione um corpo curto de 2-4 bullets (formato
  "- bullet").
- **Resumo de PR**: título em UMA linha + 3-5 bullets com o que mudou e por
  quê + seção final "## Teste" com 1-2 sugestões de verificação.
- Seja conciso e objetivo. NÃO liste nomes de arquivos se não agregar valor.
- NÃO invente mudanças que não estejam no diff. NÃO use placeholders.
"""

SYSTEM_PROMPT_EN = """You are a git expert agent (Git Commit & PR Agent).
Analyze the diff provided by the user and generate ready-to-use text.

Rules:
- **Commit message**: ONE main line following Conventional Commits
  (feat:, fix:, refactor:, docs:, chore:, test:, build:, style:). If the
  change has distinct parts, add a short body of 2-4 bullets (format
  "- bullet").
- **PR summary**: one-line title + 3-5 bullets on what changed and why +
  a final "## Test" section with 1-2 verification suggestions.
- Be concise and objective. Do NOT list file names unless they add value.
- Do NOT invent changes that are not in the diff. Do NOT use placeholders.
- IMPORTANT: the diff may contain comments/docstrings in another language
  (e.g. Portuguese). Ignore the language of the diff content and ALWAYS
  reply in English.
"""

TASK_COMMIT_PT = "Gere uma MENSAGEM DE COMMIT (linha principal + corpo se necessário)."
TASK_COMMIT_EN = "Generate a COMMIT MESSAGE (main line + body if needed)."
TASK_PR_PT = "Gere um RESUMO DE PULL REQUEST: título + bullets + seção ## Teste."
TASK_PR_EN = "Generate a PULL REQUEST SUMMARY: title + bullets + a ## Test section."


class CommitAgent:
    """Gera mensagens de commit / resumos de PR a partir do diff."""

    def __init__(self) -> None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY não encontrada. Crie o arquivo .env a partir de .env.example."
            )
        self.client = OpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)

    def _build_context(
        self,
        diff: str,
        status: str,
        recent_commits: str,
        branch: str,
    ) -> str:
        return (
            f"Branch atual: {branch}\n\n"
            f"## Status (git status --short)\n{status or '(vazio)'}\n\n"
            f"## Commits recentes (estilo do repo)\n{recent_commits or '(repo sem commits)'}\n\n"
            f"## Diff\n{diff or '(diff vazio)'}"
        )

    def generate(
        self,
        *,
        diff: str,
        status: str,
        recent_commits: str,
        branch: str,
        pr: bool = False,
        language: str = "auto",
    ) -> str:
        """Gera mensagem de commit (pr=False) ou resumo de PR (pr=True).

        `language` aceita 'auto' (detecta do repo), 'en' ou 'pt'.
        Todo o prompt é montado no idioma alvo para o LLM não "vazar"
        para o idioma das instruções.
        """
        if not diff.strip():
            raise ValueError("Diff vazio — não há o que gerar. Faça mudanças antes de rodar.")

        if language == "auto":
            from src.git_diff import detect_language

            language = detect_language(recent_commits)

        en = language == "en"
        system = SYSTEM_PROMPT_EN if en else SYSTEM_PROMPT_PT
        task = (TASK_PR_EN if pr else TASK_COMMIT_EN) if en else (
            TASK_PR_PT if pr else TASK_COMMIT_PT
        )
        context = self._build_context(diff, status, recent_commits, branch)

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"{task}\n\n{context}"},
                ],
                temperature=0.3,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as exc:
            return f"(erro ao chamar o LLM: {exc})"
