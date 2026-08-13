# L5 Project for a Friend - agente.py

"""Módulo central do agente personalizado para o amigo.

Este agente:
1. Carrega contexto do amigo (dados, perfil, histórico)
2. Fornece assistência contextualizada baseada no perfil
3. Usa provedores de IA compatíveis com as preferências
4. Mantém disclaimers e limitações claras
5. Filtra recomendações baseadas na base de conhecimento restrita
"""

from typing import Dict, Optional, Any, List
from . import dados as dados_modulo
from .dados import PerfilInvestidor


class AgenteFriend:
    """Agente de IA personalizado para assistência a um amigo."""
    
    # Provedores disponíveis
    PROVEDORES = ["openai", "anthropic", "gemini", "groq", "ollama"]
    
    # Perfis de risco aceitos
    PERFIS_VALIDOS = ["conservador", "moderado", "arrojado"]
    
    def __init__(
        self,
        nome_amigo: str,
        perfil_investidor: str = "moderado",
        provedor: str = "groq",
        modelo: str = "llama-3.3-70b-versatile",
        base_conhecimento: Optional[Dict] = None,
    ):
        self.nome_amigo = nome_amigo
        self.perfil_investidor = perfil_investidor
        self.provedor = provedor
        self.modelo = modelo
        self.base_conhecimento = base_conhecimento or {}
        
        # Validar configurações
        self._validar_config()
    
    def _validar_config(self) -> None:
        """Valida a configuração do agente."""
        if self.perfil_investidor not in self.PERFIS_VALIDOS:
            raise ValueError(
                f"Perfil inválido: {self.perfil_investidor}. "
                f"Use um de: {', '.join(self.PERFIS_VALIDOS)}"
            )
        
        if self.provedor not in self.PROVEDORES:
            print(f"⚠️  Provedor '{self.provedor}' pode não estar disponível. "
                  f"Use um de: {', '.join(self.PROVEDORES)}")
    
    def carregar_contexto(self, contexto: Dict[str, Any]) -> None:
        """Carrega contexto do amigo.
        
        Atualiza a base de conhecimento do agente com dados do amigo.
        """
        self.base_conhecimento.update(contexto)
        print(f"📋 Contexto carregado para {self.nome_amigo}")
        print(f"   - Perfil: {self.perfil_investidor}")
        print(f"   - Provedor: {self.provedor}/{self.modelo}")
    
    def get_perfil(self) -> str:
        """Retorna o perfil de investidor do amigo."""
        return self.perfil_investidor
    
    def set_provedor(self, provedor: str) -> None:
        """Altera o provedor de IA."""
        self.provedor = provedor
        print(f"🔄 Provedor alterado para: {self.provedor}")
    
    def set_modelo(self, modelo: str) -> None:
        """Altera o modelo de IA."""
        self.modelo = modelo
        print(f"🔄 Modelo alterado para: {self.modelo}")
    
    def gerar_resposta(
        self,
        mensagem: str,
        contexto_adicional: Optional[Dict] = None,
    ) -> str:
        """Gera uma resposta contextualizada para o amigo.
        
        Este é o método principal do agente. Ele:
        1. Analisa a mensagem considerando o perfil do amigo
        2. Filtra recomendações baseadas na base de conhecimento
        3. Adiciona disclaimers apropriados ao perfil
        4. Retorna resposta formatada
        
        Args:
            mensagem: Mensagem do usuário
            contexto_adicional: Contexto extra (dados atuais, etc.)
            
        Returns:
            Resposta contextualizada do agente
        """
        # Buildar contexto completo
        contexto = self._build_contexto(mensagem, contexto_adicional)
        
        # Filtrar baseado no perfil
        resposta = self._filtrar_por_perfil(contexto)
        
        # Adicionar disclaimer
        resposta_com_disclaimer = self._adicionar_disclaimer(resposta)
        
        return resposta_com_disclaimer
    
    def _build_contexto(
        self, 
        mensagem: str, 
        adicional: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Constrói contexto completo para a resposta."""
        base = dados_modulo.get_contexto_amigo()
        
        # Mesclar com adicional se fornecido
        if adicional:
            base.update(adicional)
        
        return {
            "nome_amigo": self.nome_amigo,
            "perfil": self.perfil_investidor,
            "mensagem": mensagem,
            "conhecimento_base": self.base_conhecimento,
            "contexto_amigo": base,
        }
    
    def _filtrar_por_perfil(self, contexto: Dict[str, Any]) -> str:
        """Filtra e gera resposta baseada no perfil do amigo."""
        perfil = contexto["perfil"]
        mensagem = contexto["mensagem"]
        nome = contexto["nome_amigo"]
        conhecimento = contexto["conhecimento_base"]
        
        # Resposta baseada no perfil
        if perfil == PerfilInvestidor.CONSERVADOR:
            return self._resposta_conservadora(mensagem, nome, conhecimento)
        elif perfil == PerfilInvestidor.ARROJADO:
            return self._resposta_arrojada(mensagem, nome, conhecimento)
        else:  # MODERADO
            return self._resposta_moderada(mensagem, nome, conhecimento)
    
    def _resposta_conservadora(self, mensagem: str, nome: str, conhecimento: Dict) -> str:
        """Gera resposta conservadora (foco em segurança, baixo risco)."""
        # Baseia recomendações em ativos conhecidos e de baixo risco
        observacao = conhecimento.get("observacoes", "")
        
        return (
            f"Olá {nome}, considerando seu perfil **conservador**, aqui estão "
            f"recomendações mais seguras:\n\n"
            f"- Focar em ativos de renda fixa e diversificação\n"
            f"- Evitar posições altamente voláteis sem análise prévia\n"
            f"- Manter reserva de emergência adequada\n"
            f"- Qualquer investimento deve ser alinhado aos seus objetivos de longo prazo\n\n"
            f"{observacao if observacao else ''}"
        )
    
    def _resposta_arrojada(self, mensagem: str, nome: str, conhecimento: Dict) -> str:
        """Gera resposta arrojada (foco em crescimento, maior risco)."""
        observacao = conhecimento.get("observacoes", "")
        
        return (
            f"Olá {nome}, considerando seu perfil **arrojado**, aqui estão "
            f"oportunidades de crescimento:\n\n"
            f"- Posicionamentos em setores de crescimento e inovação\n"
            f"- Alocação em ativos de maior volatilidade (com cautela)\n"
            f"- Estratégias de timing de mercado (com gestão de risco)\n"
            f"- Considere balanceamento com ativos mais seguros\n\n"
            f"{observacao if observacao else ''}"
        )
    
    def _resposta_moderada(self, mensagem: str, nome: str, conhecimento: Dict) -> str:
        """Gera resposta moderada (balanceado entre risco e segurança)."""
        observacao = conhecimento.get("observacoes", "")
        
        return (
            f"Olá {nome}, considerando seu perfil **moderado**, aqui está um "
            f"balanceamento entre segurança e crescimento:\n\n"
            f"- Mix equilibrado entre renda fixa e variável\n"
            f"- Diversificação setorial e geográfica\n"
            f"- Revisão periódica da alocação (trimestral/semestral)\n"
            f"- Manter disciplina de investimento a longo prazo\n\n"
            f"{observacao if observacao else ''}"
        )
    
    def _adicionar_disclaimer(self, resposta: str) -> str:
        """Adiciona disclaimer obrigatório à resposta.
        
        Todos os agentes devem incluir disclaimers claros sobre:
        - Limitações do agente
        - Não constitute aconselhamento financeiro
        - Importância de consultar profissional qualificado
        """
        disclaimer = (
            "\n\n"
            "--- \n"
            "⚠️ **Disclaimer**: Este agente fornece sugestões baseadas em "
            "padrões e dados disponíveis, mas não constitui aconselhamento "
            "financeiro ou profissional. Para decisões financeiras, "
            "consulte sempre um profissional qualificado. O agente não "
            "responde por decisões tomadas com base nestas sugestões.\n"
            "---"
        )
        
        return resposta + disclaimer
    
    def recomendar_acoes(
        self, 
        acoes_disponiveis: List[Dict[str, Any]], 
        limite: int = 5
    ) -> List[Dict[str, Any]]:
        """Recomenda ações baseadas no perfil e base de conhecimento.
        
        Args:
            acoes_disponiveis: Lista de dicionários com info das ações
            limite: Número máximo de recomendações
            
        Returns:
            Lista filtrada e classificada de recomendações
        """
        perfil = self.perfil_investidor
        recomendacoes = []
        
        for acao in acoes_disponiveis[:20]:  # Limitar busca
            # Filtro básico por perfil
            if perfil == PerfilInvestidor.CONSERVADOR:
                # Ações de empresas estabelecidas, baixo beta
                if acao.get("risco", "alto") == "baixo":
                    recomendacoes.append(acao)
            elif perfil == PerfilInvestidor.ARROJADO:
                # Todas as ações consideradas, com preferência para crescimento
                recomendacoes.append(acao)
            else:  # MODERADO
                # Mix: metade de risco baixo, metade moderado
                if acao.get("risco") in ("baixo", "moderado"):
                    recomendacoes.append(acao)
        
        # Ordenar e limitar
        recomendacoes.sort(key=lambda x: x.get("potencial", 0), reverse=True)
        return recomendacoes[:limite]
    
    def executar_analise(
        self, 
        simbolos: List[str],
        incluir_historico: bool = True
    ) -> Dict[str, Any]:
        """Executa análise técnica/fundamental de símbolos.
        
        Args:
            simbolos: Lista de códigos de ações (ex: ['PETR4', 'VALE3'])
            incluir_historico: Se deve incluir histórico de transações do amigo
            
        Returns:
            Dict com resultados da análise
        """
        resultado = {
            "amigo": self.nome_amigo,
            "perfil": self.perfil_investidor,
            "analises": {},
            "simbolos_analisados": len(simbolos),
        }
        
        for simbolo in simbolos:
            # Análise simulada/baseada em dados
            analise = {
                "simbolo": simbolo,
                "perfil_compatibilidade": self.perfil_investidor,
                "recomendacao": "consulte_profissional",
                "riesgo": "medium",
            }
            
            # Se tiver histórico, pode enriquecer
            if incluir_historico:
                contexto = dados_modulo.carregar_historico()
                if contexto:
                    analise["historico_considerado"] = True
                else:
                    analise["historico_considerado"] = False
            
            resultado["analises"][simbolo] = analise
        
        return resultado


def main() -> None:
    """Ponto de entrada CLI para o agente L5."""
    import sys
    import json
    
    print("=== L5 Project for a Friend: Agente Personalizado ===\n")
    
    # Coletar parâmetros
    nome = sys.argv[1] if len(sys.argv) > 1 else "João"
    perfil = sys.argv[2] if len(sys.argv) > 2 else "moderado"
    provedor = sys.argv[3] if len(sys.argv) > 3 else "groq"
    modelo = sys.argv[4] if len(sys.argv) > 4 else "llama-3.3-70b-versatile"
    
    # Criar agente
    agente = AgenteFriend(
        nome_amigo=nome,
        perfil_investidor=perfil,
        provedor=provedor,
        modelo=modelo,
    )
    
    # Carregar contexto se houver arquivos
    contexto = dados_modulo.get_contexto_amigo()
    if contexto["nome"]:
        agente.carregar_contexto(contexto)
    
    # Loop de interação
    print(f"\nAgente pronto para {nome} (perfil: {perfil})")
    print("Digite 'sair' para encerrar ou uma pergunta para o agente.\n")
    
    while True:
        try:
            mensagem = input("> ")
            if mensagem.lower() in ('sair', 'exit', 'quit'):
                print("👋 Até!")
                break
            
            resposta = agente.gerar_resposta(mensagem)
            print("\n" + "=" * 60)
            print(resposta)
            print("=" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Até!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")