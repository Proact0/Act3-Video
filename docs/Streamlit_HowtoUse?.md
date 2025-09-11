# Streamlit 사용 방법 (With VSCODE)

## 1. 스트림릿이란?

- 파이썬 코드만으로 웹 앱을 쉽게 만들 수 있는 오픈소스 프레임워크
- 데이터 분석, 인공지능 모델 시각화, 대시보드 제작에 자주 활용됨
- HTML, CSS, 자바스크립트 몰라도 웹 앱이 제작 가능하다!!!

### 스트림릿을 설치하기 전에!!

1.  Python 최신 버전 설치
2.  VSCODE + 확장프로그램(Python)

## 2. 설치 방법

### 1. 폴더 만들기 & VS Code 열기

```bash
# 원하는 위치에서
mkdir my-streamlit-app
cd my-streamlit-app
```

### 2. 가상환경 만들기 & 활성화

> macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows(PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\activate
```

- VSCode 오른쪽 아래에서 인터프리터 선택 팝업이 뜨면 ".venv" 선택
  안뜨면 Ctrl/Cmd + shift + P -> "Python: Select Interpreter" -> .venv 선택.

### 3. 스트림릿 설치

```bash
pip install --upgrade pip
pip install streamlit pandas numpy
pip install Altair
```

#pandas numpy: 파이썬의 대표적인 데이터 분석, 계산용 패키지이자
스트림릿에서 데이터를 다루고 시각화 할 때 자주 함께 사용됨
#Altair는 데이터 분석과 관련된 소프트웨어임.

### 4. 첫앱 만들기(app.py)

#지금까지 설치한 환경이 정상적으로 작동하는지 확인해보겠습니다.

- VS Code에서 app.py 파일을 만들고 아래 코드 붙여넣기

```python
import streamlit as st

st.title("나의 첫 스트림릿 앱 🎉")
st.write("환경이 잘 준비되었다는 뜻이에요!")
```

### 5. 실행하기

#### 방법 A. 터미널

```bash
streamlit run app.py
```

- 자동으로 브라우저가 열리며 기본 주소는 http://localhost:8501
- 코드 저장하면 자동 반영(핫 리로드)

#### 방법 B. VS Code 런 버튼

- 상단 “Run > Run Without Debugging” 또는 우측 상단 ▶️로 실행
- 명령이 streamlit run app.py로 되어 있는지 확인

#종료 방법은 Ctrl + C 를 터미널에 적으면 된다.

---

### 6. 기본문법 & 위젯 체험

첫 앱이 성공적으로 실행되었다면, 스트림릿을 통해 파이썬 코드 몇 줄만으로 버튼, 입력창, 슬라이더 같은 다양한 위젯을 쉽게 추가하는 방법에 대해 설명하겠습니다.

#그전에 저희는 스티림릿을 st로 치환한 상태로 진행해야하니 꼭 맨 윗줄에는 아래의 사항을 적어주세요

```python
import streamlit as st
```

#### 1) 텍스트와 제목

```python
st.title("스트림릿 기본 문법 ✨")
st.header("이것은 헤더입니다")
st.subheader("이것은 서브헤더입니다")
st.write("이건 일반 텍스트에요!")
```

#### 2) 버튼과 입력창

```python
name = st.text_input("이름을 입력하세요")
if st.button("눌러보세요!"):
    st.write(f"반가워요, {name}님!")
```

#### 3) 슬라이더

```python
age = st.slider("나이를 선택하세요", 1, 100, 20)
st.write(f"나이는 {age}살이군요!")
```

👉 이렇게 간단한 위젯들을 사용해보면, 스트림릿이 단순한 출력 도구가 아니라
실제로 움직이는 웹 앱이라는 걸 확실히 체감할 수 있어요.
앞으로는 데이터를 불러와서 시각화도 해보고, 페이지를 더 예쁘게 꾸며볼 거예요.

### 7. 데이터 다루기 & 차트

스트림릿은 단순히 글자나 버튼만 보여주는 게 아니라,
데이터 분석 결과를 시각적으로 표현하는 데 최적화되어 있습니다.
판다스(Pandas)와 넘파이(NumPy)를 함께 쓰면 엑셀 같은 표도 만들고, 그래프나 차트를 바로 웹에 띄울 수 있습니다.

#### 1) 데이터프레임

```python
import pandas as pd

data = {
    "이름": ["철수", "영희", "민수", "수지"],
    "점수": [85, 90, 78, 92],
}
df = pd.DataFrame(data)

st.write("학생 점수표")
st.dataframe(df)  # 스크롤/정렬 가능한 표
```

#### 2) 차트

```python
import numpy as np

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["국어", "영어", "수학"]
)

st.line_chart(chart_data)   # 선 그래프
st.bar_chart(chart_data)    # 막대 그래프
```

#### 3) 조금 더 예쁘게 만들기

스트림릿은 Altair, Plotly 와 같은 시각화 라이브러리도 지원합니다!

```python
import altair as alt

chart = alt.Chart(chart_data.reset_index()).mark_line().encode(
    x='index:Q',    # Q = Quantitative (숫자형)
    y='국어:Q'
)

st.altair_chart(chart, use_container_width=True)

```

👉 이 단계까지 오면, 단순한 페이지가 아니라
“데이터 → 표 → 차트 → 상호작용” 이 흐름이 다 연결돼서
진짜 대시보드 같은 느낌을 만들 수 있어요. 🚀

### 8. 레이아웃 꾸미기

웹 앱은 보기 좋고, 사용하기 편해야 하잖아요
스트림릿은 복잡한 CSS나 HTML을 몰라도 사이드바, 컬럼, 확장 박스 같은 레이아웃 기능을 바로 쓸 수 있게 해줍니다.

#### 1) 사이드바

사이드바는 보통 설정이나 필터 같은 걸 넣을 때 사용합니다.

```python
st.sidebar.title("사이드바 메뉴")
option = st.sidebar.selectbox("메뉴를 고르세요", ["홈", "데이터", "설정"])
st.sidebar.write("선택된 메뉴:", option)
```

#### 2) 컬럼

한 줄에 여러 개의 요소를 나란히 배치할 수 있습니다.

```python
col1, col2 = st.columns(2)

with col1:
    st.subheader("왼쪽 칸")
    st.write("여기에 내용 추가")

with col2:
    st.subheader("오른쪽 칸")
    st.write("여기에 다른 내용 추가")
```

#### 3) 확장 박스

처음에는 접혀 있다가, 클릭하면 펼쳐지는 구조입니다.

```python
with st.expander("자세히 보기"):
    st.write("여기에 추가 설명이나 데이터 표 등을 넣을 수 있습니다.")
```

#### 4) 탭 레이아웃

탭을 사용하면 관련된 내용을 그룹으로 묶을 수 있어요.

```python
tab1, tab2 = st.tabs(["차트 보기", "데이터 보기"])

with tab1:
    st.line_chart(chart_data)

with tab2:
    st.dataframe(chart_data)
```

### 9. 앱 배포하기

이제 로컬에서만 보던 앱을 url 로 공유해볼 것입니다. GitHub에 올려서 클릭 몇 번만 하면 됩니다.

#### 0) 준비 체크

- 'app.py'가 저장소 루트에 있는지 확인해주세요
- 'requirements.txt'에 필요한 패키지 기록

```bash
pip freeze > requirements.txt
```

#### 1) GitHub에 올리기

```bash
git init
git add .
git commit -m "feat: first streamlit app"
git branch -M main
git remote add origin https://github.com/<your-id>/<repo>.git
git push -u origin main
```

#### 2) Streamlit Cloud 접속 & 배포

```
1. https://share.streamlit.io
(또는 https://streamlit.io -> Sign in)
2. New app 클릭 → GitHub 저장소/브랜치 선택
3. Main file path에 app.py 경로 입력 (예: app.py or src/app.py)
4. Deploy 클릭 → 잠시 후 배포 완료, 공유용 URL 발급

이후에는 git push만 하면 자동으로 재배포됨(빌드 후 최신화).
```

#### 3) 비밀키/토큰관리

API 키나 비밀번호는 코드에 넣지 말고 Secrets 에 저장:

##### 1. 배포된 앱의 -> setting -> Secrets

##### 2. 예시

```toml
API_KEY = "xxxxxx"
```

##### 3.코드에서 사용

```python
import streamlit as st
api_key = st.secrets["API_KEY"]
```

#### 4) 파이썬 고정

runtime.txt 파일 추가:

```
python-3.1X.X
```

#### 5) 자주 겪는 이슈 & 해결

- ModuleNotFoundError: requirements.txt에 패키지 누락 → 추가 후 커밋/푸시

- Main file not found: Main file path 오타 → 배포 설정에서 경로 수정

- Secrets KeyError: 키 이름 불일치 → Secrets 페이지와 코드의 키 철자 확인

- 대용량 파일/모델 로딩 느림: 최초 빌드가 느릴 수 있음 → 캐싱(@st.cache_data) 활용

- pages 폴더: 멀티 페이지는 pages/01\_...py 형태로 두면 자동 탭 생성

#### 6) 로컬 공유(빠르게 보여주기)

같은 네트워크에서:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

상대방은 http://<내IP>:8501 접속

이제 url 하나로 누구에게나 보여줄 수 있습니다.
