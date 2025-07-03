async function enviar() {
  const input = document.getElementById("entrada");
  const chatBox = document.getElementById("chat-box");
  const texto = input.value;

  chatBox.innerHTML += `<div class="user-msg">${texto}</div>`;
  input.value = "";

  const resp = await fetch("http://localhost:8000/perguntar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });

  const data = await resp.json();
  let respostaHTML = `<div class="bot-msg">${data.resposta}<ul>`;
  data.videos.forEach((v) => {
    respostaHTML += `<li><a href="${v.link}" target="_blank">${v.titulo}</a> - ${v.canal}</li>`;
  });
  respostaHTML += `</ul><p>${data.questoes.replace(/\n/g, "<br>")}</p></div>`;

  chatBox.innerHTML += respostaHTML;
}
