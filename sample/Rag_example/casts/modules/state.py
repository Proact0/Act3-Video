from langgraph.graph import MessagesState

# Agentic RAG에서 사용할 상태 정의
class RagState(MessagesState):
    """RAG 그래프 상태 (messages 리스트 포함)."""
    pass
