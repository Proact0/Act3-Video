from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .client import ask_openrouter
from .brief import Brief, parse_brief

# (옵션) Midjourney 프롬프트 빌더가 없을 때도 동작하도록 안전 import
try:
    from .mj import build_midjourney_prompt  # type: ignore
except Exception:  # 파일이 없으면 MJ 기능만 비활성
    build_midjourney_prompt = None  # type: ignore


# ---------------- SYSTEM_PROMPT ----------------
# 파일 prompts/system_prompt.txt 가 있으면 그걸 쓰고, 없으면 기본 프롬프트 사용
def _load_system_prompt() -> str:
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    txt_path = os.path.join(os.path.dirname(here), "prompts", "system_prompt.txt")
    if os.path.isfile(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    # 기본값 (fallback)
    return """
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
""".strip()


SYSTEM_PROMPT = _load_system_prompt()
# ------------------------------------------------


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


def generate(
    brief_text: str,
    *,
    equalize: bool = True,
    mj_generate: bool = False,
    mj_aspect_ratio: str = "9:16",
) -> Dict[str, Any]:
    """엔드투엔드: 브리프 파싱 → LLM 생성 → 후처리 → 검증 (+옵션: MJ 프롬프트)."""
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

    # Midjourney 프롬프트(선택)
    if mj_generate and build_midjourney_prompt:
        try:
            data["midjourney_prompt"] = build_midjourney_prompt(
                brief, data, beat_index=0, aspect_ratio=mj_aspect_ratio
            )
        except Exception as e:
            data["midjourney_prompt_error"] = str(e)

    return data
