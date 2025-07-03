async function mostrarRespostaComDigitacao(container, textoCompleto) {
  return new Promise((resolve) => {
    let i = 0;
    const velocidade = 3; // ms por caractere
    container.innerHTML = ""; // limpa

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
  const chatBox = document.getElementById("chat-box");
  const texto = input.value.trim();

  if (!texto) return;

  chatBox.innerHTML += `<div class="user-msg bolha"><p>${texto}</p></div>`;
  input.value = "";

  try {
    const resposta = await fetch("http://localhost:8000/perguntar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
    });

    const data = await resposta.json();

    // Cria a bolha do bot com <p> vazio para digitação
    chatBox.innerHTML += `<div class="bot-msg bolha"><p class="typing"></p></div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    const p = chatBox.querySelector("div.bot-msg.bolha:last-child p.typing");

    // Mostra a resposta letra a letra
    await mostrarRespostaComDigitacao(p, data.resposta);

    // Depois adiciona vídeos, se houver
    if (data.videos && data.videos.length > 0) {
      let ul = document.createElement("ul");
      data.videos.forEach((v) => {
        let li = document.createElement("li");
        li.innerHTML = `<a href="${v.link}" target="_blank">${v.titulo}</a> - ${v.canal}`;
        ul.appendChild(li);
      });
      chatBox.querySelector("div.bot-msg.bolha:last-child").appendChild(ul);
    }

    // Depois adiciona questões, se houver
    if (data.questoes) {
      let pQuest = document.createElement("p");
      pQuest.innerHTML = data.questoes.replace(/\n/g, "<br>");
      chatBox.querySelector("div.bot-msg.bolha:last-child").appendChild(pQuest);
    }

    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (erro) {
    console.error("Erro ao enviar pergunta:", erro);
    chatBox.innerHTML += `<div class="bot-msg bolha">❌ Erro ao se comunicar com o servidor.</div>`;
  }
}

// Envia ao apertar Enter
const input = document.getElementById("entrada");
input.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    event.preventDefault();
    enviar();
  }
});
