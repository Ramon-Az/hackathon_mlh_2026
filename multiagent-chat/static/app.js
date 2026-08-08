const mensagensEl = document.getElementById("mensagens");
const formEl = document.getElementById("form-chat");
const entradaEl = document.getElementById("entrada");
const agenteAtivoEl = document.getElementById("agente-ativo");
const listaAgentesEl = document.getElementById("lista-agentes");

function adicionarMensagem(tipo, texto, autor) {
  const div = document.createElement("div");
  div.className = `msg ${tipo}`;
  if (autor) {
    const span = document.createElement("span");
    span.className = "autor";
    span.textContent = autor;
    div.appendChild(span);
  }
  div.appendChild(document.createTextNode(texto));
  mensagensEl.appendChild(div);
  mensagensEl.scrollTop = mensagensEl.scrollHeight;
}

function renderizarAgentes(agentes) {
  listaAgentesEl.innerHTML = "";
  agentes.forEach((a) => {
    const pct = a.token_quota > 0 ? Math.min(100, (a.tokens_usados / a.token_quota) * 100) : 0;
    const card = document.createElement("div");
    card.className = `agente-card ${a.ativo ? "ativo" : ""} ${a.esgotado ? "esgotado" : ""}`;
    card.innerHTML = `
      <div class="nome">${a.nome}${a.ativo ? " ⭐" : ""}</div>
      <div>${a.provider} · ${a.model}</div>
      <div>${a.tokens_usados}/${a.token_quota} tokens</div>
      <div class="barra"><div class="barra-fill" style="width:${pct}%"></div></div>
      ${!a.chave_disponivel ? '<div style="color:#e06666;margin-top:4px;">sem chave de API</div>' : ""}
    `;
    listaAgentesEl.appendChild(card);
  });
  const atual = agentes.find((a) => a.ativo);
  if (atual) agenteAtivoEl.textContent = `agente ativo: ${atual.nome}`;
}

async function carregarStatus() {
  const resp = await fetch("/api/status");
  const dados = await resp.json();
  renderizarAgentes(dados.agentes);
}

formEl.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const texto = entradaEl.value.trim();
  if (!texto) return;

  adicionarMensagem("usuario", texto, "Você");
  entradaEl.value = "";
  entradaEl.disabled = true;

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensagem: texto }),
    });
    const dados = await resp.json();

    if (dados.erro) {
      adicionarMensagem("sistema", dados.mensagem);
    } else {
      adicionarMensagem("agente", dados.resposta, dados.agente);
      if (dados.trocou_para) {
        adicionarMensagem(
          "sistema",
          `Cota de tokens esgotada. A próxima resposta será do agente: ${dados.trocou_para}.`
        );
      }
      renderizarAgentes(dados.agentes);
    }
  } catch (err) {
    adicionarMensagem("sistema", "Erro ao contatar o servidor: " + err.message);
  } finally {
    entradaEl.disabled = false;
    entradaEl.focus();
  }
});

carregarStatus();
