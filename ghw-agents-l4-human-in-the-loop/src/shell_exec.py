#!/usr/bin/env python3
"""L4 Human-in-the-Loop Workflow - shell_exec.py

Execução segura de comandos com timeout e encoding adaptativo.

Padrões de segurança:
- Timeout padrão de 30 segundos
- Decodificação adaptativa (CP437/CP1252 -> UTF-8) no Windows
- Execução no shell nativo (PowerShell no Windows, bash no Linux)
- Confirmação explícita para risco alto
"""

import subprocess
import sys
import time
import signal
from typing import Optional, Tuple

# Timeout padrão de execução em segundos
DEFAULT_TIMEOUT = 30

# Encoding preferido e fallbacks para Windows
ENCODING_FALLBACK = "utf-8"
WINDOWS_ENCODINGS = ["cp850", "cp437", "cp1252", "latin-1"]


def _decode_output(output_bytes: bytes, preferred: str = None) -> str:
    """Decodifica output do terminal com fallback de encoding para Windows.
    
    Windows muitas vezes usa CP437 ou CP1252 em vez de UTF-8.
    Tenta múltiplos encodings até um funcionar.
    """
    encodings_to_try = [e for e in [preferred, ENCODING_FALLBACK] + WINDOWS_ENCODINGS if e]
    
    for encoding in encodings_to_try:
        try:
            return output_bytes.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    
    # Fallback último recurso com substituição de caracteres inválidos
    return output_bytes.decode("utf-8", errors="replace")


def _safe_run(
    comando: str,
    timeout: int = DEFAULT_TIMEOUT,
    input_data: Optional[str] = None,
) -> Tuple[int, str, str]:
    """Executa um comando de forma segura com timeout e encoding adaptativo.

    Executa no shell nativo do sistema: PowerShell no Windows (cmdlets como
    Get-ChildItem/New-Item funcionam), bash no Linux.

    Returns:
        Tuple de (returncode, stdout, stderr)
    """
    try:
        # Argumentos em lista: comando vai como argumento único do shell,
        # sem problemas de escaping de aspas
        if sys.platform == "win32":
            args = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", comando]
        else:
            args = ["bash", "-lc", comando]

        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        try:
            stdout_bytes, stderr_bytes = process.communicate(
                input=input_data, timeout=timeout
            )
            return_code = process.returncode
            stdout = _decode_output(stdout_bytes)
            stderr = _decode_output(stderr_bytes)
            return return_code, stdout, stderr
            
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            return -1, "", f"Timeout de {timeout}s expirado. Comando cancelado."
            
    except Exception as e:
        return -1, "", f"Erro ao executar comando: {e}"


def executar_comando_seguro(
    comando: str,
    risco: str = "low",
    timeout: int = DEFAULT_TIMEOUT,
    aguardar_confirmacao: bool = True,
) -> dict:
    """Executa um comando com protocolo human-in-the-loop.
    
    Flow:
    1. Exibir comando a ser executado
    2. Se risco alto, solicitar confirmação 'sim' explícita
    3. Se confirmado (ou risco baixo), executar com timeout
    4. Retornar resultado estruturado
    
    Args:
        comando: Comando de terminal a executar
        risco: 'low', 'medium' ou 'high'
        timeout: Tempo máximo em segundos (padrão 30)
        aguardar_confirmacao: Se True, pede confirmação para risco alto
        
    Returns:
        Dict com status, output, erro e confirmado
    """
    # Step 1: Exibir comando
    print("\n" + "=" * 60)
    print("📋 COMANDO A SER EXECUTADO:")
    print("=" * 60)
    print(f"$ {comando}")
    print("=" * 60)
    
    # Step 2: Verificação de risco e confirmação
    if risco.upper() == "HIGH" or aguardar_confirmacao:
        print("\n⚠️  NÍVEL DE RISCO: ALTO")
        print("Este comando pode causar perda de dados ou danos ao sistema.")
        print("Digite 'sim' para confirmar a execução (qualquer outra tecla cancela).")
        
        try:
            resposta = input("> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Operação cancelada pelo usuário.")
            return {"status": "cancelado", "confirmado": False, "output": "", "erro": "Cancelado pelo usuário"}
        
        if resposta != "sim":
            print("❌ Operação cancelada. Nada foi executado.")
            return {"status": "cancelado", "confirmado": False, "output": "", "erro": "Confirmação negada"}
    
    # Step 3: Execução com timeout
    print("\n▶️  Executando...")
    code, stdout, stderr = _safe_run(comando, timeout=timeout)
    
    # Step 4: Resultado estruturado
    return {
        "status": "ok" if code == 0 else "erro",
        "confirmado": True,
        "output": stdout,
        "erro": stderr if code != 0 else "",
        "returncode": code,
    }


def main():
    """Modo de teste interativo."""
    print("=== L4 Human-in-the-Loop: Shell Executor ===")
    print("Digite um comando de terminal para executar (ou 'sair' para encerrar):")
    
    while True:
        try:
            comando = input("\n$ ").strip()
            if comando.lower() in ('sair', 'exit', 'quit'):
                break
            if not comando:
                continue
            
            code, stdout, stderr = _safe_run(comando)
            print(f"\n[exit code: {code}]")
            if stdout.strip():
                print(stdout)
            if stderr.strip():
                print(stderr, file=sys.stderr)
            
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
