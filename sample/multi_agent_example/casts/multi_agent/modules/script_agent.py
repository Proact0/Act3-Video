import os
import json
# from agent_core.types import Script

def run(state):
    prompt = state.get("prompt", "")
    # duration = state.get("duration_sec", 15.0)
    # aspect = state.get("aspect", "9:16")

    # 간단한 예시 (LLM 대신)
    beats = [
        "이젠 걱정 끝!",
        "두피부터 건강하게!",
        "풍성한 머릿결, 되찾아봐!",
        "100% 천연 성분!",
        "효과는 확실하게!",
        "지금 바로 체험해보세요!"
    ]

    state["script"] = {
        "title": f"{prompt} 광고 스크립트",
        "beats": beats
    }

    os.makedirs("outputs/script", exist_ok=True)
    with open("outputs/script/script.json", "w", encoding="utf-8") as f:
        json.dump(state["script"], f, ensure_ascii=False, indent=2)

    print("[script_agent] 저장됨: outputs/script/script.json")
    return state
