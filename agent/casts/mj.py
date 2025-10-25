from __future__ import annotations
from typing import Any, Dict, List, Optional

from .brief import Brief
from .translate import to_en_list

BASE_STYLE = (
    "cinematic lighting, ultra realistic, volumetric light, soft focus, film still, "
    "8k resolution, depth of field, masterpiece"
)

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
    beats = scenario.get("beats") or []
    beat = beats[beat_index] if beats else {}
    product_en = to_en_list([brief.product or "main product"])[0]
    message_en = to_en_list([brief.message or ""])[0] if brief.message else ""
    target_en = to_en_list([brief.target or ""])[0] if brief.target else ""
    scene_en = to_en_list([beat.get("scene") or brief.background or "clean studio backdrop"])[0]
    tone_en = ", ".join(to_en_list(brief.tone or [])) if brief.tone else "natural cinematic color tone"

    subject = f"{product_en}, close-up hero shot"
    mood = f"mood/style: {tone_en}"
    target_str = f"target: {target_en}" if target_en else ""

    core_parts = [
        subject,
        f"scene: {scene_en}",
        mood,
        BASE_STYLE,
        "color grade for vertical shortform video",
        target_str,
    ]
    core = " | ".join([p for p in core_parts if p])

    flags = [f"--ar {aspect_ratio}", f"--v {version}", f"--stylize {stylize}", f"--quality {quality}"]
    if seed is not None:
        flags.append(f"--seed {seed}")

    if message_en:
        core = f"{core} | concept: '{message_en}'"

    return f"{core} {' '.join(flags)}"
