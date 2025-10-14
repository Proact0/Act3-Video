from openai import OpenAI
import os

def ask_openrouter(messages, model="openai/gpt-oss-20b:free"):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "MISSING_OPENROUTER_API_KEY"}

    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
    )
    return resp.choices[0].message.content
