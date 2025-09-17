import streamlit as st
from agent_core.graph import build_graph

st.title("🎬 자동 숏폼 영상 생성기")

prompt = st.text_input("프롬프트 입력 (예: 탈모 광고)")
aspect = st.selectbox("화면비", ["9:16", "16:9"], index=0)
duration = st.number_input("길이 (초)", min_value=5, max_value=60, value=15)

if st.button("영상 생성"):
    state = {"prompt": prompt, "aspect": aspect, "duration_sec": float(duration)}
    app = build_graph()
    final_state = app.invoke(state)

    st.json({k: str(v) for k, v in final_state.items()})

    if final_state.get("video_file"):
        st.video(final_state["video_file"])
