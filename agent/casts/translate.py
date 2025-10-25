from __future__ import annotations
from typing import List
import json

from .client import ask_openrouter

_SYS = (
    "You are a precise translator. "
    "Translate each Korean phrase into natural, concise **English** suitable for visual prompts. "
    "Return **JSON array of strings only**, same order, no extra keys or explanations."
)

def to_en_list(items: List[str]) -> List[str]:
    """KO 리스트 → EN 리스트 (순서/길이 유지). 실패 시 원문 그대로 반환."""
    if items is None:
        return []
    messages = [
        {"role": "system", "content": _SYS},
        {"role": "user", "content": json.dumps(items, ensure_ascii=False)},
    ]
    raw = ask_openrouter(messages)
    if isinstance(raw, dict):  # 네트워크/키 에러 등
        return items
    try:
        data = json.loads(raw)
        if isinstance(data, list) and all(isinstance(x, str) for x in data):
            return data
    except Exception:
        pass
    return items
