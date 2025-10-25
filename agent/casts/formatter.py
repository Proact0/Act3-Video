from __future__ import annotations
from typing import Any, Dict, List


def to_text_script(data: Dict[str, Any]) -> str:
    """JSON 시나리오 → 사람이 읽는 텍스트 스크립트(+MJ 프롬프트)."""
    out: List[str] = []

    out.append(f"# HOOK: {data.get('hook', '').strip()}")
    beats = data.get("beats") or []
    for i, b in enumerate(beats, 1):
        t = b.get("t", 0)
        scene = b.get("scene", "")
        dialog = b.get("dialog", "")
        out.append(f"\n[{i}] t={t:>2}s  SCENE: {scene}\n    DIALOG: {dialog}")

    # 씬별 MJ 프롬프트(영문)
    scene_prompts = data.get("scene_prompts")
    if scene_prompts:
        out.append("\n---\n🎬 Scene-by-Scene Image Prompts (English)")
        for i, p in enumerate(scene_prompts, 1):
            out.append(f"{i}. {p}")

    # 대표 썸네일 프롬프트
    mj = data.get("midjourney_prompt")
    if mj:
        out.append("\n---\n🎨 Main Thumbnail Prompt\n" + mj)

    caption = data.get("caption", "")
    tags = data.get("hashtags", [])
    out.append("\n---\nCAPTION: " + caption)
    if tags:
        out.append("TAGS: " + " ".join(tags))

    return "\n".join(out)
