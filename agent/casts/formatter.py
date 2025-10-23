from __future__ import annotations
from typing import Dict, Any, List

def to_text_script(data: Dict[str, Any]) -> str:
    out: List[str] = []
    out.append(f"# HOOK: {data.get('hook','').strip()}")
    beats = data.get("beats") or []
    for i, b in enumerate(beats, 1):
        t = b.get("t", 0)
        scene = b.get("scene", "")
        dialog = b.get("dialog", "")
        out.append(f"\n[{i}] t={t:>2}s  SCENE: {scene}\n    DIALOG: {dialog}")
    caption = data.get("caption", "")
    tags = data.get("hashtags", [])

    # ★ MJ 프롬프트가 있으면 보여주기
    mj = data.get("midjourney_prompt")
    if mj:
        out.append("\n---\nMIDJOURNEY PROMPT:\n" + mj)

    out.append("\n---\nCAPTION: " + caption)
    if tags:
        out.append("TAGS: " + " ".join(tags))
    return "\n".join(out)
