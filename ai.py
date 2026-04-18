import openai
import os

# Set your OpenAI API key here or use an environment variable for security
openai.api_key = os.getenv("OPENAI_API_KEY", "你的API金鑰")

def ask_gpt(messages, model="gpt-4"):
    """
    Send a list of messages to OpenAI's ChatCompletion API and return the response content.
    messages: List of dicts, e.g. [{"role": "user", "content": "..."}]
    model: Model name, default 'gpt-4'.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message["content"]

if __name__ == "__main__":
    # Example usage
    messages = [
        {"role": "system", "content": "你是一個幫手。"},
        {"role": "user", "content": "請用繁體中文自我介紹。"}
    ]
    answer = ask_gpt(messages)
    print(answer)
