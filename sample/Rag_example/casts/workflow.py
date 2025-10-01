import os
from pathlib import Path
from typing import List

from langgraph.graph import StateGraph, START, END
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama

# ❗ 절대 import (relative import 오류 방지)
from casts.modules.state import RagState


# ----------------------------
# 0) README 탐색 & 로드
# ----------------------------
def _find_readme() -> Path:
    here = Path(__file__).resolve()
    candidates = [
        here.parents[1] / "README.md",   # Rag_Example/README.md
        here.parents[2] / "README.md",   # 상위 프로젝트 루트/README.md
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("README.md를 찾지 못했습니다. Rag_Example/README.md 를 생성하세요.")

def _load_docs() -> List[str]:
    path = _find_readme()
    loader = TextLoader(str(path), encoding="utf-8")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    splits = splitter.split_documents(docs)
    return [d.page_content for d in splits]


# ----------------------------
# 1) 임베딩/리트리버 (Ollama)
# ----------------------------
# Ollama 임베딩 서버: nomic-embed-text
_embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))

_docs = _load_docs()
# InMemory 벡터스토어 → 추가 패키지 설치 불필요
_vectorstore = InMemoryVectorStore.from_texts(_docs, _embeddings)
_retriever = _vectorstore.as_retriever(search_kwargs={"k": 4})

# ----------------------------
# 2) LLM (Ollama Chat)
# ----------------------------
# 예: mistral / llama3 등. (미리 pull 필요)
_llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "mistral"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.2
)


# ----------------------------
# 3) 유틸
# ----------------------------
def _last_user_text(state: RagState) -> str:
    if not state["messages"]:
        return ""
    last = state["messages"][-1]
    # dict or BaseMessage 모두 안전 처리
    return last["content"] if isinstance(last, dict) else getattr(last, "content", str(last))


# ----------------------------
# 4) 노드
# ----------------------------
def retrieve_node(state: RagState):
    query = _last_user_text(state)
    docs = _retriever.get_relevant_documents(query)
    ctx = "\n\n---\n\n".join(d.page_content for d in docs)
    # 컨텍스트를 system 메시지로 누적
    return {"messages": [{"role": "system", "content": f"CONTEXT:\n{ctx}" if ctx else "CONTEXT: (no docs)"}]}

def generate_node(state: RagState):
    # 누적된 system CONTEXT + user 질문을 하나의 프롬프트로 구성
    full = "\n\n".join(m["content"] if isinstance(m, dict) else getattr(m, "content", str(m)) for m in state["messages"])
    prompt = (
        "You are a helpful RAG assistant. Use the CONTEXT to answer the USER question. "
        "If the answer is not in the context, say you are not sure.\n\n"
        f"{full}\n\nAnswer in Korean:"
    )
    out = _llm.invoke(prompt)
    text = out.content if hasattr(out, "content") else str(out)
    return {"messages": [{"role": "assistant", "content": text}]}


# ----------------------------
# 5) 그래프
# ----------------------------
def rag_workflow():
    g = StateGraph(RagState)
    g.add_node("retrieve", retrieve_node)
    g.add_node("generate", generate_node)

    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", END)
    return g.compile()
