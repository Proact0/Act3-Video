from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

@dataclass
class Brief:
    product: str = ""
    message: str = ""
    target: str = ""
    tone: List[str] = None
    background: str = ""
    duration_sec: int = 60
    cuts: Optional[int] = None
    narration: str = ""
    music: str = ""
    banned_words: List[str] = None

    def to_prompt_dict(self) -> Dict:
        return {
            "product": self.product,
            "message": self.message,
            "target": self.target,
            "tone": ", ".join(self.tone or []),
            "background": self.background,
            "duration_sec": self.duration_sec,
            "cuts": self.cuts,
            "narration": self.narration,
            "music": self.music,
            "banned_words": ", ".join(self.banned_words or []),
        }

    def to_json_ready(self) -> Dict:
        d = asdict(self)
        d["tone"] = self.tone or []
        d["banned_words"] = self.banned_words or []
        return d

def _split_list(val: str) -> List[str]:
    if not val:
        return []
    raw = [x.strip() for x in val.replace(";", ",").replace("/", ",").split(",")]
    return [x for x in raw if x]

def parse_brief(text: str) -> Brief:
    mapping = {
        "제품": "product", "product": "product",
        "메시지": "message", "message": "message",
        "타깃": "target", "target": "target",
        "톤": "tone", "tone": "tone",
        "배경": "background", "background": "background",
        "길이": "duration_sec", "duration": "duration_sec",
        "컷": "cuts", "cuts": "cuts",
        "나레이션": "narration", "narration": "narration",
        "음악": "music", "music": "music",
        "금지어": "banned_words", "banned": "banned_words",
    }
    pairs: Dict[str, str] = {}
    for chunk in text.replace(";", "\n").replace(",", "\n").splitlines():
        if "=" not in chunk: 
            continue
        k, v = chunk.split("=", 1)
        key = mapping.get(k.strip().lower())
        if key:
            pairs[key] = v.strip()

    b = Brief()
    b.product = pairs.get("product", "")
    b.message = pairs.get("message", "")
    b.target = pairs.get("target", "")
    b.tone = _split_list(pairs.get("tone", ""))
    b.background = pairs.get("background", "")
    try:
        if "duration_sec" in pairs:
            b.duration_sec = max(5, min(120, int(pairs["duration_sec"])))
    except ValueError:
        pass
    try:
        if "cuts" in pairs:
            c = int(pairs["cuts"])
            b.cuts = max(1, min(12, c))
    except ValueError:
        b.cuts = None
    b.narration = pairs.get("narration", "")
    b.music = pairs.get("music", "")
    b.banned_words = _split_list(pairs.get("banned_words", ""))
    return b

def get_brief_guide() -> str:
    return """\
[입력 가이드 예시]
제품=복숭아향 향수
메시지=첫사랑의 향기처럼 설렘
타깃=10대~20대 여학생
톤=핑크, 맑음, 투명
배경=햇살 드는 교실 창가
길이=60
컷=6
나레이션=잔잔하고 몽환적으로
음악=로맨틱 피아노
금지어=다이어트, 치료
"""

def _safe_int(text: str, default: int) -> int:
    try: return int(text.strip())
    except Exception: return default

def build_brief_interactively() -> Brief:
    print("\n[간단 입력 모드] 엔터=기본값\n")
    product = input("제품(예: 복숭아향 향수): ").strip()
    message = input("메시지/USP(예: 첫사랑의 설렘): ").strip()
    target = input("타깃(예: 10대~20대 여학생): ").strip()
    tone = input("톤(쉼표 구분, 예: 핑크, 맑음, 투명): ").strip()
    background = input("배경(예: 햇살 드는 교실 창가): ").strip()
    duration = _safe_int(input("길이(초, 기본 60): ").strip() or "60", 60)
    cuts_in = input("컷 수(빈칸=자동, 예: 6): ").strip()
    cuts = _safe_int(cuts_in, None) if cuts_in else None
    narration = input("나레이션 스타일: ").strip()
    music = input("음악 키워드: ").strip()
    banned = input("금지어(쉼표 구분): ").strip()
    return Brief(
        product=product, message=message, target=target,
        tone=_split_list(tone), background=background,
        duration_sec=max(5, min(120, duration)),
        cuts=(max(1, min(12, cuts)) if isinstance(cuts, int) else None),
        narration=narration, music=music, banned_words=_split_list(banned),
    )

def brief_to_kv_lines(brief: Brief) -> str:
    lines = [
        f"제품={brief.product}",
        f"메시지={brief.message}",
        f"타깃={brief.target}",
        f"톤={', '.join(brief.tone or [])}",
        f"배경={brief.background}",
        f"길이={brief.duration_sec}",
        (f"컷={brief.cuts}" if brief.cuts is not None else ""),
        f"나레이션={brief.narration}",
        f"음악={brief.music}",
        f"금지어={', '.join(brief.banned_words or [])}",
    ]
    return "\n".join([x for x in lines if x])
