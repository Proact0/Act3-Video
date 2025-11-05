# 🪞 Reflection Example with LangGraph + Streamlit

LangGraph를 활용한 **Reflection Workflow** 예제입니다.  
AI가 자기 답변을 생성하고 → 되돌아보고 → 수정하는 과정을 단계별로 체험할 수 있습니다.
단, 시간이 많이 오래걸려요.

---

## 🚀 실행 방법

아래 명령어들을 순서대로 실행하세요.  
(OS에 따라 Ollama 설치 방법만 선택해서 진행)

```bash
# 1. uv 환경 설정
cd Reflection_example
uv venv
uv sync --all-packages


# 2. Ollama 설치 (환경에 맞게 선택)

## Mac
brew install ollama

## Linux
curl -fsSL https://ollama.com/install.sh | sh

## Windows
# 👉 https://ollama.com/download 에서 직접 설치


# 3. 모델 다운로드
ollama pull llama3

# 4. Ollama 서버 실행 (항상 켜져 있어야 함)
ollama serve


# 5. LangGraph dev 서버 실행 (새 터미널)
cd Reflection_example
uv run langgraph dev

# 6. Streamlit 실행 (또 다른 터미널)
cd Reflection_example
uv run streamlit run casts/reflection/app_streamlit.py
```
