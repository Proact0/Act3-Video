# Multi Agent Project

이 예제는 LangGraph + Streamlit 기반의 간단한 멀티에이전트 워크플로우를 보여줍니다.  
사용자는 광고 프롬프트를 입력하면 다음 단계를 통해 최종 영상을 생성합니다:

1. Script Agent – 광고 대본 생성
2. Shotlist Agent – 대본 기반 샷리스트 생성
3. TTS Agent – 각 대사에 대한 음성 합성
4. Image Agent – Unsplash API를 이용한 이미지 생성
5. Video Agent – 오디오와 이미지를 합쳐 영상으로 렌더링

근데 아직. 탈모광고밖에 생성을 못합니다.

## 실행 방법

1. 가상환경 활성화 후 필요한 패키지 설치:
   ```bash
   uv pip install -r requirements.txt
   ```
2. 환경변수 설정.
   UNSPLASH_ACCESS_KEY=your_unsplash_api_key
3. streamlit 실행

```
PYTHONPATH=samples/multi_agent/src streamlit run samples/multi_agent/src/ui/app_streamlit.py
```

5. 주의사항

외부 API Key가 없으면 일부 Agent(TTS, Image)는 스킵될 수 있음

moviepy 사용 시 Pillow 버전 문제 발생 가능 → >=10.0 환경에서 실행 권장
