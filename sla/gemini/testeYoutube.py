from googleapiclient.discovery import build

API_KEY = "AIzaSyAUJM31FikE9_ulW7kiKIQwJ2mDK6m50vM"  # Substitua pela sua chave de API do YouTube
youtube = build("youtube", "v3", developerKey=API_KEY)
nome = input("Digite o nome do canal: ")
request = youtube.search().list(
    part="snippet",
    type="channel",
    q= nome,
    maxResults=1  # Limita a busca a um resultado
)
response = request.execute()

if response['items']:
    channel = response['items'][0]
    channel_id = channel['snippet']['channelId']
    channel_title = channel['snippet']['title']
    channel_url = f"https://www.youtube.com/channel/{channel_id}"

    print(f"Título do canal: {channel_title}")
    print(f"URL do canal: {channel_url}")
else:
    print(f"Nenhum canal encontrado com o termo {nome}.")

