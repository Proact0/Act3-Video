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
code .
```

### 2. 가상환경 만들기 & 활성화

> macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windowws(PowerShell)

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
```

#pandas numpy: 파이썬의 대표적인 데이터 분석, 계산용 패키지이자
스트림릿에서 데이터를 다루고 시각화 할 때 자주 함께 사용됨
