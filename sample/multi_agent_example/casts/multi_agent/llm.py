import os
from typing import Optional

from dotenv import load_dotenv

# pip: langchain-google-genai
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def make_llm(model: str = "gemini-1.5-flash", temperature: float = 0.6) -> ChatGoogleGenerativeAI:
    """
    Google Generative AI (Gemini) Chat 모델 래퍼.
    환경변수 GOOGLE_API_KEY 필요.
    """
    api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY 가 설정되지 않았습니다. 루트에 .env 파일을 만들고 키를 넣어주세요.\n"
            "예) GOOGLE_API_KEY=xxxxxxxxxxxxxxxx"
        )

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
    )
