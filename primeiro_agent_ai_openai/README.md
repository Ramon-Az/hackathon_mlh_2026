# Primeiro agente de IA com OpenAI

Um agente de terminal com **function calling** (chamada de ferramentas).

A diferença entre um chat simples e um agente: o chat só responde texto;
o agente pode **decidir** que precisa de uma ferramenta, pedir para executá-la
e usar o resultado na resposta.

## Como funciona

```
Usuário: "que horas são?"
   |
   v
[1] Modelo recebe a pergunta + a lista de ferramentas (tools.py)
   |
   v
[2] Modelo decide chamar a ferramenta obter_hora_atual
   |
   v
[3] main.py executa a função Python correspondente
   |
   v
[4] Resultado volta ao modelo, que monta a resposta final
   |
   v
Usuário: "São 14:32:05 do dia 08/08/2026."
```

Esse ciclo [modelo pede → programa executa → devolve o resultado] pode
repetir várias vezes até o modelo considerar a resposta pronta
(por exemplo: `calcular` e depois `salvar_anotacao`).

## Ferramentas

| Nome              | O que faz                                        |
| ----------------- | ------------------------------------------------ |
| `obter_hora_atual`| Devolve a data e hora atuais.                    |
| `calcular`        | Calcula expressões (ex.: `10 * (2 + 3)`) com segurança. |
| `salvar_anotacao` | Salva um texto em `anotacoes.txt`.               |

## Configuração e execução

```bash
pip install -r requirements.txt
copy .env.example .env
# preencha OPENAI_API_KEY no .env

python main.py
```

Exemplos para testar no chat:
- "Que horas são?"
- "Quanto é 7 elevado a 3?"
- "Salve uma anotação dizendo que vou apresentar o agente amanhã."
- "Calcule 15% de 200 e salve o resultado como anotação." (usa 2 ferramentas!)

## Arquivos

- `main.py` — o loop do agente e a conversa no terminal.
- `tools.py` — definições (JSON) e implementações (Python) das ferramentas.
