"""
App multiagente de conversação. Backend em Python (FastAPI) servindo uma
interface HTML/JS. Troca automaticamente de agente quando a cota de tokens
do agente ativo se esgota.
"""
import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents import AgentManager

load_dotenv()

BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / "conversation_log.txt"

app = FastAPI(title="Chat Multiagente")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

manager = AgentManager()
historico_sessao: list[dict] = []  # formato OpenAI: [{"role": "user"/"assistant", "content": str}]


class MensagemEntrada(BaseModel):
    mensagem: str


def registrar_log(remetente: str, conteudo: str) -> None:
    linha = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {remetente}: {conteudo}\n"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(linha)


@app.get("/")
def raiz():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/status")
def status():
    return {"agentes": manager.status(), "atual": manager.agente_atual.id}


@app.get("/api/historico")
def obter_historico():
    return {"historico": historico_sessao}


@app.post("/api/chat")
def chat(entrada: MensagemEntrada):
    historico_sessao.append({"role": "user", "content": entrada.mensagem})
    registrar_log("usuario", entrada.mensagem)

    resultado = manager.responder(historico_sessao)

    if resultado["erro"]:
        registrar_log("sistema", resultado["mensagem"])
        return {"erro": True, "mensagem": resultado["mensagem"], "agentes": manager.status()}

    historico_sessao.append({"role": "assistant", "content": resultado["mensagem"]})
    registrar_log(f"agente:{resultado['agente']}", resultado["mensagem"])
    if resultado["trocou_para"]:
        registrar_log("sistema", f"Cota esgotada. Próxima resposta usará: {resultado['trocou_para']}")

    return {
        "erro": False,
        "resposta": resultado["mensagem"],
        "agente": resultado["agente"],
        "tokens_usados_nesta_resposta": resultado["tokens_usados_nesta_resposta"],
        "tokens_restantes_agente": resultado["tokens_restantes_agente"],
        "trocou_para": resultado["trocou_para"],
        "agentes": manager.status(),
    }


@app.post("/api/reset")
def reset():
    historico_sessao.clear()
    return {"ok": True}
