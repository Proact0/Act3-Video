from openai import OpenAI, APIConnectionError
import os

OPENROUTER_BASE = os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1").strip()

def ask_openrouter(messages, model="openai/gpt-oss-20b:free", timeout=30):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "MISSING_OPENROUTER_API_KEY"}
    client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            timeout=timeout,
        )
        return resp.choices[0].message.content
    except APIConnectionError as e:
        return {"error": "NETWORK", "detail": str(e), "base_url": OPENROUTER_BASE}
    except Exception as e:
        return {"error": "UNEXPECTED", "detail": str(e)}
