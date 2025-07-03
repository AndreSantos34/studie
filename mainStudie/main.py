from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
from googleapiclient.discovery import build
from temas import TEMAS_POR_MATERIA

# === CHAVES DE API ===
YOUTUBE_API_KEY = 'AIzaSyClB66YUAolBTKU7mN3Wucs2vgixHZvsjE'
GEMINI_API_KEY = 'AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI'

# === Função para identificar a matéria de um tema ===
def identificar_materia(tema):
    tema = tema.lower().strip()
    for materia, temas in TEMAS_POR_MATERIA.items():
        for t in temas:
            if t in tema:
                return materia
    return None

# === Função para buscar vídeos escolares ===
def buscar_videos_escolares(tema, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
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
        descricao = item['snippet'].get('description', '')  # pega a descrição do vídeo
        video_id = item['id']['videoId']
        link = f"https://www.youtube.com/watch?v={video_id}"

        resultados.append({
            'titulo': titulo,
            'canal': canal,
            'descricao': descricao,
            'link': link
        })

    return resultados

# === Função para gerar questões com base nos vídeos (títulos + descrições) ===
def gerar_questoes_gemini(tema, videos, api_key):
    genai.configure(api_key=api_key)
    modelo = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

    # Formata título + descrição para cada vídeo
    detalhes_videos = "\n\n".join(
        [f"Título: {v['titulo']}\nDescrição: {v['descricao']}" for v in videos]
    )

    prompt = f"""
Você é um assistente educacional. Com base nos seguintes vídeos e suas descrições sobre o tema "{tema}", gere 10 questões objetivas, curtas e de nível escolar (ensino médio). As perguntas devem estar diretamente relacionadas ao conteúdo sugerido pelos vídeos.

Vídeos:
{detalhes_videos}
    """

    resposta = modelo.generate_content(prompt)
    return resposta.text.strip()

# === Função principal para execução no terminal ===
def executar_pesquisa(tema):
    materia = identificar_materia(tema)

    if not materia:
        print(f"❌ Tema '{tema}' não é permitido. Escolha um tema escolar como 'Guerra Fria', 'Frações', etc.")
        print("✅ Exemplos aceitos por matéria:")
        for mat, temas in TEMAS_POR_MATERIA.items():
            print(f"  - {mat.title()}: {', '.join(temas)}")
        return

    print(f"\n📚 Tema aceito: '{tema.title()}' (Matéria: {materia.title()})")
    print(f"🔎 Buscando vídeos escolares sobre: {tema.title()}\n")
    videos = buscar_videos_escolares(tema, YOUTUBE_API_KEY)

    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['titulo']}\n   Canal: {video['canal']}\n   Link: {video['link']}\n")

    print("🧠 Gerando questões relacionadas aos vídeos com Gemini...\n")
    questoes = gerar_questoes_gemini(tema, videos, GEMINI_API_KEY)
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

class Pergunta(BaseModel):
    texto: str

@app.post("/perguntar")
async def perguntar(pergunta: Pergunta):
    tema = pergunta.texto.strip().lower()
    materia = identificar_materia(tema)

    if not materia:
        return {
            "resposta": f"Tema inválido ou não reconhecido. Tente temas como: guerra fria, frações, genética, etc.",
            "videos": [],
            "questoes": ""
        }

    videos = buscar_videos_escolares(tema, YOUTUBE_API_KEY)
    questoes = gerar_questoes_gemini(tema, videos, GEMINI_API_KEY)

    return {
        "resposta": f"Aqui estão os vídeos sobre '{tema}' (Matéria: {materia}):",
        "videos": videos,
        "questoes": questoes
    }

# === Execução por terminal ===
if __name__ == "__main__":
    tema = input("Digite um tema escolar: ").strip().lower()
    executar_pesquisa(tema)
