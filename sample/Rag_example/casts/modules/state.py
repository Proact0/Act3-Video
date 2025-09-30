from langgraph.graph import MessagesState
from typing import List, Dict, Any

class RagState(MessagesState):
    """RAG 그래프 상태 (messages + 검색결과 포함)."""
    retrieved_docs: List[Dict[str, Any]] = []   # RAG 검색 결과
    context: str = ""                           # 컨텍스트 텍스트
