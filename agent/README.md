# 🎬 Shortform Scenario Agent (OpenRouter 기반)

## 📘 개요

이 프로젝트는 OpenRouter의 **GPT-OSS-20B 모델**을 활용해  
TikTok, Reels, Shorts용 **60초 시나리오**를 자동 생성하는 에이전트입니다.  
현재는 기본 뼈대와 OpenRouter 연동이 완료된 상태입니다.

---

## ⚙️ 실행 방법

### 1. 폴더 이동

```bash
cd agent
```

### 2. 환경변수 설정

```bash
OPENROUTER_API_KEY=sk-여기에_키_입력
```

### 3. 의존성 설치

```bash
uv sync
```

### 4. 실행

```bash
uv run python main.py
```

### 5. 입력 예시

````bash
제품=복숭아향 향수
메시지=첫사랑의 향기처럼 설렘
타깃=10대~20대 여학생
톤=핑크, 맑음, 투명
배경=햇살 드는 교실 창가
길이=60
컷=6
나레이션=잔잔하고 몽환적으로
음악=로맨틱 피아노
금지어=다이어트, 치료
```ß

### 6. 스트림릿 실행
```bash
cd agent
uv run streamlit run app_streamlit.py
````
