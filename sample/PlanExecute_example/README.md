# Act 3: Video – Plan & Execute Example

LangGraph + LangChain + Ollama를 활용한 **비디오 제작 에이전트 워크플로우** 예제입니다.  
사용자가 입력한 프롬프트를 기반으로 **계획(Planner)** → **실행(Executor)** 단계를 거쳐 결과를 출력합니다.  
Streamlit UI를 통해 쉽게 실행할 수 있으며, 결과는 **한국어로 번역/출력**됩니다.

---

## 🚀 기능

- **LangGraph 워크플로우**: Planner → Executor 노드 연결
- **모듈화 구조**: `cast/` 디렉토리 안에 `workflow.py`, `state.py`, `agents/`
- **Ollama 연동**: 로컬에서 LLM 실행 (예: `llama3`)
- **Streamlit UI 지원**: 입력 → 실행 → 결과를 브라우저에서 확인
- **한국어 강제 출력**: 모든 결과는 한국어로 표시
- **진행률 바 지원**: 실행 동안 게이지가 서서히 올라가며, 완료 시 100% 표시

---

## 1. uv환경설정

```bash
uv venv
uv sync --all-packages
```

## 2. Ollma 설치

로컬에서 설치해야합니다...

- Mac (brew 설치)

```bash
brew install ollama
```

- Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh

```

- window

```
https://ollama.com/download
```

- 모델 다운로드

```
ollama pull llama3
```

- 스트림릿과 랭그래프 실행 전 반드시 Ollma 서버가 켜져 있어야합니다.

```bash
ollama serve
```

## 3. 실행

### langgraph dev 서버 실행

```bash
cd sample/PlanExecute_example
uv run langgraph dev
```

### streamlit 실행

```bash
cd ~/Act3-Video
uv run streamlit run sample/PlanExecute_example/app.py
```
