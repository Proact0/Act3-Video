# LangChain, 기본 문법 및 핵심 개념 정리

## 1. LangChain이란?

LangChain은 ChatGPT와 같은 거대 언어 모델(LLM)을 외부 데이터 소스나 다른 기능들과 '연결(Chain)'하여, 더 강력하고 유용한 애플리케이션을 쉽게 만들 수 있도록 도와주는 개발 프레임워크이다.

## 2. 필수 기본 용어

- **LLM (Large Language Model):** '거대 언어 모델'. 방대한 텍스트 데이터로 학습하여 인간과 유사한 텍스트를 이해하고 생성하는 인공지능 모델 (ex. 챗지피티)

- **LCEL (LangChain Expression Language):** LangChain의 '문법' 파이프 기호(`|`)를 사용하여 여러 컴포넌트를 연결하고 데이터 흐름을 만드는 방식

- **Component (컴포넌트):** LangChain 애플리케이션을 구성하는 '부품' 또는 '블록' `Model`, `Prompt`, `Output Parser` 등

- **Chain (체인):** 컴포넌트들을 LCEL로 연결하여 만든 하나의 완전한 '작업 흐름' 또는 '파이프라인'

- **Output Parser (출력 파서):** LLM의 출력(보통 복잡한 객체 형태)을 사용하기 쉬운 형식(ex. 순수 텍스트, JSON)으로 변환해주는 컴포넌트

- **Retrieval (검색):** LLM이 알지 못하는 외부 데이터(예: PDF, 웹사이트, 데이터베이스)를 가져와 LLM의 답변에 활용하는 과정 'RAG(Retrieval-Augmented Generation, 검색 증강 생성)'의 핵심 요소.

- **Embedding (임베딩):** 텍스트(단어, 문장)를 컴퓨터가 이해할 수 있는 숫자 벡터(Vector)로 변환하는 과정 또는 그 결과물. 텍스트 간의 의미적 유사도를 계산하는 데 사용.

- **Vector Store (벡터 스토어):** 텍스트의 임베딩 벡터를 효율적으로 저장하고 검색할 수 있도록 설계된 특수한 데이터베이스, Retrieval 과정에서 유사한 문서를 빠르게 찾는 데 사용됨.

- **Agent (에이전트):** LLM을 '추론 엔진'으로 사용하여, 주어진 목표를 달성하기 위해 어떤 도구(Tool)를 어떤 순서로 사용할지 스스로 결정하고 실행하는 컴포넌트.

## 3. 핵심 컴포넌트 1: Models (모델)

애플리케이션의 '뇌' 역할이자 LangChain은 다양한 모델을 쉽게 교체하며 사용할 수 있도록 추상화된 인터페이스를 제공

**기본 사용법 (Python)**

```python
# 필요한 라이브러리 설치
# pip install langchain-openai

from langchain_openai import ChatOpenAI

# ChatModel 객체 생성 (OpenAI의 gpt-4 모델 사용)
# 실행 전 OPENAI_API_KEY 환경 변수 설정이 필요합니다.
chat_model = ChatOpenAI(model="gpt-4")

# 모델에 직접 질문하기 (invoke)
response = chat_model.invoke("대한민국의 수도는 어디야?")

print(response.content)
# 출력: 대한민국의 수도는 서울입니다.
```

## 4. 핵심 컴포넌트 2: Prompts (프롬프트)

모델에게 원하는 작업을 정확하게 지시하기 위한 '지시서' 또는 '템플릿'

- PromptTemplate / ChatPromptTemplate: 프롬프트의 템플릿을 정의합니다.

```python
from langchain_core.prompts import ChatPromptTemplate

# {topic} 이라는 변수를 가진 프롬프트 템플릿 생성
template = ChatPromptTemplate.from_template("{topic}에 대해 초보자도 이해하기 쉽게 설명해줘.")

# 템플릿에 변수 값을 넣어 실제 프롬프트 완성
prompt_value = template.format_prompt(topic="블록체인")

# 생성된 프롬프트 객체를 모델에 전달할 수 있습니다.
# chat_model은 위 3번 항목에서 생성한 객체를 사용합니다.
response = chat_model.invoke(prompt_value)
print(response.content)
```

## 5. 핵심 컴포넌트 3: Chains (체인) - LCEL

LangChain의 가장 핵심적인 개념으로, 여러 컴포넌트를 파이프(|) 기호로 연결하여 데이터의 흐름(파이프라인)을 만듭니다.

- LCEL 기본 구조

```python

[첫 번째 컴포넌트] | [두 번째 컴포넌트] | [세 번째 컴포넌트]

데이터 흐름: 왼쪽에서 오른쪽으로 데이터가 순차적으로 전달됩니다.
결합: 프롬프트, 모델, 출력 파서 등 다양한 컴포넌트를 유연하게 결합할 수 있습니다.

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 모델 준비
chat_model = ChatOpenAI(model="gpt-4")

# 2. 프롬프트 템플릿 준비
prompt = ChatPromptTemplate.from_template("{country}의 대표적인 음식 3가지를 추천해줘.")

# 3. 출력 파서 준비 (모델의 출력 객체에서 텍스트만 깔끔하게 추출)
output_parser = StrOutputParser()

# 4. 체인(Chain)으로 연결 (LCEL 사용)
# [프롬프트] -> [모델] -> [출력 파서] 순서로 데이터가 흐릅니다.
chain = prompt | chat_model | output_parser

# 5. 체인 실행 (invoke)
# 'country' 변수에 '이탈리아'를 넣어 체인을 실행합니다.
result = chain.invoke({"country": "이탈리아"})

print(result)

<결과>
물론이죠! 이탈리아의 대표적인 음식 3가지를 추천해 드릴게요.

1.  **피자 (Pizza):** 전 세계적으로 사랑받는 이탈리아의 상징적인 음식입니다. 특히 나폴리 스타일의 피자는 신선한 토마토소스, 모차렐라 치즈, 바질만으로 맛을 낸 마르게리타 피자가 유명합니다.

2.  **파스타 (Pasta):** 수백 가지 종류의 면과 소스가 조합된 이탈리아의 주식입니다. 로마의 카르보나라, 볼로냐의 볼로네제 라구 소스 파스타 등이 대표적입니다.

3.  **젤라토 (Gelato):** 일반 아이스크림보다 유지방이 적고 밀도가 높아 쫀득한 식감이 특징인 이탈리아식 아이스크림입니다. 식사 후 디저트로 완벽합니다.

```
