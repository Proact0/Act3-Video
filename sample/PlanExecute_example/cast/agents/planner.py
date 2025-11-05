from langchain_community.chat_models import ChatOllama

def run_planner(state):
    """
    사용자 프롬프트를 바탕으로 계획(Plan)을 세우는 단계
    출력은 반드시 한국어로 강제
    """
    llm = ChatOllama(model="llama3")
    plan_text = llm.invoke(f"다음 요청에 대해 반드시 한국어로 답변해줘:\n{state['prompt']}")
    state["plan"] = plan_text
    return state
