import json
from .client import ask_openrouter  # ← 상대 임포트 (중요!)

SYSTEM_PROMPT = """
You are a short-form video scenario agent.
Return JSON only:
{
 "duration_sec": 60,
 "hook": "string",
 "beats": [{"t":0,"scene":"string","dialog":"string"}],
 "caption": "string",
 "hashtags": ["string"]
}
Rules:
- 60초, 6컷
- 0~3초 강한 훅
- 각 대사 15자 이내(한글)
- 모든 텍스트는 한국어
"""

def generate_scenario(brief: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"브리프: {brief}"}
    ]
    raw = ask_openrouter(messages)
    if isinstance(raw, dict):  # 에러 메시지일 경우 그대로 반환
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {"error": "JSON_PARSE_FAIL", "raw": raw}
