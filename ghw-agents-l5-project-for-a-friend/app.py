# L5 Project for a Friend - app.py (Streamlit interface)

"""Interface Streamlit para o agente L5 Project for a Friend.

Esta é uma interface web simples usando Streamlit para interagir
com o agente personalizado.

Requisitos:
- streamlit
- openai, anthropic, google-generai, groq (opcional)
- pandas (para dados)
"""

import streamlit as st
from typing import Optional, List, Dict, Any

from src import dados as dados_modulo
from src import agente as agente_modulo


# Configuração da página
st.set_page_config(
    page_title="Agente L5 - Project for a Friend",
    page_icon="🤝",
    layout="wide"
)

# Título e descrição
st.title("🤝 Agente L5: Project for a Friend")
st.markdown("""
Agente de IA personalizado para assistência específica. 
Construído para ajudar um amigo com contexto e preferências individuais.
""")

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações do Agente")
    
    # Nome do amigo
    nome_amigo = st.text_input("Nome do amigo", value="João")
    
    # Perfil de investidor
    perfil_opcoes = ["conservador", "moderado", "arrojado"]
    perfil_amigo = st.selectbox(
        "Perfil de investidor", 
        options=perfil_opcoes,
        index=1  # default: moderado
    )
    
    # Provedor de IA
    provedor_opcoes = ["groq", "openai", "anthropic", "gemini", "ollama"]
    provedor_selecionado = st.selectbox(
        "Provedor de IA", 
        options=provedor_opcoes,
        index=0  # default: groq
    )
    
    # Modelo
    modelo_opcoes = {
        "groq": "llama-3.3-70b-versatile",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-haiku-20240307",
        "gemini": "gemini-flash-latest",
        "ollama": "llama3.1:8b",
    }
    modelo_escolhido = st.selectbox(
        "Modelo", 
        options=list(modelo_opcoes.keys()),
        format_func=lambda x: modelo_opcoes[x],
        index=0
    )
    
    st.divider()
    st.markdown("---")
    st.markdown("### Dados do Amigo")
    
    # Upload de arquivos
    st.markdown("**Arquivos de dados (opcional):**")
    perfil_file = st.file_uploader("perfil_investidor.json", type=["json"])
    transacoes_file = st.file_uploader("transacoes.csv", type=["csv"])
    historico_file = st.file_uploader("historico_atendimento.csv", type=["csv"])
    
    # Processar uploads
    contexto = {}
    if perfil_file:
        import json
        try:
            perfil_data = json.load(perfil_file)
            contexto["nome"] = perfil_data.get("nome", nome_amigo)
            contexto["perfil"] = perfil_data.get("perfil", perfil_amigo)
            contexto["observacoes"] = perfil_data.get("observacoes", "")
            st.success("✅ Perfil carregado!")
        except Exception as e:
            st.error(f"❌ Erro ao ler perfil: {e}")
    
    if transacoes_file:
        import csv
        try:
            import io
            content = io.StringIO(transacoes_file.getvalue().decode("utf-8"))
            reader = csv.DictReader(content)
            st.success(f"✅ {sum(1 for _ in reader)} transações carregadas!")
        except Exception as e:
            st.error(f"❌ Erro ao ler transações: {e}")
    
    if historico_file:
        import csv
        try:
            import io
            content = io.StringIO(historico_file.getvalue().decode("utf-8"))
            reader = csv.DictReader(content)
            st.success(f"✅ {sum(1 for _ in reader)} registros de histórico carregados!")
        except Exception as e:
            st.error(f"❌ Erro ao ler histórico: {e}")
    
    st.divider()
    st.markdown("### Sobre")
    st.info(
        "Este agente fornece sugestões baseadas em dados disponíveis "
        "e perfis definidos. Não constitui aconselhamento financeiro. "
        "Sempre consulte um profissional qualificado."
    )


# Área principal - chat
st.header("💬 Conversa com o Agente")

# Inicializar agente no session_state se não existir
if "agente_l5" not in st.session_state:
    # Determinar modelo baseado no provedor
    modelo_map = {
        "groq": "llama-3.3-70b-versatile",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-haiku-20240307",
        "gemini": "gemini-flash-latest",
        "ollama": "llama3.1:8b",
    }
    
    contexto_inicial = {}
    if contexto.get("nome"):
        contexto_inicial["nome"] = contexto["nome"]
        contexto_inicial["perfil"] = contexto.get("perfil", "moderado")
        contexto_inicial["observacoes"] = contexto.get("observacoes", "")
    
    st.session_state.agente_l5 = agente_modulo.AgenteFriend(
        nome_amigo=nome_amigo,
        perfil_investidor=perfil_amigo,
        provedor=provedor_selecionado,
        modelo=modelo_map[provedor_selecionado],
        base_conhecimento=contexto_inicial,
    )

# Mostrar contexto carregado
if contexto.get("nome"):
    with st.expander("Ver contexto carregado", expanded=False):
        st.json({
            "nome": contexto.get("nome"),
            "perfil": contexto.get("perfil"),
            "tem_transacoes": contexto.get("tem_transacoes", False),
            "num_transacoes": contexto.get("num_transacoes", 0),
            "tem_historico": contexto.get("tem_historico", False),
            "num_historico": contexto.get("num_historico", 0),
        })


# Container de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Aceitar entrada do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exibir mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Processar com o agente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                resposta = st.session_state.agente_l5.gerar_resposta(prompt)
                
                # Adicionar resposta ao histórico
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": resposta
                })
                
                # Exibir resposta
                st.markdown(resposta)
                
            except Exception as e:
                erro_msg = f"❌ Desculpe, ocorreu um erro: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": erro_msg
                })
                st.error(erro_msg)


# Rodapé com disclaimer
st.divider()
st.caption("""
⚠️ **Disclaimer**: Este agente fornece sugestões baseadas em padrões 
e dados disponíveis, mas não constitui aconselhamento financeiro ou profissional. 
Para decisões financeiras, sempre consulte um profissional qualificado. 
O agente não responde por decisões tomadas com base nestas sugestões.
""")