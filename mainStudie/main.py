from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict
import re
import os
import yt_dlp
import google.generativeai as genai
from googleapiclient.discovery import build
from google.cloud import videointelligence_v1 as vi
from temas import TEMAS_POR_MATERIA

# === CHAVES DE API ===
YOUTUBE_API_KEY = 'AIzaSyClB66YUAolBTKU7mN3Wucs2vgixHZvsjE'
GEMINI_API_KEY = 'AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI'
<<<<<<< Updated upstream
=======
genai.configure(api_key=GEMINI_API_KEY)
>>>>>>> Stashed changes

# === Memória simples por IP (volátil) ===
conversas: Dict[str, Dict] = {}

# === Função para identificar a matéria de um tema ===
def identificar_materia(tema):
    tema = tema.lower().strip()
    for materia, temas in TEMAS_POR_MATERIA.items():
        for t in temas:
            if t in tema:
                return materia
    return None

# === Buscar vídeos escolares ===
def buscar_videos_escolares(tema, api_key, max_results=5):
    youtube = build('youtube', 'v3', developerKey=api_key)
<<<<<<< Updated upstream
    consulta = f"{tema} explicação escolar aula"

=======
    consulta = f"{tema} {materia} explicação escolar aula"
>>>>>>> Stashed changes
    resposta = youtube.search().list(
        q=consulta,
        part='snippet',
        type='video',
        maxResults=max_results,
        safeSearch='strict'
    ).execute()

    resultados = []
    for item in resposta['items']:
        titulo = item['snippet']['title']
        canal = item['snippet']['channelTitle']
        descricao = item['snippet'].get('description', '')
        video_id = item['id']['videoId']
        link = f"https://www.youtube.com/watch?v={video_id}"
        resultados.append({'titulo': titulo, 'canal': canal, 'descricao': descricao, 'link': link})
    return resultados

<<<<<<< Updated upstream
# === Gerar questões com Gemini ===
def gerar_questoes_gemini(tema, videos, api_key, num_questoes=10):
    genai.configure(api_key=api_key)
=======
# === Baixar áudio do YouTube usando FFmpeg local ===
def baixar_audio_youtube(link, caminho_saida="video_audio.mp3"):
    ffmpeg_local = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': caminho_saida,
        'quiet': True,
        'ffmpeg_location': ffmpeg_local,  # FFmpeg local
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
    return caminho_saida

# === Analisar vídeo com Google Video AI ===
def analisar_video_google(video_path):
    client = vi.VideoIntelligenceServiceClient()
    features = [vi.Feature.SPEECH_TRANSCRIPTION, vi.Feature.LABEL_DETECTION]

    with open(video_path, "rb") as f:
        input_content = f.read()

    operation = client.annotate_video(request={"features": features, "input_content": input_content})
    result = operation.result(timeout=300)

    transcricao = ""
    if result.annotation_results:
        for speech in result.annotation_results[0].speech_transcriptions:
            for alternative in speech.alternatives:
                transcricao += alternative.transcript + " "

    labels_detectados = [label.entity.description for label in result.annotation_results[0].segment_label_annotations]
    return transcricao.strip(), labels_detectados

# === Gerar resumo e questões com Gemini ===
def gerar_resumo_questoes_gemini(transcricao, labels, tema, num_questoes=10):
>>>>>>> Stashed changes
    modelo = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")
    prompt = f"""
<<<<<<< Updated upstream
Você é um assistente educacional. Com base nos seguintes vídeos e suas descrições sobre o tema \"{tema}\", gere {num_questoes} questões objetivas, curtas e de nível escolar (ensino médio). As perguntas devem estar diretamente relacionadas ao conteúdo sugerido pelos vídeos.
=======
Você é um assistente educacional.
Analise o conteúdo do vídeo sobre o tema "{tema}".
>>>>>>> Stashed changes

Transcrição do áudio:
{transcricao}

Objetos e cenas detectadas:
{', '.join(labels)}

Com base nisso, gere:
1. Resumo do vídeo
2. Lista de tópicos principais
3. {num_questoes} questões de múltipla escolha (A-E), curtas e de nível escolar
"""
    resposta = modelo.generate_content(prompt)
    return resposta.text.strip()

# === Execução por terminal ===
def executar_pesquisa(tema, num_videos=5, num_questoes=10):
    materia = identificar_materia(tema)

    if not materia:
        print(f"❌ Tema '{tema}' não é permitido. Escolha um tema escolar como 'Guerra Fria', 'Frações', etc.")
        print("✅ Exemplos aceitos por matéria:")
        for mat, temas in TEMAS_POR_MATERIA.items():
            print(f"  - {mat.title()}: {', '.join(temas)}")
        return

    print(f"\n📚 Tema aceito: '{tema.title()}' (Matéria: {materia.title()})")
    print(f"🔎 Buscando {num_videos} vídeos escolares sobre: {tema.title()}\n")
    videos = buscar_videos_escolares(tema, YOUTUBE_API_KEY, max_results=num_videos)

    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['titulo']}\n   Canal: {video['canal']}\n   Link: {video['link']}\n")

    print(f"🧠 Gerando {num_questoes} questões relacionadas aos vídeos com Gemini...\n")
    questoes = gerar_questoes_gemini(tema, videos, GEMINI_API_KEY, num_questoes=num_questoes)
    print(questoes)

# === FASTAPI INTEGRAÇÃO ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("index.html")

# === Modelo da requisição ===
class Pergunta(BaseModel):
    texto: str

# === Rota de interação ===
@app.post("/perguntar")
async def perguntar(pergunta: Pergunta, request: Request):
    texto = pergunta.texto.strip().lower()
    user_ip = request.client.host

<<<<<<< Updated upstream
    # Etapa 3 – número de questões
    if re.fullmatch(r"\d{1,2}", texto) and user_ip in conversas and conversas[user_ip].get("etapa") == "aguardando_questoes":
        num_questoes = int(texto)
        tema = conversas[user_ip]["tema"]
        videos = conversas[user_ip]["videos"]
        materia = identificar_materia(tema)

        questoes = gerar_questoes_gemini(tema, videos, GEMINI_API_KEY, num_questoes=num_questoes)

        del conversas[user_ip]

        return {
            "resposta": f"Aqui estão {num_questoes} questões sobre '{tema}' (Matéria: {materia}):",
            "videos": [],
            "questoes": questoes
        }

    # Etapa 2 – número de vídeos
    if re.fullmatch(r"\d{1,2}", texto) and user_ip in conversas and conversas[user_ip].get("etapa") == "aguardando_videos":
=======
    # === Novo tema ===
    if not conversa:
        tema = texto
        materia = identificar_materia(tema)
        if not materia:
            return {"resposta": "Tema inválido ou não reconhecido. Tente temas como: guerra fria, frações, genética, etc.", "videos": [], "questoes": ""}
        conversas[user_ip] = {"tema": tema, "etapa": "aguardando_videos"}
        return {"resposta": f"Tema reconhecido: '{tema}' (Matéria: {materia}). Quantos vídeos você gostaria de ver sobre esse tema?", "videos": [], "questoes": ""}

    # === Etapa 2 – buscar vídeos ===
    if re.fullmatch(r"\d{1,2}", texto) and conversa.get("etapa") == "aguardando_videos":
>>>>>>> Stashed changes
        num_videos = int(texto)
        tema = conversas[user_ip]["tema"]
        materia = identificar_materia(tema)
        videos = buscar_videos_escolares(tema, YOUTUBE_API_KEY, max_results=num_videos)

        conversas[user_ip]["videos"] = videos
        conversas[user_ip]["etapa"] = "processando_videos"

        resultados_processados = []
        for v in videos:
            audio_path = baixar_audio_youtube(v["link"])
            transcricao, labels = analisar_video_google(audio_path)
            resumo_questoes = gerar_resumo_questoes_gemini(transcricao, labels, tema)
            resultados_processados.append({"titulo": v["titulo"], "link": v["link"], "resumo_questoes": resumo_questoes})

<<<<<<< Updated upstream
    # Etapa 1 – entrada do tema
    tema = texto
    materia = identificar_materia(tema)

    if not materia:
        return {
            "resposta": "Tema inválido ou não reconhecido. Tente temas como: guerra fria, frações, genética, etc.",
            "videos": [],
            "questoes": ""
        }

    conversas[user_ip] = {
        "tema": tema,
        "etapa": "aguardando_videos"
    }

    return {
        "resposta": f"Tema reconhecido: '{tema}' (Matéria: {materia}). Quantos vídeos você gostaria de ver sobre esse tema?",
        "videos": [],
        "questoes": ""
    }

# === Execução via terminal ===
if __name__ == "__main__":
    tema = input("Digite um tema escolar: ").strip().lower()
    num_videos = int(input("Quantos vídeos deseja buscar? (padrão: 5): ") or "5")
    num_questoes = int(input("Quantas questões deseja gerar? (padrão: 10): ") or "10")
    executar_pesquisa(tema, num_videos, num_questoes)
=======
        conversas[user_ip]["etapa"] = "finalizado"
        return {"resposta": f"Aqui estão os vídeos e análises sobre '{tema}':", "videos": resultados_processados, "questoes": ""}

    return {"resposta": "Não entendi. Tente enviar um tema ou um número de vídeos.", "videos": [], "questoes": ""}
>>>>>>> Stashed changes
