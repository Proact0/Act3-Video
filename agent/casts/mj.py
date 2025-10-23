from __future__ import annotations
from typing import Dict, Any, List, Optional

from .brief import Brief

# 톤 키워드 → 스타일/무드 매핑(필요시 더 추가)
_TONE_MAP = {
    "핑크": ["soft pastel", "romantic vibe"],
    "맑음": ["clean light", "airy"],
    "투명": ["subsurface scattering", "glass-like clarity"],
    "쿨": ["minimal", "cool tone"],
    "레트로": ["analog film", "grain"],
    "따뜻함": ["warm light", "cozy"],
    "하이틴": ["teen movie", "bright color grade"],
    "미니멀": ["minimal composition", "negative space"],
}

def _style_from_tone(tone_list: Optional[List[str]]) -> List[str]:
    tone_list = tone_list or []
    styles: List[str] = []
    for t in tone_list:
        tkey = t.strip().lower()
        for k, v in _TONE_MAP.items():
            if k.lower() in tkey:
                styles.extend(v)
    # 중복 제거
    seen, uniq = set(), []
    for s in styles:
        if s not in seen:
            uniq.append(s); seen.add(s)
    return uniq

def build_midjourney_prompt(
    brief: Brief,
    scenario: Dict[str, Any],
    beat_index: int = 0,
    *,
    aspect_ratio: str = "9:16",
    version: str = "6.0",
    stylize: int = 250,
    quality: float = 1.0,
    seed: Optional[int] = None,
) -> str:
    """시나리오의 특정 컷(기본 0번) 기준으로 MJ 프롬프트 생성."""
    beats = scenario.get("beats") or []
    beat = beats[beat_index] if beats else {}
    subject = brief.product or "hero product"
    scene = beat.get("scene") or brief.background or "clean studio backdrop"
    mood_words = _style_from_tone(brief.tone)
    mood = ", ".join(mood_words) if mood_words else "cinematic, soft lighting"
    target = brief.target or "teen audience"

    parts = [
        f"{subject}, close-up product focus",
        f"scene: {scene}",
        f"mood/style: {mood}",
        "high detail, shallow depth of field, volumetric light",
        "color grade for shortform vertical video",
        f"target: {target}",
    ]
    core = " | ".join(parts)

    flags = [f"--ar {aspect_ratio}", f"--v {version}", f"--stylize {stylize}", f"--quality {quality}"]
    if seed is not None:
        flags.append(f"--seed {seed}")

    return f"{core} {' '.join(flags)}"
