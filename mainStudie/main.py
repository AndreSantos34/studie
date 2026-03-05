from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
from googleapiclient.discovery import build
from typing import Dict
import re
from temas import TEMAS_POR_MATERIA

# === CHAVES DE API ===
YOUTUBE_API_KEY = '#'
GEMINI_API_KEY = '#'

# === Configura Gemini explicitamente ===
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
        safeSearch='strict',
        videoDuration='medium', # Vídeos de duração média
        order='relevance', # Ordenar por relevância
        relevanceLanguage='pt'  # Relevância para o português
    ).execute()

    resultados = []
    for item in resposta['items']:
        titulo = item['snippet']['title']
        canal = item['snippet']['channelTitle']
        descricao = item['snippet'].get('description', '')
        video_id = item['id']['videoId']
        link = f"https://www.youtube.com/watch?v={video_id}"

        resultados.append({
            'titulo': titulo,
            'canal': canal,
            'descricao': descricao,
            'link': link
        })

    return resultados

# === Gerar questões com Gemini ===
def gerar_questoes_gemini(tema, videos, num_questoes=10):
    modelo = genai.GenerativeModel(model_name="models/gemini-2.5-flash")

    detalhes_videos = "\n\n".join(
        [f"Título: {v['titulo']}\nDescrição: {v['descricao']}" for v in videos]
    )

    prompt = f"""
        Você é um assistente educacional. 
        Com base nos seguintes vídeos e suas descrições sobre o tema "{tema}", 
        gere {num_questoes} questões objetivas, curtas e de nível escolar (ensino médio).

        Regras obrigatórias:
        - Cada questão deve ter enunciado claro.
        - Sempre 5 alternativas: A, B, C, D, E.
        - NÃO forneça o gabarito.
        - Numere as questões de 1 até {num_questoes}.
        - Formato exatamente assim:

        1) Pergunta aqui?
        A) Alternativa 1
        B) Alternativa 2
        C) Alternativa 3
        D) Alternativa 4
        E) Alternativa 5
        Vídeos:
{detalhes_videos}
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

from starlette.staticfiles import StaticFiles

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


from fastapi.responses import FileResponse

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("index.html", headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })
    
class Pergunta(BaseModel):
    texto: str

@app.post("/perguntar")
async def perguntar(pergunta: Pergunta, request: Request):
    texto = pergunta.texto.strip().lower()
    user_ip = request.client.host
    conversa = conversas.get(user_ip)

    # === INTENÇÃO: mais vídeos ===
    if conversa and re.search(r"(?:mais|outros)\s*(\d{0,2})?\s*vídeos?", texto):
        tema = conversa["tema"]
        materia = identificar_materia(tema)
        videos_anteriores = conversa.get("videos", [])
        num_videos = int(re.search(r"(\d{1,2})", texto).group(1)) if re.search(r"(\d{1,2})", texto) else 5

        novos_videos = buscar_videos_escolares(tema, materia, YOUTUBE_API_KEY, max_results=num_videos)
        ids_existentes = {v["link"].split("=")[-1] for v in videos_anteriores}
        novos_unicos = [v for v in novos_videos if v["link"].split("=")[-1] not in ids_existentes]

        conversas[user_ip]["videos"] = videos_anteriores + novos_unicos
        conversas[user_ip]["etapa"] = "aguardando_questoes"

        return {
            "resposta": f"Aqui estão mais vídeos sobre '{tema}' (Matéria: {materia}):",
            "videos": novos_unicos,
            "questoes": "Quantas questões deseja gerar agora?"
        }

    # === INTENÇÃO: mais questões ===
    if conversa and re.search(r"(?:mais|outras)\s*(\d{0,2})?\s*(questões|perguntas)", texto):
        tema = conversa["tema"]
        materia = identificar_materia(tema)
        videos = conversa.get("videos", [])
        num_q = int(re.search(r"(\d{1,2})", texto).group(1)) if re.search(r"(\d{1,2})", texto) else 10

        questoes = gerar_questoes_gemini(tema, videos, num_questoes=num_q)
        conversas[user_ip]["etapa"] = "finalizado"

        return {
            "resposta": f"Aqui estão mais {num_q} questões sobre '{tema}' (Matéria: {materia}):",
            "videos": [],
            "questoes": questoes
        }

    # === Etapa 3 – número de questões ===
    if re.fullmatch(r"\d{1,2}", texto) and conversa and conversa.get("etapa") == "aguardando_questoes":
        num_questoes = int(texto)
        tema = conversa["tema"]
        videos = conversa["videos"]
        materia = identificar_materia(tema)

        questoes = gerar_questoes_gemini(tema, videos, num_questoes=num_questoes)
        conversas[user_ip]["etapa"] = "finalizado"

        return {
            "resposta": f"Aqui estão {num_questoes} questões sobre '{tema}' (Matéria: {materia}):",
            "videos": [],
            "questoes": questoes
        }

    # === Etapa 2 – número de vídeos ===
    if re.fullmatch(r"\d{1,2}", texto) and conversa and conversa.get("etapa") == "aguardando_videos":
        num_videos = int(texto)
        tema = conversa["tema"]
        materia = identificar_materia(tema)
        videos = buscar_videos_escolares(tema, materia, YOUTUBE_API_KEY, max_results=num_videos)

        conversas[user_ip]["videos"] = videos
        conversas[user_ip]["etapa"] = "aguardando_questoes"

        return {
            "resposta": f"Aqui estão os vídeos sobre '{tema}' (Matéria: {materia}):",
            "videos": videos,
            "questoes": "Quantas questões você deseja gerar?"
        }

    # === Etapa 1 – novo tema ===
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
