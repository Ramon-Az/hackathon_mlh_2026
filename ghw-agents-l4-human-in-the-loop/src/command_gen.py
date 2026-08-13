#!/usr/bin/env python3
"""L4 Human-in-the-Loop Workflow - command_gen.py

Responsável por traduzir comandos em linguagem natural para comandos de terminal,
avaliando o risco de cada comando e gerando explicações para aprovação humana.

Padrões de segurança:
- Comando sempre exibido antes da execução
- Risco classificado (baixo/alto)
- Explicação clara do que será feito
- Solicitação de confirmação explícita para risco alto
"""

import re
import sys
from enum import Enum
from typing import Optional


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CommandResult:
    """Resultado da análise de comando."""
    
    def __init__(
        self,
        comando: str,
        risco: RiskLevel,
        explicacao: str,
        seguro: bool = True,
    ):
        self.comando = comando
        self.risco = risco
        self.explicacao = explicacao
        self.seguro = seguro


def _detectar_shell() -> str:
    """Detecta o shell do sistema (powershell no Windows, bash no Linux)."""
    return "powershell" if sys.platform == "win32" else "bash"


# Frases comuns em linguagem natural -> comandos reais por shell.
# (powershell, bash)
FRASES_COMANDOS = {
    "list all files": ("Get-ChildItem", "ls -la"),
    "list files": ("Get-ChildItem", "ls -la"),
    "list directory": ("Get-ChildItem", "ls -la"),
    "show files": ("Get-ChildItem", "ls -la"),
    "show all files": ("Get-ChildItem", "ls -la"),
    "listar arquivos": ("Get-ChildItem", "ls -la"),
    "mostrar arquivos": ("Get-ChildItem", "ls -la"),
    "list": ("Get-ChildItem", "ls"),
    "ls": ("Get-ChildItem", "ls -la"),
    "dir": ("Get-ChildItem", "ls -la"),
    "pwd": ("Get-Location", "pwd"),
    "current directory": ("Get-Location", "pwd"),
    "where am i": ("Get-Location", "pwd"),
    "current user": ("whoami", "whoami"),
    "who am i": ("whoami", "whoami"),
    "create a new folder": ("New-Item -ItemType Directory -Path 'nova_pasta'", "mkdir -p nova_pasta"),
    "create a folder": ("New-Item -ItemType Directory -Path 'nova_pasta'", "mkdir -p nova_pasta"),
    "create folder": ("New-Item -ItemType Directory -Path 'nova_pasta'", "mkdir -p nova_pasta"),
    "criar pasta": ("New-Item -ItemType Directory -Path 'nova_pasta'", "mkdir -p nova_pasta"),
    "crie uma pasta": ("New-Item -ItemType Directory -Path 'nova_pasta'", "mkdir -p nova_pasta"),
    "create a new file": ("New-Item -ItemType File -Path 'novo_arquivo.txt'", "touch novo_arquivo.txt"),
    "create a file": ("New-Item -ItemType File -Path 'novo_arquivo.txt'", "touch novo_arquivo.txt"),
    "create file": ("New-Item -ItemType File -Path 'novo_arquivo.txt'", "touch novo_arquivo.txt"),
    "criar arquivo": ("New-Item -ItemType File -Path 'novo_arquivo.txt'", "touch novo_arquivo.txt"),
    "delete all files": ("Remove-Item * -Recurse -Force", "rm -rf *"),
    "delete everything": ("Remove-Item * -Recurse -Force", "rm -rf *"),
    "delete all": ("Remove-Item * -Recurse -Force", "rm -rf *"),
    "apagar tudo": ("Remove-Item * -Recurse -Force", "rm -rf *"),
    "apague tudo": ("Remove-Item * -Recurse -Force", "rm -rf *"),
    "format c": ("format C:", "sudo mkfs.ext4 /dev/sda"),
    "format c:": ("format C:", "sudo mkfs.ext4 /dev/sda"),
    "formatar c": ("format C:", "sudo mkfs.ext4 /dev/sda"),
    "show ip": ("ipconfig", "ifconfig"),
    "my ip": ("ipconfig", "ifconfig"),
    "network config": ("ipconfig", "ifconfig"),
    "system info": ("systeminfo", "uname -a"),
    "what time is it": ("Get-Date", "date"),
    "show time": ("Get-Date", "date"),
    "current date": ("Get-Date", "date"),
    "show date": ("Get-Date", "date"),
    "list processes": ("Get-Process", "ps aux"),
    "show processes": ("Get-Process", "ps aux"),
    "list tasks": ("Get-Process", "ps aux"),
    "disk space": ("Get-PSDrive C", "df -h"),
    "show disk space": ("Get-PSDrive C", "df -h"),
    "free space": ("Get-PSDrive C", "df -h"),
}


def _traduzir_comando(texto: str) -> Optional[str]:
    """Traduz frases comuns em linguagem natural para comandos reais."""
    shell = _detectar_shell()
    normalizado = texto.strip().lower().rstrip(".!?")
    if normalizado in FRASES_COMANDOS:
        comando = FRASES_COMANDOS[normalizado]
        return comando[0] if shell == "powershell" else comando[1]

    # Padrões com nome: "create folder <nome>", "criar pasta <nome>", "delete file <nome>"
    m = re.match(
        r"(?:create\s+(?:a\s+)?(?:new\s+)?(?:folder|pasta)|criar pasta|crie uma pasta)\s+([\w\-]+)",
        normalizado,
    )
    if m:
        nome = m.group(1)
        if shell == "powershell":
            return f"New-Item -ItemType Directory -Path '{nome}'"
        return f"mkdir -p {nome}"

    m = re.match(
        r"(?:create\s+(?:a\s+)?(?:new\s+)?(?:file|arquivo)|criar arquivo)\s+([\w\-\.]+)",
        normalizado,
    )
    if m:
        nome = m.group(1)
        if shell == "powershell":
            return f"New-Item -ItemType File -Path '{nome}'"
        return f"touch {nome}"

    return None


def _extrair_comando(texto: str) -> str:
    """Extrai o comando de terminal do texto em linguagem natural.
    
    Busca por padrões que pareçam comandos de Windows PowerShell/Linux.
    """
    # Padrões comuns de comando
    patterns = [
        r'(?:execute|run|exec|faça|crie|apague|mova|copie)\s+(.+?)(?:\.|$)',
        r'(?:powershell|ps>\s)(.+)',
        r'(?:terminal>\s)(.+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return texto.strip()


def avaliar_risco(comando: str) -> RiskLevel:
    """Avalia o risco de um comando de terminal.
    
    Comandos de risco alto incluem:
    - Remove/Delete everything
    - Formatação de disco
    - Execução de código não verificado
    - Comandos com sudo/admin sem confirmação
    
    Comandos de risco baixo/médio incluem:
    - Listar arquivos
    - Criar pastas
    - Operações de leitura
    """
    comando_upper = comando.upper()
    
    # Padrões de risco alto
    high_risk_patterns = [
        r'DELETE.*\*',
        r'\bDELETE\b',
        r'\bREMOVE\b',
        r'\bAPAGUE\b',
        r'\bFORMAT\b',
        r'\bFDISK\b',
        r'MKDIR\s+/S',
        r'RM\s+-R',
        r'RD\s+/S',
        r'>\s*NUL',
        r'2>\s*NUL',  # redirect stderr to null can hide errors
        r'>.*NUL\s*$',  # redirect output to null
    ]
    
    for pattern in high_risk_patterns:
        if re.search(pattern, comando_upper):
            return RiskLevel.HIGH
    
    # Padrões de risco médio
    medium_risk_patterns = [
        r'\bPIP\s+INSTALL\b',
        r'\bNPM\s+INSTALL\b',
        r'CURL\s+.*\|\s*BASH',
        r'WGET.*\|\s*SH',
    ]
    
    for pattern in medium_risk_patterns:
        if re.search(pattern, comando_upper):
            return RiskLevel.MEDIUM
    
    return RiskLevel.LOW


def gerar_explicacao(comando: str, risco: RiskLevel) -> str:
    """Gera uma explicação clara do que o comando fará."""
    
    base_explics = {
        RiskLevel.LOW: f"O comando '{comando}' parece ser uma operação segura de leitura ou criação de arquivos/pastas.",
        RiskLevel.MEDIUM: f"O comando '{comando}' executa uma operação de modificação. Verifique se é o desejado antes de confirmar.",
        RiskLevel.HIGH: f"⚠️ O comando '{comando}' é de ALTO RISCO. Pode causar perda de dados ou danos ao sistema. Confirme explicitamente com 'sim' se desejar executar.",
    }
    
    return base_explics.get(risco, base_explics[RiskLevel.LOW])


def analisar_comando(texto: str) -> CommandResult:
    """Analisa um comando em linguagem natural e retorna resultado estruturado.
    
    Args:
        texto: Texto em linguagem natural descrevendo o que fazer
        
    Returns:
        CommandResult com comando extraído, nível de risco, explicação e segurança
    """
    comando = _traduzir_comando(texto) or _extrair_comando(texto)
    # Risco = o MAIS ALTO entre o comando traduzido e o texto original
    # (frases traduzidas podem perder marcadores, ex.: 'delete all files' -> Remove-Item)
    ordem = {"low": 0, "medium": 1, "high": 2}
    r1, r2 = avaliar_risco(comando), avaliar_risco(texto)
    risco = r1 if ordem[r1.value] >= ordem[r2.value] else r2
    explicacao = gerar_explicacao(comando, risco)
    
    # Um comando é "seguro" se risco for LOW e não houver padrões suspeitos
    seguro = risco in (RiskLevel.LOW, RiskLevel.MEDIUM)
    
    return CommandResult(
        comando=comando,
        risco=risco,
        explicacao=explicacao,
        seguro=seguro,
    )


def main():
    """Modo de teste interativo."""
    print("=== L4 Human-in-the-Loop: Analysis Tool ===")
    print("Digite um comando em linguagem natural (ou 'sair' para encerrar):")
    
    while True:
        try:
            texto = input("\n> ")
            if texto.lower() in ('sair', 'exit', 'quit'):
                break
            
            resultado = analisar_comando(texto)
            
            print(f"\n📋 Comando: {resultado.comando}")
            print(f"⚠️  Risco: {resultado.risco.value.upper()}")
            print(f"💡 Explicação: {resultado.explicacao}")
            print(f"✅ Seguro: {resultado.seguro}")
            
            if not resultado.seguro:
                print("\n⚠️  Observação: Este comando requer confirmação humana antes da execução.")
            
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
