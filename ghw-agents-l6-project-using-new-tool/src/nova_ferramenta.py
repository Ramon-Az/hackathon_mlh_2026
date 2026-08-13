# L6 Project Using a New Tool - nova_ferramenta.py

"""Módulo adapter para integração da nova ferramenta.

Este módulo implementa o padrão Adapter para integrar uma nova tecnologia/tool
ao agente existente, seguindo as convenções do framework agentlocal.

O adapter converte chamadas do agente para o formato da nova ferramenta,
garantindo compatibilidade e isolamento de mudanças.
"""

from typing import Dict, Any, Optional, List
import json
import abc


# Interface base para todos os adapters de nova ferramenta
class NovaFerramentaAdapter(abc.ABC):
    """Classe abstrata base para adapters de nova ferramenta."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._validado = False
    
    @abc.abstractmethod
    def executar(self, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a ferramenta com os parâmetros fornecidos.
        
        Args:
            parametros: Dicionário com parâmetros da operação
            
        Returns:
            Dict com resultado da execução
        """
        pass
    
    @abc.abstractmethod
    def validar(self) -> bool:
        """Valida se a ferramenta está configurada corretamente.
        
        Returns:
            True se a ferramenta está pronta para uso
        """
        pass
    
    @property
    @abc.abstractmethod
    def nome(self) -> str:
        """Retorna o nome da ferramenta."""
        pass
    
    @property
    @abc.abstractmethod
    def descricao(self) -> str:
        """Retorna a descrição da ferramenta."""
        pass


# Exemplo de adapter template - ser substituído pela ferramenta real
class AdapterTemplate(NovaFerramentaAdapter):
    """Adapter template para nova ferramenta - exemplo de implementação.
    
    Este adapter serve como modelo para quando Ramon adicionar uma nova ferramenta.
    A estrutura segue o pattern do agentlocal com injeção de dependências.
    """
    
    @property
    def nome(self) -> str:
        return "Ferramenta Template"
    
    @property
    def descricao(self) -> str:
        return "Adapter template - substituir pela nova ferramenta real"
    
    def validar(self) -> bool:
        """Valida configurações mínimas."""
        # Verificar se config essencial está presente
        return bool(self.config)
    
    def executar(self, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """Executa operação da ferramenta template."""
        # Exemplo de retorno padrão
        return {
            "sucesso": True,
            "resultado": {
                "mensagem": "Operação do adapter template concluída",
                "parametros": parametros,
                "ferramenta": self.nome,
            },
            "metadados": {
                "timestamp": __import__("datetime").datetime.now().isoformat(),
                "adapter": self.nome,
            }
        }


# Registry de adapters disponíveis - usado pelo agentlocal
REGISTRY_ADAPTERS: Dict[str, NovaFerramentaAdapter] = {}

def registrar_adapter(nome: str, adapter: NovaFerramentaAdapter) -> None:
    """Registra um adapter no registry global.
    
    Args:
        nome: Nome da ferramenta
        adapter: Instância do adapter
    """
    REGISTRY_ADAPTERS[nome] = adapter
    print(f"🔧 Adapter registrado: {nome}")


def obter_adapter(nome: str) -> Optional[NovaFerramentaAdapter]:
    """Obtém adapter pelo nome do registro.
    
    Args:
        nome: Nome da ferramenta
        
    Returns:
        Instância do adapter ou None se não encontrado
    """
    return REGISTRY_ADAPTERS.get(nome)


def listar_adapters() -> List[str]:
    """Lista todos os adapters registrados."""
    return list(REGISTRY_ADAPTERS.keys())


# Função helper para criar adapter a partir de config
def criar_adapter(nome_ferramenta: str, config: Dict[str, Any]) -> Optional[NovaFerramentaAdapter]:
    """Cria adapter baseado no nome e configuração.
    
    Args:
        nome_ferramenta: Nome da ferramenta
        config: Dicionário com configurações
        
    Returns:
        Instância do adapter ou None se não conseguir criar
    """
    # Tentar obter do registry
    adapter = obter_adapter(nome_ferramenta)
    if adapter:
        return adapter
    
    # Factory baseada em nome (será expandido conforme novas ferramentas são adicionadas)
    print(f"⚠️  Adapter '{nome_ferramenta}' não encontrado no registry.")
    print(f"   Available: {listar_adapters()}")
    
    # Retornar adapter template como fallback provisório
    from .nova_ferramenta import AdapterTemplate
    template = AdapterTemplate(config)
    registrar_adapter(nome_ferramenta, template)
    return template