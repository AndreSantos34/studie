async function mostrarRespostaComDigitacao(container, textoCompleto) {
  return new Promise((resolve) => {
    let i = 0;
    const velocidade = 10; // ms por caractere
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

  // Exibe a mensagem do usuário
  chatBox.innerHTML += `<div class="user-msg bolha"><p>${texto}</p></div>`;
  input.value = "";

  // Cria bolha com indicador "digitando..."
  let botBolha = document.createElement("div");
  botBolha.classList.add("bot-msg", "bolha");
  botBolha.innerHTML = `
    <div class="typing-indicator">
      <span></span><span></span><span></span>
    </div>
  `;
  chatBox.appendChild(botBolha);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    // Faz a requisição
    const resposta = await fetch("http://localhost:8000/perguntar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
    });

    const data = await resposta.json();

    // Substitui o indicador pelo texto da resposta
    botBolha.innerHTML = `<p class="typing"></p>`;
    const p = botBolha.querySelector("p.typing");
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

      // Após os vídeos, nova bolha com a pergunta sobre questões
      chatBox.innerHTML += `<div class="bot-msg bolha"><p class="typing"></p></div>`;
      chatBox.scrollTop = chatBox.scrollHeight;

      const novaPergunta = chatBox.querySelector(
        "div.bot-msg.bolha:last-child p.typing"
      );
      await mostrarRespostaComDigitacao(
        novaPergunta,
        "Quantas questões você deseja gerar?"
      );
    }

    // Depois adiciona questões, se houver
    if (data.questoes) {
      let questoesBolha = document.createElement("div");
      questoesBolha.classList.add("bot-msg", "bolha");
      questoesBolha.innerHTML = `
        <div class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      `;
      chatBox.appendChild(questoesBolha);
      chatBox.scrollTop = chatBox.scrollHeight;

      // Troca indicador pelas questões reais
      questoesBolha.innerHTML = `<p>${data.questoes.replace(
        /\n/g,
        "<br>"
      )}</p>`;
      chatBox.scrollTop = chatBox.scrollHeight;
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
