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
_build_scene_prompts = None
_build_main_prompt = None
_parse_brief = None
_import_error: Optional[str] = None
try:
    from casts.pipeline import generate as _generate  # noqa: F401
    from casts.formatter import to_text_script as _to_text_script  # noqa: F401
    from casts.mj_scene import build_scene_prompts as _build_scene_prompts  # noqa: F401
    from casts.mj import build_midjourney_prompt as _build_main_prompt  # noqa: F401
    from casts.brief import parse_brief as _parse_brief  # noqa: F401
except Exception as e:
    _import_error = f"{type(e).__name__}: {e}"

# ================= UI =================

st.title("🎬 Shortform Scenario Agent")
st.caption("OpenRouter `gpt-oss-20b:free` 기반 — 2-Step: 시나리오 → (버튼) 씬별 2D 애니 프롬프트")

with st.sidebar:
    st.header("⚙️ Settings")
    key_exists = bool(os.getenv("OPENROUTER_API_KEY"))
    if key_exists:
        st.success("OPENROUTER_API_KEY: detected", icon="🔑")
    else:
        st.warning("Set OPENROUTER_API_KEY in env.", icon="⚠️")

    # 시나리오 옵션
    equalize = st.toggle("Equalize cut times", value=True)
    out_format = st.radio("Scenario Output", ["JSON", "TEXT"], horizontal=True, index=0)

    # 프롬프트 옵션 (stylize 제거됨)
    mj_ar = st.selectbox("MJ Aspect Ratio", ["9:16", "3:4", "1:1", "4:5"], index=0)
    mj_version = st.selectbox("MJ Version", ["6.0", "6.1"], index=0)
    mj_quality = st.selectbox("MJ Quality", ["1.0", "0.5", "2.0"], index=0)

    st.markdown("---")
    st.markdown("Flow: 시나리오 생성 → 아래 결과 확인 → 프롬프트 생성 버튼")

# 임포트 에러 공지
if _import_error:
    st.error(f"Import error: {_import_error}")
    st.info("폴더 구조/경로를 확인해주세요. 그래도 폼은 표시됩니다.")

# 세션 상태 초기화
if "scenario_data" not in st.session_state:
    st.session_state["scenario_data"] = None
if "brief_text" not in st.session_state:
    st.session_state["brief_text"] = ""

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

    btn_generate = st.form_submit_button("🚀 1) 시나리오 생성")


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


# ================= 1) 시나리오 생성 =================
if btn_generate:
    if _generate is None or _to_text_script is None:
        st.error("내부 모듈 로드 실패. 위 임포트 에러 확인.")
    else:
        brief_text = _build_kv_text()
        st.session_state["brief_text"] = brief_text
        with st.status("Generating scenario...", expanded=False) as status:
            status.update(label="Calling OpenRouter & building scenario", state="running")
            try:
                # 1단계는 시나리오만 생성 (MJ 프롬프트 끔)
                data: Dict[str, Any] = _generate(
                    brief_text,
                    equalize=equalize,
                    mj_generate=False,
                )  # type: ignore
            except Exception as err:
                st.error(f"Unexpected error: {type(err).__name__}: {err}")
                status.update(label="Failed", state="error")
            else:
                status.update(label="Done", state="complete")
                st.success("시나리오 생성 완료!", icon="✅")
                st.session_state["scenario_data"] = data

                if isinstance(data, dict) and data.get("error"):
                    st.error(f"Error: {data.get('error')}")
                    detail = data.get("detail") or data.get("raw")
                    if detail:
                        with st.expander("Raw response"):
                            st.code(str(detail))
                else:
                    if out_format == "TEXT":
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

# ================= 2) 프롬프트 생성(2D 애니) =================
st.markdown("---")
st.subheader("🎨 2) 프롬프트 생성 (씬별 2D 애니메이션)")

btn_prompts = st.button("🎬 씬별 프롬프트 생성 (영문 키워드, stylize 제외)")

if btn_prompts:
    data = st.session_state.get("scenario_data")
    brief_text = st.session_state.get("brief_text", "")
    if not data:
        st.warning("먼저 시나리오를 생성해 주세요.")
    elif _build_scene_prompts is None or _parse_brief is None or _build_main_prompt is None:
        st.error("내부 모듈 로드 실패. 위 임포트 에러 확인.")
    else:
        try:
            brief = _parse_brief(brief_text)
            # 씬별 2D 프롬프트 생성 (stylize 없음)
            scene_prompts = _build_scene_prompts(
                brief,
                data,
                aspect_ratio=mj_ar,
                version=mj_version,
            )
            data["scene_prompts"] = scene_prompts

            # 대표 썸네일 프롬프트도 2D로 생성(stylize 없음)
            data["midjourney_prompt"] = _build_main_prompt(
                brief,
                data,
                beat_index=0,
                aspect_ratio=mj_ar,
                version=mj_version,
                quality=float(mj_quality),
            )

            st.success("프롬프트 생성 완료!", icon="✅")
            st.markdown("#### 🎬 Scene Prompts (2D animation)")
            for i, p in enumerate(scene_prompts, 1):
                st.markdown(f"**Scene {i}:**")
                st.code(p)

            st.markdown("#### 🖼️ Main Thumbnail Prompt (2D animation)")
            st.code(data["midjourney_prompt"])

            # 세션 업데이트
            st.session_state["scenario_data"] = data

        except Exception as err:
            st.error(f"Unexpected error: {type(err).__name__}: {err}")
