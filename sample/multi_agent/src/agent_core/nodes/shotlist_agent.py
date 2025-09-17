import os, json

def run(state):
    script = state.get("script", {})
    beats = script.get("beats", [])

    shots = [{"id": i+1, "text": beat} for i, beat in enumerate(beats)]
    state["shotlist"] = shots

    os.makedirs("outputs/shotlist", exist_ok=True)
    with open("outputs/shotlist/shotlist.json", "w", encoding="utf-8") as f:
        json.dump(shots, f, ensure_ascii=False, indent=2)

    print("[shotlist_agent] 저장됨: outputs/shotlist/shotlist.json")
    return state
