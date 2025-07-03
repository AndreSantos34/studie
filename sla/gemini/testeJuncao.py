import google.generativeai as genai
from googleapiclient.discovery import build

try:
    # Configuração da API Gemini
    genai.configure(api_key="AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI")
    gemini_model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
    gemini_chat = gemini_model.start_chat()

    # Configuração da API do YouTube
    youtube_api_key = "AIzaSyAUJM31FikE9_ulW7kiKIQwJ2mDK6m50vM"
    youtube = build("youtube", "v3", developerKey=youtube_api_key)

    # Mensagem inicial do Gemini
    sys_instruct = "Você é Gemini."
    gemini_response = gemini_chat.send_message(sys_instruct)
    print(f"Gemini: {gemini_response.text}\n")

    while True:
        user_input = input("Digite algo para Gemini ou digite 'youtube [nome do canal]' para buscar no YouTube (ou 'exit' para sair): ")

        if user_input.lower() == "exit":
            break

        if user_input.lower().startswith("youtube "):
            channel_name = user_input[8:].strip()  # Remove "youtube " e espaços em branco
            youtube_request = youtube.search().list(
                part="snippet",
                type="channel",
                q=channel_name,
                maxResults=1
            )
            youtube_response = youtube_request.execute()

            if youtube_response['items']:
                channel = youtube_response['items'][0]
                channel_id = channel['snippet']['channelId']
                channel_title = channel['snippet']['title']
                channel_url = f"https://www.youtube.com/channel/{channel_id}"

                print(f"Título do canal (YouTube): {channel_title}")
                print(f"URL do canal (YouTube): {channel_url}")
            else:
                print(f"Nenhum canal encontrado com o termo '{channel_name}'.")

        elif user_input == "1":
            print("----- Chat History -----")
            for message in gemini_chat.history:
                print(f"  {message.role}: {message.parts[0].text}")
            print("------------------------")

        else:
            gemini_response = gemini_chat.send_message(user_input)
            print(f"Gemini: {gemini_response.text}\n")

except Exception as e:
    print(f"An error occurred: {e}")