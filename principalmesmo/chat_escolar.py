import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build

# === SUAS CHAVES DE API ===
YOUTUBE_API_KEY = "AIzaSyClB66YUAolBTKU7mN3Wucs2vgixHZvsjE"
GEMINI_API_KEY = "AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI"

# === Temas permitidos por matéria ===
TEMAS_POR_MATERIA = {
    "História": ["guerra fria", "revolução francesa", "era vargas", "segunda guerra mundial", "independência do brasil", "Historia", "História"],
    "Geografia": ["clima", "relevo", "migração", "urbano e rural", "globalização", "geografia"],
    "Matemática": ["frações", "porcentagem", "equações", "funções", "probabilidade", "matematica", "Matemática"],
    "Biologia": ["célula", "ecologia", "fotossíntese", "genética", "sistema digestório", "biologia", "Biologia"],
    "Química": ["tabela periódica", "ligações químicas", "reações", "ácidos e bases", "química orgânica ", "quimica", "Química"]
}

# === Identificar a matéria baseada no tema ===
def identificar_materia(tema):
    tema = tema.lower()
    for materia, temas in TEMAS_POR_MATERIA.items():
        for t in temas:
            if t in tema:
                return materia
    return None

# === Buscar vídeos no YouTube ===
def buscar_videos_escolares(tema):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    consulta = f"{tema} explicação escolar aula"

    resposta = youtube.search().list(
        q=consulta,
        part='snippet',
        type='video',
        maxResults=5,
        safeSearch='strict'
    ).execute()

    resultados = []
    for item in resposta['items']:
        titulo = item['snippet']['title']
        canal = item['snippet']['channelTitle']
        video_id = item['id']['videoId']
        link = f"https://www.youtube.com/watch?v={video_id}"

        resultados.append({
            'titulo': titulo,
            'canal': canal,
            'link': link
        })

    return resultados

# === Gerar perguntas com Gemini ===
def gerar_questoes(tema, titulos):
    genai.configure(api_key=GEMINI_API_KEY)
    modelo = genai.GenerativeModel("models/gemini-1.5-flash-latest")

    prompt = f"""
Você é um assistente educacional. Com base nos seguintes vídeos sobre o tema "{tema}",
 gere 10 questões objetivas e curtas para alunos do ensino médio sem dar as respostas.:

Vídeos:
{chr(10).join(['- ' + titulo for titulo in titulos])}
    """

    resposta = modelo.generate_content(prompt)
    return resposta.text.strip()

# === Interface do Chat com Streamlit ===
st.set_page_config(page_title="Chat Escolar com IA", layout="centered")
st.title("🤖📚 Chat Escolar com IA")

if "chat" not in st.session_state:
    st.session_state.chat = []

pergunta = st.chat_input("Digite sua dúvida ou tema escolar (ex: Guerra Fria, Frações)")

if pergunta:
    st.session_state.chat.append({"role": "user", "content": pergunta})

    tema = pergunta.lower().strip()
    materia = identificar_materia(tema)

    if materia:
        resposta = f"✅ Entendi! Você quer estudar **{tema.title()}**, que faz parte de **{materia}**.\n\n"
        resposta += "🎥 Buscando vídeos escolares...\n"

        with st.spinner("Buscando vídeos..."):
            videos = buscar_videos_escolares(tema)

        for i, v in enumerate(videos, 1):
            resposta += f"\n{i}. [{v['titulo']}]({v['link']}) — *{v['canal']}*"

        resposta += "\n\n🧠 Gerando 10 questões com IA...\n"

        with st.spinner("Gerando questões..."):
            questoes = gerar_questoes(tema, [v['titulo'] for v in videos])
        resposta += "\n" + questoes

    else:
        resposta = "❌ Desculpe, esse tema não parece ser de uma matéria escolar.\n\n"
        resposta += "📚 Tente algo como:\n"
        for mat, temas in TEMAS_POR_MATERIA.items():
            resposta += f"**{mat}**: {', '.join(temas)}\n"

    st.session_state.chat.append({"role": "assistant", "content": resposta})

# Mostrar histórico do chat
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
