from __future__ import annotations
from typing import Any, Dict, List, Optional

from .brief import Brief
from .translate import to_en_list

BASE_STYLE = (
    "cinematic lighting, ultra realistic, volumetric light, soft focus, film still, "
    "8k resolution, depth of field, masterpiece"
)

# 자주 쓰는 톤 키워드 → EN 스타일 보강
TONE_STYLE_MAP = {
    "핑크": "soft pastel colors, romantic atmosphere, warm tone",
    "맑음": "bright daylight, crisp focus, airy feeling",
    "투명": "translucent light, dreamy glow, airy composition",
    "쿨": "cool tone, minimal aesthetic, clean light",
    "따뜻": "golden hour lighting, cozy and emotional",
    "레트로": "vintage film grain, nostalgic mood",
    "하이틴": "teen-movie tone, vivid and colorful lighting",
    "몽환": "dreamlike ambience, ethereal haze, bokeh light",
}

def _tone_to_en_phrases(tone_list: Optional[List[str]]) -> str:
    if not tone_list:
        return "natural cinematic color tone"
    mapped: List[str] = []
    leftovers: List[str] = []
    for t in tone_list:
        matched = False
        for k, v in TONE_STYLE_MAP.items():
            if k in t:
                mapped.append(v)
                matched = True
                break
        if not matched:
            leftovers.append(t)
    if leftovers:
        mapped += to_en_list(leftovers)
    # 중복 제거
    seen, out = set(), []
    for m in mapped:
        if m and m not in seen:
            out.append(m); seen.add(m)
    return ", ".join(out) if out else "natural cinematic color tone"

def build_scene_prompts(
    brief: Brief,
    scenario: Dict[str, Any],
    *,
    aspect_ratio: str = "9:16",
    version: str = "6.0",
    stylize: int = 250,
) -> List[str]:
    """
    Build **English** Midjourney prompts per scene.
    - Korean brief/scene/dialog are auto-translated to natural English phrases.
    - Global context keeps the product/message consistent across all scenes.
    """
    beats = scenario.get("beats") or []

    # 1) 번역 대상 수집
    product_ko = brief.product or "제품"
    message_ko = brief.message or ""
    tone_ko = brief.tone or []
    scenes_ko = [str(b.get("scene") or "") for b in beats]
    dialogs_ko = [str(b.get("dialog") or "") for b in beats]

    # 2) 영어 변환
    product_en = to_en_list([product_ko])[0]
    message_en = to_en_list([message_ko])[0] if message_ko else ""
    tone_en = _tone_to_en_phrases(tone_ko)
    scenes_en = to_en_list(scenes_ko) if scenes_ko else []
    dialogs_en = to_en_list(dialogs_ko) if dialogs_ko else []

    subject_context = (
        f"A cinematic scene about {product_en}"
        + (f", expressing '{message_en}'." if message_en else ".")
    )

    prompts: List[str] = []
    for idx, beat in enumerate(beats):
        t = beat.get("t", idx * 10)
        scene_en = scenes_en[idx] if idx < len(scenes_en) else ""
        dialog_en = dialogs_en[idx] if idx < len(dialogs_en) else ""
        emotion_clause = f"The emotion of this moment is '{dialog_en}'." if dialog_en else ""

        prompt = (
            f"{subject_context} Scene {idx+1} at {t}s: {scene_en}. "
            f"{emotion_clause} Visualize it with {tone_en}. "
            f"{BASE_STYLE} --ar {aspect_ratio} --v {version} --stylize {stylize}"
        ).strip()
        prompts.append(prompt)

    return prompts
