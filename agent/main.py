import os
import sys
import json
import argparse
from dotenv import load_dotenv


def main() -> None:
    # === 기본 경로 설정 ===
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    # === 내부 모듈 불러오기 ===
    from casts.brief import get_brief_guide, build_brief_interactively, brief_to_kv_lines
    from casts.pipeline import generate
    from casts.formatter import to_text_script

    # === 환경변수 로드 ===
    load_dotenv()

    # === CLI 옵션 정의 ===
    parser = argparse.ArgumentParser(description="Shortform Scenario Agent (OpenRouter 기반)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="출력 형식 선택")
    parser.add_argument("--cuts", type=int, help="강제 컷 수 (예: 6)")
    parser.add_argument("--duration", type=int, default=60, help="영상 길이(초, 기본 60)")
    parser.add_argument("--no-equalize", dest="no_equalize", action="store_true", help="컷별 균등 분배 끄기")
    args = parser.parse_args()

    # === 인트로 출력 ===
    print("🎬 쇼츠 시나리오 에이전트 (OpenRouter 기반)\n")
    print(get_brief_guide())

    # === 사용자 입력 ===
    try:
        user_raw = input("그대로 입력(엔터=간단 입력 모드): ").strip()
    except EOFError:
        user_raw = ""

    # === 브리프 처리 ===
    if user_raw:
        brief_text = user_raw
    else:
        b = build_brief_interactively()
        # CLI 옵션으로 덮어쓰기
        if args.cuts:
            b.cuts = max(1, min(12, args.cuts))
        if args.duration:
            b.duration_sec = max(5, min(120, args.duration))
        brief_text = brief_to_kv_lines(b)
        print("\n[입력 요약]\n" + brief_text)

    # === 에이전트 실행 ===
    data = generate(brief_text, equalize=(not args.no_equalize))

    # === 결과 보정 (선택) ===
    if isinstance(data, dict) and "error" not in data:
        if args.cuts and ("beats" in data):
            from casts.pipeline import _equalize_timeline  # noqa: E402
            _equalize_timeline(data, args.duration, args.cuts)

    # === 출력 ===
    print("\n=== 생성 결과 ===")
    if args.format == "text" and isinstance(data, dict) and "error" not in data:
        print(to_text_script(data))
    else:
        try:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            print(data)


if __name__ == "__main__":
    main()
