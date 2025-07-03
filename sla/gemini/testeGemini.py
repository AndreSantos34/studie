import google.generativeai as genai

try:
    genai.configure(api_key='AIzaSyBQk6I7IV7YEU26iKYJvi2mKEqWcdTDboI')  # Replace with your actual API key

    model_id = 'models/gemini-1.5-flash-latest'  #  <---  CHANGE THIS TO EACH MODEL
    model = genai.GenerativeModel(model_id)
    response = model.generate_content("faça uma contagem de 0 ate.")
    print(f"Model {model_id} response: {response.text}")

except Exception as e:
    print(f"Error: {e}")