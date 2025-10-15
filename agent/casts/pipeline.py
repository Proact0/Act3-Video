from __future__ import annotations

import json
from typing import Any, Dict

from .client import ask_openrouter
from .brief import Brief, parse_brief

SYSTEM_PROMPT = """
You are a short-form video scenario agent for TikTok/Reels/Shorts.

Return **JSON only**:
{
  "duration_sec": 60,
  "hook": "string",
  "beats": [{"t":0,"scene":"string","dialog":"string"}],
  "caption": "string",
  "hashtags": ["string"]
}

Rules:
- Keep total duration ~ user brief (default 60s).
- Prefer 6–10 cuts unless user sets cuts explicitly (e.g., 컷=6).
- First 3s: strong hook (emotion/question/twist).
- Each dialog ≤ 15 Korean characters.
- All output in Korean, concise and visual.
- Respect banned_words if provided (do not use them).
"""


def _equalize_timeline(data: Dict[str, Any], duration: int, cuts: int) -> None:
    """균등 분배(예: 10초 간격)."""
    beats = data.get("beats") or []
    beats = beats[:cuts]
    while len(beats) < cuts:
        beats.append({"t": 0, "scene": "", "dialog": ""})
    slot = max(1, duration // max(1, cuts))
    for i, b in enumerate(beats):
        b["t"] = i * slot
    data["beats"] = beats
    data["duration_sec"] = duration


def _quality_checks(data: Dict[str, Any], banned: str) -> Dict[str, Any]:
    issues = []
    beats = data.get("beats") or []

    if not data.get("hook"):
        issues.append("missing_hook")

    for i, b in enumerate(beats):
        dlg = (b.get("dialog") or "").replace(" ", "")
        if len(dlg) > 15:
            issues.append(f"dialog_too_long@{i}")

    if banned:
        low = banned.lower().split(",")
        blob = json.dumps(data, ensure_ascii=False).lower()
        for w in [x.strip() for x in low if x.strip()]:
            if w and w in blob:
                issues.append(f"banned:{w}")

    return {"ok": len(issues) == 0, "issues": issues}


def generate(brief_text: str, *, equalize: bool = True) -> Dict[str, Any]:
    """엔드투엔드: 브리프 파싱 → LLM 생성 → 후처리 → 검증."""
    brief: Brief = parse_brief(brief_text)
    brief_dict = brief.to_prompt_dict()

    user_msg = "다음 브리프를 반영해 시나리오를 JSON으로만 생성:\n" + json.dumps(
        brief_dict, ensure_ascii=False
    )
    if brief.cuts:
        user_msg += f"\n- 컷 수는 정확히 {brief.cuts}개로 구성해줘."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    raw = ask_openrouter(messages)
    if isinstance(raw, dict):
        return raw

    try:
        data = json.loads(raw)
    except Exception:
        return {"error": "JSON_PARSE_FAIL", "raw": raw}

    cuts = brief.cuts
    duration = brief.duration_sec
    if cuts and equalize:
        _equalize_timeline(data, duration, cuts)

    qc = _quality_checks(data, brief_dict.get("banned_words", ""))
    data["_quality"] = qc
    return data
