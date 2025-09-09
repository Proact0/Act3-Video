# LangGraph, 기본 용어 및 문법 정리

## 1. 기본 개념

### 1.1. 그래프 (Graph)

LangGraph의 핵심 구성 요소로, 노드(Node)와 엣지(Edge)의 연결로 이루어진 상태 머신(State Machine)입니다. 전체 워크플로우를 시각화하고 관리하는 데 사용됩니다.

### 1.2. 스테이트 (State)

그래프의 각 노드를 거치면서 전달되고 업데이트되는 데이터 객체입니다. 일반적으로 Python의 `TypedDict`를 상속하여 정의하며, 그래프의 현재 상태를 나타냅니다.

**예시:**

```python
from typing import TypedDict, List

class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[str]
```

### 1.3. 노드 (Node)

그래프의 기본 실행 단위로, 특정 작업을 수행하는 함수 또는 호출 가능한 객체입니다. 각 노드는 `State` 객체를 입력으로 받아 `State`의 일부 또는 전체를 업데이트하여 반환합니다.

**예시:**

```python
def generate_node(state):
    print("---GENERATE---")
    question = state["question"]
    # ... LLM 호출 로직 ...
    generation = "LangGraph is a library for building stateful, multi-actor applications with LLMs."
    return {"generation": generation}
```

### 1.4. 엣지 (Edge)

노드와 노드 사이의 연결을 정의합니다. 한 노드의 작업이 끝난 후 다음에 어떤 노드를 실행할지 지정합니다.

- **일반 엣지**: 항상 정해진 다음 노드로 이동합니다.
- **조건부 엣지 (Conditional Edge)**: `State`를 기반으로 동적으로 다음 노드를 결정합니다. 특정 조건에 따라 다른 분기로 워크플로우를 제어할 수 있습니다.

## 2. 그래프 구성 및 실행

### 2.1. Graph 객체 생성

`StateGraph` 클래스를 사용하여 그래프 객체를 생성합니다. 이때 그래프의 `State`를 정의한 클래스를 전달합니다.

```python
from langgraph.graph import StateGraph

workflow = StateGraph(GraphState)
```

### 2.2. 노드 추가

`add_node` 메서드를 사용하여 그래프에 노드를 추가합니다.

```python
workflow.add_node("generate", generate_node)
workflow.add_node("research", research_node)
```

### 2.3. 진입점 설정 (Entry Point)

`set_entry_point` 메서드로 그래프가 시작될 노드를 지정합니다.

```python
workflow.set_entry_point("generate")
```

### 2.4. 엣지 추가

#### 일반 엣지

`add_edge` 메서드를 사용하여 두 노드를 직접 연결합니다.

```python
# generate 노드 다음에 research 노드를 실행
workflow.add_edge("generate", "research")
```

- `END`: 그래프의 실행을 종료하는 특별한 노드 이름입니다.

```python
workflow.add_edge("research", END)
```

#### 조건부 엣지

`add_conditional_edges` 메서드를 사용하여 조건에 따라 다음 노드를 선택합니다.

- **Source Node**: 조건을 검사할 노드
- **Condition Function**: `State`를 입력으로 받아 다음 노드의 이름을 문자열로 반환하는 함수
- **Path Mapping**: Condition 함수의 반환값과 실제 노드 이름을 매핑하는 딕셔너리

**예시:**

```python
def should_continue(state):
    if "weather" in state["generation"].lower():
        return "search_weather"
    else:
        return "end"

workflow.add_conditional_edges(
    "generate",
    should_continue,
    {
        "search_weather": "research",
        "end": END,
    },
)
```

### 2.5. 그래프 컴파일 및 실행

#### 컴파일

`compile` 메서드를 사용하여 정의된 워크플로우를 실행 가능한 객체로 만듭니다.

```python
app = workflow.compile()
```

#### 실행

`stream` 또는 `invoke` 메서드를 사용하여 그래프를 실행합니다.

- **`stream`**: 각 노드의 실행 결과를 실시간으로 스트리밍합니다.
- **`invoke`**: 모든 워크플로우가 완료된 후 최종 `State`를 반환합니다.

**예시:**

```python
# 스트리밍 실행
inputs = {"question": "What is LangGraph?"}
for output in app.stream(inputs):
    for key, value in output.items():
        print(f"Finished running: {key}:")
        print(value)
    print("---")

# 단일 실행
final_state = app.invoke(inputs)
print(final_state["generation"])
```

## 3. 전체 코드 예시

```python
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

# 1. State 정의
class GraphState(TypedDict):
    question: str
    generation: str

# 2. Node 함수 정의
def generate_node(state: GraphState) -> dict:
    print("---ACTION: Generating---")
    # LLM을 사용하여 질문에 대한 답변 생성 (예시)
    generation = f"The answer to '{state['question']}' is 42."
    return {"generation": generation}

def final_node(state: GraphState) -> dict:
    print("---ACTION: Final Output---")
    # 최종 상태를 출력하거나 다른 작업을 수행
    print(f"Final Generation: {state['generation']}")
    return {}

# 3. Graph 객체 생성
workflow = StateGraph(GraphState)

# 4. 노드 추가
workflow.add_node("generate", generate_node)
workflow.add_node("final", final_node)

# 5. 진입점 및 엣지 설정
workflow.set_entry_point("generate")
workflow.add_edge("generate", "final")
workflow.add_edge("final", END)

# 6. 그래프 컴파일
app = workflow.compile()

# 7. 그래프 실행
inputs = {"question": "What is the meaning of life?"}
for event in app.stream(inputs, {"recursion_limit": 5}):
    for key, value in event.items():
        print(f"Node '{key}' output:")
        print(value)
    print("---")

```
