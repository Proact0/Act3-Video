from agent_core.nodes import script_agent, tts_agent

state = {
    "prompt": "테스트 광고",
    "aspect": "9:16",
    "duration_sec": 15.0,
}

# 먼저 스크립트 생성
state = script_agent.run(state)
print("\n[테스트] script 결과:", state.get("script"))

# TTS 실행
state = tts_agent.run(state)
print("\n[테스트] tts 결과:", state.get("tts_files"))
