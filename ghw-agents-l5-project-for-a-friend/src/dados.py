# L5 Project for a Friend - dados.py

"""Módulo de carregamento e gestão de dados do "amigo".

Este módulo lê os arquivos de perfil do usuário e fornece
contexto estruturado para o agente.

Arquivos esperados na pasta do projeto:
- perfil_investidor.json: perfil de risco (conservador/moderado/arrojado)
- transacoes.csv: histórico de transações (se aplicar)
- historico_atendimento.csv: histórico de atendimentos (se aplicar)
"""

import json
import csv
import os
from typing import Dict, Optional, Any, List
from pathlib import Path


# Caminhos relativos aos arquivos de dados
PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Caminhos específicos
PERFIL_PATH = DATA_DIR / "perfil_investidor.json"
TRANSACOES_PATH = DATA_DIR / "transacoes.csv"
HISTORICO_PATH = DATA_DIR / "historico_atendimento.csv"


class PerfilInvestidor:
    """Classificação de perfil de investidor."""
    
    CONSERVADOR = "conservador"
    MODERADO = "moderado"
    ARROJADO = "arrojado"
    
    def __init__(self, nome: str, perfil: str, observacoes: str = ""):
        self.nome = nome
        self.perfil = perfil
        self.observacoes = observacoes
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nome": self.nome,
            "perfil": self.perfil,
            "observacoes": self.observacoes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerfilInvestidor":
        return cls(
            nome=data.get("nome", ""),
            perfil=data.get("perfil", cls.MODERADO),
            observacoes=data.get("observacoes", ""),
        )


def carregar_perfil(nome_arquivo: str = None) -> Optional[PerfilInvestidor]:
    """Carrega perfil do investidor do arquivo JSON.
    
    Args:
        nome_arquivo: Caminho do arquivo (padrão: data/perfil_investidor.json)
        
    Returns:
        PerfilInvestidor ou None se arquivo não existir
    """
    path = Path(nome_arquivo) if nome_arquivo else PERFIL_PATH
    
    if not path.exists():
        print(f"⚠️  Arquivo {path} não encontrado. Criando perfil padrão...")
        return None
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return PerfilInvestidor.from_dict(data)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Erro ao carregar perfil: {e}")
        return None


def salvar_perfil(perfil: PerfilInvestidor, nome_arquivo: str = None) -> bool:
    """Salva perfil do investidor no arquivo JSON.
    
    Args:
        perfil: Instância de PerfilInvestidor
        nome_arquivo: Caminho do arquivo (padrão: data/perfil_investidor.json)
        
    Returns:
        True se salvo com sucesso
    """
    path = Path(nome_arquivo) if nome_arquivo else PERFIL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(perfil.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"✅ Perfil salvo em {path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar perfil: {e}")
        return False


def carregar_transacoes(nome_arquivo: str = None) -> List[Dict[str, Any]]:
    """Carrega histórico de transações do arquivo CSV.
    
    Args:
        nome_arquivo: Caminho do arquivo (padrão: data/transacoes.csv)
        
    Returns:
        Lista de dicts com dados de transação
    """
    path = Path(nome_arquivo) if nome_arquivo else TRANSACOES_PATH
    
    if not path.exists():
        print(f"⚠️  Arquivo {path} não encontrado. Nenhuma transação carregada.")
        return []
    
    transacoes = []
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                transacoes.append(dict(row))
        print(f"✅ Carregadas {len(transacoes)} transações de {path}")
        return transacoes
    except Exception as e:
        print(f"❌ Erro ao carregar transações: {e}")
        return []


def carregar_historico(nome_arquivo: str = None) -> List[Dict[str, Any]]:
    """Carrega histórico de atendimento do arquivo CSV.
    
    Args:
        nome_arquivo: Caminho do arquivo (padrão: data/historico_atendimento.csv)
        
    Returns:
        Lista de dicts com dados de atendimento
    """
    path = Path(nome_arquivo) if nome_arquivo else HISTORICO_PATH
    
    if not path.exists():
        print(f"⚠️  Arquivo {path} não encontrado. Nenhum histórico carregado.")
        return []
    
    historico = []
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                historico.append(dict(row))
        print(f"✅ Carregados {len(historico)} registros de {path}")
        return historico
    except Exception as e:
        print(f"❌ Erro ao carregar histórico: {e}")
        return []


def get_contexto_amigo(
    perfil_arquivo: str = None,
    transacoes_arquivo: str = None,
    historico_arquivo: str = None,
) -> Dict[str, Any]:
    """Coleta todo o contexto do amigo para o agente.
    
    Args:
        perfil_arquivo: Caminho do perfil JSON
        transacoes_arquivo: Caminho do CSV de transações
        historico_arquivo: Caminho do CSV de histórico
        
    Returns:
        Dict estruturado com todo o contexto
    """
    perfil = carregar_perfil(perfil_arquivo)
    transacoes = carregar_transacoes(transacoes_arquivo)
    historico = carregar_historico(historico_arquivo)
    
    # Determinar perfil string
    perfil_str = PerfilInvestidor.MODERADO  # default
    if perfil:
        perfil_str = perfil.perfil
    
    return {
        "nome": perfil.nome if perfil else "Amigo",
        "perfil": perfil_str,
        "tem_transacoes": len(transacoes) > 0,
        "num_transacoes": len(transacoes),
        "tem_historico": len(historico) > 0,
        "num_historico": len(historico),
        "observacoes": perfil.observacoes if perfil else "",
    }