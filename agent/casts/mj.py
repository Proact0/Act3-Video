from __future__ import annotations
from typing import Any, Dict, Optional

from .brief import Brief

ANIM2D_STYLE = (
    "2D animation, anime-inspired, cel shading, clean line art, flat colors, "
    "toon shading, high detail"
)

BASE_STYLE = (
    "cinematic lighting, soft focus, film still, "
    "8k resolution, depth of field, masterpiece"
)

def build_midjourney_prompt(
    brief: Brief,
    scenario: Dict[str, Any],
    beat_index: int = 0,
    *,
    aspect_ratio: str = "9:16",
    version: str = "6.0",
    quality: float = 1.0,
    seed: Optional[int] = None,
) -> str:
    tone = ", ".join([t for t in (brief.tone or []) if t]) or "clean color grade"

    core_parts = [
        "hero product shot, commercial poster frame",
        "minimal background, crisp composition",
        f"mood: {tone}",
        ANIM2D_STYLE,
        BASE_STYLE,
        "vertical shortform frame",
    ]
    core = " | ".join([p for p in core_parts if p])

    flags = [f"--ar {aspect_ratio}", f"--v {version}", f"--quality {quality}"]
    if seed is not None:
        flags.append(f"--seed {seed}")

    return f"{core} {' '.join(flags)}"
