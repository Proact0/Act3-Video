import os
import sys
import json
from dotenv import load_dotenv


def main() -> None:
    # 경로 보정은 함수 안에서 처리 → E402 회피
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    # 상대 임포트가 아닌 패키지 임포트, 함수 안에서 수행
    from casts.scenario_agent import generate_scenario  # noqa: E402

    load_dotenv()

    print("🎬 쇼츠 시나리오 에이전트 (OpenRouter 기반)")
    try:
        brief = input("브리프를 입력하세요 (예: 제품=콜드브루, 톤=쿨&미니멀, 타깃=20대): ").strip()
    except EOFError:
        brief = ""
    if not brief:
        brief = "제품=콜드브루, 톤=쿨&미니멀, 타깃=20대"

    data = generate_scenario(brief)

    print("\n=== 생성된 시나리오 ===")
    try:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        print(data)


if __name__ == "__main__":
    main()
