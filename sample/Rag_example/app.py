import streamlit as st
from langchain_community.llms import Ollama

st.set_page_config(page_title="LangGraph RAG Demo", page_icon="🦙")

st.title("🦙 LangGraph + Ollama Demo")

# Ollama 모델 초기화 (mistral 예시)
llm = Ollama(model="mistral")

# 입력창
query = st.text_input("Enter your question:")

if query:
    st.write("### Question:")
    st.write(query)

    try:
        response = llm.invoke(query)
        st.write("### Answer:")
        st.write(response)
    except Exception as e:
        st.error(f"Error: {e}")
