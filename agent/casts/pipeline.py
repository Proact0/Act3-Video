from __future__ import annotations

import json
import os
import re
from typing import Any, Dict

from .client import ask_openrouter
from .brief import Brief, parse_brief

# MJ 모듈은 선택 기능이므로 안전 임포트
try:
    from .mj import build_midjourney_prompt  # type: ignore
except Exception:
    build_midjourney_prompt = None  # type: ignore

try:
    from .mj_scene import build_scene_prompts  # type: ignore
except Exception:
    build_scene_prompts = None  # type: ignore


def _load_system_prompt() -> str:
    """
    prompts/system_prompt.txt 가 있으면 우선 사용.
    없으면 내장 기본 프롬프트로 대체. (scene=설명형, 한국어 출력)
    """
    here = os.path.dirname(os.path.abspath(__file__))
    txt_path = os.path.join(os.path.dirname(here), "prompts", "system_prompt.txt")
    if os.path.isfile(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return (
        "당신은 TikTok/Reels/Shorts용 60초 내외 쇼츠 시나리오 에이전트입니다.\n\n"
        "반드시 **JSON만** 반환하세요:\n"
        "{\n"
        '  "duration_sec": 60,\n'
        '  "hook": "string",\n'
        '  "beats": [{"t":0,"scene":"string","dialog":"string"}],\n'
        '  "caption": "string",\n'
        '  "hashtags": ["string"]\n'
        "}\n\n"
        "규칙(한국어 출력):\n"
        "- 전체 길이는 브리프에 맞추되 기본 60초.\n"
        "- 컷 수는 기본 6–10 (사용자가 컷 지정 시 정확히 준수).\n"
        "- 0–3초에 강한 훅.\n"
        "- **scene은 키워드 나열이 아닌 '설명형 문장'**(카메라/동작/빛/분위기 포함)으로 작성.\n"
        "- dialog는 15자 이내의 자연스러운 한국어 대사.\n"
        "- caption/hashtags도 한국어.\n"
        "- 금지어(banned_words)가 있으면 사용 금지.\n"
    )


SYSTEM_PROMPT = _load_system_prompt()


def _equalize_timeline(data: Dict[str, Any], duration: int, cuts: int) -> None:
    """균등 분배(예: 60초/6컷 → 10초 간격)."""
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


def _best_effort_json_parse(raw: str) -> Dict[str, Any] | None:
    """LLM이 가끔 텍스트+JSON 섞어서 반환할 때 JSON만 뽑아내기."""
    # 1) 그대로 시도
    try:
        return json.loads(raw)
    except Exception:
        pass
    # 2) 가장 큰 { ... } 블록 추출
    m = re.search(r"\{(?:[^{}]|(?R))*\}", raw, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


def generate(
    brief_text: str,
    *,
    equalize: bool = True,
    mj_generate: bool = False,
    mj_aspect_ratio: str = "9:16",
) -> Dict[str, Any]:
    """엔드투엔드: 브리프 파싱 → LLM 생성(설명형 scene) → 후처리 → 검증 (+MJ 프롬프트)."""
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
        return raw  # 네트워크/키 등 에러 패스스루

    data = _best_effort_json_parse(raw)
    if not data:
        return {"error": "JSON_PARSE_FAIL", "raw": raw}

    cuts = brief.cuts
    duration = brief.duration_sec
    if cuts and equalize:
        _equalize_timeline(data, duration, cuts)

    qc = _quality_checks(data, brief_dict.get("banned_words", ""))
    data["_quality"] = qc

    # Midjourney 프롬프트(대표 썸네일 + 씬별) — 선택
    if mj_generate:
        if build_midjourney_prompt:
            try:
                data["midjourney_prompt"] = build_midjourney_prompt(
                    brief, data, beat_index=0, aspect_ratio=mj_aspect_ratio
                )
            except Exception as e:
                data["midjourney_prompt_error"] = str(e)
        if build_scene_prompts:
            try:
                data["scene_prompts"] = build_scene_prompts(
                    brief, data, aspect_ratio=mj_aspect_ratio
                )
            except Exception as e:
                data["scene_prompts_error"] = str(e)

    return data
