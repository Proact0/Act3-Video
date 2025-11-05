from langgraph.graph import StateGraph
from pydantic import BaseModel
from langchain_community.llms import Ollama   # ✅ 변경된 부분


class ReflectionState(BaseModel):
    input_text: str
    draft: str | None = None
    feedback: str | None = None
    final_answer: str | None = None


# ✅ 무료 LLM: 로컬에서 실행되는 llama3
llm = Ollama(model="llama3")


def reflection_workflow():
    graph = StateGraph(ReflectionState)

    @graph.add_node
    def generate_draft(state: ReflectionState) -> ReflectionState:
        draft = llm.invoke(f"질문: {state.input_text}\n\n답변을 작성해줘.")
        return ReflectionState(input_text=state.input_text, draft=draft)

    @graph.add_node
    def reflect_on_draft(state: ReflectionState) -> ReflectionState:
        feedback = llm.invoke(f"다음 답변을 검토하고 부족한 점을 지적해줘:\n\n{state.draft}")
        return ReflectionState(input_text=state.input_text, draft=state.draft, feedback=feedback)

    @graph.add_node
    def refine_answer(state: ReflectionState) -> ReflectionState:
        final = llm.invoke(
            f"원래 질문: {state.input_text}\n"
            f"초안: {state.draft}\n"
            f"피드백: {state.feedback}\n\n"
            f"피드백을 반영한 최종 답변을 작성해줘."
        )
        return ReflectionState(
            input_text=state.input_text,
            draft=state.draft,
            feedback=state.feedback,
            final_answer=final
        )

    graph.set_entry_point("generate_draft")
    graph.add_edge("generate_draft", "reflect_on_draft")
    graph.add_edge("reflect_on_draft", "refine_answer")
    graph.set_finish_point("refine_answer")

    return graph.compile()
