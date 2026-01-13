import google.generativeai as genai

# Replace with your key
API_KEY = "AIzaSyB430xmOWFPsFZ97eOlwnSKwduO1et2Vlo"

def gemini_chat(prompt: str, model: str = "gemini-flash-latest"):
    genai.configure(api_key=API_KEY)

    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt)

    return response.text


if __name__ == "__main__":
    print("Sending request to Gemini...")
    reply = gemini_chat("Explain quantum computers like I'm 10.")
    print("Gemini reply:\n", reply)
