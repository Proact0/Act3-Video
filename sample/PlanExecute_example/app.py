import streamlit as st
import time
from sample.PlanExecute_example.cast.workflow import plan_execute_workflow
from sample.PlanExecute_example.cast.state import PlanExecuteState

st.set_page_config(page_title="Plan & Execute Demo (한국어)", page_icon="🤖")

st.title("🤖 Plan & Execute (한국어 버전)")
st.write("LangGraph + Ollama 기반으로 **계획 → 실행** 단계를 거쳐 결과를 한국어로 보여줍니다.")

# 사용자 입력
user_prompt = st.text_area("프롬프트를 입력하세요:", "AI 기반 비디오 제작 기획안을 짜줘")

if st.button("실행"):
    progress = st.progress(0)   # 진행률 바
    status_text = st.empty()    # 상태 메시지

    with st.spinner("⏳ Plan & Execute 실행 중입니다... 시간이 조금 걸립니다."):
        workflow = plan_execute_workflow()
        init_state = PlanExecuteState(prompt=user_prompt, plan=None, result=None)

        # -----------------------------
        # 1단계: Planner (진행률 50%)
        # -----------------------------
        status_text.text("📋 Planner 실행 중...")
        time.sleep(1)  # 가짜 대기 (실제 Planner 내부는 workflow.invoke 안에서 실행됨)
        progress.progress(50)

        # -----------------------------
        # 2단계: Executor (진행률 100%)
        # -----------------------------
        status_text.text("⚙️ Executor 실행 중...")
        final_state = workflow.invoke(init_state)
        progress.progress(100)

    st.success("✅ 실행 완료!")
    status_text.empty()

    # 결과 출력
    st.subheader("📋 계획 (Planner Output)")
    st.write(final_state["plan"])

    st.subheader("⚙️ 실행 단계 (Executor Output)")
    st.write(final_state["result"])
