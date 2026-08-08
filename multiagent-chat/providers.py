"""
Adaptadores para cada provedor de LLM. Cada função recebe o histórico de
mensagens (formato OpenAI: [{"role": ..., "content": ...}, ...]) e retorna
uma tupla (texto_da_resposta, tokens_usados_total).
"""
import os


def _openai_chat(model: str, system_prompt: str, messages: list[dict]) -> tuple[str, int]:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    full_messages = [{"role": "system", "content": system_prompt}, *messages]
    resp = client.chat.completions.create(model=model, messages=full_messages)
    texto = resp.choices[0].message.content or ""
    tokens = resp.usage.total_tokens if resp.usage else 0
    return texto, tokens


def _anthropic_chat(model: str, system_prompt: str, messages: list[dict]) -> tuple[str, int]:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model=model,
        system=system_prompt,
        max_tokens=1024,
        messages=messages, # pyright: ignore[reportArgumentType]
    )
    texto = "".join(block.text for block in resp.content if block.type == "text")
    tokens = resp.usage.input_tokens + resp.usage.output_tokens
    return texto, tokens


PROVIDERS = {
    "openai": _openai_chat,
    "anthropic": _anthropic_chat,
}


def call_provider(provider: str, model: str, system_prompt: str, messages: list[dict]) -> tuple[str, int]:
    if provider not in PROVIDERS:
        raise ValueError(f"Provider desconhecido: {provider}")
    return PROVIDERS[provider](model, system_prompt, messages)
