import os
from langgraph.graph import StateGraph, END
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import Chroma   # ✅ Chroma로 교체
from langchain_community.llms import HuggingFaceEndpoint

from .modules.state import RagState


# --------------------------
# 1. 문서 로드 + 분할
# --------------------------
def _load_docs():
    if os.path.exists("README.md"):
        loader = TextLoader("README.md")
        docs = loader.load()
    else:
        raise FileNotFoundError("README.md를 찾지 못했습니다.")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(docs)


_docs = _load_docs()

# --------------------------
# 2. 임베딩 + 벡터DB (Chroma)
# --------------------------
_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv("HF_API_KEY"),  # HuggingFace API 키 (환경변수)
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

vectorstore = Chroma.from_texts([d.page_content for d in _docs], _embeddings)
retriever = vectorstore.as_retriever()


# --------------------------
# 3. LLM (HuggingFace API)
# --------------------------
llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",  # 원하는 모델로 교체 가능
    huggingfacehub_api_token=os.getenv("HF_API_KEY"),
    temperature=0.7,
    max_new_tokens=256,
    return_full_text=False,
)


# --------------------------
# 4. 노드 정의
# --------------------------
def retrieve_node(state: RagState) -> RagState:
    """사용자 질문 기반으로 문서 검색"""
    query = state["messages"][-1]["content"] if state["messages"] else ""
    docs = retriever.get_relevant_documents(query)
    state["retrieved_docs"] = [d.page_content for d in docs]
    return state


def generate_node(state: RagState) -> RagState:
    """검색 결과 + LLM 기반 답변 생성"""
    query = state["messages"][-1]["content"]
    context = "\n".join(state.get("retrieved_docs", []))
    prompt = f"사용자 질문: {query}\n참고 문서:\n{context}\n\n답변:"
    answer = llm.invoke(prompt)
    state["messages"].append({"role": "assistant", "content": answer})
    return state


# --------------------------
# 5. 그래프 정의
# --------------------------
workflow = StateGraph(RagState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

workflow.add_edge("retrieve", "generate")
workflow.set_entry_point("retrieve")
workflow.set_finish_point("generate")

rag_workflow = workflow.compile()
