from __future__ import annotations
from typing import Any, Dict, List

from .brief import Brief

# 2D 애니메이션 공통 스타일 (영문 키워드)
ANIM2D_STYLE = (
    "2D animation, anime-inspired, cel shading, clean line art, flat colors, "
    "toon shading, high detail, dramatic composition, expressive poses"
)

BASE_STYLE = (
    "cinematic lighting, soft focus, film still, "
    "8k resolution, depth of field, masterpiece"
)

DEFAULT_SCENE_KEYWORDS = [
    "dynamic camera angle",
    "clear subject focus",
    "simple background",
    "commercial framing",
]

def build_scene_prompts(
    brief: Brief,
    scenario: Dict[str, Any],
    *,
    aspect_ratio: str = "9:16",
    version: str = "6.0",
) -> List[str]:
    """
    씬별 Midjourney 프롬프트(영문 키워드).
    - 시나리오 beats의 scene/dialog 뉘앙스를 반영
    - 2D 애니메이션 스타일 고정
    - stylize 플래그 제거
    """
    beats = scenario.get("beats") or []
    tone = ", ".join([t for t in (brief.tone or []) if t]) or "clean color tone"

    prompts: List[str] = []
    for idx, beat in enumerate(beats):
        t = beat.get("t", idx * 10)
        scene_txt = (beat.get("scene") or "").strip()
        dialog_txt = (beat.get("dialog") or "").strip()

        # scene/dialog를 키워드 분위기로 살짝 투영(영문 키워드 구문)
        mood_bits: List[str] = []
        if scene_txt:
            mood_bits.append(f"visual idea: {scene_txt}")
        if dialog_txt:
            mood_bits.append(f"emotion: {dialog_txt}")

        parts: List[str] = [
            f"scene {idx+1} at {t}s",
            *DEFAULT_SCENE_KEYWORDS,
            f"mood: {tone}",
            *mood_bits,
            ANIM2D_STYLE,
            BASE_STYLE,
            f"--ar {aspect_ratio} --v {version}",
        ]
        prompt = " | ".join([p for p in parts if p])
        prompts.append(prompt)

    return prompts
