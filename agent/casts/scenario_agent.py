from __future__ import annotations

import json
from typing import Dict, Any

from .client import ask_openrouter
from .brief import Brief, parse_brief


SYSTEM_PROMPT = """
You are a short-form video scenario agent for TikTok/Reels/Shorts.

Strictly return **JSON only** with:
{
  "duration_sec": 60,
  "hook": "string",
  "beats": [
    {"t": 0, "scene": "string", "dialog": "string"}
  ],
  "caption": "string",
  "hashtags": ["string"]
}

Rules:
- Keep total duration around the user brief (default 60s).
- 6–10 cuts unless user explicitly sets cuts (e.g., 컷=6).
- First 3 seconds: strong hook (emotion / question / twist).
- Each dialog ≤ 15 Korean characters.
- All text in Korean, concise and visual.
- Respect banned_words if provided (do not use them).
"""


def _postprocess(data: Dict[str, Any], desired_cuts: int | None, duration_sec: int) -> Dict[str, Any]:
    """옵션: 컷 수/타임라인 보정(요청 시)"""
    beats = data.get("beats") or []
    if desired_cuts is not None:
        beats = beats[:desired_cuts]
        while len(beats) < desired_cuts:
            beats.append({"t": 0, "scene": "", "dialog": ""})
        # 균등 분배(예: 10초씩): 요청 길이를 기준으로 컷 수로 나눔
        if desired_cuts > 0:
            slot = max(1, duration_sec // desired_cuts)
            for i, b in enumerate(beats):
                b["t"] = i * slot
    data["beats"] = beats
    data["duration_sec"] = duration_sec
    return data


def generate_scenario(brief_text: str) -> Dict[str, Any]:
    # 1) 브리프 파싱
    brief: Brief = parse_brief(brief_text)
    brief_dict = brief.to_prompt_dict()

    # 2) 메시지 구성
    user_msg = (
        "다음 브리프를 반영해 60초 시나리오를 JSON으로만 생성해줘.\n"
        f"{json.dumps(brief_dict, ensure_ascii=False)}"
    )
    # cuts를 강하게 요구하고 싶을 때만 아래 주석 해제
    # if brief.cuts:
    #     user_msg += f"\n- 정확히 {brief.cuts}컷으로 구성해줘."

    # 3) LLM 호출
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    raw = ask_openrouter(messages)
    if isinstance(raw, dict):
        return raw  # 에러 패스스루

    # 4) JSON 파싱
    try:
        data = json.loads(raw)
    except Exception:
        return {"error": "JSON_PARSE_FAIL", "raw": raw}

    # 5) 후처리(요청 컷 수/길이 반영)
    data = _postprocess(data, brief.cuts, brief.duration_sec)
    return data
