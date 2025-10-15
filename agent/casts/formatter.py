from __future__ import annotations
from typing import Dict, Any, List

def to_text_script(data: Dict[str, Any]) -> str:
    """JSON 시나리오 → 사람이 읽는 텍스트 스크립트"""
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
    out.append("\n---\nCAPTION: " + caption)
    if tags:
        out.append("TAGS: " + " ".join(tags))
    return "\n".join(out)
