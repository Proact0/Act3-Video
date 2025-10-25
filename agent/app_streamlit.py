# --- 표준 임포트 (E402 규칙 준수: 최상단) ---
import os
import sys
import json
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import streamlit as st

# --- Streamlit 페이지 설정 ---
st.set_page_config(page_title="Shortform Scenario Agent", page_icon="🎬", layout="centered")


def _bootstrap_paths() -> None:
    """agent/ 내부 모듈 임포트를 위해 sys.path 보정"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)


_bootstrap_paths()
load_dotenv()

# 내부 모듈 임포트 (실패해도 UI는 뜨게)
_generate = None
_to_text_script = None
_import_error: Optional[str] = None
try:
    from casts.pipeline import generate as _generate  # noqa: F401
    from casts.formatter import to_text_script as _to_text_script  # noqa: F401
except Exception as e:
    _import_error = f"{type(e).__name__}: {e}"

# ================= UI =================

st.title("🎬 Shortform Scenario Agent")
st.caption("OpenRouter `gpt-oss-20b:free` 기반 — 60초 쇼츠 시나리오 생성 (MJ prompts in English)")

with st.sidebar:
    st.header("⚙️ Settings")
    # 키 상태
    key_exists = bool(os.getenv("OPENROUTER_API_KEY"))
    if key_exists:
        st.success("OPENROUTER_API_KEY: 감지됨", icon="🔑")
    else:
        st.warning("환경변수에 OPENROUTER_API_KEY가 없습니다.", icon="⚠️")

    # 옵션
    equalize = st.toggle("컷 시간 균등 분배(권장)", value=True)
    out_format = st.radio("출력 형식", ["JSON", "텍스트"], horizontal=True, index=0)

    # Midjourney 옵션
    generate_mj = st.toggle("Midjourney 프롬프트 생성(영문)", value=True)
    mj_ar = st.selectbox("MJ Aspect Ratio", ["9:16", "3:4", "1:1", "4:5"], index=0)

    st.markdown("---")
    st.markdown("Tip: 컷 수를 6으로 지정하면 0,10,20,30,40,50초로 자동 분배됩니다.")

# 임포트 에러 공지
if _import_error:
    st.error(f"내부 모듈 임포트 실패: {_import_error}")
    st.info("폴더 구조/경로를 확인해주세요. 그래도 폼은 표시됩니다.")

# 입력 폼
with st.form("scenario_form"):
    st.subheader("📝 Brief (Korean OK)")

    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("제품", placeholder="예: 치킨")
        message = st.text_input("핵심 메시지/USP", placeholder="예: 바삭함과 육즙")
        target = st.text_input("타깃", placeholder="예: 10대~20대")
        background = st.text_input("배경", placeholder="예: 퇴근길 작은 포장마차")
    with col2:
        tone = st.text_input("톤(쉼표로 구분)", placeholder="예: 따뜻함, 레트로")
        narration = st.text_input("나레이션/대사 스타일", placeholder="예: 담백하고 현실적으로")
        music = st.text_input("음악 키워드", placeholder="예: 어쿠스틱 기타")
        banned = st.text_input("금지어(쉼표로 구분)", placeholder="예: 치료, 다이어트")

    st.markdown("### ⏱️ 길이 & 컷")
    dur_col, cuts_col = st.columns(2)
    with dur_col:
        duration = st.number_input("길이(초)", min_value=5, max_value=120, value=60, step=5)
    with cuts_col:
        cuts = st.number_input("컷 수(0=자동)", min_value=0, max_value=12, value=6, step=1)

    submitted = st.form_submit_button("🚀 시나리오 생성")


def _kv_line(k: str, v: str) -> str:
    return f"{k}={v}" if v is not None and v != "" else ""


def _build_kv_text() -> str:
    lines = [
        _kv_line("제품", product),
        _kv_line("메시지", message),
        _kv_line("타깃", target),
        _kv_line("톤", tone),
        _kv_line("배경", background),
        _kv_line("길이", str(duration)),
        _kv_line("컷", str(cuts) if cuts > 0 else ""),
        _kv_line("나레이션", narration),
        _kv_line("음악", music),
        _kv_line("금지어", banned),
    ]
    return "\n".join([x for x in lines if x])


# ================= RUN =================
if submitted:
    brief_text = _build_kv_text()

    if _generate is None or _to_text_script is None:
        st.error("내부 모듈이 로드되지 않아 실행할 수 없습니다. 위의 임포트 에러를 확인하세요.")
    else:
        with st.status("생성 중...", expanded=False) as status:
            status.update(label="OpenRouter 호출 & 시나리오 생성", state="running")
            try:
                data: Dict[str, Any] = _generate(
                    brief_text,
                    equalize=equalize,
                    mj_generate=generate_mj,      # EN MJ prompts on
                    mj_aspect_ratio=mj_ar,
                )  # type: ignore
            except Exception as err:
                st.error(f"예상치 못한 에러: {type(err).__name__}: {err}")
                status.update(label="실패", state="error")
            else:
                status.update(label="완료", state="complete")
                st.success("시나리오 생성 완료!", icon="✅")

                if isinstance(data, dict) and data.get("error"):
                    st.error(f"에러: {data.get('error')}")
                    detail = data.get("detail") or data.get("raw")
                    if detail:
                        with st.expander("상세 보기"):
                            st.code(str(detail))
                else:
                    # 텍스트/JSON 출력
                    if out_format == "텍스트":
                        try:
                            script = _to_text_script(data)  # type: ignore
                        except Exception:
                            script = json.dumps(data, ensure_ascii=False, indent=2)
                        st.code(script)
                    else:
                        try:
                            st.json(data)
                        except Exception:
                            st.code(json.dumps(data, ensure_ascii=False, indent=2))

                    # MJ 프롬프트 섹션
                    if isinstance(data, dict) and data.get("scene_prompts"):
                        st.markdown("#### 🎬 Scene-by-Scene Prompts (English)")
                        for i, p in enumerate(data["scene_prompts"], 1):
                            st.markdown(f"**Scene {i}:**")
                            st.code(p)
                    if isinstance(data, dict) and data.get("midjourney_prompt"):
                        st.markdown("#### 🎨 Main Thumbnail Prompt (English)")
                        st.code(data["midjourney_prompt"])

# 하단 도움말
with st.expander("입력 예시 보기"):
    st.code(
        """제품=치킨
메시지=바삭함과 육즙
타깃=10대~20대
톤=따뜻함, 레트로
배경=퇴근길 작은 포장마차
길이=60
컷=6
나레이션=담백하고 현실적으로
음악=어쿠스틱 기타
금지어=치료""",
        language="text",
    )
