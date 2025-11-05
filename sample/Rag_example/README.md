# Act3-Video (LangGraph + Ollama)

## 실행 방법

```bash
# 가상환경 생성
uv venv
uv sync --all-packages
```

# Ollama 설치

## Mac

```
brew install ollama
```

## Linux

curl -fsSL https://ollama.com/install.sh | sh

## Windows

# 👉 https://ollama.com/download 에서 설치 진행

# Ollama 서버 실행

```
ollama serve
```

# 모델 다운로드 (workflow.py에서 사용하는 모델명과 동일해야 함)

```
ollama pull mistral
ollama pull llama3
ollama pull gemma
ollama pull nomic-embed-text
```

# LangGraph 실행

```
uv run langgraph dev
```

# Streamlit 실행

```
uv run streamlit run /Users/username/Act3-Video/sample/Rag_example/app.py
```
