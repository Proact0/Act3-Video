from langchain_community.chat_models import ChatOllama

def run_executor(state):
    """
    Planner가 만든 계획을 구체적인 실행 단계로 변환
    출력은 반드시 한국어로 강제
    """
    llm = ChatOllama(model="llama3")
    result_text = llm.invoke(f"다음 계획을 한국어로 실행 단계로 구체화해줘:\n{state['plan']}")
    state["result"] = result_text
    return state
