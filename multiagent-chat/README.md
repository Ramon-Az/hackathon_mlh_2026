# Chat Multiagente

App de conversação com backend em Python (FastAPI) e interface web em HTML/JS.
Vários agentes (modelos/provedores diferentes) ficam disponíveis; quando a cota
de tokens do agente ativo se esgota, o app troca automaticamente para o
próximo agente disponível.

## Configuração

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Copie `.env.example` para `.env` e preencha as chaves de API dos
   provedores que for usar (OpenAI e/ou Anthropic).
3. Ajuste os agentes em `agents.config.json` (nome, provedor, modelo, cota de
   tokens `token_quota`, prompt de sistema). A ordem da lista define a ordem
   de troca automática.

## Executar

```
uvicorn main:app --reload
```

Acesse `http://127.0.0.1:8000` no navegador.

## Como funciona a troca automática

- Cada agente tem uma cota (`token_quota`) de tokens totais consumidos
  (prompt + resposta).
- Ao esgotar a cota do agente ativo, a próxima mensagem do usuário é
  respondida pelo próximo agente da lista que ainda tenha cota e chave de API
  configurada.
- Se todos os agentes esgotarem a cota (ou faltar chave de API), o app avisa
  no chat e para de responder até que as cotas sejam ajustadas.
- O histórico de conversa é registrado em `conversation_log.txt`.
