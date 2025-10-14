import os, sys, json
from dotenv import load_dotenv

# agent 폴더를 파이썬 경로에 추가
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from casts.scenario_agent import generate_scenario

def main():
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
