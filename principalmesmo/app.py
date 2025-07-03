import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build

# === CHAVES DE API ===
YOUTUBE_API_KEY = "AIzaSyClB66YUAolBTKU7mN3Wucs2vgixHZvsjE"
GEMINI_API_KEY = "AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI"

# === TEMAS ESCOLARES ACEITOS POR MATÉRIA ===
TEMAS_POR_MATERIA = {
    "História": ["guerra fria", "revolução francesa", "era vargas", "segunda guerra mundial", "independência do brasil", "Historia", "História"],
    "Geografia": ["clima", "relevo", "migração", "urbano e rural", "globalização", "geografia"],
    "Matemática": ["frações", "porcentagem", "equações", "funções", "probabilidade", "matematica", "Matemática"],
    "Biologia": ["célula", "ecologia", "fotossíntese", "genética", "sistema digestório", "biologia", "Biologia"],
    "Química": ["tabela periódica", "ligações químicas", "reações", "ácidos e bases", "química orgânica ", "quimica", "Química"]
}

# === Função para descobrir a matéria com base no tema ===
def identificar_materia(tema):
    tema = tema.lower()
    for materia, temas in TEMAS_POR_MATERIA.items():
        for t in temas:
            if t in tema:
                return materia
    return None

# === Buscar vídeos escolares no YouTube ===
def buscar_videos_escolares(tema):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
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

# === Gerar perguntas com base nos vídeos ===
def gerar_questoes_gemini(tema, titulos_videos):
    genai.configure(api_key=GEMINI_API_KEY)
    modelo = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

    titulos_formatados = "\n".join([f"- {titulo}" for titulo in titulos_videos])

    prompt = f"""
Você é um assistente educacional. Com base nos seguintes títulos de vídeos sobre o tema "{tema}", gere 10 questões objetivas, curtas e de nível escolar (ensino médio). As perguntas devem estar diretamente relacionadas ao conteúdo sugerido pelos vídeos, sem as respostas.

Títulos dos vídeos:
{titulos_formatados}
    """

    resposta = modelo.generate_content(prompt)
    return resposta.text.strip()

# === INTERFACE COM STREAMLIT ===
st.set_page_config(page_title="Studie IA", layout="centered")
st.title("🎓 Estudo com IA - Busque vídeos e questões escolares")
tema = st.text_input("Digite um tema escolar (ex: Guerra Fria, Fotossíntese, Frações)")

if st.button("Pesquisar"):
    if not tema:
        st.warning("Por favor, digite um tema.")
    else:
        materia = identificar_materia(tema)
        if not materia:
            st.error("❌ Tema não reconhecido como escolar.")
            st.markdown("**Temas aceitos por matéria:**")
            for mat, temas in TEMAS_POR_MATERIA.items():
                st.markdown(f"**{mat}**: {', '.join(temas)}")
        else:
            st.success(f"Tema reconhecido como parte de **{materia}**.")

            with st.spinner("🔎 Buscando vídeos escolares no YouTube..."):
                videos = buscar_videos_escolares(tema)

            st.subheader("📺 Vídeos encontrados:")
            for video in videos:
                st.markdown(f"**{video['titulo']}**  \nCanal: *{video['canal']}*  \n[Assistir vídeo]({video['link']})\n")

            titulos_videos = [v['titulo'] for v in videos]

            with st.spinner("🧠 Gerando questões educativas com Gemini..."):
                questoes = gerar_questoes_gemini(tema, titulos_videos)

            st.subheader("📘 Questões sugeridas:")
            st.markdown(questoes)
