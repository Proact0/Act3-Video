from casts.reflection.workflow import reflection_workflow, ReflectionState
import streamlit as st

# 워크플로우 불러오기
graph = reflection_workflow()

st.set_page_config(page_title="Reflection Example", page_icon="✨")

st.title("🪞 Reflection Example with LangGraph")
st.write("AI가 자기 답변을 되돌아보고 고치는 과정을 체험해보세요")

# 입력 폼
user_input = st.text_input("질문을 입력하세요:", "")

if st.button("Reflection 시작!"):
    if not user_input.strip():
        st.warning("⚠️ 질문을 입력해주세요!")
    else:
        # 초기 상태
        state = ReflectionState(input_text=user_input)

        # 그래프 실행 (전체)
        final_state = graph.invoke(state)

        # dict/객체 모두 대응
        if isinstance(final_state, dict):
            draft = final_state.get("draft")
            feedback = final_state.get("feedback")
            final_answer = final_state.get("final_answer")
        else:
            draft = getattr(final_state, "draft", None)
            feedback = getattr(final_state, "feedback", None)
            final_answer = getattr(final_state, "final_answer", None)

        # 단계별 출력
        if draft:
            st.subheader("✏️ Draft (초안)")
            st.info(draft)

        if feedback:
            st.subheader("🧐 Feedback (피드백)")
            st.warning(feedback)

        if final_answer:
            st.subheader("🌟 Final Answer (최종 답변)")
            st.success(final_answer)

        # 전체 상태 확인 (디버깅용)
        with st.expander("📦 Raw State 보기"):
            st.json(final_state if isinstance(final_state, dict) else final_state.dict())
