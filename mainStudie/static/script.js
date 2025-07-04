async function mostrarRespostaComDigitacao(container, textoCompleto) {
  return new Promise((resolve) => {
    let i = 0;
    const velocidade = 10;
    container.innerHTML = "";

    function digitar() {
      if (i < textoCompleto.length) {
        container.innerHTML += textoCompleto.charAt(i);
        i++;
        setTimeout(digitar, velocidade);
      } else {
        resolve();
      }
    }

    digitar();
  });
}

async function enviar() {
  const input = document.getElementById("entrada");
  const mensagens = document.getElementById("chat-mensagens");
  const texto = input.value.trim();

  if (!texto) return;

  mensagens.innerHTML += `<div class="user-msg bolha"><p>${texto}</p></div>`;
  input.value = "";

  try {
    const resposta = await fetch("http://localhost:8000/perguntar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
    });

    const data = await resposta.json();

    mensagens.innerHTML += `<div class="bot-msg bolha"><p class="typing"></p></div>`;
    mensagens.scrollTop = mensagens.scrollHeight;

    const p = mensagens.querySelector("div.bot-msg.bolha:last-child p.typing");

    await mostrarRespostaComDigitacao(p, data.resposta);

    if (data.videos && data.videos.length > 0) {
      let ul = document.createElement("ul");
      data.videos.forEach((v) => {
        let li = document.createElement("li");
        li.innerHTML = `<a href="${v.link}" target="_blank">${v.titulo}</a> - ${v.canal}`;
        ul.appendChild(li);
      });
      mensagens.querySelector("div.bot-msg.bolha:last-child").appendChild(ul);
    }

    if (data.questoes) {
      let pQuest = document.createElement("p");
      pQuest.innerHTML = data.questoes.replace(/\n/g, "<br>");
      mensagens.querySelector("div.bot-msg.bolha:last-child").appendChild(pQuest);
    }

    mensagens.scrollTop = mensagens.scrollHeight;
  } catch (erro) {
    console.error("Erro ao enviar pergunta:", erro);
    mensagens.innerHTML += `<div class="bot-msg bolha">❌ Erro ao se comunicar com o servidor.</div>`;
  }
}

const inputInicial = document.getElementById("entrada-inicial");
if (inputInicial) {
  inputInicial.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      enviainicia();
    }
  });
}

const input = document.getElementById("entrada");
if (input) {
  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      enviar();
    }
  });
}

function iniciarChat() {
  document.querySelector(".intro").style.display = "none";
  document.getElementById("chat-box").style.display = "flex";
  document.getElementById("newChatBtn").style.display = "block";
}

function openUserPage() {
  alert("Abrir página de conta do usuário");
}

function enviainicia() {
  iniciarChat();
  const entradaInicial = document.getElementById("entrada-inicial");
  const entradaChat = document.getElementById("entrada");
  if (entradaInicial && entradaChat) {
    entradaChat.value = entradaInicial.value;
    entradaInicial.value = "";
  }
  enviar();
}
