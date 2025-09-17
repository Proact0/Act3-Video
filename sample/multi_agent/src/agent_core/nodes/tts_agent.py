import os
from gtts import gTTS

def run(state):
    script = state.get("script", {})
    beats = script.get("beats", [])
    if not beats:
        print("[tts_agent] beats 없음 → 스킵")
        return state

    out_dir = "outputs/audio"
    os.makedirs(out_dir, exist_ok=True)

    tts_files = []
    for i, line in enumerate(beats, start=1):
        out_path = os.path.join(out_dir, f"line_{i}.mp3")
        try:
            tts = gTTS(text=line, lang="ko")
            tts.save(out_path)
            print(f"[tts_agent] 저장됨: {out_path}")
            tts_files.append(out_path)
        except Exception as e:
            print(f"[tts_agent] 오류: {e}")

    state["tts_files"] = tts_files
    return state
