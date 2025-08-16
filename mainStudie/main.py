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
genai.configure(api_key=GEMINI_API_KEY)

# === Memória simples por IP (volátil) ===
conversas: Dict[str, Dict] = {}

# === Identificar matéria ===
def identificar_materia(tema):
    tema = tema.lower().strip()
    for materia, temas in TEMAS_POR_MATERIA.items():
        for t in temas:
            if t in tema:
                return materia
    return None

# === Buscar vídeos escolares ===
def buscar_videos_escolares(tema, materia, api_key, max_results=5):
    youtube = build('youtube', 'v3', developerKey=api_key)
    consulta = f"{tema} {materia} explicação escolar aula"
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
    modelo = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")
    prompt = f"""
Você é um assistente educacional.
Analise o conteúdo do vídeo sobre o tema "{tema}".

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

# === FASTAPI ===
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

class Pergunta(BaseModel):
    texto: str

@app.post("/perguntar")
async def perguntar(pergunta: Pergunta, request: Request):
    texto = pergunta.texto.strip().lower()
    user_ip = request.client.host
    conversa = conversas.get(user_ip)

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
        num_videos = int(texto)
        tema = conversa["tema"]
        materia = identificar_materia(tema)
        videos = buscar_videos_escolares(tema, materia, YOUTUBE_API_KEY, max_results=num_videos)

        conversas[user_ip]["videos"] = videos
        conversas[user_ip]["etapa"] = "processando_videos"

        resultados_processados = []
        for v in videos:
            audio_path = baixar_audio_youtube(v["link"])
            transcricao, labels = analisar_video_google(audio_path)
            resumo_questoes = gerar_resumo_questoes_gemini(transcricao, labels, tema)
            resultados_processados.append({"titulo": v["titulo"], "link": v["link"], "resumo_questoes": resumo_questoes})

        conversas[user_ip]["etapa"] = "finalizado"
        return {"resposta": f"Aqui estão os vídeos e análises sobre '{tema}':", "videos": resultados_processados, "questoes": ""}

    return {"resposta": "Não entendi. Tente enviar um tema ou um número de vídeos.", "videos": [], "questoes": ""}
