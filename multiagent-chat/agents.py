"""
Gerencia a lista de agentes disponíveis e a troca automática entre eles
conforme a cota de tokens de cada um se esgota.
"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from providers import call_provider

CONFIG_PATH = Path(__file__).parent / "agents.config.json"


@dataclass
class Agent:
    id: str
    nome: str
    provider: str
    model: str
    api_key_env: str
    token_quota: int
    system_prompt: str
    tokens_usados: int = 0

    @property
    def tokens_restantes(self) -> int:
        return max(self.token_quota - self.tokens_usados, 0)

    @property
    def esgotado(self) -> bool:
        return self.tokens_usados >= self.token_quota

    @property
    def chave_disponivel(self) -> bool:
        return bool(os.environ.get(self.api_key_env))


class AgentManager:
    def __init__(self, config_path: Path = CONFIG_PATH):
        data = json.loads(config_path.read_text(encoding="utf-8"))
        self.agents: list[Agent] = [Agent(**a) for a in data["agents"]]
        if not self.agents:
            raise ValueError("Nenhum agente configurado em agents.config.json")
        self.current_index = self._proximo_indice_disponivel(0)

    def _proximo_indice_disponivel(self, a_partir_de: int) -> int:
        """Procura, a partir do índice dado, o primeiro agente com chave de API
        configurada e cota de tokens não esgotada. Se nenhum servir, retorna
        o índice original (o chamador decide o que fazer)."""
        n = len(self.agents)
        for offset in range(n):
            idx = (a_partir_de + offset) % n
            agente = self.agents[idx]
            if agente.chave_disponivel and not agente.esgotado:
                return idx
        return a_partir_de

    @property
    def agente_atual(self) -> Agent:
        return self.agents[self.current_index]

    def todos_esgotados_ou_indisponiveis(self) -> bool:
        return all(a.esgotado or not a.chave_disponivel for a in self.agents)

    def status(self) -> list[dict]:
        return [
            {
                "id": a.id,
                "nome": a.nome,
                "provider": a.provider,
                "model": a.model,
                "token_quota": a.token_quota,
                "tokens_usados": a.tokens_usados,
                "tokens_restantes": a.tokens_restantes,
                "esgotado": a.esgotado,
                "chave_disponivel": a.chave_disponivel,
                "ativo": a.id == self.agente_atual.id,
            }
            for a in self.agents
        ]

    def responder(self, historico: list[dict]) -> dict:
        """Garante um agente válido, chama o provedor e atualiza a cota.
        Troca automaticamente de agente quando a cota atual se esgota."""
        # Se o agente atual já esgotou (ou perdeu a chave), tenta trocar antes de responder.
        if self.agente_atual.esgotado or not self.agente_atual.chave_disponivel:
            self.current_index = self._proximo_indice_disponivel(self.current_index)

        if self.todos_esgotados_ou_indisponiveis():
            return {
                "erro": True,
                "mensagem": (
                    "Todos os agentes esgotaram a cota de tokens ou estão sem "
                    "chave de API configurada. Ajuste agents.config.json ou "
                    "aumente as cotas para continuar."
                ),
                "agente": None,
            }

        agente = self.agente_atual
        agente_anterior_id = agente.id
        texto, tokens = call_provider(agente.provider, agente.model, agente.system_prompt, historico)
        agente.tokens_usados += tokens

        trocou = False
        # Se essa resposta esgotou a cota do agente, já prepara o próximo para a
        # próxima mensagem do usuário.
        if agente.esgotado:
            proximo = self._proximo_indice_disponivel(self.current_index + 1)
            if self.agents[proximo].id != agente_anterior_id:
                self.current_index = proximo
                trocou = True

        return {
            "erro": False,
            "mensagem": texto,
            "agente": agente.nome,
            "agente_id": agente.id,
            "tokens_usados_nesta_resposta": tokens,
            "tokens_restantes_agente": agente.tokens_restantes,
            "trocou_para": self.agente_atual.nome if trocou else None,
        }
