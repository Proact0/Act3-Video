
import os
from dotenv import load_dotenv
import streamlit as st
from .workflow import build_graph  # ✅ import를 위쪽으로 이동

# 환경변수 로드
load_dotenv()




prompt = st.text_area("광고 프롬프트를 입력하세요:", "치킨 광고를 만들어줘 🍗")
aspect = st.selectbox("영상 비율", ["9:16", "1:1", "16:9"], index=0)
duration = st.number_input("영상 길이(초)", min_value=5.0, max_value=60.0, value=15.0, step=1.0)

if st.button("영상 생성"):
    state = {
        "prompt": prompt.strip(),
        "aspect": aspect,
        "duration": float(duration),
        "script": None,
        "shotlist": None,
        "tts_files": [],
        "image_files": [],
        "video_file": None,
    }
    try:
        app = build_graph()
        final_state = app.invoke(state)  # invoke가 실제 있는지 확인 필요
        st.subheader("최종 상태")
        st.json({k: str(v) for k, v in (final_state or {}).items()})

        video_path = (final_state or {}).get("video_file")
        if video_path and os.path.exists(video_path):
            st.video(video_path)
        else:
            st.warning("🎥 영상이 생성되지 않았습니다. 로그를 확인하세요.")
    except Exception as e:
        import traceback
        st.error(f"에러 발생: {e}")
        st.code(traceback.format_exc())