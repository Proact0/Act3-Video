from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import OllamaEmbeddings  # ✅ Ollama 임베딩
from langchain_community.chat_models import ChatOllama       # ✅ Ollama 챗모델
from langchain.tools.retriever import create_retriever_tool

from .modules.state import RagState

# ----------------------------
# 1. 문서 로드 및 전처리
# ----------------------------
urls = [
    "https://lilianweng.github.io/posts/2024-11-28-reward-hacking/",
    "https://lilianweng.github.io/posts/2024-07-07-hallucination/",
    "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/",
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=300, chunk_overlap=50
)
doc_splits = text_splitter.split_documents(docs_list)

# ----------------------------
# 2. 벡터스토어 및 리트리버
# ----------------------------
vectorstore = InMemoryVectorStore.from_documents(
    documents=doc_splits,
    embedding=OllamaEmbeddings(model="nomic-embed-text")  # ✅ 임베딩 전용 모델
)
retriever = vectorstore.as_retriever()
retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_blog_posts",
    "Search and return information about Lilian Weng blog posts.",
)

# ----------------------------
# 3. 모델 정의 (Ollama)
# ----------------------------
response_model = ChatOllama(model="llama3", temperature=0)


def generate_query_or_respond(state: RagState):
    """질문을 받고 검색할지, 바로 답변할지 결정"""
    response = response_model.bind_tools([retriever_tool]).invoke(state["messages"])
    return {"messages": [response]}


def rewrite_question(state: RagState):
    """검색이 잘 안될 경우 질문을 다시 작성"""
    rewrite = response_model.invoke(
        [{"role": "system", "content": "질문을 더 명확하게 다시 작성해줘."}] + state["messages"]
    )
    return {"messages": [rewrite]}


def generate_answer(state: RagState):
    """검색 결과를 포함해 최종 답변 생성"""
    answer = response_model.invoke(state["messages"])
    return {"messages": [answer]}


def grade_documents(state: RagState):
    """retriever 결과의 관련성 판단 (안전하게 문자열 처리)"""
    # 전체 메시지를 합쳐 문자열로 변환
    all_text = " ".join(
        getattr(m, "content", str(m)) for m in state["messages"]
    ).lower()

    if "reward" in all_text or "hacking" in all_text:
        return "generate_answer"   # 관련 있음
    else:
        return "rewrite_question"  # 관련 없음


# ----------------------------
# 4. 워크플로우 구성
# ----------------------------
def rag_workflow():
    workflow = StateGraph(RagState)

    # 노드 추가
    workflow.add_node(generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([retriever_tool]))
    workflow.add_node(rewrite_question)
    workflow.add_node(generate_answer)

    # 시작 → 질의 or 응답
    workflow.add_edge(START, "generate_query_or_respond")

    # retriever 호출 여부
    workflow.add_conditional_edges(
        "generate_query_or_respond",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )

    # retriever 후 문서 평가
    workflow.add_conditional_edges("retrieve", grade_documents)

    workflow.add_edge("generate_answer", END)
    workflow.add_edge("rewrite_question", "generate_query_or_respond")

    return workflow.compile()
