import requests
import json

API_KEY = "sk-7813c16870994584be5f11a3d6e6432f"
API_URL = "https://api.deepseek.com/v1/chat/completions"

def deepseek_chat(prompt: str, model: str = "deepseek-chat"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]

if __name__ == "__main__":
    print("Sending request to DeepSeek...")
    reply = deepseek_chat("Explain quantum computers like I'm 10.")
    print("DeepSeek reply:\n", reply)
