import google.generativeai as genai
try:
    genai.configure(api_key="AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI")
    model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
    chat = model.start_chat( sys_instruct = "Você é Studie, um assistente virtual que ajuda usuários a encontrar informações sobre canais do YouTube. Você deve responder de forma clara e objetiva, fornecendo o nome do canal e o link para o canal no YouTube. Se não encontrar o canal, informe que não foi possível encontrar o canal com as informações fornecidas.")
    print("Iniciando o chat com Studie...")
    response = chat.send_message(chat)
    print(f"Studie: {response.text}\n") 

    while True:
        user_input = input("Digite algo para Studie ou digite 0 para ver o historico: ")
        sys_input = "you"
        if user_input.lower() == "exit":
            break

        if user_input == "0":
            print("Exibindo histórico de mensagens...")
            for message in chat.history:
                print(f"{message.role}: {message.parts[0].text}")
            continue
        
        response = chat.send_message(user_input)
        print(f"Gemini: {response.text}\n")

        if user_input == "1":
            print("----- Chat History -----")
            for message in chat.history:
                print(f"  {message.role}: {message.parts[0].text}")
            print("------------------------")

        

except Exception as e:
    print(f"An error occurred: {e}")




