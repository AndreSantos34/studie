// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function() {
  const sidebar = document.querySelector(".sidebar");
  const floatingBtn = document.querySelector(".menu-btn.floating");
  
  // Garantir que o botão flutuante comece oculto
  floatingBtn.style.display = "none";
  
  // Configurar o botão "Novo chat" para também alternar a sidebar
  const newChatBtn = document.getElementById("newChatBtn");
  if (newChatBtn) {
    newChatBtn.addEventListener("click", function(e) {
      e.preventDefault();
      toggleSidebar();
    });
  }
  
  // Adicionar event listeners para os campos de entrada
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
});

// Função para alternar a sidebar
function toggleSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const floatingBtn = document.querySelector(".menu-btn.floating");
  const mainContainer = document.querySelector(".main-container"); // peguei a main

  sidebar.classList.toggle("hidden");
  
  if (sidebar.classList.contains("hidden")) {
    floatingBtn.style.display = "block";
    mainContainer.classList.add("fullscreen");   // <<< aqui entra o modo tela cheia
  } else {
    floatingBtn.style.display = "none";
    mainContainer.classList.remove("fullscreen"); // <<< remove quando reabre a sidebar
  }
}


// Função para mostrar resposta com efeito de digitação
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

// Função para enviar mensagem
async function enviar() {
  const input = document.getElementById("entrada");
  const mensagens = document.getElementById("chat-mensagens");
  const texto = input.value.trim();

  if (!texto) return;

  // Exibe mensagem do usuário
  mensagens.innerHTML += `<div class="user-msg bolha"><p>${texto}</p></div>`;
  input.value = "";

  try {
    const resposta = await fetch("http://localhost:8000/perguntar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
    });

    const data = await resposta.json();

    // Cria bolha do bot para resposta principal
    const botDiv = document.createElement("div");
    botDiv.classList.add("bot-msg", "bolha");

    const p = document.createElement("p");
    p.classList.add("typing");
    botDiv.appendChild(p);

    mensagens.appendChild(botDiv);
    mensagens.scrollTop = mensagens.scrollHeight;

    // Escreve resposta principal
    await mostrarRespostaComDigitacao(p, data.resposta);

    // Se vieram vídeos
    if (data.videos && data.videos.length > 0) {
      let ul = document.createElement("ul");
      data.videos.forEach((v) => {
        let li = document.createElement("li");
        li.innerHTML = `<a href="${v.link}" target="_blank">${v.titulo}</a> - ${v.canal}`;
        ul.appendChild(li);
      });
      botDiv.appendChild(ul);
    }

    // Se vier pergunta OU lista de questões -> sempre em bolha separada
    if (data.questoes) {
      const botQuestDiv = document.createElement("div");
      botQuestDiv.classList.add("bot-msg", "bolha");

      let pQuest = document.createElement("p");
      pQuest.innerHTML = data.questoes.replace(/\n/g, "<br>");

      botQuestDiv.appendChild(pQuest);
      mensagens.appendChild(botQuestDiv);
    }

    mensagens.scrollTop = mensagens.scrollHeight;
  } catch (erro) {
    console.error("Erro ao enviar pergunta:", erro);
    mensagens.innerHTML += `<div class="bot-msg bolha">❌ Erro ao se comunicar com o servidor.</div>`;
  }
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
  const intro = document.querySelector(".intro");
  if (intro) intro.style.display = "none";

  const entradaInicial = document.getElementById("entrada-inicial");
  const entradaChat = document.getElementById("entrada");
  if (entradaInicial && entradaChat) {
    entradaChat.value = entradaInicial.value;
    entradaInicial.value = "";
  }
  enviar();
}


// login flip card

const flipCard = document.getElementById('flip-card');
const toRegister = document.getElementById('to-register');
const toLogin = document.getElementById('to-login');

toRegister.addEventListener('click', (e) => {
  e.preventDefault();
  flipCard.classList.add('flipped');
});

toLogin.addEventListener('click', (e) => {
  e.preventDefault();
  flipCard.classList.remove('flipped');
});

// pop up

// Função para abrir/fechar o popup do usuário
function toggleUserPopup() {
  const popup = document.getElementById('user-popup');
  popup.style.display = (popup.style.display === 'flex') ? 'none' : 'flex';
}

// Fecha o popup ao clicar fora
document.addEventListener('click', function (e) {
  const popup = document.getElementById('user-popup');
  const userBtn = document.querySelector('.user-btn');

  if (popup && userBtn && !popup.contains(e.target) && !userBtn.contains(e.target)) {
    popup.style.display = 'none';
  }
});
