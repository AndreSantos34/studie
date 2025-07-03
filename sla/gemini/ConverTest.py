import google.generativeai as genai

try:
    # 1. Configure the API key using genai.configure()
    genai.configure(api_key="AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI") # Replace with your actual API key

    # 2. Use the GenerativeModel class to create a model instance
    model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')  # Use the model name you prefer
    # Ensure it supports generateContent from the list_models output!

    # 3. Start the conversation
    chat = model.start_chat()

    # 4. Send messages and get responses
    response1 = chat.send_message("Tenho 40 pães")
    print(response1.text)

    response2 = chat.send_message("Tenho dois irmão e dei 10 para cada quantos pães eu fiquei?")
    print(response2.text)

    # 5. Print the chat history (optional)
    for message in chat.history:  # Use chat.history, not chat._curated_history
        print(f'role - {message.role}: {message.parts[0].text}') #Fix print, remove end=


except Exception as e:
    print(f"An error occurred: {e}")