# L5 Project for a Friend

"""Agente de IA personalizado para um amigo/usuário específico.

Este módulo implementa um agente que:
1. Carrega perfil do usuário ("amigo") com preferências e contexto
2. Fornece assistência contextualizada baseada no perfil
3. Usa provedores de IA compatíveis com as preferências do amigo
4. Mantém disclaimers e limitações claras

Padrões:
- Dados do amigo em arquivos JSON/CSV dedicados
- Múltiplos provedores de IA (OpenAI, Anthropic, Gemini, Groq, Ollama)
- Filtro por perfil de risco (conservador/moderado/arrojado)
- Anti-alucinação com base de conhecimento restrita
- Disclaimers obrigatórios em todas as respostas
"""

# Módulos principais
from . import dados, agente