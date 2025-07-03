import google.generativeai as genai
from googleapiclient.discovery import build

# === CHAVES DE API ===
YOUTUBE_API_KEY = 'AIzaSyClB66YUAolBTKU7mN3Wucs2vgixHZvsjE'
GEMINI_API_KEY = 'AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI'

# === MATÉRIAS E TEMAS PERMITIDOS ===
TEMAS_POR_MATERIA = {
    "História": ["guerra fria", "revolução francesa", "era vargas", "segunda guerra mundial", "independência do brasil", "Historia", "História"],
    "Geografia": ["clima", "relevo", "migração", "urbano e rural", "globalização", "geografia"],
    "Matemática": ["frações", "porcentagem", "equações", "funções", "probabilidade", "matematica", "Matemática"],
    "Biologia": ["célula", "ecologia", "fotossíntese", "genética", "sistema digestório", "biologia", "Biologia"],
    "Química": ["tabela periódica", "ligações químicas", "reações", "ácidos e bases", "química orgânica ", "quimica", "Química"]
}

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
        video_id = item['id']['videoId']
        link = f"https://www.youtube.com/watch?v={video_id}"

        resultados.append({
            'titulo': titulo,
            'canal': canal,
            'link': link
        })

    return resultados

# === Função para gerar questões com base nos vídeos ===
def gerar_questoes_gemini(tema, titulos_videos, api_key):
    genai.configure(api_key=api_key)
    modelo = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

    titulos_formatados = "\n".join([f"- {titulo}" for titulo in titulos_videos])

    prompt = f"""
Você é um assistente educacional. Com base nos seguintes títulos de vídeos sobre o tema "{tema}", gere 10 questões objetivas, curtas e de nível escolar (ensino médio). As perguntas devem estar diretamente relacionadas ao conteúdo sugerido pelos vídeos.

Títulos dos vídeos:
{titulos_formatados}
    """

    resposta = modelo.generate_content(prompt)
    return resposta.text.strip()

# === Função principal ===
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

    titulos_videos = [v['titulo'] for v in videos]

    print("🧠 Gerando questões relacionadas aos vídeos com Gemini...\n")
    questoes = gerar_questoes_gemini(tema, titulos_videos, GEMINI_API_KEY)
    print(questoes)

# === Execução ===
if __name__ == "__main__":
    tema = input("Digite um tema escolar: ").strip().lower()
    executar_pesquisa(tema)
