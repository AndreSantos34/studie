import google.generativeai as genai
from googleapiclient.discovery import build

# === CONFIGURAÇÕES ===
YOUTUBE_API_KEY = 'AIzaSyAUJM31FikE9_ulW7kiKIQwJ2mDK6m50vM'
GEMINI_API_KEY = 'AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI'

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
        video_id = item['id']['videoId']
        link = f"https://www.youtube.com/watch?v={video_id}"

        resultados.append({
            'titulo': titulo,
            'canal': canal,
            'link': link
        })

    return resultados

# === Função para gerar questões com Gemini ===
def gerar_questoes_gemini(tema, api_key):
    genai.configure(api_key=api_key)
    modelo = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Gere 10 questões objetivas, curtas e de nível escolar sobre o tema "{tema}".
    As questões devem ser educativas e adequadas para alunos do ensino médio.
    """

    resposta = modelo.generate_content(prompt)
    return resposta.text

# === Função principal ===
def executar_pesquisa(tema):
    print(f"\n🔎 Buscando vídeos escolares sobre: {tema}\n")
    videos = buscar_videos_escolares(tema, YOUTUBE_API_KEY)

    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['titulo']}\n   Canal: {video['canal']}\n   Link: {video['link']}\n")

    print("🧠 Gerando questões relacionadas ao tema com Gemini...\n")
    questoes = gerar_questoes_gemini(tema, GEMINI_API_KEY)
    print(questoes)

# === Execução ===
if __name__ == "__main__":
    tema = input("Digite o tema desejado: ")
    executar_pesquisa(tema)
