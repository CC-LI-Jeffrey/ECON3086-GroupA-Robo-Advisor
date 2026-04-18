import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HKBU_AI_API_KEY")
base_url = "https://genai.hkbu.edu.hk/api/v0/rest"
model_name = "gpt-4.1"
api_version = "2024-12-01-preview"

def submit(user_message: str):
    system_message = (
        
    )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    url = f"{base_url}/deployments/{model_name}/chat/completions?api-version={api_version}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "api-key": api_key,
    }
    payload = {"messages": messages, "temperature": 0.7, "max_tokens": 150, "top_p": 1, "stream": False}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}
    
print(submit("Compare VOO and DYNF"))